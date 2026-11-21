from enum import Enum
from uuid import uuid4
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.database import get_db
from app.schemas.document import DocumentUploadResponse
from app.services.ingestion_service import process_document
from app.services.vector_service import store_chunks
from app.repositories.document_repository import create_document

router = APIRouter()
class ChunkingStrategy(str, Enum):
    FIXED_SIZE = "fixed_size"
    RECURSIVE = "recursive"

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...), chunking_strategy: ChunkingStrategy = Form(ChunkingStrategy.RECURSIVE), db: Session = Depends(get_db)) -> DocumentUploadResponse:
    filename = file.filename or ""
    if not filename.lower().endswith((".pdf", ".txt")):
        raise HTTPException(status_code=400, detail="Only PDF and TXT files are accepted")
    content = await file.read()
    await file.close()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    if len(content) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File exceeds {settings.max_upload_mb} MB limit")
    if filename.lower().endswith(".pdf") and not content.startswith(b"%PDF"):
        raise HTTPException(status_code=400, detail="File does not appear to be a valid PDF")
    if filename.lower().endswith(".txt"):
        try:
            content.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise HTTPException(status_code=400, detail="TXT must be UTF-8 encoded") from exc
    try:
        processed = process_document(content, filename, chunking_strategy.value)
        doc_id = str(uuid4())
        store_chunks(doc_id, filename, processed.chunks)
        create_document(db, document_id=doc_id, filename=filename, strategy=chunking_strategy.value, chunk_count=len(processed.chunks), extracted_characters=len(processed.extracted_text))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Processing service error: {exc}") from exc
    return DocumentUploadResponse(document_id=doc_id, filename=filename, chunking_strategy=chunking_strategy.value, extracted_characters=len(processed.extracted_text), chunks_created=len(processed.chunks), message="Document processed and indexed successfully")

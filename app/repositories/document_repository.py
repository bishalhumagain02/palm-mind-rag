from sqlalchemy.orm import Session
from app.db.models import DocumentRecord

def create_document(db: Session, *, document_id: str, filename: str, strategy: str, chunk_count: int, extracted_characters: int) -> DocumentRecord:
    record = DocumentRecord(id=document_id, filename=filename, strategy=strategy, chunk_count=chunk_count, extracted_characters=extracted_characters)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

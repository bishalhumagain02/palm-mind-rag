from dataclasses import dataclass
from app.core.config import settings
from app.services.document_extraction import clean_text, extract_document_text
from app.services.chunking_service import chunk_text

@dataclass
class ProcessedDocument:
    extracted_text: str
    chunks: list[str]

def process_document(content: bytes, filename: str, strategy: str) -> ProcessedDocument:
    text = clean_text(extract_document_text(content, filename))
    if not text:
        raise ValueError("No readable text was found in this document")
    chunks = chunk_text(text, strategy, settings.chunk_size, settings.chunk_overlap)
    return ProcessedDocument(extracted_text=text, chunks=chunks)

from pydantic import BaseModel

class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    chunking_strategy: str
    extracted_characters: int
    chunks_created: int
    message: str

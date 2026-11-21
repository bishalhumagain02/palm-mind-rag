from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=100)
    question: str = Field(min_length=1, max_length=8000)

class ChatResponse(BaseModel):
    session_id: str
    answer: str
    source_documents: list[dict[str, str]] = []
    booking_id: str | None = None

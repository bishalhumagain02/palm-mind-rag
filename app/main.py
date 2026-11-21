from fastapi import FastAPI
from app.api.routes.documents import router as documents_router
from app.api.routes.chat import router as chat_router
from app.core.config import settings
from app.db.database import init_db

app = FastAPI(title=settings.app_name, version="1.0.0", description="Document ingestion and custom RAG chat backend")

@app.on_event("startup")
def startup() -> None:
    init_db()

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}

app.include_router(documents_router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(chat_router, prefix="/api/v1/chat", tags=["Chat and bookings"])

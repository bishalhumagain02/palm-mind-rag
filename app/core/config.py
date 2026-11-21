from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Palm Mind AI RAG Backend"

    # Gemini configuration
    gemini_api_key: str = ""
    gemini_chat_model: str = "gemini-2.5-flash"
    gemini_embedding_model: str = "gemini-embedding-001"
    embedding_dimensions: int = 3072

    # Qdrant
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "document_chunks"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # PostgreSQL
    database_url: str = (
        "postgresql+psycopg://raguser:ragpassword"
        "@localhost:5432/ragdb"
    )

    # Chunking
    chunk_size: int = 1000
    chunk_overlap: int = 150

    # Upload
    max_upload_mb: int = 10

    # Timezone
    timezone: str = "Asia/Kathmandu"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
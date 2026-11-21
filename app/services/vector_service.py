from uuid import uuid4

from google import genai
from google.genai import types
from qdrant_client import QdrantClient, models

from app.core.config import settings


# Gemini client
gemini_client = genai.Client(
    api_key=settings.gemini_api_key
)

# Qdrant client
qdrant = QdrantClient(
    url=settings.qdrant_url
)


def ensure_collection() -> None:
    """Create the Qdrant collection if it does not exist."""

    existing = {
        collection.name
        for collection in qdrant.get_collections().collections
    }

    if settings.qdrant_collection not in existing:
        qdrant.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=models.VectorParams(
                size=settings.embedding_dimensions,
                distance=models.Distance.COSINE,
            ),
        )


def embed_texts(
    texts: list[str],
    task_type: str = "RETRIEVAL_DOCUMENT",
) -> list[list[float]]:
    """Generate embeddings using Gemini."""

    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Set it in your .env file."
        )

    if not texts:
        return []

    result = gemini_client.models.embed_content(
        model=settings.gemini_embedding_model,
        contents=texts,
        config=types.EmbedContentConfig(
            task_type=task_type,
            output_dimensionality=settings.embedding_dimensions,
        ),
    )

    return [
        embedding.values
        for embedding in result.embeddings
    ]


def store_chunks(
    document_id: str,
    filename: str,
    chunks: list[str],
) -> None:
    """Embed chunks and store them in Qdrant."""

    ensure_collection()

    vectors = embed_texts(
        chunks,
        task_type="RETRIEVAL_DOCUMENT",
    )

    points = [
        models.PointStruct(
            id=str(uuid4()),
            vector=vector,
            payload={
                "document_id": document_id,
                "filename": filename,
                "chunk_index": index,
                "text": chunk,
            },
        )
        for index, (chunk, vector) in enumerate(
            zip(chunks, vectors, strict=True)
        )
    ]

    qdrant.upsert(
        collection_name=settings.qdrant_collection,
        points=points,
        wait=True,
    )


def search_chunks(
    question: str,
    limit: int = 5,
) -> list[dict[str, str]]:
    """Search Qdrant using the question embedding."""

    ensure_collection()

    vector = embed_texts(
        [question],
        task_type="RETRIEVAL_QUERY",
    )[0]

    hits = qdrant.query_points(
        collection_name=settings.qdrant_collection,
        query=vector,
        limit=limit,
        with_payload=True,
    ).points

    return [
        {
            "text": str(hit.payload.get("text", "")),
            "filename": str(
                hit.payload.get("filename", "")
            ),
            "document_id": str(
                hit.payload.get("document_id", "")
            ),
            "score": str(hit.score),
        }
        for hit in hits
    ]
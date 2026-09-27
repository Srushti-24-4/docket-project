"""Thin wrapper around the Qdrant client: collection setup, upsert, and search."""
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchAny, MatchValue

from app.core.config import get_settings
from app.models.schemas import Chunk, SearchResult

settings = get_settings()
EMBEDDING_DIM = 768  # matches OUTPUT_DIM in embeddings.py

_client: QdrantClient | None = None


def get_client() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key or None)
        _ensure_collection(_client)
    return _client


def _ensure_collection(client: QdrantClient) -> None:
    existing = [c.name for c in client.get_collections().collections]
    if settings.qdrant_collection not in existing:
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
        )


def upsert_chunks(chunks: list[Chunk], vectors: list[list[float]]) -> None:
    client = get_client()
    points = [
        PointStruct(
            id=chunk.id,
            vector=vector,
            payload=chunk.model_dump(),
        )
        for chunk, vector in zip(chunks, vectors)
    ]
    client.upsert(collection_name=settings.qdrant_collection, points=points)


def search(
    query_vector: list[float],
    user_id: str,
    top_k: int = 20,
    document_ids: list[str] | None = None,
) -> list[SearchResult]:
    client = get_client()

    must_conditions = [FieldCondition(key="user_id", match=MatchValue(value=user_id))]
    if document_ids:
        must_conditions.append(FieldCondition(key="document_id", match=MatchAny(any=document_ids)))

    hits = client.search(
        collection_name=settings.qdrant_collection,
        query_vector=query_vector,
        limit=top_k,
        query_filter=Filter(must=must_conditions),
    )

    return [
        SearchResult(chunk=Chunk(**hit.payload), score=hit.score)
        for hit in hits
    ]

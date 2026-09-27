"""Wraps the Gemini embeddings API. Batches requests and retries transient failures.

Uses the current `google-genai` SDK (the old `google-generativeai` package is
deprecated and its model names, like "embedding-001", are no longer served).
"""
from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import get_settings

settings = get_settings()
client = genai.Client(api_key=settings.gemini_api_key)

BATCH_SIZE = 32
OUTPUT_DIM = 768  # must match EMBEDDING_DIM in vector_store.py


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
def _embed_batch(texts: list[str], task_type: str) -> list[list[float]]:
    result = client.models.embed_content(
        model=settings.gemini_embedding_model,
        contents=texts,
        config=types.EmbedContentConfig(
            task_type=task_type,
            output_dimensionality=OUTPUT_DIM,
        ),
    )
    return [e.values for e in result.embeddings]


def embed_documents(texts: list[str]) -> list[list[float]]:
    """Embed chunk text for storage. Uses task_type=RETRIEVAL_DOCUMENT."""
    vectors: list[list[float]] = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        vectors.extend(_embed_batch(batch, task_type="RETRIEVAL_DOCUMENT"))
    return vectors


def embed_query(text: str) -> list[float]:
    """Embed a user question. Uses task_type=RETRIEVAL_QUERY for asymmetric search."""
    return _embed_batch([text], task_type="RETRIEVAL_QUERY")[0]

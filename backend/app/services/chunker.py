"""
Semantic chunking.

Splits page text into overlapping chunks along sentence boundaries rather
than a hard character cutoff. Each chunk keeps a reference back to its
source page and owning user, which is what lets Docket cite an exact page
and scope search results per user later.
"""
import re
import uuid
from app.models.schemas import Chunk, DocumentRoute

TARGET_CHUNK_CHARS = 1200
OVERLAP_CHARS = 150


def _split_into_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    return re.split(r"(?<=[.!?])\s+", text)


def chunk_pages(
    pages: list[dict],
    document_id: str,
    user_id: str,
    filename: str,
    route: DocumentRoute,
) -> list[Chunk]:
    chunks: list[Chunk] = []

    for page in pages:
        sentences = _split_into_sentences(page["text"])
        if not sentences:
            continue

        buffer = ""
        for sentence in sentences:
            if len(buffer) + len(sentence) + 1 > TARGET_CHUNK_CHARS and buffer:
                chunks.append(_make_chunk(buffer, document_id, user_id, filename, page["page"], route))
                buffer = buffer[-OVERLAP_CHARS:] + " " + sentence
            else:
                buffer = (buffer + " " + sentence).strip()

        if buffer.strip():
            chunks.append(_make_chunk(buffer, document_id, user_id, filename, page["page"], route))

    return chunks


def _make_chunk(text: str, document_id: str, user_id: str, filename: str, page: int, route: DocumentRoute) -> Chunk:
    return Chunk(
        id=str(uuid.uuid4()),
        document_id=document_id,
        user_id=user_id,
        filename=filename,
        page=page,
        text=text.strip(),
        route=route,
    )

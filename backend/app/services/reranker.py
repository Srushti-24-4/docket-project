"""
Lightweight lexical reranker applied on top of vector search.

Qdrant's cosine search gives good recall; this reranker re-scores the
top candidates using a simple term-overlap signal so that chunks which
literally contain the question's key terms (numbers, proper nouns) are
promoted above merely-similar-in-meaning chunks. Swap this out for a
cross-encoder model if higher precision is needed later.
"""
import re
from app.models.schemas import SearchResult

_STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "of", "to", "in", "on",
    "for", "and", "or", "what", "how", "did", "does", "do", "with", "that",
}


def _keywords(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return {w for w in words if w not in _STOPWORDS and len(w) > 2}


def rerank(query: str, results: list[SearchResult], top_k: int = 8) -> list[SearchResult]:
    query_terms = _keywords(query)
    if not query_terms:
        return results[:top_k]

    def combined_score(result: SearchResult) -> float:
        chunk_terms = _keywords(result.chunk.text)
        overlap = len(query_terms & chunk_terms) / max(len(query_terms), 1)
        # blend vector similarity with lexical overlap
        return 0.7 * result.score + 0.3 * overlap

    reranked = sorted(results, key=combined_score, reverse=True)
    return reranked[:top_k]

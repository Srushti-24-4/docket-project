"""
Evidence Verification.

A cheap final check before an answer is returned to the user: confirm the
sentences in the generated answer actually overlap with the cited source
chunks, and assign each citation a confidence score based on that overlap.
This catches cases where the model cited a passage but drifted from it.
"""
import re
from app.models.schemas import SearchResult, Citation

_STOPWORDS = {"the", "a", "an", "is", "are", "was", "were", "of", "to", "in", "on", "for", "and"}


def _keywords(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return {w for w in words if w not in _STOPWORDS and len(w) > 2}


def verify_and_build_citations(
    answer: str,
    used_indices: list[int],
    results: list[SearchResult],
) -> tuple[list[Citation], bool]:
    answer_terms = _keywords(answer)
    citations: list[Citation] = []

    for idx in used_indices:
        pos = idx - 1
        if pos < 0 or pos >= len(results):
            continue
        chunk = results[pos].chunk
        chunk_terms = _keywords(chunk.text)
        overlap = len(answer_terms & chunk_terms) / max(len(answer_terms), 1)

        snippet = chunk.text[:220].strip()
        citations.append(
            Citation(
                filename=chunk.filename,
                page=chunk.page,
                snippet=snippet + ("…" if len(chunk.text) > 220 else ""),
                confidence=round(min(overlap * 1.4, 1.0), 2),
            )
        )

    verified = len(citations) > 0 and all(c.confidence >= 0.15 for c in citations)
    return citations, verified

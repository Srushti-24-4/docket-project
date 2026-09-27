"""Calls Gemini to produce a grounded answer from retrieved chunks.

Uses the current `google-genai` SDK. Retries automatically on transient
server-side errors (e.g. "503 UNAVAILABLE, model experiencing high demand"),
which Gemini returns periodically and which resolve on their own.
"""
from google import genai
from google.genai import types
from google.genai.errors import ServerError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.core.config import get_settings
from app.models.schemas import SearchResult

settings = get_settings()
client = genai.Client(api_key=settings.gemini_api_key)

SYSTEM_PROMPT = """You are Docket, a document question-answering assistant.
Answer ONLY using the numbered context passages below. Every factual claim
must be traceable to a passage. If the passages don't contain the answer,
say so plainly instead of guessing.

After your answer, on a new line, list which passage numbers you used,
like: SOURCES: [1, 3]
"""


def _build_context(results: list[SearchResult]) -> str:
    lines = []
    for i, r in enumerate(results, start=1):
        lines.append(f"[{i}] (source: {r.chunk.filename}, page {r.chunk.page})\n{r.chunk.text}")
    return "\n\n".join(lines)


@retry(
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=2, min=2, max=20),
    retry=retry_if_exception_type(ServerError),
    reraise=True,
)
def _call_gemini(prompt: str) -> str:
    response = client.models.generate_content(
        model=settings.gemini_chat_model,
        contents=prompt,
        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
    )
    return response.text


def generate_answer(question: str, results: list[SearchResult]) -> tuple[str, list[int]]:
    context = _build_context(results)
    try:
        raw_text = _call_gemini(f"Context passages:\n\n{context}\n\nQuestion: {question}")
    except ServerError as exc:
        # Gemini is overloaded even after retries — fail gracefully instead
        # of a raw 500, so the frontend can show something sensible.
        return (
            "Gemini is temporarily overloaded and didn't respond after several retries. "
            "Please try asking again in a moment.",
            [],
        )

    answer, used_indices = _split_sources(raw_text)
    return answer, used_indices


def _split_sources(raw_text: str) -> tuple[str, list[int]]:
    if "SOURCES:" not in raw_text:
        return raw_text.strip(), []

    answer_part, _, sources_part = raw_text.partition("SOURCES:")
    indices = []
    for token in sources_part.replace("[", "").replace("]", "").split(","):
        token = token.strip()
        if token.isdigit():
            indices.append(int(token))
    return answer_part.strip(), indices

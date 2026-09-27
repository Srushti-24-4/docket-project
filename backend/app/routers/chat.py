from fastapi import APIRouter, HTTPException, Depends

from app.core.security import get_current_user_id
from app.models.schemas import ChatRequest, ChatResponse
from app.services import embeddings, vector_store, reranker, llm, verification

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def ask(
    payload: ChatRequest,
    user_id: str = Depends(get_current_user_id),
) -> ChatResponse:
    if not payload.question.strip():
        raise HTTPException(400, "question must not be empty")

    # 1. Embed the question
    query_vector = embeddings.embed_query(payload.question)

    # 2. Vector search, scoped to this user's documents (and optionally a subset of them)
    candidates = vector_store.search(
        query_vector, user_id=user_id, top_k=20, document_ids=payload.document_ids
    )
    if not candidates:
        return ChatResponse(
            answer="I couldn't find any relevant content in your uploaded documents.",
            citations=[],
            verified=False,
        )

    # 3. Rerank down to the best few chunks
    top_results = reranker.rerank(payload.question, candidates, top_k=payload.top_k)

    # 4. Generate a grounded answer with Gemini
    answer, used_indices = llm.generate_answer(payload.question, top_results)

    # 5. Evidence verification pass
    citations, verified = verification.verify_and_build_citations(answer, used_indices, top_results)

    return ChatResponse(answer=answer, citations=citations, verified=verified)

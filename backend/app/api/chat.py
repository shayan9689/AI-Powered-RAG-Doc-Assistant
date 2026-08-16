import json
from collections.abc import Iterator

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.api.deps import (
    get_app_store,
    get_embedder,
    get_llm,
    get_user_id,
    get_vector_store,
)
from app.persistence.store import AppStore
from app.rag.embeddings.base import EmbeddingClient
from app.rag.generation.base import LLMClient
from app.rag.generation.exceptions import GenerationError
from app.rag.retrieval.base import VectorStore
from app.rag.retrieval.exceptions import RetrievalError
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.generation import answer_question

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    embedder: EmbeddingClient = Depends(get_embedder),
    vector_store: VectorStore = Depends(get_vector_store),
    llm: LLMClient = Depends(get_llm),
    store: AppStore = Depends(get_app_store),
    user_id: str = Depends(get_user_id),
) -> ChatResponse:
    try:
        return answer_question(
            payload.query,
            embedder=embedder,
            vector_store=vector_store,
            llm=llm,
            top_k=payload.top_k,
            document_id=payload.document_id,
            document_ids=payload.document_ids,
            user_id=user_id,
            conversation_id=payload.conversation_id,
            store=store,
        )
    except (RetrievalError, GenerationError) as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.post("/chat/stream")
def chat_stream(
    payload: ChatRequest,
    embedder: EmbeddingClient = Depends(get_embedder),
    vector_store: VectorStore = Depends(get_vector_store),
    llm: LLMClient = Depends(get_llm),
    store: AppStore = Depends(get_app_store),
    user_id: str = Depends(get_user_id),
) -> StreamingResponse:
    try:
        result = answer_question(
            payload.query,
            embedder=embedder,
            vector_store=vector_store,
            llm=llm,
            top_k=payload.top_k,
            document_id=payload.document_id,
            document_ids=payload.document_ids,
            user_id=user_id,
            conversation_id=payload.conversation_id,
            store=store,
        )
    except (RetrievalError, GenerationError) as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    def events() -> Iterator[str]:
        words = result.answer.split(" ")
        current = ""
        for index, word in enumerate(words):
            current = word if index == 0 else f"{current} {word}"
            yield f"data: {json.dumps({'type': 'token', 'text': current})}\n\n"
        done = json.dumps({"type": "done", "payload": result.model_dump()})
        yield f"data: {done}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream")

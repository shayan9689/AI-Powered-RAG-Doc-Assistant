from fastapi import HTTPException

from app.core.auth import get_user_id
from app.persistence.factory import get_app_store
from app.rag.embeddings.factory import get_embedder as _get_embedder
from app.rag.generation.exceptions import GenerationError
from app.rag.generation.factory import get_llm as _get_llm
from app.rag.ingestion.exceptions import IngestionError
from app.rag.retrieval.factory import get_vector_store as _get_vector_store


def get_embedder():
    try:
        return _get_embedder()
    except IngestionError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


def get_llm():
    try:
        return _get_llm()
    except GenerationError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


def get_vector_store():
    return _get_vector_store()


__all__ = [
    "get_app_store",
    "get_embedder",
    "get_llm",
    "get_user_id",
    "get_vector_store",
]

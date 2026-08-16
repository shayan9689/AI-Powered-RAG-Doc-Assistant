from app.core.config import settings
from app.rag.retrieval.base import VectorStore

_vector_store: VectorStore | None = None


def get_vector_store() -> VectorStore:
    global _vector_store
    if _vector_store is None:
        from app.rag.retrieval.chroma_store import ChromaVectorStore

        _vector_store = ChromaVectorStore(
            persist_dir=settings.chroma_persist_path,
            collection_name=settings.chroma_collection,
        )
    return _vector_store

from app.core.config import settings
from app.core.constants import DEFAULT_USER_ID
from app.rag.embeddings.base import EmbeddingClient
from app.rag.retrieval.base import VectorStore
from app.rag.retrieval.search import retrieve_chunks
from app.schemas.retrieval import RetrieveResponse


def retrieve(
    query: str,
    *,
    embedder: EmbeddingClient,
    vector_store: VectorStore,
    top_k: int | None = None,
    document_id: str | None = None,
    document_ids: list[str] | None = None,
    user_id: str = DEFAULT_USER_ID,
) -> RetrieveResponse:
    results = retrieve_chunks(
        query,
        embedder=embedder,
        vector_store=vector_store,
        top_k=top_k or settings.retrieval_top_k,
        document_id=document_id,
        document_ids=document_ids,
        user_id=user_id,
    )
    return RetrieveResponse(query=query.strip(), results=results)

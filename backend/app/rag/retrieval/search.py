from app.core.config import settings
from app.rag.embeddings.base import EmbeddingClient
from app.rag.retrieval.base import VectorStore
from app.rag.retrieval.exceptions import RetrievalError
from app.rag.retrieval.hybrid import lexical_rerank, reciprocal_rank_fusion
from app.schemas.retrieval import RetrievedChunk


def retrieve_chunks(
    query: str,
    *,
    embedder: EmbeddingClient,
    vector_store: VectorStore,
    top_k: int | None = None,
    document_id: str | None = None,
    document_ids: list[str] | None = None,
    user_id: str | None = None,
    hybrid: bool | None = None,
    rerank: bool | None = None,
) -> list[RetrievedChunk]:
    cleaned = query.strip()
    if not cleaned:
        raise RetrievalError("Query must not be empty.")
    limit = top_k or settings.retrieval_top_k
    if document_id or document_ids:
        limit = max(limit, 8)
    embedding = embedder.embed_query(cleaned)
    semantic = vector_store.similarity_search(
        embedding,
        top_k=limit,
        document_id=document_id,
        document_ids=document_ids,
        user_id=user_id,
    )
    use_hybrid = settings.hybrid_retrieval if hybrid is None else hybrid
    if not use_hybrid:
        ranked = semantic
    else:
        lexical = vector_store.lexical_search(
            cleaned,
            top_k=limit,
            document_id=document_id,
            document_ids=document_ids,
            user_id=user_id,
        )
        ranked = reciprocal_rank_fusion([semantic, lexical])[:limit]
    use_rerank = settings.rerank_results if rerank is None else rerank
    if use_rerank:
        ranked = lexical_rerank(cleaned, ranked)[:limit]
    return ranked

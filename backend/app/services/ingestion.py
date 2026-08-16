from datetime import UTC, datetime
from uuid import uuid4

from app.core.config import settings
from app.core.constants import DEFAULT_USER_ID
from app.persistence.store import AppStore
from app.rag.chunking.chunker import chunk_pages
from app.rag.embeddings.base import EmbeddingClient
from app.rag.embeddings.factory import get_embedder
from app.rag.ingestion.normalize import normalize_text
from app.rag.ingestion.parser import extract_pages
from app.rag.ingestion.validate import validate_pdf
from app.rag.retrieval.base import VectorStore
from app.rag.retrieval.factory import get_vector_store
from app.schemas.document import IngestionResult, PageText
from app.services.pdf_storage import save_pdf


def ingest_pdf(
    file_bytes: bytes,
    filename: str,
    *,
    embedder: EmbeddingClient | None = None,
    vector_store: VectorStore | None = None,
    store: AppStore | None = None,
    user_id: str = DEFAULT_USER_ID,
) -> IngestionResult:
    safe_name = validate_pdf(file_bytes, filename, settings.max_upload_bytes)
    pages = extract_pages(file_bytes)
    cleaned_pages = [
        PageText(page_number=page.page_number, text=normalize_text(page.text))
        for page in pages
    ]
    document_id = str(uuid4())
    chunks = chunk_pages(
        cleaned_pages,
        document_id=document_id,
        filename=safe_name,
        chunk_size=settings.chunk_size,
        overlap=settings.chunk_overlap,
    )
    active_embedder = embedder or get_embedder()
    active_store = vector_store or get_vector_store()
    for chunk in chunks:
        chunk.metadata["embedding_model"] = active_embedder.model_name
        chunk.metadata["user_id"] = user_id
    if chunks:
        embeddings = active_embedder.embed_texts([chunk.text for chunk in chunks])
        active_store.upsert_chunks(chunks, embeddings)
    result = IngestionResult(
        document_id=document_id,
        filename=safe_name,
        file_type="pdf",
        size_bytes=len(file_bytes),
        status="ready",
        page_count=len(cleaned_pages),
        chunk_count=len(chunks),
        chunks=chunks,
    )
    if store is not None:
        save_pdf(file_bytes, document_id, user_id)
        store.upsert_document(
            {
                "id": document_id,
                "user_id": user_id,
                "filename": safe_name,
                "file_type": "pdf",
                "size_bytes": len(file_bytes),
                "status": "ready",
                "page_count": len(cleaned_pages),
                "chunk_count": len(chunks),
                "created_at": datetime.now(UTC).isoformat(),
            }
        )
    return result


def reindex_saved_pdf(
    document_id: str,
    filename: str,
    *,
    embedder: EmbeddingClient,
    vector_store: VectorStore,
    user_id: str = DEFAULT_USER_ID,
) -> int:
    from app.services.pdf_storage import pdf_path

    path = pdf_path(document_id, user_id)
    if not path.exists():
        return 0
    file_bytes = path.read_bytes()
    pages = extract_pages(file_bytes)
    cleaned_pages = [
        PageText(page_number=page.page_number, text=normalize_text(page.text))
        for page in pages
    ]
    chunks = chunk_pages(
        cleaned_pages,
        document_id=document_id,
        filename=filename,
        chunk_size=settings.chunk_size,
        overlap=settings.chunk_overlap,
    )
    for chunk in chunks:
        chunk.metadata["embedding_model"] = embedder.model_name
        chunk.metadata["user_id"] = user_id
    if chunks:
        embeddings = embedder.embed_texts([chunk.text for chunk in chunks])
        vector_store.upsert_chunks(chunks, embeddings)
    return len(chunks)

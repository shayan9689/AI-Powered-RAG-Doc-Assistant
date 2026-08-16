from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from fastapi.responses import Response

from app.api.deps import get_app_store, get_embedder, get_user_id, get_vector_store
from app.persistence.store import AppStore
from app.rag.embeddings.base import EmbeddingClient
from app.rag.ingestion.exceptions import IngestionError
from app.rag.retrieval.base import VectorStore
from app.rag.retrieval.exceptions import RetrievalError
from app.schemas.document import DocumentSummary, IngestionResult
from app.schemas.retrieval import RetrieveRequest, RetrieveResponse
from app.services.ingestion import ingest_pdf
from app.services.pdf_storage import delete_pdf, render_page_png
from app.services.retrieval import retrieve

router = APIRouter(tags=["documents"])


@router.post("/documents/upload", response_model=IngestionResult)
async def upload_document(
    file: UploadFile = File(...),
    embedder: EmbeddingClient = Depends(get_embedder),
    vector_store: VectorStore = Depends(get_vector_store),
    store: AppStore = Depends(get_app_store),
    user_id: str = Depends(get_user_id),
) -> IngestionResult:
    file_bytes = await file.read()
    try:
        return ingest_pdf(
            file_bytes,
            file.filename or "document.pdf",
            embedder=embedder,
            vector_store=vector_store,
            store=store,
            user_id=user_id,
        )
    except (IngestionError, RetrievalError) as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.get("/documents", response_model=list[DocumentSummary])
def list_documents(
    store: AppStore = Depends(get_app_store),
    user_id: str = Depends(get_user_id),
) -> list[DocumentSummary]:
    return [
        DocumentSummary.model_validate(item) for item in store.list_documents(user_id)
    ]


@router.delete("/documents/{document_id}")
def delete_document(
    document_id: str,
    background_tasks: BackgroundTasks,
    store: AppStore = Depends(get_app_store),
    vector_store: VectorStore = Depends(get_vector_store),
    user_id: str = Depends(get_user_id),
) -> dict[str, str]:
    deleted = store.delete_document(document_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found.")
    delete_pdf(document_id, user_id)
    background_tasks.add_task(
        vector_store.delete_document,
        document_id,
        user_id,
    )
    return {"status": "deleted", "document_id": document_id}


@router.get("/documents/{document_id}/pages/{page_number}")
def preview_document_page(
    document_id: str,
    page_number: int,
    store: AppStore = Depends(get_app_store),
    user_id: str = Depends(get_user_id),
) -> Response:
    document = store.get_document(document_id)
    if not document or document.get("user_id") != user_id:
        raise HTTPException(status_code=404, detail="Document not found.")
    try:
        png = render_page_png(document_id, user_id, page_number)
    except IngestionError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return Response(
        content=png,
        media_type="image/png",
        headers={"Cache-Control": "private, max-age=120"},
    )


@router.post("/retrieve", response_model=RetrieveResponse)
def retrieve_documents(
    payload: RetrieveRequest,
    embedder: EmbeddingClient = Depends(get_embedder),
    vector_store: VectorStore = Depends(get_vector_store),
    user_id: str = Depends(get_user_id),
) -> RetrieveResponse:
    try:
        return retrieve(
            payload.query,
            embedder=embedder,
            vector_store=vector_store,
            top_k=payload.top_k,
            document_id=payload.document_id,
            document_ids=payload.document_ids,
            user_id=user_id,
        )
    except RetrievalError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

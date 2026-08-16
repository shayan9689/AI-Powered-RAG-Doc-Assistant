import re
from pathlib import Path
from uuid import UUID

import fitz

from app.core.config import settings
from app.rag.ingestion.exceptions import IngestionError

_USER_RE = re.compile(r"[^a-zA-Z0-9_-]+")


def _safe_user_id(user_id: str) -> str:
    cleaned = _USER_RE.sub("_", user_id).strip("_")[:80]
    return cleaned or "user"


def _safe_document_id(document_id: str) -> str:
    try:
        return str(UUID(document_id))
    except ValueError as exc:
        raise IngestionError("Invalid document id.", 400) from exc


def pdf_path(document_id: str, user_id: str) -> Path:
    folder = settings.data_path / "uploads" / _safe_user_id(user_id)
    return folder / f"{_safe_document_id(document_id)}.pdf"


def save_pdf(file_bytes: bytes, document_id: str, user_id: str) -> Path:
    path = pdf_path(document_id, user_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(file_bytes)
    return path


def delete_pdf(document_id: str, user_id: str) -> None:
    try:
        path = pdf_path(document_id, user_id)
    except IngestionError:
        return
    if path.exists():
        path.unlink()


def render_page_png(document_id: str, user_id: str, page_number: int) -> bytes:
    path = pdf_path(document_id, user_id)
    if not path.exists():
        raise IngestionError(
            "Original PDF is not available. Re-upload the file to preview pages.",
            404,
        )
    if page_number < 1:
        raise IngestionError("Page not found.", 404)
    document = fitz.open(path)
    try:
        if page_number > document.page_count:
            raise IngestionError("Page not found.", 404)
        page = document[page_number - 1]
        pixmap = page.get_pixmap(matrix=fitz.Matrix(1.7, 1.7), alpha=False)
        return pixmap.tobytes("png")
    finally:
        document.close()

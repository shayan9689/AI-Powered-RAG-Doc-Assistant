import re
from pathlib import Path

from app.rag.ingestion.exceptions import IngestionError

PDF_MAGIC = b"%PDF"


def sanitize_filename(filename: str) -> str:
    name = Path(filename).name
    name = re.sub(r"[^\w.\- ]+", "_", name).strip(" .")
    if not name:
        return "document.pdf"
    if not name.lower().endswith(".pdf"):
        name = f"{name}.pdf"
    return name[:255]


def validate_pdf(file_bytes: bytes, filename: str, max_bytes: int) -> str:
    safe_name = sanitize_filename(filename)
    if not file_bytes:
        raise IngestionError("Uploaded file is empty.")
    if len(file_bytes) > max_bytes:
        raise IngestionError("Uploaded file exceeds the size limit.", 413)
    if not safe_name.lower().endswith(".pdf"):
        raise IngestionError("Only PDF files are supported in this phase.")
    if not file_bytes.lstrip().startswith(PDF_MAGIC):
        raise IngestionError("File is not a valid PDF.")
    return safe_name

import fitz

from app.rag.ingestion.exceptions import IngestionError
from app.schemas.document import PageText


def extract_pages(pdf_bytes: bytes) -> list[PageText]:
    try:
        document = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception as exc:
        raise IngestionError("Unable to read PDF.") from exc

    try:
        if document.is_encrypted:
            raise IngestionError("Encrypted PDFs are not supported.")
        pages = [
            PageText(page_number=index + 1, text=page.get_text("text") or "")
            for index, page in enumerate(document)
        ]
        if not pages:
            raise IngestionError("PDF has no pages.")
        return pages
    finally:
        document.close()

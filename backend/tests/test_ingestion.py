from pathlib import Path

from app.rag.ingestion.exceptions import IngestionError
from app.rag.ingestion.normalize import normalize_text
from app.rag.ingestion.parser import extract_pages
from app.rag.ingestion.validate import sanitize_filename, validate_pdf
from app.rag.retrieval.chroma_store import ChromaVectorStore
from app.services.ingestion import ingest_pdf
from tests.fakes import FakeEmbedder
from tests.pdf_fixtures import make_pdf_bytes


def test_sanitize_filename_strips_paths() -> None:
    assert sanitize_filename("../secret/../notes.pdf") == "notes.pdf"


def test_validate_pdf_rejects_non_pdf() -> None:
    try:
        validate_pdf(b"not a pdf", "notes.pdf", max_bytes=1024)
    except IngestionError as exc:
        assert "not a valid PDF" in exc.message
    else:
        raise AssertionError("Expected IngestionError")


def test_extract_pages_keeps_page_numbers() -> None:
    pdf_bytes = make_pdf_bytes(["First page text", "Second page text"])
    pages = extract_pages(pdf_bytes)
    assert [page.page_number for page in pages] == [1, 2]
    assert "First page text" in pages[0].text
    assert "Second page text" in pages[1].text


def test_normalize_text_fixes_wraps_and_hyphens() -> None:
    raw = "This is infor-\nmation about\nretrieval.\n\n\nNext paragraph."
    cleaned = normalize_text(raw)
    assert "information" in cleaned
    assert "about retrieval." in cleaned
    assert "\n\nNext paragraph." in cleaned


def test_ingest_pdf_returns_page_aware_chunks(tmp_path: Path) -> None:
    pdf_bytes = make_pdf_bytes(
        [
            "Alpha document content lives on page one.",
            "Beta document content lives on page two.",
        ]
    )
    result = ingest_pdf(
        pdf_bytes,
        "../uploads/sample.pdf",
        embedder=FakeEmbedder(),
        vector_store=ChromaVectorStore(str(tmp_path / "chroma"), "test_chunks"),
    )
    assert result.status == "ready"
    assert result.filename == "sample.pdf"
    assert result.page_count == 2
    assert result.chunk_count >= 2
    assert result.chunks[0].page_number == 1
    assert result.chunks[-1].page_number == 2
    assert all(chunk.metadata["filename"] == "sample.pdf" for chunk in result.chunks)

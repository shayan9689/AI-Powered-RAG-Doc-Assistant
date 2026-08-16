from app.rag.chunking.chunker import chunk_pages, split_text
from app.schemas.document import PageText


def test_split_text_respects_size_and_overlap() -> None:
    text = "alpha beta gamma delta epsilon zeta eta theta"
    chunks = split_text(text, chunk_size=20, overlap=5)
    assert len(chunks) > 1
    assert all(len(chunk) <= 20 for chunk in chunks)


def test_chunk_pages_attaches_document_metadata() -> None:
    pages = [
        PageText(page_number=1, text="Page one has enough words for a small chunk."),
        PageText(page_number=2, text="Page two also has words for another chunk."),
    ]
    chunks = chunk_pages(
        pages,
        document_id="doc-1",
        filename="guide.pdf",
        chunk_size=80,
        overlap=10,
    )
    assert chunks[0].chunk_index == 0
    assert chunks[0].page_number == 1
    assert chunks[0].metadata["document_id"] == "doc-1"
    assert chunks[-1].page_number == 2
    assert [chunk.chunk_index for chunk in chunks] == list(range(len(chunks)))

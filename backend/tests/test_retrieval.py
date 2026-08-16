from pathlib import Path

from app.rag.retrieval.chroma_store import ChromaVectorStore
from app.rag.retrieval.search import retrieve_chunks
from app.schemas.document import Chunk
from tests.fakes import FakeEmbedder


def _chunk(document_id: str, index: int, page: int, text: str) -> Chunk:
    return Chunk(
        chunk_index=index,
        page_number=page,
        text=text,
        metadata={
            "document_id": document_id,
            "filename": "notes.pdf",
            "page_number": page,
            "chunk_index": index,
            "embedding_model": "fake-embedder",
        },
    )


def test_similarity_search_ranks_matching_chunk(tmp_path: Path) -> None:
    embedder = FakeEmbedder()
    store = ChromaVectorStore(str(tmp_path / "chroma"), "test_chunks")
    chunks = [
        _chunk("doc-a", 0, 1, "cats sit on mats"),
        _chunk("doc-a", 1, 2, "quantum physics notes"),
    ]
    store.upsert_chunks(chunks, embedder.embed_texts([chunk.text for chunk in chunks]))

    results = retrieve_chunks(
        "cats",
        embedder=embedder,
        vector_store=store,
        top_k=2,
    )
    assert results[0].page_number == 1
    assert "cats" in results[0].text
    assert results[0].score >= results[1].score


def test_similarity_search_can_filter_by_document(tmp_path: Path) -> None:
    embedder = FakeEmbedder()
    store = ChromaVectorStore(str(tmp_path / "chroma"), "test_chunks")
    chunks = [
        _chunk("doc-a", 0, 1, "apple banana fruit"),
        _chunk("doc-b", 0, 1, "apple banana fruit"),
    ]
    store.upsert_chunks(chunks, embedder.embed_texts([chunk.text for chunk in chunks]))

    results = retrieve_chunks(
        "apple",
        embedder=embedder,
        vector_store=store,
        top_k=5,
        document_id="doc-b",
    )
    assert results
    assert all(item.metadata["document_id"] == "doc-b" for item in results)


def test_vectors_persist_on_disk(tmp_path: Path) -> None:
    persist_dir = str(tmp_path / "chroma")
    embedder = FakeEmbedder()
    first_store = ChromaVectorStore(persist_dir, "test_chunks")
    chunks = [_chunk("doc-a", 0, 1, "dogs chase balls")]
    first_store.upsert_chunks(chunks, embedder.embed_texts([chunks[0].text]))

    reopened = ChromaVectorStore(persist_dir, "test_chunks")
    results = retrieve_chunks(
        "dogs",
        embedder=embedder,
        vector_store=reopened,
        top_k=1,
    )
    assert results
    assert "dogs" in results[0].text

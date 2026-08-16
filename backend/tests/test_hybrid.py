from pathlib import Path

from app.rag.retrieval.chroma_store import ChromaVectorStore
from app.rag.retrieval.hybrid import reciprocal_rank_fusion
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
            "user_id": "local-user",
        },
    )


def test_hybrid_retrieval_finds_keyword_only_chunk(tmp_path: Path) -> None:
    embedder = FakeEmbedder()
    store = ChromaVectorStore(str(tmp_path / "chroma"), "test_chunks")
    chunks = [
        _chunk("doc-a", 0, 1, "cats sit on mats"),
        _chunk("doc-a", 1, 2, "uniquekeyword lives only on this page"),
    ]
    store.upsert_chunks(chunks, embedder.embed_texts([chunk.text for chunk in chunks]))
    results = retrieve_chunks(
        "uniquekeyword",
        embedder=embedder,
        vector_store=store,
        top_k=2,
        user_id="local-user",
        hybrid=True,
        rerank=True,
    )
    assert results
    assert "uniquekeyword" in results[0].text.lower()


def test_rrf_merges_rankings() -> None:
    from app.schemas.retrieval import RetrievedChunk

    left = [
        RetrievedChunk(
            chunk_index=0,
            page_number=1,
            text="a",
            score=0.9,
            metadata={"document_id": "d", "filename": "a.pdf"},
        )
    ]
    right = [
        RetrievedChunk(
            chunk_index=1,
            page_number=2,
            text="b",
            score=0.8,
            metadata={"document_id": "d", "filename": "a.pdf"},
        )
    ]
    fused = reciprocal_rank_fusion([left, right])
    assert {item.chunk_index for item in fused} == {0, 1}

from pathlib import Path

from app.rag.generation.prompt import REFUSAL_MESSAGE, SYSTEM_PROMPT, build_user_prompt
from app.rag.retrieval.chroma_store import ChromaVectorStore
from app.schemas.retrieval import RetrievedChunk
from app.services.citations import (
    compose_chat_answer,
    strip_inline_citations,
    summarize_snippet,
)
from app.services.generation import answer_question
from app.services.ingestion import ingest_pdf
from tests.fakes import FakeEmbedder, FakeLLM
from tests.pdf_fixtures import make_pdf_bytes


def test_prompt_constrains_model_to_evidence() -> None:
    evidence = [
        RetrievedChunk(
            chunk_index=0,
            page_number=1,
            text="Cats sit on mats.",
            score=0.9,
            metadata={"filename": "pets.pdf", "document_id": "doc-1"},
        )
    ]
    user_prompt = build_user_prompt("Where do cats sit?", evidence)
    assert "untrusted" in SYSTEM_PROMPT.lower()
    assert "not found" in SYSTEM_PROMPT.lower()
    assert "pets.pdf page 1" in user_prompt
    assert "Cats sit on mats." in user_prompt
    assert "Where do cats sit?" in user_prompt
    assert "direct answer" in user_prompt.lower()
    assert "paraphrase" in SYSTEM_PROMPT.lower()


def test_summarize_snippet_skips_header_and_shortens() -> None:
    raw = (
        "NAME City | +123 | mail@x.com SUMMARY Computer Science student "
        "and full-stack developer focused on AI products. Extra filler."
    )
    summary = summarize_snippet(raw)
    assert "Computer Science student" in summary
    assert "+123" not in summary
    assert "mail@x.com" not in summary


def test_compose_chat_answer_adds_summary_to_conversation() -> None:
    composed = compose_chat_answer(
        "+923107679332",
        "NAME City | +123 | mail@x.com SUMMARY Computer Science student "
        "and full-stack developer focused on AI products. Extra filler.",
    )
    assert composed.startswith("+923107679332")
    assert "Computer Science student" in composed
    assert "mail@x.com" not in composed


def test_answer_question_uses_retrieved_evidence(tmp_path: Path) -> None:
    embedder = FakeEmbedder()
    store = ChromaVectorStore(str(tmp_path / "chroma"), "test_chunks")
    llm = FakeLLM()
    ingest_pdf(
        make_pdf_bytes(["Cats sit on mats.", "Dogs chase balls."]),
        "pets.pdf",
        embedder=embedder,
        vector_store=store,
    )
    result = answer_question(
        "cats",
        embedder=embedder,
        vector_store=store,
        llm=llm,
    )
    assert result.refused is False
    assert llm.called is True
    assert "cats" in llm.last_user_prompt.lower()
    assert result.sources
    assert result.sources[0].page_number == 1
    assert result.sources[0].filename == "pets.pdf"
    assert "Grounded answer from the evidence." in result.answer
    assert "Cats sit on mats." in result.answer


def test_answer_question_refuses_unsupported_query(tmp_path: Path) -> None:
    embedder = FakeEmbedder()
    store = ChromaVectorStore(str(tmp_path / "chroma"), "test_chunks")
    llm = FakeLLM()
    ingest_pdf(
        make_pdf_bytes(["Cats sit on mats."]),
        "pets.pdf",
        embedder=embedder,
        vector_store=store,
    )
    result = answer_question(
        "zebra spaceship",
        embedder=embedder,
        vector_store=store,
        llm=llm,
    )
    assert result.refused is True
    assert result.answer == REFUSAL_MESSAGE
    assert llm.called is False


def test_strip_inline_citations_removes_filename_page() -> None:
    raw = (
        "His contact number is +923107679332 "
        "(SHAYAN UMAIR_Full Stack Engineer.pdf, page 1)."
    )
    cleaned = strip_inline_citations(raw)
    assert cleaned == "His contact number is +923107679332."
    assert "page" not in cleaned.lower()
    assert ".pdf" not in cleaned.lower()

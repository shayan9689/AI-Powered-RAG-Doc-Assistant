from fastapi.testclient import TestClient

from app.rag.generation.prompt import REFUSAL_MESSAGE
from tests.fakes import FakeLLM
from tests.pdf_fixtures import make_pdf_bytes


def test_chat_returns_grounded_answer(client: TestClient, fake_llm: FakeLLM) -> None:
    pdf_bytes = make_pdf_bytes(["Cats sit on mats.", "Dogs chase balls."])
    upload = client.post(
        "/documents/upload",
        files={"file": ("pets.pdf", pdf_bytes, "application/pdf")},
    )
    assert upload.status_code == 200
    document_id = upload.json()["document_id"]

    response = client.post(
        "/chat",
        json={"query": "cats", "document_id": document_id},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["refused"] is False
    assert payload["answer"].startswith(fake_llm.response)
    assert "Cats sit on mats." in payload["answer"]
    assert payload["sources"][0]["page_number"] == 1
    assert payload["sources"][0]["filename"] == "pets.pdf"
    assert payload["sources"][0]["chunk_id"]
    assert fake_llm.called is True


def test_chat_refuses_when_evidence_is_missing(
    client: TestClient, fake_llm: FakeLLM
) -> None:
    pdf_bytes = make_pdf_bytes(["Cats sit on mats."])
    upload = client.post(
        "/documents/upload",
        files={"file": ("pets.pdf", pdf_bytes, "application/pdf")},
    )
    assert upload.status_code == 200

    response = client.post("/chat", json={"query": "zebra spaceship"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["refused"] is True
    assert payload["answer"] == REFUSAL_MESSAGE
    assert fake_llm.called is False

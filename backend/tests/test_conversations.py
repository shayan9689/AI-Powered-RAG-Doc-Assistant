from fastapi.testclient import TestClient

from tests.fakes import FakeLLM
from tests.pdf_fixtures import make_pdf_bytes


def test_chat_persists_conversation(client: TestClient, fake_llm: FakeLLM) -> None:
    upload = client.post(
        "/documents/upload",
        files={
            "file": (
                "pets.pdf",
                make_pdf_bytes(["Cats sit on mats.", "Dogs chase balls."]),
                "application/pdf",
            )
        },
    )
    assert upload.status_code == 200
    first = client.post("/chat", json={"query": "cats"})
    assert first.status_code == 200
    conversation_id = first.json()["conversation_id"]
    assert conversation_id

    second = client.post(
        "/chat",
        json={"query": "what about dogs?", "conversation_id": conversation_id},
    )
    assert second.status_code == 200
    assert any("standalone search query" in call[0].lower() for call in fake_llm.calls)

    listed = client.get("/conversations")
    assert listed.status_code == 200
    assert any(item["id"] == conversation_id for item in listed.json())

    detail = client.get(f"/conversations/{conversation_id}")
    assert detail.status_code == 200
    roles = [item["role"] for item in detail.json()["messages"]]
    assert roles == ["user", "assistant", "user", "assistant"]

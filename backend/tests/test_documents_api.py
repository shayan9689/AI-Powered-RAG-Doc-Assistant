from fastapi.testclient import TestClient

from tests.pdf_fixtures import make_pdf_bytes


def test_upload_pdf_returns_chunks(client: TestClient) -> None:
    pdf_bytes = make_pdf_bytes(["Upload page one.", "Upload page two."])
    response = client.post(
        "/documents/upload",
        files={"file": ("demo.pdf", pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["filename"] == "demo.pdf"
    assert payload["status"] == "ready"
    assert payload["page_count"] == 2
    assert payload["chunk_count"] >= 2
    assert payload["chunks"][0]["page_number"] == 1
    assert payload["chunks"][0]["metadata"]["embedding_model"] == "fake-embedder"


def test_upload_rejects_non_pdf(client: TestClient) -> None:
    response = client.post(
        "/documents/upload",
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 400


def test_retrieve_returns_matching_chunk(client: TestClient) -> None:
    pdf_bytes = make_pdf_bytes(["Cats sit on mats.", "Dogs chase balls."])
    upload = client.post(
        "/documents/upload",
        files={"file": ("pets.pdf", pdf_bytes, "application/pdf")},
    )
    assert upload.status_code == 200
    document_id = upload.json()["document_id"]

    response = client.post(
        "/retrieve",
        json={"query": "cats", "top_k": 2, "document_id": document_id},
    )
    assert response.status_code == 200
    results = response.json()["results"]
    assert results
    assert "Cats" in results[0]["text"]
    assert results[0]["page_number"] == 1


def test_list_and_delete_documents(client: TestClient) -> None:
    first = client.post(
        "/documents/upload",
        files={
            "file": (
                "alpha.pdf",
                make_pdf_bytes(["Alpha page one."]),
                "application/pdf",
            )
        },
    )
    second = client.post(
        "/documents/upload",
        files={
            "file": (
                "beta.pdf",
                make_pdf_bytes(["Beta page one."]),
                "application/pdf",
            )
        },
    )
    assert first.status_code == 200
    assert second.status_code == 200
    listed = client.get("/documents")
    assert listed.status_code == 200
    names = {item["filename"] for item in listed.json()}
    assert names == {"alpha.pdf", "beta.pdf"}

    doc_id = first.json()["document_id"]
    deleted = client.delete(f"/documents/{doc_id}")
    assert deleted.status_code == 200
    remaining = {item["filename"] for item in client.get("/documents").json()}
    assert remaining == {"beta.pdf"}


def test_documents_are_isolated_by_user(client: TestClient) -> None:
    upload = client.post(
        "/documents/upload",
        files={
            "file": (
                "secret.pdf",
                make_pdf_bytes(["Cats sit on mats."]),
                "application/pdf",
            )
        },
        headers={"X-User-Id": "user-a"},
    )
    assert upload.status_code == 200
    other = client.get("/documents", headers={"X-User-Id": "user-b"})
    assert other.json() == []
    owner = client.get("/documents", headers={"X-User-Id": "user-a"})
    assert len(owner.json()) == 1


def test_page_preview_renders_selected_page(client: TestClient) -> None:
    upload = client.post(
        "/documents/upload",
        files={
            "file": (
                "guide.pdf",
                make_pdf_bytes(["First page text", "Second page text"]),
                "application/pdf",
            )
        },
    )
    assert upload.status_code == 200
    document_id = upload.json()["document_id"]

    preview = client.get(f"/documents/{document_id}/pages/2")
    assert preview.status_code == 200
    assert preview.headers["content-type"].startswith("image/png")
    assert preview.content.startswith(b"\x89PNG")

    missing_page = client.get(f"/documents/{document_id}/pages/9")
    assert missing_page.status_code == 404

    other_user = client.get(
        f"/documents/{document_id}/pages/1",
        headers={"X-User-Id": "user-b"},
    )
    assert other_user.status_code == 404

    client.delete(f"/documents/{document_id}")
    after_delete = client.get(f"/documents/{document_id}/pages/1")
    assert after_delete.status_code == 404

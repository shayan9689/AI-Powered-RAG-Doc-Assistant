from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_app_store, get_embedder, get_llm, get_vector_store
from app.core.config import settings
from app.main import app
from app.persistence.store import AppStore
from app.rag.retrieval.chroma_store import ChromaVectorStore
from tests.fakes import FakeEmbedder, FakeLLM

settings.rate_limit_per_minute = 0


@pytest.fixture
def fake_embedder() -> FakeEmbedder:
    return FakeEmbedder()


@pytest.fixture
def vector_store(tmp_path: Path) -> ChromaVectorStore:
    return ChromaVectorStore(
        persist_dir=str(tmp_path / "chroma"),
        collection_name="test_chunks",
    )


@pytest.fixture
def fake_llm() -> FakeLLM:
    return FakeLLM()


@pytest.fixture
def app_store(tmp_path: Path) -> AppStore:
    return AppStore(tmp_path / "app_store.json")


@pytest.fixture
def client(
    fake_embedder: FakeEmbedder,
    vector_store: ChromaVectorStore,
    fake_llm: FakeLLM,
    app_store: AppStore,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[TestClient]:
    monkeypatch.setattr(settings, "data_dir", str(tmp_path / "appdata"))
    app.dependency_overrides[get_embedder] = lambda: fake_embedder
    app.dependency_overrides[get_vector_store] = lambda: vector_store
    app.dependency_overrides[get_llm] = lambda: fake_llm
    app.dependency_overrides[get_app_store] = lambda: app_store
    yield TestClient(app)
    app.dependency_overrides.clear()

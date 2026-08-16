from typing import Protocol

from app.schemas.document import Chunk
from app.schemas.retrieval import RetrievedChunk


class VectorStore(Protocol):
    def upsert_chunks(
        self,
        chunks: list[Chunk],
        embeddings: list[list[float]],
    ) -> None: ...

    def similarity_search(
        self,
        embedding: list[float],
        *,
        top_k: int,
        document_id: str | None = None,
        document_ids: list[str] | None = None,
        user_id: str | None = None,
    ) -> list[RetrievedChunk]: ...

    def lexical_search(
        self,
        query: str,
        *,
        top_k: int,
        document_id: str | None = None,
        document_ids: list[str] | None = None,
        user_id: str | None = None,
    ) -> list[RetrievedChunk]: ...

    def delete_document(self, document_id: str, user_id: str | None = None) -> None: ...

    def fetch_document_chunks(
        self,
        document_id: str,
        *,
        user_id: str | None = None,
        limit: int | None = None,
    ) -> list[RetrievedChunk]: ...

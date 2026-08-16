from app.rag.retrieval.exceptions import RetrievalError
from app.rag.retrieval.filters import build_where
from app.schemas.document import Chunk
from app.schemas.retrieval import RetrievedChunk


def _chunk_from_record(
    text: str,
    metadata: dict[str, object],
    score: float,
) -> RetrievedChunk:
    meta = dict(metadata or {})
    return RetrievedChunk(
        chunk_index=int(meta.get("chunk_index", 0)),
        page_number=int(meta.get("page_number", 0)),
        text=text or "",
        score=round(score, 4),
        metadata=meta,
    )


class ChromaVectorStore:
    def __init__(self, persist_dir: str, collection_name: str) -> None:
        import chromadb

        self._client = chromadb.PersistentClient(path=persist_dir)
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def upsert_chunks(
        self,
        chunks: list[Chunk],
        embeddings: list[list[float]],
    ) -> None:
        if not chunks:
            return
        if len(chunks) != len(embeddings):
            raise RetrievalError("Chunk and embedding counts do not match.", 500)
        ids = [
            f"{chunk.metadata['document_id']}:{chunk.chunk_index}" for chunk in chunks
        ]
        metadatas = [
            {
                "document_id": str(chunk.metadata["document_id"]),
                "filename": str(chunk.metadata["filename"]),
                "page_number": int(chunk.page_number),
                "chunk_index": int(chunk.chunk_index),
                "embedding_model": str(chunk.metadata.get("embedding_model", "")),
                "user_id": str(chunk.metadata.get("user_id", "")),
            }
            for chunk in chunks
        ]
        try:
            self._collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=[chunk.text for chunk in chunks],
                metadatas=metadatas,
            )
        except Exception as exc:
            raise RetrievalError("Failed to persist embeddings.", 500) from exc

    def similarity_search(
        self,
        embedding: list[float],
        *,
        top_k: int,
        document_id: str | None = None,
        document_ids: list[str] | None = None,
        user_id: str | None = None,
    ) -> list[RetrievedChunk]:
        count = self._collection.count()
        if count == 0:
            return []
        query_kwargs: dict[str, object] = {
            "query_embeddings": [embedding],
            "n_results": min(top_k, max(count, 1)),
            "include": ["documents", "metadatas", "distances"],
        }
        where = build_where(
            user_id=user_id,
            document_id=document_id,
            document_ids=document_ids,
        )
        if where:
            query_kwargs["where"] = where
        try:
            result = self._collection.query(**query_kwargs)
        except Exception:
            if document_id:
                return self.fetch_document_chunks(
                    document_id, user_id=user_id, limit=top_k
                )
            raise RetrievalError("Similarity search failed.", 500)

        documents = (result.get("documents") or [[]])[0]
        metadatas = (result.get("metadatas") or [[]])[0]
        distances = (result.get("distances") or [[]])[0]
        retrieved: list[RetrievedChunk] = []
        for text, metadata, distance in zip(
            documents, metadatas, distances, strict=True
        ):
            retrieved.append(
                _chunk_from_record(
                    text or "", dict(metadata or {}), 1 - float(distance)
                )
            )
        return retrieved

    def lexical_search(
        self,
        query: str,
        *,
        top_k: int,
        document_id: str | None = None,
        document_ids: list[str] | None = None,
        user_id: str | None = None,
    ) -> list[RetrievedChunk]:
        where = build_where(
            user_id=user_id,
            document_id=document_id,
            document_ids=document_ids,
        )
        try:
            get_kwargs: dict[str, object] = {"include": ["documents", "metadatas"]}
            if where:
                get_kwargs["where"] = where
            result = self._collection.get(**get_kwargs)
        except Exception as exc:
            raise RetrievalError("Keyword search failed.", 500) from exc
        terms = [token for token in query.lower().split() if token]
        if not terms:
            return []
        scored: list[RetrievedChunk] = []
        documents = result.get("documents") or []
        metadatas = result.get("metadatas") or []
        for text, metadata in zip(documents, metadatas, strict=True):
            blob = (text or "").lower()
            hits = sum(1 for term in terms if term in blob)
            if hits == 0:
                continue
            scored.append(
                _chunk_from_record(text or "", dict(metadata or {}), hits / len(terms))
            )
        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:top_k]

    def delete_document(self, document_id: str, user_id: str | None = None) -> None:
        where = build_where(user_id=user_id, document_id=document_id)
        try:
            if where:
                self._collection.delete(where=where)
            else:
                self._collection.delete(where={"document_id": document_id})
        except Exception as exc:
            raise RetrievalError("Failed to delete document vectors.", 500) from exc

    def fetch_document_chunks(
        self,
        document_id: str,
        *,
        user_id: str | None = None,
        limit: int | None = None,
    ) -> list[RetrievedChunk]:
        where: dict[str, object] = {"document_id": document_id}
        if user_id:
            where = {"$and": [{"document_id": document_id}, {"user_id": user_id}]}
        try:
            result = self._collection.get(
                where=where,
                include=["documents", "metadatas"],
            )
        except Exception:
            if user_id:
                return self.fetch_document_chunks(
                    document_id, user_id=None, limit=limit
                )
            return []
        documents = result.get("documents") or []
        metadatas = result.get("metadatas") or []
        retrieved: list[RetrievedChunk] = []
        for text, metadata in zip(documents, metadatas, strict=True):
            retrieved.append(
                _chunk_from_record(text or "", dict(metadata or {}), 1.0)
            )
        retrieved.sort(key=lambda item: item.chunk_index)
        if limit is not None:
            return retrieved[:limit]
        return retrieved

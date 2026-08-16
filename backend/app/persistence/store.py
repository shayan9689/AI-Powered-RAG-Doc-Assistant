import json
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock
from typing import Any
from uuid import uuid4


def _now() -> str:
    return datetime.now(UTC).isoformat()


class AppStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._lock = Lock()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write(
                {"documents": {}, "conversations": {}, "messages": {}},
            )

    def _read(self) -> dict[str, Any]:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write(self, payload: dict[str, Any]) -> None:
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def upsert_document(self, record: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            data = self._read()
            data["documents"][record["id"]] = record
            self._write(data)
        return record

    def get_document(self, document_id: str) -> dict[str, Any] | None:
        return self._read()["documents"].get(document_id)

    def list_documents(self, user_id: str) -> list[dict[str, Any]]:
        docs = [
            doc
            for doc in self._read()["documents"].values()
            if doc.get("user_id") == user_id
        ]
        return sorted(docs, key=lambda item: item.get("created_at", ""), reverse=True)

    def delete_document(self, document_id: str, user_id: str) -> bool:
        with self._lock:
            data = self._read()
            doc = data["documents"].get(document_id)
            if not doc or doc.get("user_id") != user_id:
                return False
            del data["documents"][document_id]
            self._write(data)
        return True

    def create_conversation(self, user_id: str, title: str) -> dict[str, Any]:
        record = {
            "id": str(uuid4()),
            "user_id": user_id,
            "title": title[:80] or "New conversation",
            "created_at": _now(),
            "updated_at": _now(),
        }
        with self._lock:
            data = self._read()
            data["conversations"][record["id"]] = record
            data["messages"][record["id"]] = []
            self._write(data)
        return record

    def list_conversations(self, user_id: str) -> list[dict[str, Any]]:
        convos = [
            item
            for item in self._read()["conversations"].values()
            if item.get("user_id") == user_id
        ]
        return sorted(convos, key=lambda item: item.get("updated_at", ""), reverse=True)

    def get_conversation(self, conversation_id: str) -> dict[str, Any] | None:
        return self._read()["conversations"].get(conversation_id)

    def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        with self._lock:
            data = self._read()
            convo = data["conversations"].get(conversation_id)
            if not convo or convo.get("user_id") != user_id:
                return False
            del data["conversations"][conversation_id]
            data["messages"].pop(conversation_id, None)
            self._write(data)
        return True

    def add_message(
        self,
        conversation_id: str,
        *,
        role: str,
        content: str,
        sources: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        record = {
            "id": str(uuid4()),
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "sources": sources or [],
            "created_at": _now(),
        }
        with self._lock:
            data = self._read()
            data["messages"].setdefault(conversation_id, []).append(record)
            if conversation_id in data["conversations"]:
                data["conversations"][conversation_id]["updated_at"] = _now()
            self._write(data)
        return record

    def list_messages(self, conversation_id: str) -> list[dict[str, Any]]:
        return list(self._read()["messages"].get(conversation_id, []))

from typing import Any
from uuid import uuid4

import httpx

from app.persistence.store import _now


class SupabaseStore:
    def __init__(self, url: str, service_role_key: str) -> None:
        self._base = url.rstrip("/") + "/rest/v1"
        self._client = httpx.Client(
            headers={
                "apikey": service_role_key,
                "Authorization": f"Bearer {service_role_key}",
                "Content-Type": "application/json",
                "Prefer": "return=representation",
            },
            timeout=10.0,
        )

    def _request(
        self,
        method: str,
        path: str,
        extra_headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> Any:
        try:
            response = self._client.request(
                method,
                f"{self._base}{path}",
                headers=extra_headers,
                **kwargs,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise RuntimeError("Supabase request failed.") from exc
        if not response.content:
            return None
        return response.json()

    def upsert_document(self, record: dict[str, Any]) -> dict[str, Any]:
        rows = self._request(
            "POST",
            "/documents?on_conflict=id",
            extra_headers={
                "Prefer": "resolution=merge-duplicates,return=representation"
            },
            json=record,
        )
        return rows[0] if rows else record

    def get_document(self, document_id: str) -> dict[str, Any] | None:
        rows = self._request("GET", f"/documents?id=eq.{document_id}&select=*")
        return rows[0] if rows else None

    def list_documents(self, user_id: str) -> list[dict[str, Any]]:
        return (
            self._request(
                "GET",
                f"/documents?user_id=eq.{user_id}&select=*&order=created_at.desc",
            )
            or []
        )

    def delete_document(self, document_id: str, user_id: str) -> bool:
        rows = self._request(
            "DELETE",
            f"/documents?id=eq.{document_id}&user_id=eq.{user_id}",
        )
        return bool(rows)

    def create_conversation(self, user_id: str, title: str) -> dict[str, Any]:
        record = {
            "id": str(uuid4()),
            "user_id": user_id,
            "title": title[:80] or "New conversation",
            "created_at": _now(),
            "updated_at": _now(),
        }
        rows = self._request("POST", "/conversations", json=record)
        return rows[0] if rows else record

    def list_conversations(self, user_id: str) -> list[dict[str, Any]]:
        return (
            self._request(
                "GET",
                f"/conversations?user_id=eq.{user_id}&select=*&order=updated_at.desc",
            )
            or []
        )

    def get_conversation(self, conversation_id: str) -> dict[str, Any] | None:
        rows = self._request(
            "GET",
            f"/conversations?id=eq.{conversation_id}&select=*",
        )
        return rows[0] if rows else None

    def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        rows = self._request(
            "DELETE",
            f"/conversations?id=eq.{conversation_id}&user_id=eq.{user_id}",
        )
        return bool(rows)

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
        rows = self._request("POST", "/messages", json=record)
        self._request(
            "PATCH",
            f"/conversations?id=eq.{conversation_id}",
            json={"updated_at": _now()},
        )
        return rows[0] if rows else record

    def list_messages(self, conversation_id: str) -> list[dict[str, Any]]:
        return (
            self._request(
                "GET",
                "/messages?conversation_id=eq."
                f"{conversation_id}&select=*&order=created_at.asc",
            )
            or []
        )

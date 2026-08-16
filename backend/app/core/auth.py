import threading
import time

import httpx
from fastapi import Header, HTTPException

from app.core.config import settings
from app.core.constants import DEFAULT_USER_ID

_TTL_SECONDS = 300
_MAX_CACHE = 256
_cache: dict[str, tuple[float, str]] = {}
_lock = threading.Lock()
_client = httpx.Client(timeout=5.0)


def get_user_id(
    authorization: str | None = Header(default=None),
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
) -> str:
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
        if settings.supabase_project_url and settings.supabase_anon_key:
            return _user_from_supabase(token)
    if settings.auth_required:
        raise HTTPException(status_code=401, detail="Authentication required.")
    if x_user_id and settings.environment == "development":
        return x_user_id.strip()
    return DEFAULT_USER_ID


def clear_user_cache() -> None:
    with _lock:
        _cache.clear()


def _user_from_supabase(token: str) -> str:
    now = time.monotonic()
    with _lock:
        cached = _cache.get(token)
        if cached and cached[0] > now:
            return cached[1]
    url = settings.supabase_project_url.rstrip("/") + "/auth/v1/user"
    try:
        response = _client.get(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "apikey": settings.supabase_anon_key,
            },
        )
        response.raise_for_status()
        user_id = response.json().get("id")
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid access token.") from exc
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid access token.")
    user = str(user_id)
    with _lock:
        if len(_cache) >= _MAX_CACHE:
            _cache.clear()
        _cache[token] = (now + _TTL_SECONDS, user)
    return user

from app.core import auth


def test_user_from_supabase_caches_token(monkeypatch) -> None:
    auth.clear_user_cache()
    calls = {"count": 0}

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, str]:
            return {"id": "user-1"}

    def fake_get(*_args, **_kwargs) -> FakeResponse:
        calls["count"] += 1
        return FakeResponse()

    monkeypatch.setattr(auth._client, "get", fake_get)
    monkeypatch.setattr(auth.settings, "supabase_url", "https://example.supabase.co")
    monkeypatch.setattr(auth.settings, "supabase_anon_key", "anon")

    assert auth._user_from_supabase("tok") == "user-1"
    assert auth._user_from_supabase("tok") == "user-1"
    assert calls["count"] == 1
    auth.clear_user_cache()

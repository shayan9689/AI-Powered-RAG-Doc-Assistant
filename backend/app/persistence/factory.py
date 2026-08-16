from app.core.config import settings
from app.persistence.store import AppStore

_store: AppStore | None = None


def get_app_store() -> AppStore:
    global _store
    if _store is None:
        if settings.supabase_url and settings.supabase_service_role_key:
            from app.persistence.supabase_store import SupabaseStore

            _store = SupabaseStore(  # type: ignore[assignment]
                settings.supabase_project_url,
                settings.supabase_service_role_key,
            )
        else:
            _store = AppStore(settings.data_path / "app_store.json")
    return _store

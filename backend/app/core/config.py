from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "RAG Document Assistant"
    environment: str = "development"
    cors_origins: str = (
        "http://localhost:5173,https://ai-powered-rag-doc-assistant.vercel.app"
    )

    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""

    max_upload_bytes: int = 10 * 1024 * 1024
    chunk_size: int = 1000
    chunk_overlap: int = 150

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chroma_persist_dir: str = "./data/chroma"
    chroma_collection: str = "document_chunks"
    retrieval_top_k: int = 5
    min_retrieval_score: float = 0.25
    hybrid_retrieval: bool = True
    rerank_results: bool = True
    rewrite_followups: bool = True
    rate_limit_per_minute: int = 60
    auth_required: bool = False
    data_dir: str = "./data"

    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"
    llm_timeout_seconds: float = 30
    openai_api_key: str = ""
    gemini_api_key: str = ""

    @property
    def supabase_project_url(self) -> str:
        url = self.supabase_url.strip().rstrip("/")
        for suffix in ("/rest/v1", "/auth/v1", "/storage/v1"):
            if url.endswith(suffix):
                url = url[: -len(suffix)].rstrip("/")
        return url

    @property
    def cors_origin_list(self) -> list[str]:
        origins = [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]
        for extra in (
            "http://localhost:5173",
            "https://ai-powered-rag-doc-assistant.vercel.app",
        ):
            if extra not in origins:
                origins.append(extra)
        return origins

    @property
    def chroma_persist_path(self) -> str:
        path = Path(self.chroma_persist_dir)
        if path.is_absolute():
            return str(path)
        repo_root = Path(__file__).resolve().parents[3]
        return str((repo_root / path).resolve())

    @property
    def data_path(self) -> Path:
        path = Path(self.data_dir)
        if path.is_absolute():
            return path
        repo_root = Path(__file__).resolve().parents[3]
        return (repo_root / path).resolve()


settings = Settings()

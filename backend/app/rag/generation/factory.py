from app.core.config import settings
from app.rag.generation.base import LLMClient
from app.rag.generation.exceptions import GenerationError

_llm: LLMClient | None = None


def get_llm() -> LLMClient:
    global _llm
    if _llm is None:
        _llm = _create_llm()
    return _llm


def _create_llm() -> LLMClient:
    provider = settings.llm_provider.strip().lower()
    if provider == "openai":
        from app.rag.generation.openai_client import OpenAILLM

        return OpenAILLM(
            api_key=settings.openai_api_key,
            model_name=settings.llm_model,
            timeout_seconds=settings.llm_timeout_seconds,
        )
    if provider == "gemini":
        from app.rag.generation.gemini_client import GeminiLLM

        return GeminiLLM(
            api_key=settings.gemini_api_key,
            model_name=settings.llm_model,
            timeout_seconds=settings.llm_timeout_seconds,
        )
    raise GenerationError(f"Unsupported LLM provider: {provider}", 500)

import httpx

from app.rag.generation.exceptions import GenerationError

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
)


class GeminiLLM:
    provider = "gemini"

    def __init__(self, api_key: str, model_name: str, timeout_seconds: float) -> None:
        if not api_key:
            raise GenerationError("GEMINI_API_KEY is not configured.", 503)
        self.model_name = model_name
        self._api_key = api_key
        self._timeout = timeout_seconds

    def generate(self, *, system_prompt: str, user_prompt: str) -> str:
        url = GEMINI_URL.format(model=self.model_name)
        payload = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "generationConfig": {"temperature": 0},
        }
        try:
            response = httpx.post(
                url,
                params={"key": self._api_key},
                json=payload,
                timeout=self._timeout,
            )
            response.raise_for_status()
            data = response.json()
        except Exception as exc:
            raise GenerationError("Gemini request failed.") from exc

        try:
            text = data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError) as exc:
            raise GenerationError("Gemini returned an unexpected response.") from exc
        if not text or not str(text).strip():
            raise GenerationError("Gemini returned an empty response.")
        return str(text).strip()

from app.rag.generation.exceptions import GenerationError


class OpenAILLM:
    provider = "openai"

    def __init__(self, api_key: str, model_name: str, timeout_seconds: float) -> None:
        if not api_key:
            raise GenerationError("OPENAI_API_KEY is not configured.", 503)
        from openai import OpenAI

        self.model_name = model_name
        self._client = OpenAI(api_key=api_key, timeout=timeout_seconds)

    def generate(self, *, system_prompt: str, user_prompt: str) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self.model_name,
                temperature=0,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
        except Exception as exc:
            raise GenerationError("OpenAI request failed.") from exc
        content = response.choices[0].message.content if response.choices else None
        if not content or not content.strip():
            raise GenerationError("OpenAI returned an empty response.")
        return content.strip()

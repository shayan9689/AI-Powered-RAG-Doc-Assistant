import logging

from app.rag.generation.exceptions import GenerationError

logger = logging.getLogger(__name__)


class OpenAILLM:
    provider = "openai"

    def __init__(self, api_key: str, model_name: str, timeout_seconds: float) -> None:
        key = api_key.strip()
        if not key:
            raise GenerationError("OPENAI_API_KEY is not configured.", 503)
        from openai import OpenAI

        self.model_name = model_name
        self._client = OpenAI(api_key=key, timeout=timeout_seconds)

    def generate(self, *, system_prompt: str, user_prompt: str) -> str:
        from openai import (
            APIConnectionError,
            APIStatusError,
            APITimeoutError,
            AuthenticationError,
            NotFoundError,
            RateLimitError,
        )

        try:
            response = self._client.chat.completions.create(
                model=self.model_name,
                temperature=0,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
        except AuthenticationError as exc:
            raise GenerationError(
                "OpenAI rejected the API key. Set OPENAI_API_KEY on Railway.",
                502,
            ) from exc
        except RateLimitError as exc:
            raise GenerationError(
                "OpenAI quota or rate limit reached. Check billing at platform.openai.com.",
                429,
            ) from exc
        except NotFoundError as exc:
            raise GenerationError(
                f"OpenAI model '{self.model_name}' was not found. Set LLM_MODEL=gpt-4o-mini.",
                502,
            ) from exc
        except APITimeoutError as exc:
            raise GenerationError("OpenAI timed out. Try again.", 504) from exc
        except APIConnectionError as exc:
            raise GenerationError(
                "The server could not reach OpenAI from Railway.",
                502,
            ) from exc
        except APIStatusError as exc:
            logger.exception("OpenAI API status error")
            raise GenerationError(
                f"OpenAI request failed ({exc.status_code}).",
                502,
            ) from exc
        except Exception as exc:
            logger.exception("OpenAI request failed")
            raise GenerationError("OpenAI request failed.") from exc
        content = response.choices[0].message.content if response.choices else None
        if not content or not content.strip():
            raise GenerationError("OpenAI returned an empty response.")
        return content.strip()

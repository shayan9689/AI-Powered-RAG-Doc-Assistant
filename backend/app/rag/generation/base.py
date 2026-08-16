from typing import Protocol


class LLMClient(Protocol):
    provider: str
    model_name: str

    def generate(self, *, system_prompt: str, user_prompt: str) -> str: ...

from collections.abc import Sequence
from typing import Protocol


class EmbeddingClient(Protocol):
    model_name: str

    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]: ...

    def embed_query(self, text: str) -> list[float]: ...

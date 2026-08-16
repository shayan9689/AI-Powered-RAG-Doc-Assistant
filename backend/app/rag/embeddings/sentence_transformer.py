from collections.abc import Sequence


class SentenceTransformerEmbedder:
    def __init__(self, model_name: str) -> None:
        from sentence_transformers import SentenceTransformer

        self.model_name = model_name
        try:
            self._model = SentenceTransformer(
                model_name,
                device="cpu",
                local_files_only=True,
            )
        except Exception:
            self._model = SentenceTransformer(model_name, device="cpu")

    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []
        vectors = self._model.encode(
            list(texts),
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return vectors.tolist()

    def embed_query(self, text: str) -> list[float]:
        return self.embed_texts([text])[0]

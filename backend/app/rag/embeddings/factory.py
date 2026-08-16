import logging
import sys
import threading

from app.core.config import settings
from app.rag.embeddings.base import EmbeddingClient
from app.rag.ingestion.exceptions import IngestionError

logger = logging.getLogger(__name__)

_embedder: EmbeddingClient | None = None
_lock = threading.Lock()


def get_embedder() -> EmbeddingClient:
    global _embedder
    if _embedder is None:
        with _lock:
            if _embedder is None:
                try:
                    from app.rag.embeddings.sentence_transformer import (
                        SentenceTransformerEmbedder,
                    )

                    _embedder = SentenceTransformerEmbedder(settings.embedding_model)
                except Exception as exc:
                    raise IngestionError(
                        "Embedding model failed to load. "
                        "Check Python package versions.",
                        503,
                    ) from exc
    return _embedder


def warmup_embedder() -> None:
    if "pytest" in sys.modules:
        return

    def _run() -> None:
        try:
            get_embedder()
            logger.info("Embedding model ready.")
        except Exception:
            logger.exception("Embedding model preload failed.")

    threading.Thread(target=_run, daemon=True, name="embedder-warmup").start()

from unittest.mock import MagicMock, patch

from app.rag.embeddings.sentence_transformer import SentenceTransformerEmbedder


def test_embedder_loads_from_local_cache_first() -> None:
    mock_model = MagicMock()
    mock_model.encode.return_value = MagicMock(tolist=lambda: [[0.1, 0.2]])
    with patch(
        "sentence_transformers.SentenceTransformer",
        return_value=mock_model,
    ) as ctor:
        embedder = SentenceTransformerEmbedder("sentence-transformers/all-MiniLM-L6-v2")
        embedder.embed_texts(["hello"])
    ctor.assert_called_once()
    assert ctor.call_args.kwargs["local_files_only"] is True
    assert ctor.call_args.kwargs["device"] == "cpu"
    mock_model.encode.assert_called_once()
    assert mock_model.encode.call_args.kwargs["show_progress_bar"] is False

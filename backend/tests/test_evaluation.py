from app.rag.evaluation.metrics import recall_at_k


def test_recall_at_k() -> None:
    retrieved = ["doc-a:0", "doc-b:1", "doc-c:2"]
    relevant = {"doc-a:0", "doc-z:9"}
    assert recall_at_k(retrieved, relevant, k=3) == 1.0
    assert recall_at_k(retrieved, relevant, k=0) == 0.0
    assert recall_at_k(["doc-x:0"], relevant, k=1) == 0.0

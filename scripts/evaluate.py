"""Run retrieval evaluation against evaluation/dataset.json."""

from __future__ import annotations

import json
import time
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.rag.evaluation.metrics import average, recall_at_k  # noqa: E402
from app.rag.retrieval.chroma_store import ChromaVectorStore  # noqa: E402
from app.services.ingestion import ingest_pdf  # noqa: E402
from app.rag.retrieval.search import retrieve_chunks  # noqa: E402
from tests.fakes import FakeEmbedder  # noqa: E402
from tests.pdf_fixtures import make_pdf_bytes  # noqa: E402


def main() -> None:
    dataset = json.loads((ROOT / "evaluation" / "dataset.json").read_text(encoding="utf-8"))
    embedder = FakeEmbedder()
    store = ChromaVectorStore(str(ROOT / "data" / "eval_chroma"), "eval_chunks")
    doc_map: dict[str, str] = {}
    for doc in dataset["documents"]:
        pdf_bytes = make_pdf_bytes(doc["pages"])
        result = ingest_pdf(
            pdf_bytes,
            doc["filename"],
            embedder=embedder,
            vector_store=store,
            user_id="eval-user",
        )
        doc_map[doc["id"]] = result.document_id

    recalls: list[float] = []
    latencies: list[float] = []
    for item in dataset["questions"]:
        started = time.perf_counter()
        results = retrieve_chunks(
            item["question"],
            embedder=embedder,
            vector_store=store,
            top_k=5,
            user_id="eval-user",
        )
        latencies.append((time.perf_counter() - started) * 1000)
        if not item["answerable"]:
            continue
        doc_id = doc_map[item["document"]]
        relevant = {f"{doc_id}:{item['page'] - 1}"}
        retrieved_ids = [
            f"{chunk.metadata.get('document_id')}:{chunk.page_number - 1}"
            for chunk in results
        ]
        # Page-level hit: any chunk from the expected page.
        page_ids = [
            f"{chunk.metadata.get('document_id')}:{chunk.page_number}"
            for chunk in results
        ]
        relevant_page = {f"{doc_id}:{item['page']}"}
        recalls.append(recall_at_k(page_ids, relevant_page, k=5))
        _ = relevant, retrieved_ids

    report = {
        "questions": len(dataset["questions"]),
        "answerable_recall_at_5": round(average(recalls), 4),
        "avg_latency_ms": round(average(latencies), 2),
        "p95_latency_ms": round(sorted(latencies)[max(int(len(latencies) * 0.95) - 1, 0)], 2),
        "note": "Retrieval-only baseline using the fake embedder in tests. Re-run with the real model after setting EMBEDDING_MODEL.",
    }
    out = ROOT / "evaluation" / "results" / "baseline.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

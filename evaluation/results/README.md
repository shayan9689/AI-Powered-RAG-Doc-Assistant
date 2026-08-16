# Evaluation results

This folder stores versioned retrieval experiments.

## Baseline

Command:

```bash
python scripts/evaluate.py
```

The first baseline uses the same fake embedder as unit tests so it can run without downloading a model. After you set a real embedding model, re-run and compare `answerable_recall_at_5` and latency.

Expected question mix:

- factual lookup
- multi-document questions
- unanswerable / negative questions
- follow-up questions

Faithfulness and answer relevance require an LLM key. Measure those after Phase 3 configuration by sampling `/chat` answers against `evaluation/dataset.json`.

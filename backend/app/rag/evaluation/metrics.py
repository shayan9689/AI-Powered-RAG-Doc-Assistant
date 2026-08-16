def recall_at_k(retrieved_ids: list[str], relevant_ids: set[str], k: int) -> float:
    if k <= 0 or not relevant_ids:
        return 0.0
    hit = any(item in relevant_ids for item in retrieved_ids[:k])
    return 1.0 if hit else 0.0


def average(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)

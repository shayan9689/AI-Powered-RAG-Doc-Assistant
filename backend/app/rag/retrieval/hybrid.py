from app.schemas.retrieval import RetrievedChunk


def reciprocal_rank_fusion(
    ranked_lists: list[list[RetrievedChunk]],
    *,
    k: int = 60,
) -> list[RetrievedChunk]:
    scores: dict[str, float] = {}
    chunks: dict[str, RetrievedChunk] = {}
    for ranked in ranked_lists:
        for rank, chunk in enumerate(ranked, start=1):
            key = f"{chunk.metadata.get('document_id')}:{chunk.chunk_index}"
            scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank)
            if key not in chunks or chunk.score > chunks[key].score:
                chunks[key] = chunk
    ordered = sorted(scores, key=scores.get, reverse=True)
    return [chunks[key] for key in ordered]


def lexical_rerank(query: str, chunks: list[RetrievedChunk]) -> list[RetrievedChunk]:
    terms = [token for token in query.lower().split() if token]
    if not terms:
        return chunks
    scored: list[tuple[float, RetrievedChunk]] = []
    for chunk in chunks:
        blob = chunk.text.lower()
        overlap = sum(1 for term in terms if term in blob) / len(terms)
        scored.append((0.7 * chunk.score + 0.3 * overlap, chunk))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [
        chunk.model_copy(update={"score": round(score, 4)}) for score, chunk in scored
    ]

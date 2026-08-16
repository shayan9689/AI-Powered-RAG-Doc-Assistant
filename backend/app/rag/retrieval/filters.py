def build_where(
    *,
    user_id: str | None = None,
    document_id: str | None = None,
    document_ids: list[str] | None = None,
) -> dict[str, object] | None:
    clauses: list[dict[str, object]] = []
    if user_id:
        clauses.append({"user_id": user_id})
    if document_id:
        clauses.append({"document_id": document_id})
    elif document_ids:
        clauses.append({"document_id": {"$in": document_ids}})
    if not clauses:
        return None
    if len(clauses) == 1:
        return clauses[0]
    return {"$and": clauses}

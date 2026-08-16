from pydantic import BaseModel, Field


class RetrieveRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int | None = Field(default=None, ge=1, le=20)
    document_id: str | None = None
    document_ids: list[str] | None = None


class RetrievedChunk(BaseModel):
    chunk_index: int
    page_number: int
    text: str
    score: float
    metadata: dict[str, str | int | float]


class RetrieveResponse(BaseModel):
    query: str
    results: list[RetrievedChunk]

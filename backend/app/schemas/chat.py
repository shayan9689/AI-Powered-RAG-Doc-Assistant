from pydantic import BaseModel, Field

from app.schemas.citation import Citation


class ChatRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int | None = Field(default=None, ge=1, le=20)
    document_id: str | None = None
    document_ids: list[str] | None = None
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    answer: str
    refused: bool
    model: str
    sources: list[Citation]
    conversation_id: str | None = None

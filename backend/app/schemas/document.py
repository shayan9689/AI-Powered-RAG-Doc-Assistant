from pydantic import BaseModel, Field


class PageText(BaseModel):
    page_number: int
    text: str


class Chunk(BaseModel):
    chunk_index: int
    page_number: int
    text: str
    metadata: dict[str, str | int] = Field(default_factory=dict)


class IngestionResult(BaseModel):
    document_id: str
    filename: str
    file_type: str
    size_bytes: int
    status: str
    page_count: int
    chunk_count: int
    chunks: list[Chunk]


class DocumentSummary(BaseModel):
    id: str
    filename: str
    file_type: str
    size_bytes: int
    status: str
    page_count: int
    chunk_count: int
    created_at: str

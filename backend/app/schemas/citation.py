from pydantic import BaseModel, Field


class Citation(BaseModel):
    document_id: str
    filename: str
    page_number: int
    chunk_id: str
    chunk_index: int
    relevance_score: float
    snippet: str = Field(default="")

from pydantic import BaseModel


class ConversationSummary(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str


class ConversationMessage(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    sources: list[dict] = []
    created_at: str


class ConversationDetail(ConversationSummary):
    messages: list[ConversationMessage]

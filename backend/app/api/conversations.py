from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_app_store, get_user_id
from app.persistence.store import AppStore
from app.schemas.conversation import (
    ConversationDetail,
    ConversationMessage,
    ConversationSummary,
)

router = APIRouter(tags=["conversations"])


@router.get("/conversations", response_model=list[ConversationSummary])
def list_conversations(
    store: AppStore = Depends(get_app_store),
    user_id: str = Depends(get_user_id),
) -> list[ConversationSummary]:
    return [
        ConversationSummary.model_validate(item)
        for item in store.list_conversations(user_id)
    ]


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
def get_conversation(
    conversation_id: str,
    store: AppStore = Depends(get_app_store),
    user_id: str = Depends(get_user_id),
) -> ConversationDetail:
    convo = store.get_conversation(conversation_id)
    if not convo or convo.get("user_id") != user_id:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    messages = [
        ConversationMessage.model_validate(item)
        for item in store.list_messages(conversation_id)
    ]
    return ConversationDetail(**convo, messages=messages)


@router.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: str,
    store: AppStore = Depends(get_app_store),
    user_id: str = Depends(get_user_id),
) -> dict[str, str]:
    deleted = store.delete_conversation(conversation_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return {"status": "deleted", "conversation_id": conversation_id}

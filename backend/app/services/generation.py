from app.core.config import settings
from app.core.constants import DEFAULT_USER_ID
from app.persistence.store import AppStore
from app.rag.embeddings.base import EmbeddingClient
from app.rag.generation.base import LLMClient
from app.rag.generation.prompt import (
    REFUSAL_MESSAGE,
    SYSTEM_PROMPT,
    build_user_prompt,
    is_smalltalk,
    welcome_message,
)
from app.rag.retrieval.base import VectorStore
from app.rag.retrieval.rewrite import rewrite_followup
from app.rag.retrieval.search import retrieve_chunks
from app.schemas.chat import ChatResponse
from app.services.citations import compose_chat_answer, to_citations
from app.services.ingestion import reindex_saved_pdf

MISSING_INDEX_MESSAGE = (
    "This PDF is not indexed on the server. Re-upload it, then ask again."
)


def answer_question(
    query: str,
    *,
    embedder: EmbeddingClient,
    vector_store: VectorStore,
    llm: LLMClient,
    top_k: int | None = None,
    document_id: str | None = None,
    document_ids: list[str] | None = None,
    user_id: str = DEFAULT_USER_ID,
    conversation_id: str | None = None,
    store: AppStore | None = None,
) -> ChatResponse:
    history: list[dict[str, str]] = []
    if store and conversation_id:
        history = [
            {"role": item["role"], "content": item["content"]}
            for item in store.list_messages(conversation_id)
        ]
    filename = "this document"
    if store and document_id:
        record = store.get_document(document_id)
        if record and record.get("filename"):
            filename = str(record["filename"])

    if is_smalltalk(query):
        response = ChatResponse(
            answer=welcome_message(filename),
            refused=False,
            model=llm.model_name,
            sources=[],
            conversation_id=conversation_id,
        )
    else:
        search_query = query.strip()
        if settings.rewrite_followups and history:
            search_query = rewrite_followup(query, history, llm)

        retrieved = retrieve_chunks(
            search_query,
            embedder=embedder,
            vector_store=vector_store,
            top_k=top_k,
            document_id=document_id,
            document_ids=document_ids,
            user_id=user_id,
        )
        if not retrieved and document_id:
            reindex_saved_pdf(
                document_id,
                filename,
                embedder=embedder,
                vector_store=vector_store,
                user_id=user_id,
            )
            retrieved = retrieve_chunks(
                search_query,
                embedder=embedder,
                vector_store=vector_store,
                top_k=top_k,
                document_id=document_id,
                document_ids=document_ids,
                user_id=user_id,
            )
        evidence = [
            chunk
            for chunk in retrieved
            if chunk.score >= settings.min_retrieval_score
        ]
        if not evidence and retrieved and (document_id or document_ids):
            evidence = retrieved
        citations = to_citations(evidence if evidence else retrieved)
        if not evidence:
            response = ChatResponse(
                answer=(
                    MISSING_INDEX_MESSAGE
                    if document_id
                    else REFUSAL_MESSAGE
                ),
                refused=True,
                model=llm.model_name,
                sources=citations,
                conversation_id=conversation_id,
            )
        else:
            answer = compose_chat_answer(
                llm.generate(
                    system_prompt=SYSTEM_PROMPT,
                    user_prompt=build_user_prompt(query, evidence),
                ),
                evidence[0].text,
            )
            response = ChatResponse(
                answer=answer,
                refused=False,
                model=llm.model_name,
                sources=to_citations(evidence),
                conversation_id=conversation_id,
            )

    if store:
        active_id = conversation_id
        if not active_id:
            title = query.strip()[:80] or "New conversation"
            active_id = store.create_conversation(user_id, title)["id"]
            response.conversation_id = active_id
        convo = store.get_conversation(active_id)
        if convo and convo.get("user_id") == user_id:
            store.add_message(active_id, role="user", content=query.strip())
            store.add_message(
                active_id,
                role="assistant",
                content=response.answer,
                sources=[item.model_dump() for item in response.sources],
            )
    return response

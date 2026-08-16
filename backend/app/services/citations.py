import re

from app.schemas.citation import Citation
from app.schemas.retrieval import RetrievedChunk

_SNIPPET_LEN = 160
_MARKERS = ("SUMMARY", "OBJECTIVE", "PROFILE", "ABOUT")
_INLINE_CITE = re.compile(
    r"\s*\([^)]+\.(?:pdf|docx?|txt|md)[^)]*(?:page\s*\d+)?[^)]*\)",
    re.IGNORECASE,
)


def summarize_snippet(text: str, limit: int = _SNIPPET_LEN) -> str:
    cleaned = re.sub(r"\s+", " ", text.replace("|", " ")).strip()
    upper = cleaned.upper()
    for marker in _MARKERS:
        index = upper.find(marker)
        if index != -1:
            cleaned = cleaned[index + len(marker) :].strip(" :-")
            break
    match = re.search(r"(.+?[.!?])(?:\s|$)", cleaned)
    sentence = match.group(1).strip() if match else cleaned
    if len(sentence) > limit:
        trimmed = sentence[: limit - 1].rsplit(" ", 1)[0]
        sentence = f"{trimmed}…"
    return sentence


def strip_inline_citations(answer: str) -> str:
    return _INLINE_CITE.sub("", answer).strip()


def compose_chat_answer(answer: str, evidence_text: str) -> str:
    cleaned = strip_inline_citations(answer)
    summary = summarize_snippet(evidence_text)
    if not summary:
        return cleaned
    key = summary.rstrip("….").lower()[:50]
    if key and key in cleaned.lower():
        return cleaned
    return f"{cleaned}\n\n{summary}"


def to_citation(chunk: RetrievedChunk) -> Citation:
    document_id = str(chunk.metadata.get("document_id", ""))
    filename = str(chunk.metadata.get("filename", "document"))
    return Citation(
        document_id=document_id,
        filename=filename,
        page_number=chunk.page_number,
        chunk_id=f"{document_id}:{chunk.chunk_index}",
        chunk_index=chunk.chunk_index,
        relevance_score=chunk.score,
        snippet=summarize_snippet(chunk.text),
    )


def to_citations(chunks: list[RetrievedChunk]) -> list[Citation]:
    return [to_citation(chunk) for chunk in chunks]

from app.schemas.document import Chunk, PageText


def split_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    cleaned = text.strip()
    if not cleaned:
        return []
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and smaller than chunk_size")

    chunks: list[str] = []
    start = 0
    length = len(cleaned)
    while start < length:
        end = min(start + chunk_size, length)
        if end < length:
            split_at = cleaned.rfind(" ", start, end)
            if split_at > start:
                end = split_at
        piece = cleaned[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= length:
            break
        start = max(end - overlap, start + 1)
    return chunks


def chunk_pages(
    pages: list[PageText],
    *,
    document_id: str,
    filename: str,
    chunk_size: int,
    overlap: int,
) -> list[Chunk]:
    chunks: list[Chunk] = []
    chunk_index = 0
    for page in pages:
        for text in split_text(page.text, chunk_size, overlap):
            chunks.append(
                Chunk(
                    chunk_index=chunk_index,
                    page_number=page.page_number,
                    text=text,
                    metadata={
                        "document_id": document_id,
                        "filename": filename,
                        "page_number": page.page_number,
                        "chunk_index": chunk_index,
                    },
                )
            )
            chunk_index += 1
    return chunks

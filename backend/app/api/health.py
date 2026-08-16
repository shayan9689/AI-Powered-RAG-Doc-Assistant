from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/")
def root() -> dict[str, str]:
    return {"status": "ok", "service": "RAG Document Assistant"}


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

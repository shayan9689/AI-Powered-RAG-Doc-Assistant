import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.chat import router as chat_router
from app.api.conversations import router as conversations_router
from app.api.documents import router as documents_router
from app.api.health import router as health_router
from app.core.config import settings
from app.core.logging_middleware import RequestLoggingMiddleware
from app.core.rate_limit import RateLimitMiddleware
from app.rag.embeddings.factory import warmup_embedder

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s"
)


def create_app() -> FastAPI:
    application = FastAPI(title=settings.app_name, version="0.4.0")
    application.add_middleware(RequestLoggingMiddleware)
    application.add_middleware(RateLimitMiddleware)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_origin_regex=r"https://ai-powered-rag-doc-assistant(?:-[a-z0-9-]+)?\.vercel\.app",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(health_router)
    application.include_router(documents_router)
    application.include_router(chat_router)
    application.include_router(conversations_router)
    warmup_embedder()

    @application.exception_handler(Exception)
    async def unhandled_error(_request: Request, exc: Exception) -> JSONResponse:
        if isinstance(exc, HTTPException):
            raise exc
        return JSONResponse(
            {"detail": "An unexpected error occurred."},
            status_code=500,
        )

    return application


app = create_app()

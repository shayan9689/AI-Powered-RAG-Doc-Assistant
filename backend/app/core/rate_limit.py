import time
from collections import defaultdict, deque

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app) -> None:
        super().__init__(app)
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.method == "OPTIONS" or request.url.path in {
            "/health",
            "/docs",
            "/openapi.json",
            "/",
        }:
            return await call_next(request)
        limit = settings.rate_limit_per_minute
        if limit <= 0:
            return await call_next(request)
        key = request.client.host if request.client else "unknown"
        now = time.time()
        window = self._hits[key]
        while window and now - window[0] > 60:
            window.popleft()
        if len(window) >= limit:
            return JSONResponse(
                {"detail": "Rate limit exceeded. Try again shortly."},
                status_code=429,
            )
        window.append(now)
        return await call_next(request)

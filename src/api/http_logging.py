import logging
from collections.abc import Awaitable, Callable
from time import perf_counter

from fastapi import FastAPI, Request, Response

from src.config import Settings

logger = logging.getLogger("src.http")
CallNext = Callable[[Request], Awaitable[Response]]


def register_http_logging(app: FastAPI, settings: Settings) -> None:
    @app.middleware("http")
    async def log_request(request: Request, call_next: CallNext) -> Response:
        start = perf_counter()
        response = await call_next(request)
        duration_ms = round((perf_counter() - start) * 1000, 2)
        logger.info(
            "request completed",
            extra={
                "environment": settings.environment,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        return response

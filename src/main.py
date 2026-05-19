import logging
from time import perf_counter

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.api.v1.router import api_router
from src.config import get_settings
from src.domain.users.exceptions import UserAlreadyExistsError, UserNotFoundError
from src.logging import configure_logging

settings = get_settings()
configure_logging(settings)
logger = logging.getLogger("src.http")

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description=(
        "RESTful user management API built with FastAPI, PostgreSQL, SQLAlchemy async, "
        "Alembic, and a pragmatic Clean Architecture approach."
    ),
    openapi_tags=[
        {"name": "health", "description": "Service health and runtime environment checks."},
        {"name": "users", "description": "CRUD operations for user profiles."},
    ],
)


@app.middleware("http")
async def log_request(request: Request, call_next):
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


@app.exception_handler(UserNotFoundError)
async def user_not_found_handler(_: Request, exc: UserNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(UserAlreadyExistsError)
async def user_already_exists_handler(_: Request, exc: UserAlreadyExistsError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.get(
    "/health",
    tags=["health"],
    summary="Health check",
    description="Returns API liveness status and current runtime environment.",
)
async def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment}


app.include_router(api_router, prefix="/api/v1")

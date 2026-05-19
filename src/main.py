from fastapi import FastAPI

from src.api.exception_handlers import register_exception_handlers
from src.api.health import router as health_router
from src.api.http_logging import register_http_logging
from src.api.v1.router import api_router
from src.config import Settings, get_settings
from src.logging_config import configure_logging

OPENAPI_TAGS = [
    {"name": "health", "description": "Service health and runtime environment checks."},
    {"name": "users", "description": "CRUD operations for user profiles."},
]


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings)

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description=(
            "RESTful user management API built with FastAPI, PostgreSQL, SQLAlchemy async, "
            "Alembic, and a pragmatic Clean Architecture approach."
        ),
        openapi_tags=OPENAPI_TAGS,
    )

    register_http_logging(app, settings)
    register_exception_handlers(app)
    app.include_router(health_router)
    app.include_router(api_router, prefix="/api/v1")
    return app


app = create_app()

from fastapi import APIRouter, Depends

from src.api.schemas import HealthResponse
from src.config import Settings, get_settings

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns API liveness status and current runtime environment.",
)
async def health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    return HealthResponse(status="ok", environment=settings.environment)

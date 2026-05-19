from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "ok",
                "environment": "production",
            }
        }
    )

    status: str = Field(description="Service liveness status.", examples=["ok"])
    environment: str = Field(description="Current runtime environment.", examples=["local", "production"])


class ErrorResponse(BaseModel):
    detail: str = Field(examples=["User 11111111-1111-1111-1111-111111111111 was not found"])

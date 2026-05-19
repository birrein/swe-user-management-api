from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from src.domain.users.enums import UserRole

USERNAME_PATTERN = r"^[A-Za-z0-9_-]+$"


class UserBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    username: str = Field(
        min_length=3,
        max_length=50,
        pattern=USERNAME_PATTERN,
        description="Unique username. Use 3-50 letters, numbers, underscores, or hyphens.",
        examples=["manuel_marin"],
    )
    email: EmailStr = Field(description="Unique valid email address.", examples=["manuel.marin@example.com"])
    first_name: str = Field(min_length=1, max_length=100, description="User first name.", examples=["Manuel"])
    last_name: str = Field(min_length=1, max_length=100, description="User last name.", examples=["Marin"])
    role: UserRole = Field(
        default=UserRole.USER,
        description="User role: admin, user, or guest.",
        examples=[UserRole.USER],
    )
    active: bool = Field(default=True, description="Whether the user is active.", examples=[True])


class UserCreate(UserBase):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "description": "Payload for creating a user. Unknown fields are rejected.",
            "example": {
                "username": "manuel_marin",
                "email": "manuel.marin@example.com",
                "first_name": "Manuel",
                "last_name": "Marin",
                "role": "user",
                "active": True,
            },
        },
    )


class UserUpdate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "description": "Payload for partially updating a user. At least one known field is required.",
            "example": {
                "first_name": "Manuel",
                "last_name": "Marin",
                "role": "admin",
                "active": True,
            },
        },
    )

    username: str | None = Field(
        default=None,
        min_length=3,
        max_length=50,
        pattern=USERNAME_PATTERN,
        description="New unique username. Use 3-50 letters, numbers, underscores, or hyphens.",
    )
    email: EmailStr | None = Field(default=None, description="New unique valid email address.")
    first_name: str | None = Field(default=None, min_length=1, max_length=100, description="New first name.")
    last_name: str | None = Field(default=None, min_length=1, max_length=100, description="New last name.")
    role: UserRole | None = Field(default=None, description="New role: admin, user, or guest.")
    active: bool | None = Field(default=None, description="New active status.")

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> "UserUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided for update")
        return self


class UserRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "11111111-1111-1111-1111-111111111111",
                "username": "manuel_marin",
                "email": "manuel.marin@example.com",
                "first_name": "Manuel",
                "last_name": "Marin",
                "role": "user",
                "active": True,
                "created_at": "2026-05-18T23:00:00Z",
                "updated_at": "2026-05-18T23:00:00Z",
            }
        },
    )

    id: UUID
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    role: UserRole
    active: bool
    created_at: datetime
    updated_at: datetime


class UserListResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "id": "11111111-1111-1111-1111-111111111111",
                        "username": "manuel_marin",
                        "email": "manuel.marin@example.com",
                        "first_name": "Manuel",
                        "last_name": "Marin",
                        "role": "user",
                        "active": True,
                        "created_at": "2026-05-18T23:00:00Z",
                        "updated_at": "2026-05-18T23:00:00Z",
                    }
                ],
                "total": 1,
                "skip": 0,
                "limit": 50,
            }
        }
    )

    items: list[UserRead]
    total: int
    skip: int
    limit: int

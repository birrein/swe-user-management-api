from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.domain.users.enums import UserRole

USERNAME_PATTERN = r"^[A-Za-z0-9_-]+$"


class UserBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    username: str = Field(
        min_length=3,
        max_length=50,
        pattern=USERNAME_PATTERN,
        examples=["manuel_marin"],
    )
    email: EmailStr = Field(examples=["manuel.marin@example.com"])
    first_name: str = Field(min_length=1, max_length=100, examples=["Manuel"])
    last_name: str = Field(min_length=1, max_length=100, examples=["Marin"])
    role: UserRole = Field(default=UserRole.USER, examples=[UserRole.USER])
    active: bool = Field(default=True, examples=[True])


class UserCreate(UserBase):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "username": "manuel_marin",
                "email": "manuel.marin@example.com",
                "first_name": "Manuel",
                "last_name": "Marin",
                "role": "user",
                "active": True,
            }
        },
    )


class UserUpdate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "first_name": "Manuel",
                "last_name": "Marin",
                "role": "admin",
                "active": True,
            }
        },
    )

    username: str | None = Field(default=None, min_length=3, max_length=50, pattern=USERNAME_PATTERN)
    email: EmailStr | None = None
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    role: UserRole | None = None
    active: bool | None = None


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
    items: list[UserRead]
    total: int
    skip: int
    limit: int

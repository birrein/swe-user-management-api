from typing import Annotated

from fastapi import Depends, Query

from src.api.v1.users.dependencies import get_user_use_cases
from src.application.users.use_cases import UserUseCases
from src.domain.users.enums import UserRole

UserUseCasesDependency = Annotated[UserUseCases, Depends(get_user_use_cases)]
SkipQuery = Annotated[int, Query(ge=0, description="Number of users to skip for pagination")]
LimitQuery = Annotated[int, Query(ge=1, le=100, description="Maximum users to return")]
ActiveQuery = Annotated[bool | None, Query(description="Filter by active status")]
RoleQuery = Annotated[UserRole | None, Query(description="Filter by user role")]

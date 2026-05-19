from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status

from src.api.v1.dependencies import get_user_use_cases
from src.api.v1.schemas import UserCreate, UserListResponse, UserRead, UserUpdate
from src.application.users.use_cases import UserUseCases
from src.domain.users.enums import UserRole

router = APIRouter()


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a user",
)
async def create_user(
    payload: UserCreate,
    use_cases: Annotated[UserUseCases, Depends(get_user_use_cases)],
) -> UserRead:
    user = await use_cases.create_user(**payload.model_dump())
    return UserRead.model_validate(user)


@router.get(
    "",
    response_model=UserListResponse,
    summary="List users",
)
async def list_users(
    use_cases: Annotated[UserUseCases, Depends(get_user_use_cases)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    active: bool | None = True,
    role: UserRole | None = None,
) -> UserListResponse:
    users = await use_cases.list_users(skip=skip, limit=limit, active=active, role=role)
    return UserListResponse(
        items=[UserRead.model_validate(user) for user in users.items],
        total=users.total,
        skip=users.skip,
        limit=users.limit,
    )


@router.get(
    "/{user_id}",
    response_model=UserRead,
    summary="Get a user by id",
)
async def get_user(
    user_id: UUID,
    use_cases: Annotated[UserUseCases, Depends(get_user_use_cases)],
) -> UserRead:
    user = await use_cases.get_user(user_id)
    return UserRead.model_validate(user)


@router.patch(
    "/{user_id}",
    response_model=UserRead,
    summary="Update a user",
)
async def update_user(
    user_id: UUID,
    payload: UserUpdate,
    use_cases: Annotated[UserUseCases, Depends(get_user_use_cases)],
) -> UserRead:
    user = await use_cases.update_user(user_id, **payload.model_dump(exclude_unset=True))
    return UserRead.model_validate(user)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deactivate a user",
)
async def delete_user(
    user_id: UUID,
    use_cases: Annotated[UserUseCases, Depends(get_user_use_cases)],
) -> Response:
    await use_cases.deactivate_user(user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

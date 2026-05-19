from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status

from src.api.v1.dependencies import get_user_use_cases
from src.api.v1.schemas import ErrorResponse, UserCreate, UserListResponse, UserRead, UserUpdate
from src.application.users.use_cases import UserUseCases
from src.domain.users.enums import UserRole

router = APIRouter(tags=["users"])

VALIDATION_ERROR_RESPONSE = {
    "description": "Request validation failed",
    "content": {
        "application/json": {
            "example": {
                "detail": [
                    {
                        "type": "value_error",
                        "loc": ["body", "email"],
                        "msg": "value is not a valid email address",
                    }
                ]
            }
        }
    },
}

NOT_FOUND_RESPONSE = {"model": ErrorResponse, "description": "User was not found"}
CONFLICT_RESPONSE = {"model": ErrorResponse, "description": "Username or email already exists"}
UNPROCESSABLE_CONTENT_STATUS = 422


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a user",
    description="Creates a user with a unique username and email.",
    responses={
        status.HTTP_409_CONFLICT: CONFLICT_RESPONSE,
        UNPROCESSABLE_CONTENT_STATUS: VALIDATION_ERROR_RESPONSE,
    },
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
    description="Returns a paginated list of users. Active users are returned by default.",
    responses={UNPROCESSABLE_CONTENT_STATUS: VALIDATION_ERROR_RESPONSE},
)
async def list_users(
    use_cases: Annotated[UserUseCases, Depends(get_user_use_cases)],
    skip: Annotated[int, Query(ge=0, description="Number of users to skip for pagination")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Maximum users to return")] = 50,
    active: Annotated[bool | None, Query(description="Filter by active status")] = True,
    role: Annotated[UserRole | None, Query(description="Filter by user role")] = None,
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
    description="Returns one user by UUID, including inactive users.",
    responses={
        status.HTTP_404_NOT_FOUND: NOT_FOUND_RESPONSE,
        UNPROCESSABLE_CONTENT_STATUS: VALIDATION_ERROR_RESPONSE,
    },
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
    description="Partially updates a user. Username and email remain globally unique.",
    responses={
        status.HTTP_404_NOT_FOUND: NOT_FOUND_RESPONSE,
        status.HTTP_409_CONFLICT: CONFLICT_RESPONSE,
        UNPROCESSABLE_CONTENT_STATUS: VALIDATION_ERROR_RESPONSE,
    },
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
    summary="Soft delete a user (deactivate)",
    description="Soft deletes a user by setting active=false. The record remains queryable by id.",
    responses={
        status.HTTP_404_NOT_FOUND: NOT_FOUND_RESPONSE,
        UNPROCESSABLE_CONTENT_STATUS: VALIDATION_ERROR_RESPONSE,
    },
)
async def delete_user(
    user_id: UUID,
    use_cases: Annotated[UserUseCases, Depends(get_user_use_cases)],
) -> Response:
    await use_cases.deactivate_user(user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

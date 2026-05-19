from uuid import UUID

from fastapi import APIRouter, Response, status

from src.api.v1.users.params import ActiveQuery, LimitQuery, RoleQuery, SkipQuery, UserUseCasesDependency
from src.api.v1.users.presenters import to_user_list_response, to_user_read
from src.api.v1.users.responses import (
    CONFLICT_RESPONSE,
    EMAIL_VALIDATION_ERROR_RESPONSE,
    NOT_FOUND_RESPONSE,
    PATCH_VALIDATION_ERROR_RESPONSE,
    QUERY_VALIDATION_ERROR_RESPONSE,
    UNPROCESSABLE_CONTENT_STATUS,
    UUID_VALIDATION_ERROR_RESPONSE,
)
from src.api.v1.users.schemas import UserCreate, UserListResponse, UserRead, UserUpdate

router = APIRouter(tags=["users"])


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a user",
    description=(
        "Creates a user with a unique username and email. Unknown JSON fields are rejected. "
        "Username must be 3-50 characters and contain only letters, numbers, underscores, or hyphens."
    ),
    responses={
        status.HTTP_409_CONFLICT: CONFLICT_RESPONSE,
        UNPROCESSABLE_CONTENT_STATUS: EMAIL_VALIDATION_ERROR_RESPONSE,
    },
)
async def create_user(
    payload: UserCreate,
    use_cases: UserUseCasesDependency,
) -> UserRead:
    user = await use_cases.create_user(**payload.model_dump())
    return to_user_read(user)


@router.get(
    "",
    response_model=UserListResponse,
    summary="List users",
    description=(
        "Returns a paginated list of users. Active users are returned by default. "
        "`skip` must be greater than or equal to 0, and `limit` must be between 1 and 100."
    ),
    responses={UNPROCESSABLE_CONTENT_STATUS: QUERY_VALIDATION_ERROR_RESPONSE},
)
async def list_users(
    use_cases: UserUseCasesDependency,
    skip: SkipQuery = 0,
    limit: LimitQuery = 50,
    active: ActiveQuery = True,
    role: RoleQuery = None,
) -> UserListResponse:
    users = await use_cases.list_users(skip=skip, limit=limit, active=active, role=role)
    return to_user_list_response(users)


@router.get(
    "/{user_id}",
    response_model=UserRead,
    summary="Get a user by id",
    description="Returns one user by UUID, including inactive users.",
    responses={
        status.HTTP_404_NOT_FOUND: NOT_FOUND_RESPONSE,
        UNPROCESSABLE_CONTENT_STATUS: UUID_VALIDATION_ERROR_RESPONSE,
    },
)
async def get_user(
    user_id: UUID,
    use_cases: UserUseCasesDependency,
) -> UserRead:
    user = await use_cases.get_user(user_id)
    return to_user_read(user)


@router.patch(
    "/{user_id}",
    response_model=UserRead,
    summary="Update a user",
    description=(
        "Partially updates a user. At least one known JSON field is required, and unknown fields are rejected. "
        "Username and email remain globally unique."
    ),
    responses={
        status.HTTP_404_NOT_FOUND: NOT_FOUND_RESPONSE,
        status.HTTP_409_CONFLICT: CONFLICT_RESPONSE,
        UNPROCESSABLE_CONTENT_STATUS: PATCH_VALIDATION_ERROR_RESPONSE,
    },
)
async def update_user(
    user_id: UUID,
    payload: UserUpdate,
    use_cases: UserUseCasesDependency,
) -> UserRead:
    user = await use_cases.update_user(user_id, **payload.model_dump(exclude_unset=True))
    return to_user_read(user)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft delete a user (deactivate)",
    description="Soft deletes a user by setting active=false. The record remains queryable by id.",
    responses={
        status.HTTP_404_NOT_FOUND: NOT_FOUND_RESPONSE,
        UNPROCESSABLE_CONTENT_STATUS: UUID_VALIDATION_ERROR_RESPONSE,
    },
)
async def delete_user(
    user_id: UUID,
    use_cases: UserUseCasesDependency,
) -> Response:
    await use_cases.deactivate_user(user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

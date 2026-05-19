from src.api.v1.users.schemas import UserListResponse, UserRead
from src.application.users.ports import UserList
from src.domain.users.entity import User


def to_user_read(user: User) -> UserRead:
    return UserRead.model_validate(user)


def to_user_list_response(users: UserList) -> UserListResponse:
    return UserListResponse(
        items=[to_user_read(user) for user in users.items],
        total=users.total,
        skip=users.skip,
        limit=users.limit,
    )

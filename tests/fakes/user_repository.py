from uuid import UUID

from src.application.users.ports import UserList, UserRepository
from src.domain.users.entity import User
from src.domain.users.enums import UserRole


class InMemoryUserRepository(UserRepository):
    def __init__(self) -> None:
        self.users: dict[UUID, User] = {}

    async def create(self, user: User) -> User:
        self.users[user.id] = user
        return user

    async def get_by_id(self, user_id: UUID) -> User | None:
        return self.users.get(user_id)

    async def get_by_username(self, username: str) -> User | None:
        return next((user for user in self.users.values() if user.username == username), None)

    async def get_by_email(self, email: str) -> User | None:
        return next((user for user in self.users.values() if user.email == email), None)

    async def list_users(
        self,
        *,
        skip: int,
        limit: int,
        active: bool | None,
        role: UserRole | None,
    ) -> UserList:
        users = list(self.users.values())
        if active is not None:
            users = [user for user in users if user.active is active]
        if role is not None:
            users = [user for user in users if user.role == role]
        users = sorted(users, key=lambda user: user.created_at, reverse=True)
        return UserList(items=users[skip : skip + limit], total=len(users), skip=skip, limit=limit)

    async def update(self, user: User) -> User:
        self.users[user.id] = user
        return user

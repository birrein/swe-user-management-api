from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from src.domain.users.entity import User
from src.domain.users.enums import UserRole


@dataclass(frozen=True, slots=True)
class UserList:
    items: list[User]
    total: int
    skip: int
    limit: int


class UserRepository(Protocol):
    """Persistence port used by application use cases.

    Concrete adapters can store users in PostgreSQL, memory, or another database
    without leaking storage details into the domain/application layers.
    """

    async def create(self, user: User) -> User:
        ...

    async def get_by_id(self, user_id: UUID) -> User | None:
        ...

    async def get_by_username(self, username: str) -> User | None:
        ...

    async def get_by_email(self, email: str) -> User | None:
        ...

    async def list_users(
        self,
        *,
        skip: int,
        limit: int,
        active: bool | None,
        role: UserRole | None,
    ) -> UserList:
        ...

    async def update(self, user: User) -> User:
        ...

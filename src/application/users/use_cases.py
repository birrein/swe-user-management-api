from uuid import UUID

from src.application.users.ports import UserList, UserRepository
from src.domain.users.entity import User
from src.domain.users.enums import UserRole
from src.domain.users.exceptions import UserAlreadyExistsError, UserNotFoundError


class UserUseCases:
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    async def create_user(
        self,
        *,
        username: str,
        email: str,
        first_name: str,
        last_name: str,
        role: UserRole,
        active: bool = True,
    ) -> User:
        await self._ensure_unique_username(username)
        await self._ensure_unique_email(email)

        user = User.create(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role,
            active=active,
        )
        return await self._repository.create(user)

    async def get_user(self, user_id: UUID) -> User:
        user = await self._repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(user_id)
        return user

    async def list_users(
        self,
        *,
        skip: int,
        limit: int,
        active: bool | None,
        role: UserRole | None,
    ) -> UserList:
        return await self._repository.list_users(skip=skip, limit=limit, active=active, role=role)

    async def update_user(
        self,
        user_id: UUID,
        *,
        username: str | None = None,
        email: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        role: UserRole | None = None,
        active: bool | None = None,
    ) -> User:
        user = await self.get_user(user_id)

        if username is not None and username != user.username:
            await self._ensure_unique_username(username)
        if email is not None and email != user.email:
            await self._ensure_unique_email(email)

        updated_user = user.update(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role,
            active=active,
        )
        return await self._repository.update(updated_user)

    async def deactivate_user(self, user_id: UUID) -> None:
        user = await self.get_user(user_id)
        if not user.active:
            raise UserNotFoundError(user_id)
        await self._repository.update(user.deactivate())

    async def _ensure_unique_username(self, username: str) -> None:
        existing_user = await self._repository.get_by_username(username)
        if existing_user is not None:
            raise UserAlreadyExistsError("username", username)

    async def _ensure_unique_email(self, email: str) -> None:
        existing_user = await self._repository.get_by_email(email)
        if existing_user is not None:
            raise UserAlreadyExistsError("email", email)

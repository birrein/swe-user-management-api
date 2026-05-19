from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.users.ports import UserList
from src.domain.users.entity import User
from src.domain.users.enums import UserRole
from src.domain.users.exceptions import UserAlreadyExistsError, UserNotFoundError
from src.infrastructure.models import UserModel


class SqlAlchemyUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, user: User) -> User:
        user_model = self._to_model(user)
        self._session.add(user_model)
        try:
            await self._session.commit()
            await self._session.refresh(user_model)
        except IntegrityError as exc:
            await self._session.rollback()
            raise UserAlreadyExistsError("username or email", f"{user.username}/{user.email}") from exc
        return self._to_entity(user_model)

    async def get_by_id(self, user_id: UUID) -> User | None:
        user_model = await self._session.get(UserModel, user_id)
        return self._to_entity(user_model) if user_model is not None else None

    async def get_by_username(self, username: str) -> User | None:
        result = await self._session.execute(select(UserModel).where(UserModel.username == username))
        user_model = result.scalar_one_or_none()
        return self._to_entity(user_model) if user_model is not None else None

    async def get_by_email(self, email: str) -> User | None:
        result = await self._session.execute(select(UserModel).where(UserModel.email == email))
        user_model = result.scalar_one_or_none()
        return self._to_entity(user_model) if user_model is not None else None

    async def list_users(
        self,
        *,
        skip: int,
        limit: int,
        active: bool | None,
        role: UserRole | None,
    ) -> UserList:
        stmt = self._filtered_select(active=active, role=role)
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = await self._session.scalar(count_stmt)

        result = await self._session.execute(stmt.order_by(UserModel.created_at.desc()).offset(skip).limit(limit))
        users = [self._to_entity(user_model) for user_model in result.scalars().all()]
        return UserList(items=users, total=total or 0, skip=skip, limit=limit)

    async def update(self, user: User) -> User:
        user_model = await self._session.get(UserModel, user.id)
        if user_model is None:
            raise UserNotFoundError(user.id)

        user_model.username = user.username
        user_model.email = user.email
        user_model.first_name = user.first_name
        user_model.last_name = user.last_name
        user_model.role = user.role.value
        user_model.active = user.active
        user_model.updated_at = user.updated_at

        try:
            await self._session.commit()
            await self._session.refresh(user_model)
        except IntegrityError as exc:
            await self._session.rollback()
            raise UserAlreadyExistsError("username or email", f"{user.username}/{user.email}") from exc
        return self._to_entity(user_model)

    def _filtered_select(self, *, active: bool | None, role: UserRole | None) -> Select[tuple[UserModel]]:
        stmt = select(UserModel)
        if active is not None:
            stmt = stmt.where(UserModel.active.is_(active))
        if role is not None:
            stmt = stmt.where(UserModel.role == role.value)
        return stmt

    @staticmethod
    def _to_model(user: User) -> UserModel:
        return UserModel(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role.value,
            active=user.active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    @staticmethod
    def _to_entity(user_model: UserModel) -> User:
        return User(
            id=user_model.id,
            username=user_model.username,
            email=user_model.email,
            first_name=user_model.first_name,
            last_name=user_model.last_name,
            role=UserRole(user_model.role),
            active=user_model.active,
            created_at=user_model.created_at,
            updated_at=user_model.updated_at,
        )

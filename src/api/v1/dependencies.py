from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.users.use_cases import UserUseCases
from src.infrastructure.database import get_session
from src.infrastructure.repositories.sqlalchemy_user_repository import SqlAlchemyUserRepository


async def get_user_use_cases(
    session: AsyncSession = Depends(get_session),
) -> AsyncGenerator[UserUseCases, None]:
    yield UserUseCases(SqlAlchemyUserRepository(session))

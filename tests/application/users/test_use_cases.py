from uuid import uuid4

import pytest

from src.application.users.use_cases import UserUseCases
from src.domain.users.enums import UserRole
from src.domain.users.exceptions import UserAlreadyExistsError, UserNotFoundError
from tests.fakes.user_repository import InMemoryUserRepository


@pytest.fixture
def use_cases() -> UserUseCases:
    return UserUseCases(InMemoryUserRepository())


async def test_create_user(use_cases: UserUseCases) -> None:
    user = await use_cases.create_user(
        username="manuel_perez",
        email="manuel.perez@example.com",
        first_name="Manuel",
        last_name="Perez",
        role=UserRole.USER,
    )

    assert user.username == "manuel_perez"
    assert user.active is True
    assert user.created_at == user.updated_at


async def test_reject_duplicate_username(use_cases: UserUseCases) -> None:
    await use_cases.create_user(
        username="manuel_perez",
        email="manuel.perez@example.com",
        first_name="Manuel",
        last_name="Perez",
        role=UserRole.USER,
    )

    with pytest.raises(UserAlreadyExistsError):
        await use_cases.create_user(
            username="manuel_perez",
            email="other@example.com",
            first_name="Other",
            last_name="User",
            role=UserRole.USER,
        )


async def test_update_user_checks_email_uniqueness(use_cases: UserUseCases) -> None:
    first_user = await use_cases.create_user(
        username="manuel_perez",
        email="manuel.perez@example.com",
        first_name="Manuel",
        last_name="Perez",
        role=UserRole.USER,
    )
    await use_cases.create_user(
        username="other_user",
        email="other@example.com",
        first_name="Other",
        last_name="User",
        role=UserRole.USER,
    )

    with pytest.raises(UserAlreadyExistsError):
        await use_cases.update_user(first_user.id, email="other@example.com")


async def test_list_users_filters_and_paginates(use_cases: UserUseCases) -> None:
    await use_cases.create_user(
        username="admin_user",
        email="admin@example.com",
        first_name="Admin",
        last_name="User",
        role=UserRole.ADMIN,
    )
    guest = await use_cases.create_user(
        username="guest_user",
        email="guest@example.com",
        first_name="Guest",
        last_name="User",
        role=UserRole.GUEST,
    )
    await use_cases.deactivate_user(guest.id)

    active_users = await use_cases.list_users(skip=0, limit=50, active=True, role=None)
    inactive_guests = await use_cases.list_users(skip=0, limit=50, active=False, role=UserRole.GUEST)

    assert active_users.total == 1
    assert active_users.items[0].role == UserRole.ADMIN
    assert inactive_guests.total == 1
    assert inactive_guests.items[0].active is False


async def test_deactivate_user(use_cases: UserUseCases) -> None:
    user = await use_cases.create_user(
        username="manuel_perez",
        email="manuel.perez@example.com",
        first_name="Manuel",
        last_name="Perez",
        role=UserRole.USER,
    )

    await use_cases.deactivate_user(user.id)
    deactivated_user = await use_cases.get_user(user.id)

    assert deactivated_user.active is False
    assert deactivated_user.updated_at > user.updated_at


async def test_unknown_user_raises_not_found(use_cases: UserUseCases) -> None:
    with pytest.raises(UserNotFoundError):
        await use_cases.get_user(uuid4())

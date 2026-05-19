from dataclasses import dataclass, replace
from datetime import UTC, datetime
from uuid import UUID, uuid4

from src.domain.users.enums import UserRole


@dataclass(frozen=True, slots=True)
class User:
    id: UUID
    username: str
    email: str
    first_name: str
    last_name: str
    role: UserRole
    active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        *,
        username: str,
        email: str,
        first_name: str,
        last_name: str,
        role: UserRole,
        active: bool = True,
    ) -> "User":
        now = datetime.now(UTC)
        return cls(
            id=uuid4(),
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role,
            active=active,
            created_at=now,
            updated_at=now,
        )

    def update(
        self,
        *,
        username: str | None = None,
        email: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        role: UserRole | None = None,
        active: bool | None = None,
    ) -> "User":
        return replace(
            self,
            username=self.username if username is None else username,
            email=self.email if email is None else email,
            first_name=self.first_name if first_name is None else first_name,
            last_name=self.last_name if last_name is None else last_name,
            role=self.role if role is None else role,
            active=self.active if active is None else active,
            updated_at=datetime.now(UTC),
        )

    def deactivate(self) -> "User":
        return self.update(active=False)

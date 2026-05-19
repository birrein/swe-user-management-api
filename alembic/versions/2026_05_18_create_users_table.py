"""create users table

Revision ID: 20260518_create_users
Revises:
Create Date: 2026-05-18

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260518_create_users"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("role IN ('admin', 'user', 'guest')", name=op.f("users_role_allowed_values_check")),
        sa.PrimaryKeyConstraint("id", name="users_pkey"),
        sa.UniqueConstraint("email", name="users_email_key"),
        sa.UniqueConstraint("username", name="users_username_key"),
    )
    op.create_index("users_username_idx", "users", ["username"], unique=False)
    op.create_index("users_email_idx", "users", ["email"], unique=False)
    op.create_index("users_role_idx", "users", ["role"], unique=False)
    op.create_index("users_active_idx", "users", ["active"], unique=False)


def downgrade() -> None:
    op.drop_index("users_active_idx", table_name="users")
    op.drop_index("users_role_idx", table_name="users")
    op.drop_index("users_email_idx", table_name="users")
    op.drop_index("users_username_idx", table_name="users")
    op.drop_table("users")

"""create user table

Revision ID: 41f752dcb5df
Revises: f1be1b86f919
Create Date: 2025-02-10 13:08:19.043171

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "41f752dcb5df"
down_revision: Union[str, None] = "f1be1b86f919"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("email", sa.String, nullable=False),
        sa.Column("name", sa.String, nullable=False),
        sa.Column(
            "created_at", sa.DateTime, server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime, server_default=sa.func.now(), nullable=False
        ),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
    )
    op.execute("select diesel_manage_updated_at('user');")
    # only one user per email
    op.create_index(
        "ix_user_email",
        "user",
        ["email"],
        unique=True,
        postgresql_where=sa.column("deleted_at") == None,  # noqa: E711
    )
    # insert default user
    op.execute(
        """
        INSERT INTO "user" (email, name)
        VALUES ('admin@example.com', 'admin')
        """
    )


def downgrade() -> None:
    op.drop_table("user")

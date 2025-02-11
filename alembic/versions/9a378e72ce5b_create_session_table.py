"""create session table

Revision ID: 9a378e72ce5b
Revises: 41f752dcb5df
Create Date: 2025-02-10 13:14:09.405849

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9a378e72ce5b"
down_revision: Union[str, None] = "41f752dcb5df"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "session",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("user.id"), nullable=False),
        sa.Column("token", sa.String, nullable=False),
        sa.Column("expired_at", sa.DateTime, nullable=True),
        sa.Column(
            "created_at", sa.DateTime, server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime, server_default=sa.func.now(), nullable=False
        ),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
    )
    op.execute("select diesel_manage_updated_at('session');")
    # only one non-expired session per user
    op.create_index(
        "ix_session_user_id_not_expired_not_deleted",
        "session",
        ["user_id"],
        unique=True,
        postgresql_where=sa.and_(
            sa.column("expired_at") == None,  # noqa: E711
            sa.column("deleted_at") == None,  # noqa: E711
        ),
    )


def downgrade() -> None:
    op.drop_table("session")

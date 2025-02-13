"""create autoupdate trigger

Revision ID: f1be1b86f919
Revises:
Create Date: 2025-02-10 13:04:34.706813

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f1be1b86f919"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION diesel_manage_updated_at(_tbl regclass) RETURNS VOID AS $$
        BEGIN
            EXECUTE format('CREATE TRIGGER set_updated_at BEFORE UPDATE ON %s
                            FOR EACH ROW EXECUTE PROCEDURE diesel_set_updated_at()', _tbl);
        END;
        $$ LANGUAGE plpgsql;

        CREATE OR REPLACE FUNCTION diesel_set_updated_at() RETURNS trigger AS $$
        BEGIN
            IF (
                NEW IS DISTINCT FROM OLD AND
                NEW.updated_at IS NOT DISTINCT FROM OLD.updated_at
            ) THEN
                NEW.updated_at := current_timestamp;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP FUNCTION diesel_manage_updated_at(_tbl regclass);
        DROP FUNCTION diesel_set_updated_at();
        """
    )

"""create daily_health_data table

Revision ID: a68c0140a932
Revises: 9a378e72ce5b
Create Date: 2025-04-02 23:53:25.845412

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a68c0140a932'
down_revision: Union[str, None] = '9a378e72ce5b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'daily_health_data',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('weight_kg', sa.Float(), nullable=True),
        sa.Column('height_m', sa.Float(), nullable=True),
        sa.Column('resting_hr', sa.Float(), nullable=True),
        sa.Column('sleep_duration_hr', sa.Float(), nullable=True),
        sa.Column('sleep_quality', sa.String(), nullable=True),
        sa.Column('systolic_bp', sa.Integer(), nullable=True),
        sa.Column('diastolic_bp', sa.Integer(), nullable=True)
    )

def downgrade():
    op.drop_table('daily_health_data')


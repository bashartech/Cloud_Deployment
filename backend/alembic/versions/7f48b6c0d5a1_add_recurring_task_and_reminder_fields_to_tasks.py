"""Add recurring task and reminder fields to tasks

Revision ID: 7f48b6c0d5a1
Revises: 423310aa1e43
Create Date: 2025-12-30 02:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7f48b6c0d5a1'
down_revision: Union[str, Sequence[str], None] = '423310aa1e43'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add is_recurring column with default value False
    op.add_column('task', sa.Column('is_recurring', sa.Boolean(), server_default='false', nullable=False))

    # Add recurrence_type column (optional string for daily/weekly/monthly)
    op.add_column('task', sa.Column('recurrence_type', sa.String(length=20), nullable=True))

    # Add recurrence_interval column with default value 1
    op.add_column('task', sa.Column('recurrence_interval', sa.Integer(), server_default='1', nullable=False))

    # Add next_run_at column (optional datetime)
    op.add_column('task', sa.Column('next_run_at', sa.DateTime(), nullable=True))

    # Add reminder_at column (optional datetime)
    op.add_column('task', sa.Column('reminder_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove columns in reverse order
    op.drop_column('task', 'reminder_at')
    op.drop_column('task', 'next_run_at')
    op.drop_column('task', 'recurrence_interval')
    op.drop_column('task', 'recurrence_type')
    op.drop_column('task', 'is_recurring')
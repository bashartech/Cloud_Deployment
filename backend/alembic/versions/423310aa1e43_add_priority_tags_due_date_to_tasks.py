"""Add priority, tags, due_date to tasks

Revision ID: 423310aa1e43
Revises: 
Create Date: 2025-12-28 21:19:26.253923

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '423310aa1e43'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add priority column with default value 'medium'
    op.add_column('task', sa.Column('priority', sa.String(length=20), server_default='medium', nullable=False))

    # Add tags column with default value '[]' (JSON string for tags array)
    op.add_column('task', sa.Column('tags', sa.String(length=1000), server_default='[]', nullable=False))

    # Add due_date column (optional datetime)
    op.add_column('task', sa.Column('due_date', sa.DateTime(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove columns in reverse order
    op.drop_column('task', 'due_date')
    op.drop_column('task', 'tags')
    op.drop_column('task', 'priority')

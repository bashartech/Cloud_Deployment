"""Add conversation and chat_message tables

Revision ID: 001_conversation_chat_message
Revises: 7f48b6c0d5a1  # Latest migration from the existing files
Create Date: 2026-01-11 22:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_conversation_chat_message'
down_revision: Union[str, Sequence[str], None] = '7f48b6c0d5a1'  # Previous migration
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create conversation table
    op.create_table(
        'conversation',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_conversation_user_id', 'user_id')  # Index for user_id
    )

    # Create chat_message table
    op.create_table(
        'chat_message',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.String(length=5000), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),  # user or assistant
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversation.id'], ),
        sa.Index('ix_chat_message_user_id', 'user_id'),  # Index for user_id
        sa.Index('ix_chat_message_conversation_id', 'conversation_id')  # Index for conversation_id
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop chat_message table first (due to foreign key constraint)
    op.drop_table('chat_message')

    # Drop conversation table
    op.drop_table('conversation')
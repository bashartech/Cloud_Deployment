from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class ConversationBase(SQLModel):
    pass  # No required fields at base level


class Conversation(ConversationBase, table=True):
    __tablename__ = "conversation"  # Explicitly set table name to match migration

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)  # User ID from JWT token
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True


class ConversationCreate(ConversationBase):
    pass  # No additional fields required for creation


class ConversationRead(ConversationBase):
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime
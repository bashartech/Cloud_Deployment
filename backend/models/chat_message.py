from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class RoleEnum(str, Enum):
    user = "user"
    assistant = "assistant"


class ChatMessageBase(SQLModel):
    content: str = Field(min_length=1, max_length=5000)
    role: RoleEnum = Field(sa_column_kwargs={"default": "user"})


class ChatMessage(ChatMessageBase, table=True):
    __tablename__ = "chat_message"  # Explicitly set table name to match migration

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)  # User ID from JWT token
    conversation_id: int = Field(index=True, foreign_key="conversation.id")  # Foreign key to conversation table
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True


class ChatMessageCreate(ChatMessageBase):
    conversation_id: int  # Required for creation


class ChatMessageRead(ChatMessageBase):
    id: int
    user_id: str
    conversation_id: int
    created_at: datetime
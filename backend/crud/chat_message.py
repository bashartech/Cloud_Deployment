from sqlmodel import Session, select
from datetime import datetime
from typing import Optional
from models.chat_message import ChatMessage, ChatMessageCreate
from models.conversation import Conversation


def create_chat_message(db_session: Session, message: ChatMessageCreate, user_id: str) -> ChatMessage:
    """Create a new chat message for a user in a conversation."""
    # Verify that the conversation belongs to the user
    conversation = db_session.get(Conversation, message.conversation_id)
    if not conversation or conversation.user_id != user_id:
        raise ValueError("Conversation not found or does not belong to user")

    db_message = ChatMessage(
        user_id=user_id,
        conversation_id=message.conversation_id,
        role=message.role,
        content=message.content,
        created_at=datetime.utcnow()
    )
    db_session.add(db_message)
    db_session.commit()
    db_session.refresh(db_message)

    # Update the conversation's updated_at timestamp
    from .conversation import update_conversation_timestamp
    update_conversation_timestamp(db_session, message.conversation_id)

    return db_message


def get_message_by_id(db_session: Session, message_id: int, user_id: str) -> Optional[ChatMessage]:
    """Get a chat message by ID for a specific user."""
    statement = select(ChatMessage).where(
        ChatMessage.id == message_id,
        ChatMessage.user_id == user_id
    )
    return db_session.exec(statement).first()


def get_messages_by_conversation(db_session: Session, conversation_id: int, user_id: str) -> list:
    """Get all messages in a conversation for a specific user."""
    # First verify that the conversation belongs to the user
    conversation = db_session.get(Conversation, conversation_id)
    if not conversation or conversation.user_id != user_id:
        return []

    statement = select(ChatMessage).where(
        ChatMessage.conversation_id == conversation_id
    ).order_by(ChatMessage.created_at.asc())
    return db_session.exec(statement).all()


def get_messages_by_user(db_session: Session, user_id: str) -> list:
    """Get all messages for a specific user."""
    statement = select(ChatMessage).where(ChatMessage.user_id == user_id).order_by(ChatMessage.created_at.desc())
    return db_session.exec(statement).all()


def delete_message(db_session: Session, message_id: int, user_id: str) -> bool:
    """Delete a chat message by ID for a specific user."""
    message = db_session.get(ChatMessage, message_id)
    if message and message.user_id == user_id:
        db_session.delete(message)
        db_session.commit()
        return True
    return False


def validate_role(role: str) -> bool:
    """Validate that the role is either 'user' or 'assistant'."""
    return role in ["user", "assistant"]
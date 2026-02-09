from sqlmodel import Session, select
from datetime import datetime
from typing import Optional
from models.conversation import Conversation, ConversationCreate
from models.chat_message import ChatMessage


def create_conversation(db_session: Session, conversation: ConversationCreate, user_id: str) -> Conversation:
    """Create a new conversation for a user."""
    db_conversation = Conversation(
        user_id=user_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(db_conversation)
    db_session.commit()
    db_session.refresh(db_conversation)
    return db_conversation


def get_conversation_by_id(db_session: Session, conversation_id: int, user_id: str) -> Optional[Conversation]:
    """Get a conversation by ID for a specific user."""
    statement = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id
    )
    return db_session.exec(statement).first()


def get_conversations_by_user(db_session: Session, user_id: str) -> list[Conversation]:
    """Get all conversations for a specific user."""
    statement = select(Conversation).where(Conversation.user_id == user_id).order_by(Conversation.updated_at.desc())
    return db_session.exec(statement).all()


def update_conversation_timestamp(db_session: Session, conversation_id: int) -> Optional[Conversation]:
    """Update the updated_at timestamp of a conversation."""
    conversation = db_session.get(Conversation, conversation_id)
    if conversation:
        conversation.updated_at = datetime.utcnow()
        db_session.add(conversation)
        db_session.commit()
        db_session.refresh(conversation)
    return conversation


def delete_conversation(db_session: Session, conversation_id: int, user_id: str) -> bool:
    """Delete a conversation by ID for a specific user."""
    conversation = db_session.get(Conversation, conversation_id)
    if conversation and conversation.user_id == user_id:
        # Delete all associated messages first
        delete_messages_by_conversation(db_session, conversation_id)
        db_session.delete(conversation)
        db_session.commit()
        return True
    return False


def delete_messages_by_conversation(db_session: Session, conversation_id: int) -> None:
    """Delete all messages in a conversation."""
    statement = select(ChatMessage).where(ChatMessage.conversation_id == conversation_id)
    messages = db_session.exec(statement).all()
    for message in messages:
        db_session.delete(message)
    db_session.commit()
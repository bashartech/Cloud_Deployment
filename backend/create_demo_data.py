#!/usr/bin/env python3
"""
Script to create demo data for the chat models in the database.
"""
import os
import sys
from sqlmodel import Session
from datetime import datetime

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

from db import engine
from models.conversation import ConversationCreate
from models.chat_message import ChatMessageCreate, RoleEnum
from crud.conversation import create_conversation
from crud.chat_message import create_chat_message

def create_demo_data():
    """Create demo conversations and messages in the database."""
    print("Creating demo data for chat models...")

    # Sample user ID for demo
    user_id = "demo_user_123"

    with Session(engine) as session:
        # Create a conversation
        conversation_data = ConversationCreate()
        conversation = create_conversation(session, conversation_data, user_id)
        print(f"Created conversation ID: {conversation.id} for user: {user_id}")

        # Create sample chat messages
        messages = [
            {
                "role": "user",
                "content": "Hi there! I need help organizing my tasks."
            },
            {
                "role": "assistant",
                "content": "Hello! I'd be happy to help you organize your tasks. What tasks do you need to keep track of?"
            },
            {
                "role": "user",
                "content": "I need to complete a project proposal, schedule a meeting, and buy groceries."
            },
            {
                "role": "assistant",
                "content": "Great! I can help you manage these tasks. Would you like me to create these as todo items for you?"
            }
        ]

        for i, msg_data in enumerate(messages):
            message_create = ChatMessageCreate(
                conversation_id=conversation.id,
                role=msg_data["role"],
                content=msg_data["content"]
            )
            message = create_chat_message(session, message_create, user_id)
            print(f"Created message ID: {message.id} (Role: {message.role}) - '{message.content[:50]}...'")

        # Create another conversation with different messages
        conversation2 = create_conversation(session, conversation_data, user_id)
        print(f"Created second conversation ID: {conversation2.id} for user: {user_id}")

        # Add a few messages to the second conversation
        messages2 = [
            {
                "role": "user",
                "content": "Can you remind me about my upcoming deadlines?"
            },
            {
                "role": "assistant",
                "content": "Sure! Based on your tasks, your project proposal is due soon. Would you like me to set a reminder?"
            }
        ]

        for msg_data in messages2:
            message_create = ChatMessageCreate(
                conversation_id=conversation2.id,
                role=msg_data["role"],
                content=msg_data["content"]
            )
            message = create_chat_message(session, message_create, user_id)
            print(f"Created message ID: {message.id} (Role: {message.role}) - '{message.content[:50]}...'")

        print("\nDemo data creation completed!")
        print(f"Created 2 conversations and {len(messages) + len(messages2)} messages for user: {user_id}")

if __name__ == "__main__":
    create_demo_data()
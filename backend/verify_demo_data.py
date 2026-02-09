#!/usr/bin/env python3
"""
Script to verify demo data exists in the database.
"""
import os
import sys
from sqlmodel import Session, select

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

from db import engine
from models.conversation import Conversation
from models.chat_message import ChatMessage

def verify_demo_data():
    """Verify that demo data exists in the database."""
    print("Verifying demo data in database...")

    with Session(engine) as session:
        # Count conversations
        conversation_count = session.exec(select(Conversation)).all()
        print(f"Total conversations in database: {len(conversation_count)}")

        for conv in conversation_count:
            print(f"  - Conversation ID: {conv.id}, User ID: {conv.user_id}, Created: {conv.created_at}")

        # Count messages
        message_count = session.exec(select(ChatMessage)).all()
        print(f"Total messages in database: {len(message_count)}")

        for msg in message_count:
            print(f"  - Message ID: {msg.id}, Role: {msg.role}, Content: {msg.content[:50]}...")

if __name__ == "__main__":
    verify_demo_data()
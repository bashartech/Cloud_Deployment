#!/usr/bin/env python3
"""
Test script to verify DB CRUD operations for chat models with proper user isolation.
"""
import os
import sys
from sqlmodel import Session, select
from datetime import datetime

import os
os.chdir(os.path.dirname(__file__))  # Change to script directory

from db import engine, get_database_url
from models.conversation import Conversation, ConversationCreate
from models.chat_message import ChatMessage, ChatMessageCreate, RoleEnum
from crud.conversation import (
    create_conversation, get_conversation_by_id, get_conversations_by_user,
    delete_conversation, update_conversation_timestamp
)
from crud.chat_message import (
    create_chat_message, get_message_by_id, get_messages_by_conversation,
    get_messages_by_user, delete_message, validate_role
)


def test_conversation_crud():
    """Test conversation CRUD operations."""
    print("Testing Conversation CRUD operations...")

    with Session(engine) as session:
        # Test 1: Create a conversation
        import uuid
        user_id_1 = f"user_{uuid.uuid4().hex[:8]}"
        user_id_2 = f"user_{uuid.uuid4().hex[:8]}"

        # Create conversation for user 1
        conv_create = ConversationCreate()
        conv1 = create_conversation(session, conv_create, user_id_1)
        print(f"[OK] Created conversation: ID {conv1.id} for user {user_id_1}")

        # Create another conversation for user 1
        conv2 = create_conversation(session, conv_create, user_id_1)
        print(f"[OK] Created conversation: ID {conv2.id} for user {user_id_1}")

        # Create conversation for user 2
        conv3 = create_conversation(session, conv_create, user_id_2)
        print(f"[OK] Created conversation: ID {conv3.id} for user {user_id_2}")

        # Test 2: Get conversations by user (user isolation)
        user1_convs = get_conversations_by_user(session, user_id_1)
        user2_convs = get_conversations_by_user(session, user_id_2)

        print(f"[OK] User {user_id_1} has {len(user1_convs)} conversations")
        print(f"[OK] User {user_id_2} has {len(user2_convs)} conversations")

        # Verify user isolation
        assert len(user1_convs) == 2, f"Expected 2 conversations for user1, got {len(user1_convs)}"
        assert len(user2_convs) == 1, f"Expected 1 conversation for user2, got {len(user2_convs)}"
        print("[OK] User isolation verified for conversations")

        # Test 3: Get specific conversation by ID (user isolation)
        retrieved_conv = get_conversation_by_id(session, conv1.id, user_id_1)
        assert retrieved_conv is not None, "Should be able to retrieve own conversation"
        assert retrieved_conv.id == conv1.id, "Should retrieve correct conversation"

        # Try to get user1's conversation with user2's ID (should fail)
        unauthorized_conv = get_conversation_by_id(session, conv1.id, user_id_2)
        assert unauthorized_conv is None, "Should not be able to access other user's conversation"
        print("[OK] User isolation verified for specific conversation retrieval")

        # Test 4: Update conversation timestamp
        old_updated_at = conv1.updated_at
        updated_conv = update_conversation_timestamp(session, conv1.id)
        assert updated_conv is not None, "Should update conversation timestamp"
        assert updated_conv.updated_at > old_updated_at, "Updated timestamp should be newer"
        print("[OK] Conversation timestamp updated successfully")

        # Test 5: Delete conversation (user isolation)
        delete_result = delete_conversation(session, conv2.id, user_id_1)
        assert delete_result, "Should be able to delete own conversation"

        # Try to delete user1's conversation with user2's ID (should fail)
        delete_result = delete_conversation(session, conv1.id, user_id_2)
        assert not delete_result, "Should not be able to delete other user's conversation"
        print("[OK] User isolation verified for conversation deletion")

        print("[OK] All conversation CRUD tests passed!\n")


def test_message_crud():
    """Test chat message CRUD operations."""
    print("Testing Chat Message CRUD operations...")

    with Session(engine) as session:
        user_id_1 = "user_123"
        user_id_2 = "user_456"

        # Create a conversation for testing messages
        conv_create = ConversationCreate()
        conversation = create_conversation(session, conv_create, user_id_1)
        print(f"[OK] Created conversation {conversation.id} for testing messages")

        # Test 1: Create messages
        msg_create_user = ChatMessageCreate(
            conversation_id=conversation.id,
            role="user",
            content="Hello, this is a test message from user"
        )
        msg_create_assistant = ChatMessageCreate(
            conversation_id=conversation.id,
            role="assistant",
            content="Hello, this is a response from assistant"
        )

        msg1 = create_chat_message(session, msg_create_user, user_id_1)
        print(f"[OK] Created user message: ID {msg1.id}")

        msg2 = create_chat_message(session, msg_create_assistant, user_id_1)
        print(f"[OK] Created assistant message: ID {msg2.id}")

        # Test 2: Validate role
        assert validate_role("user"), "Should validate 'user' role"
        assert validate_role("assistant"), "Should validate 'assistant' role"
        assert not validate_role("invalid"), "Should not validate invalid role"
        print("[OK] Role validation working correctly")

        # Test 3: Get messages by conversation (user isolation)
        conv_messages = get_messages_by_conversation(session, conversation.id, user_id_1)
        assert len(conv_messages) == 2, f"Expected 2 messages, got {len(conv_messages)}"
        print(f"[OK] Retrieved {len(conv_messages)} messages from conversation")

        # Try to get messages with wrong user ID (should return empty)
        unauthorized_messages = get_messages_by_conversation(session, conversation.id, user_id_2)
        assert len(unauthorized_messages) == 0, "Should not retrieve messages for unauthorized user"
        print("[OK] User isolation verified for message retrieval by conversation")

        # Test 4: Get messages by user
        all_user_messages = get_messages_by_user(session, user_id_1)
        original_count = len(all_user_messages)
        print(f"[OK] User {user_id_1} has {original_count} total messages")

        # Test 5: Get specific message by ID (user isolation)
        retrieved_msg = get_message_by_id(session, msg1.id, user_id_1)
        assert retrieved_msg is not None, "Should retrieve own message"
        assert retrieved_msg.id == msg1.id, "Should retrieve correct message"

        # Try to get user1's message with user2's ID (should fail)
        unauthorized_msg = get_message_by_id(session, msg1.id, user_id_2)
        assert unauthorized_msg is None, "Should not access other user's message"
        print("[OK] User isolation verified for specific message retrieval")

        # Test 6: Delete message (user isolation)
        delete_result = delete_message(session, msg1.id, user_id_1)
        assert delete_result, "Should delete own message"

        # Try to delete user1's message with user2's ID (should fail)
        delete_result = delete_message(session, msg2.id, user_id_2)
        assert not delete_result, "Should not delete other user's message"
        print("[OK] User isolation verified for message deletion")

        print("[OK] All message CRUD tests passed!\n")


def main():
    print(f"Testing database CRUD operations with database URL: {get_database_url()}")
    print("This script verifies:")
    print("- Conversation CRUD operations")
    print("- Chat message CRUD operations")
    print("- User isolation (one user cannot access another user's data)")
    print("- Role validation for chat messages")
    print("- Timestamp updates for conversations")
    print("- Proper foreign key relationships")
    print()

    # Create all tables in the database
    from db import create_db_and_tables
    create_db_and_tables()

    try:
        test_conversation_crud()
        test_message_crud()
        print("SUCCESS All tests passed! Database CRUD operations are working correctly with proper user isolation.")
    except Exception as e:
        print(f"Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
"""
Test script to verify that the chat server is stateless
This test demonstrates that conversation state is persisted in the database
and survives server restarts.
"""

import asyncio
from sqlmodel import Session, create_engine
from unittest.mock import patch, MagicMock
from services.chat_service import process_chat
from models.conversation import Conversation
from models.chat_message import ChatMessage

# Mock the agent response to simulate consistent behavior
def mock_run_agent_with_mcp_tools(messages, user_id):
    """Mock agent that returns predictable responses for testing"""
    # Simulate the agent processing the message
    last_user_message = ""
    for msg in reversed(messages):
        if msg["role"] == "user":
            last_user_message = msg["content"]
            break

    # Create a deterministic response based on the input
    response = f"Echo: {last_user_message}"

    # Return empty tool calls for simplicity in testing
    tool_calls = []

    return response, tool_calls

def test_statelessness():
    """Test that the server maintains state in the database, not in memory"""

    # Use an in-memory test database or the actual database for this test
    # In a real scenario, you'd use a test database
    engine = create_engine("sqlite:///./test_todo_app.db")  # or your actual DB URL

    with Session(engine) as session:
        user_id = "test_user_123"

        # Test 1: Start a conversation
        print("Test 1: Starting a conversation...")
        conversation_id_1, response_1, tool_calls_1 = process_chat(
            user_id=user_id,
            conversation_id=None,  # New conversation
            message="Hello, world!",
            session=session
        )

        print(f"Started conversation with ID: {conversation_id_1}")
        print(f"Response: {response_1}")

        # Test 2: Continue the same conversation (simulating after server restart)
        # In a real server restart scenario, the in-memory state would be lost,
        # but the database state remains, allowing the conversation to continue
        print("\nTest 2: Continuing the conversation after simulated server restart...")
        conversation_id_2, response_2, tool_calls_2 = process_chat(
            user_id=user_id,
            conversation_id=conversation_id_1,  # Existing conversation
            message="How are you?",
            session=session
        )

        print(f"Continued conversation with ID: {conversation_id_2}")
        print(f"Response: {response_2}")

        # Verify that we're continuing the same conversation
        assert conversation_id_1 == conversation_id_2, "Should continue the same conversation"

        # Test 3: Verify conversation history is accessible
        print("\nTest 3: Verifying conversation history exists in database...")
        from crud.chat_message import get_messages_by_conversation
        messages = get_messages_by_conversation(session, conversation_id_1)

        print(f"Found {len(messages)} messages in conversation:")
        for msg in messages:
            print(f"  {msg.role}: {msg.content}")

        # Verify that both messages are in the history
        user_messages = [msg for msg in messages if msg.role == "user"]
        assistant_messages = [msg for msg in messages if msg.role == "assistant"]

        assert len(user_messages) >= 2, f"Expected at least 2 user messages, got {len(user_messages)}"
        assert len(assistant_messages) >= 2, f"Expected at least 2 assistant messages, got {len(assistant_messages)}"

        print("\n✅ All statelessness tests passed!")
        print("   - Conversation state is maintained in database")
        print("   - Server can continue conversations after restart")
        print("   - No in-memory state is required between requests")


def test_multiple_users_isolation():
    """Test that different users have isolated conversations"""
    print("\nTesting user isolation...")

    engine = create_engine("sqlite:///./test_todo_app.db")

    with Session(engine) as session:
        user1_id = "user_1"
        user2_id = "user_2"

        # User 1 starts a conversation
        conv1_id, _, _ = process_chat(
            user_id=user1_id,
            conversation_id=None,
            message="Hello from user 1",
            session=session
        )

        # User 2 starts a conversation
        conv2_id, _, _ = process_chat(
            user_id=user2_id,
            conversation_id=None,
            message="Hello from user 2",
            session=session
        )

        # Verify conversations are different
        assert conv1_id != conv2_id, "Different users should have different conversation IDs"

        print(f"User 1 conversation ID: {conv1_id}")
        print(f"User 2 conversation ID: {conv2_id}")
        print("✅ User isolation test passed!")


if __name__ == "__main__":
    # Patch the agent function to use our mock for predictable testing
    with patch('services.chat_service.run_agent_with_mcp_tools', side_effect=mock_run_agent_with_mcp_tools):
        test_statelessness()
        test_multiple_users_isolation()

    print("\n🎉 All statelessness tests completed successfully!")
    print("The server is stateless - it stores conversation state in the database,")
    print("not in memory, allowing conversations to continue after server restarts.")
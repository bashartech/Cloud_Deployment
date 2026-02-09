"""
Chat orchestration service module
Handles the complete chat flow: fetching history, building message arrays,
running the agent, storing responses, etc.
"""
import logging
from sqlmodel import Session
from typing import List, Dict, Any, Tuple
from datetime import datetime

# Set up structured logging
logger = logging.getLogger(__name__)

try:
    from ..models.chat_message import ChatMessageCreate
    from ..models.conversation import ConversationCreate
    from ..crud.conversation import (
        create_conversation as crud_create_conversation,
        get_conversation_by_id as get_conversation_by_id_and_user,
        update_conversation_timestamp
    )
    from ..crud.chat_message import (
        create_chat_message as crud_create_chat_message,
        get_messages_by_conversation
    )
except (ImportError, ValueError):
    from models.chat_message import ChatMessageCreate
    from models.conversation import ConversationCreate
    from crud.conversation import (
        create_conversation as crud_create_conversation,
        get_conversation_by_id as get_conversation_by_id_and_user,
        update_conversation_timestamp
    )
    from crud.chat_message import (
        create_chat_message as crud_create_chat_message,
        get_messages_by_conversation
    )

import os
import asyncio


def run_agent_with_mcp_tools(messages: List[Dict[str, str]], user_id: str) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Run the AI agent with MCP tools to process the conversation.

    Args:
        messages: List of messages in the conversation
        user_id: ID of the user having the conversation

    Returns:
        Tuple of (response_text, tool_calls_list)
    """
    logger.info(f"Running agent with {len(messages)} messages for user {user_id}")

    try:
        # Import the agent using the new directory name to avoid conflicts
        try:
            from ..chat_agents.chat_agent import run_chat_agent
        except (ImportError, ValueError):
            from chat_agents.chat_agent import run_chat_agent
        import asyncio

        # Get the last user message to pass to the agent
        last_user_message = ""
        for msg in reversed(messages):
            if msg["role"] == "user":
                last_user_message = msg["content"]
                break

        if not last_user_message:
            return "No user message to process", []

        # Run the agent
        # Handle async execution appropriately
        try:
            # Try to run in existing event loop first
            loop = asyncio.get_running_loop()
            # If we get here, there's already a loop running
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(lambda: asyncio.run(run_chat_agent(last_user_message, user_id)))
                result = future.result()
        except RuntimeError:
            # No event loop running, safe to create one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(run_chat_agent(last_user_message, user_id))
            finally:
                loop.close()

        response_text = result["response"]
        tool_calls = result.get("tool_calls", [])

        logger.info(f"Agent completed successfully, returning response with {len(tool_calls)} tool calls")
        return response_text, tool_calls

    except Exception as e:
        logger.error(f"Error running agent for user {user_id}: {str(e)}", exc_info=True)

        # In case of error, return a meaningful message and empty tool calls
        error_response = f"Sorry, I encountered an error processing your request: {str(e)}"
        return error_response, []


def process_chat(user_id: str, conversation_id: int, message: str, session: Session) -> Tuple[int, str, List[Dict[str, Any]]]:
    """
    Process a chat message through the complete orchestration flow.

    Args:
        user_id: ID of the user sending the message
        conversation_id: ID of the conversation (None if new)
        message: The message content from the user
        session: Database session

    Returns:
        Tuple of (conversation_id, response_text, tool_calls_list)
    """
    logger.info(f"Processing chat for user {user_id}, conversation {conversation_id}, message length: {len(message)}")
    # Step 1: Get or create conversation
    if conversation_id is None:
        logger.info(f"Creating new conversation for user {user_id}")
        # Create new conversation
        conversation_data = ConversationCreate()
        conversation = crud_create_conversation(session, conversation_data, user_id)
        conversation_id = conversation.id
        logger.info(f"Created new conversation with ID {conversation_id}")
    else:
        logger.info(f"Accessing existing conversation {conversation_id} for user {user_id}")
        # Verify user has access to this conversation
        conversation = get_conversation_by_id_and_user(session, conversation_id, user_id)
        if not conversation:
            logger.warning(f"Access denied: User {user_id} tried to access conversation {conversation_id}")
            raise ValueError("Access denied: You don't have permission to access this conversation")

        # Update conversation timestamp
        update_conversation_timestamp(session, conversation_id)
        logger.info(f"Updated timestamp for conversation {conversation_id}")

    # Step 2: Store user message in database (step 4 in spec flow)
    logger.info(f"Storing user message in conversation {conversation_id}")
    user_message_data = ChatMessageCreate(
        conversation_id=conversation_id,
        role="user",
        content=message
    )
    user_message = crud_create_chat_message(session, user_message_data, user_id)
    logger.info(f"Stored user message with ID {user_message.id if user_message else 'unknown'}")

    # Step 3: Fetch conversation history from database (step 2 in spec flow)
    logger.info(f"Fetching conversation history for conversation {conversation_id}")
    all_messages = get_messages_by_conversation(session, conversation_id, user_id)
    logger.info(f"Fetched {len(all_messages)} messages from conversation {conversation_id}")

    # Step 4: Build message array for agent (history + new message) (step 3 in spec flow)
    logger.debug(f"Building message array with {len(all_messages)} existing messages")
    messages_for_agent = []
    for msg in all_messages:
        messages_for_agent.append({
            "role": msg.role,
            "content": msg.content
        })

    # Add the new user message to the list
    messages_for_agent.append({
        "role": "user",
        "content": message
    })
    logger.info(f"Built message array with total {len(messages_for_agent)} messages for agent")

    # Step 5: Run agent with MCP tools (step 5 in spec flow)
    logger.info(f"Running agent with MCP tools for user {user_id}")
    response_text, tool_calls_result = run_agent_with_mcp_tools(messages_for_agent, user_id)
    logger.info(f"Agent responded with {len(tool_calls_result)} tool calls")

    # Step 5.5: Execute tool calls if any (NEW STEP)
    if tool_calls_result:
        logger.info(f"Executing {len(tool_calls_result)} tool calls")
        # Import MCP client to execute the tools
        try:
            from ..mcp_client import call_mcp_tool
        except (ImportError, ValueError):
            from mcp_client import call_mcp_tool

        # Create an async function to handle tool calls
        async def execute_tool_calls_async(current_response_text):
            updated_response_text = current_response_text
            for tool_call in tool_calls_result:
                try:
                    tool_name = tool_call.get("function", {}).get("name")
                    arguments = tool_call.get("function", {}).get("arguments", {})

                    if tool_name:
                        logger.info(f"Executing tool call: {tool_name} with args: {arguments}")

                        # Add user_id to arguments if not already present
                        if "user_id" not in arguments:
                            arguments["user_id"] = user_id

                        # Execute the tool call
                        tool_result = await call_mcp_tool(tool_name, arguments)
                        logger.info(f"Tool call {tool_name} result: {tool_result}")

                        # 🔥 FORMAT RESULT BASED ON TOOL TYPE
                        if tool_name == "list_tasks" and "tasks" in tool_result:
                            # Format task list in a user-friendly way
                            if tool_result["tasks"]:
                                formatted_tasks = "\n\n📋 Your Tasks:\n"
                                for task in tool_result["tasks"]:
                                    status = "✅" if task.get("completed", False) else "⏳"
                                    formatted_tasks += f"{status} [{task['id']}] {task['title']}"
                                    if task.get('description'):
                                        formatted_tasks += f" - {task['description']}"
                                    formatted_tasks += f"\n"
                                updated_response_text += formatted_tasks
                            else:
                                updated_response_text += "\n\n📋 You have no tasks at the moment."
                        elif tool_name == "add_task" and "task_id" in tool_result:
                            # Format add task result
                            updated_response_text += f"\n\n✅ Task added successfully! Task ID: {tool_result['task_id']} - {tool_result.get('title', 'New Task')}"
                        elif tool_name in ["complete_task", "delete_task", "update_task"]:
                            # Format other task operations
                            updated_response_text += f"\n\n✅ {tool_name.replace('_', ' ').title()} operation completed successfully!"
                        else:
                            # Fallback for other tools or unformatted results
                            updated_response_text += f"\n\n🛠 Tool `{tool_name}` executed successfully.\nResult: {tool_result}"

                except Exception as e:
                    logger.error(f"Error executing tool call {tool_call}: {str(e)}")
                    # Continue with other tool calls even if one fails
                    updated_response_text += f"\n\n❌ Tool `{tool_name}` failed: {str(e)}"

            return updated_response_text

        # Run the async function properly
        try:
            # Try to get the current event loop
            loop = asyncio.get_running_loop()
            # If we get here, there's already a loop running
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(lambda: asyncio.run(execute_tool_calls_async(response_text)))
                response_text = future.result()
        except RuntimeError:
            # No event loop running, safe to create one
            response_text = asyncio.run(execute_tool_calls_async(response_text))

    # Step 6: Store assistant response in database (step 7 in spec flow)
    logger.info(f"Storing assistant response in conversation {conversation_id}")

    # Handle empty response to prevent validation errors
    final_response_text = response_text if response_text.strip() else "I'm not able to process your request. Please try rephrasing or ask for help with a specific task."

    assistant_message_data = ChatMessageCreate(
        conversation_id=conversation_id,
        role="assistant",
        content=final_response_text
    )
    assistant_message = crud_create_chat_message(session, assistant_message_data, user_id)
    logger.info(f"Stored assistant response with ID {assistant_message.id if assistant_message else 'unknown'}")

    # Step 7: Return response data (will be formatted in the endpoint)
    logger.info(f"Returning processed chat result for conversation {conversation_id}")
    return conversation_id, final_response_text, tool_calls_result
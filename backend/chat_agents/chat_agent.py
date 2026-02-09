"""
Chat Agent for Todo AI Chatbot
This module analyzes user intent to determine if MCP tools should be called.
The actual tool execution happens in the service layer via the MCP client.
"""

import os
import asyncio
from typing import Dict, Any, List
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())

# Import only what we need
from agents import AsyncOpenAI

async def run_chat_agent(user_message: str, user_id: str) -> Dict[str, Any]:
    """
    Analyzes user intent and determines if MCP tools should be called.
    This function detects intent and returns structured tool calls for the service layer to execute.

    Args:
        user_message: The message from the user
        user_id: The ID of the user for proper task isolation

    Returns:
        Dictionary containing the analysis result with potential tool calls
    """
    try:
        print(f"ANALYZING INTENT FOR: {user_message}")

        # Create the async client with Gemini API
        client = AsyncOpenAI(
            
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai"
        )

        # Create a structured prompt to analyze user intent
        # prompt = f"""
        # Analyze the following user message to determine if it corresponds to any of these specific actions:

        # Actions:
        # - add_task: When user wants to create/add a new task
        # - list_tasks: When user wants to see/view/list their tasks
        # - complete_task: When user wants to mark a task as done/completed
        # - delete_task: When user wants to remove/delete a task
        # - update_task: When user wants to change/edit a task

        # CRITICAL RULES:
        # 1. For complete_task, delete_task, and update_task operations, the user MUST provide a specific task ID
        # 2. If the user wants to complete, delete, or update a task but doesn't provide a task ID, do NOT call the tool
        # 3. Instead, return should_call_tool: false and provide a helpful response asking for the task ID
        # 4. For update_task, the user must provide both a task ID and the changes to make
        # 5. For list_tasks, if user asks for specific tasks, still call the tool but the response will help them identify IDs

        # User message: "{user_message}"
        # User ID: "{user_id}"

        # Respond in JSON format with the following structure:
        # {{
        #     "should_call_tool": true/false,
        #     "tool_name": "tool_name or null",
        #     "arguments": {{"param1": "value1", ...}} or {{}},
        #     "response_if_no_tool": "a friendly response if no tool should be called"
        # }}

        # For tool_name "add_task": extract title and optional description
        # For tool_name "list_tasks": extract optional status filter (all, pending, completed)
        # For tool_name "complete_task", "delete_task", or "update_task": ONLY proceed if a specific task_id is clearly mentioned in the user message
        # For tool_name "update_task": extract task_id, and optional title/description
        # Always include user_id in arguments.

        # If the user wants to perform complete_task, delete_task, or update_task without specifying a task ID, return should_call_tool: false and a helpful response explaining what information is needed. The response should be professional and helpful, such as "To update a task, I need the specific task ID. Could you please provide the task ID? You can ask me to show your tasks first to see the IDs." or "To complete a task, I need the specific task ID. Please let me know which task ID you'd like to complete."

        # Be precise and return ONLY valid JSON without any other text.
        # """

        prompt = f"""


# You are an intelligent and professional task management assistant for a TODO application.

# Your job is to analyze the user's message and decide whether it matches one of the supported task-related actions.
# If enough information is provided, prepare a tool call.
# If information is missing, respond politely and clearly, explaining exactly what the user needs to do next.

# ━━━━━━━━━━━━━━━━━━━━━━
# SUPPORTED ACTIONS
# ━━━━━━━━━━━━━━━━━━━━━━
# - add_task: The user wants to create or add a new task
# - list_tasks: The user wants to view or list their tasks
# - complete_task: The user wants to mark a task as completed
# - delete_task: The user wants to delete a task
# - update_task: The user wants to modify an existing task

# ━━━━━━━━━━━━━━━━━━━━━━
# CRITICAL RULES (VERY IMPORTANT)
# ━━━━━━━━━━━━━━━━━━━━━━
# 1. For complete_task, delete_task, and update_task:
#    - A valid numeric task_id is REQUIRED
#    - If task_id is missing or unclear, DO NOT call any tool

# 2. For update_task:
#    - The user MUST provide:
#      - task_id
#      - at least one change (new title or description)

# 3. If required information is missing:
#    - Set "should_call_tool" to false
#    - Provide a professional, friendly explanation of what is missing
#    - Clearly guide the user on how to proceed

# 4. For list_tasks:
#    - Always allow the tool call
#    - Optional status filter: all, pending, completed

# 5. Always include user_id in tool arguments when calling a tool

# ━━━━━━━━━━━━━━━━━━━━━━
# USER CONTEXT
# ━━━━━━━━━━━━━━━━━━━━━━
# User message: "{user_message}"
# User ID: "{user_id}"

  Respond in JSON format with the following structure:
        {{
            "should_call_tool": true/false,
            "tool_name": "tool_name or null",
            "arguments": {{"param1": "value1", ...}} or {{}},
            "response_if_no_tool": "a friendly response if no tool should be called"
        }}

# ━━━━━━━━━━━━━━━━━━━━━━
# ARGUMENT EXTRACTION RULES
# ━━━━━━━━━━━━━━━━━━━━━━
# - add_task:
#   - Extract title (required)
#   - Extract description (optional)

# - list_tasks:
#   - Extract status if mentioned (all, pending, completed)

# - complete_task / delete_task:
#   - Extract numeric task_id ONLY if clearly mentioned

# - update_task:
#   - Extract numeric task_id
#   - Extract updated title and/or description

# ━━━━━━━━━━━━━━━━━━━━━━
# USER EXPERIENCE GUIDELINES
# ━━━━━━━━━━━━━━━━━━━━━━
# When information is missing, respond in a calm, professional, and user-friendly tone.

# Examples:
# - “To delete a task, I need the task ID. Please tell me the task ID you want to delete. You can ask me to show your tasks first if you’re not sure.”
# - “To update a task, please provide the task ID and what you want to change (for example, a new title or description).”
# - “I can help with that, but I need a bit more information to proceed.”

# ━━━━━━━━━━━━━━━━━━━━━━
# FINAL INSTRUCTION
# ━━━━━━━━━━━━━━━━━━━━━━
# - Be precise and accurate
# - Do NOT guess task IDs
# - Do NOT call tools when required data is missing
# - Output ONLY valid JSON — no explanations, no extra text
# """


        response = await client.chat.completions.create(
            model="gemini-2.5-flash-lite",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=500,
            response_format={"type": "json_object"}  # Force JSON response
        )

        # Extract the response
        content = response.choices[0].message.content.strip()

        # Clean the content to extract JSON if there's extra text
        import json
        try:
            # Look for JSON between curly braces
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = content[start_idx:end_idx]
                result = json.loads(json_str)
            else:
                result = json.loads(content)
        except json.JSONDecodeError:
            # If JSON parsing fails, return a safe default
            print(f"Failed to parse JSON: {content}")
            result = {
                "should_call_tool": False,
                "tool_name": None,
                "arguments": {},
                "response_if_no_tool": "I'm not able to process your request. Please try rephrasing or ask for help with a specific task."
            }

        # Ensure user_id is included in arguments if calling a tool
        if result.get("should_call_tool") and result.get("arguments"):
            if "user_id" not in result["arguments"]:
                result["arguments"]["user_id"] = user_id

        # Validate and sanitize the tool name
        allowed_tools = ["add_task", "list_tasks", "complete_task", "delete_task", "update_task"]
        tool_name = result.get("tool_name")
        if tool_name and tool_name not in allowed_tools:
            print(f"Invalid tool name: {tool_name}, setting should_call_tool to False")
            result["should_call_tool"] = False

        # Prepare the return data
        tool_calls = []
        if result.get("should_call_tool") and result.get("tool_name"):
            # Convert numeric string arguments to numbers where appropriate
            arguments = result["arguments"].copy()

            # Convert task_id to integer if it exists and is a string number
            if "task_id" in arguments and isinstance(arguments["task_id"], str) and arguments["task_id"].isdigit():
                arguments["task_id"] = int(arguments["task_id"])
            elif "task_id" in arguments and isinstance(arguments["task_id"], str):
                try:
                    arguments["task_id"] = int(float(arguments["task_id"]))
                except ValueError:
                    # If conversion fails, leave as is but log a warning
                    print(f"Warning: Could not convert task_id '{arguments['task_id']}' to integer")

            # Convert other numeric fields if needed
            numeric_fields = ["id"]  # Add other fields that should be numeric
            for field in numeric_fields:
                if field in arguments and isinstance(arguments[field], str) and arguments[field].isdigit():
                    arguments[field] = int(arguments[field])
                elif field in arguments and isinstance(arguments[field], str):
                    try:
                        arguments[field] = int(float(arguments[field]))
                    except ValueError:
                        pass  # Leave as is if conversion fails

            tool_calls.append({
                "id": "tool_call_1",
                "function": {
                    "name": result["tool_name"],
                    "arguments": arguments
                },
                "type": "function"
            })

        response_text = result.get("response_if_no_tool", "") if not result.get("should_call_tool") else ""

        response_data = {
            "response": response_text,
            "tool_calls": tool_calls,
            "user_id": user_id
        }

        print(f"Intent analysis result: {response_data}")
        return response_data

    except Exception as e:
        # Handle errors gracefully
        print(f"Error in intent analysis: {str(e)}")
        return {
            "response": f"I'm sorry, I encountered an error: {str(e)}",
            "tool_calls": [],
            "user_id": user_id,
            "error": str(e)
        }


# For backward compatibility with the services/chat_service.py
def run_agent_with_mcp_tools(messages: List[Dict[str, str]], user_id: str):
    """
    Run the agent with MCP tools integration

    Args:
        messages: List of messages in the conversation
        user_id: ID of the user for proper task isolation

    Returns:
        Tuple of (response_text, tool_calls_list)
    """
    # For now, just use the last message as the user input
    # In a real implementation, we'd process the full conversation
    if messages:
        last_user_message = ""
        for msg in reversed(messages):
            if msg["role"] == "user":
                last_user_message = msg["content"]
                break

        import asyncio
        try:
            # Run the async function synchronously for compatibility
            result = asyncio.run(run_chat_agent(last_user_message, user_id))
            return result["response"], result["tool_calls"]
        except Exception as e:
            error_msg = f"Sorry, I encountered an error processing your request: {str(e)}"
            return error_msg, []
    else:
        return "No user message to process", []


# For testing purposes
async def main():
    """Test function to verify agent creation and basic functionality"""
    print("Testing chat agent intent analysis...")
    try:
        # Test a sample interaction
        result = await run_chat_agent("show all tasks", "test_user")
        print(f"Response: {result['response']}")
        print(f"Tool calls: {result['tool_calls']}")
    except Exception as e:
        print(f"Error in intent analysis: {e}")


if __name__ == "__main__":
    asyncio.run(main())
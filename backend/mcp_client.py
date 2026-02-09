"""
MCP Client for Todo AI Chatbot
Implements the MCP communication layer as described in the architecture
Spawns the MCP server process for each tool call and communicates via STDIO
Based on the demo pattern from prompt.md
"""

import asyncio
import subprocess
import json
from typing import Any, Dict
from pathlib import Path
import os

async def call_mcp_tool(tool: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call an MCP tool by spawning a new MCP server process for each call
    This follows the pattern shown in the demo from prompt.md
    """
    # Locate the MCP server executable (built version)
    mcp_server_path = Path(__file__).parent.parent / "mcp-server" / "build" / "index.js"

    print(f"DEBUG: Attempting to call MCP tool '{tool}' with input: {input_data}")

    if not mcp_server_path.exists():
        print(f"MCP server executable not found at {mcp_server_path}. Attempting to build...")
        # Try to build it first
        result = subprocess.run([
            "npm", "run", "build"
        ], cwd=str(Path(__file__).parent.parent / "mcp-server"),
           capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Failed to build MCP server: {result.stderr}")
            raise RuntimeError(f"MCP server build failed: {result.stderr}")

    print(f"DEBUG: Starting MCP server process with path: {mcp_server_path}")

    try:
        # Use subprocess with communicate method to send/receive data safely
        proc = subprocess.Popen(
            ["node", str(mcp_server_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Format the request as per MCP protocol
        request = {
            "jsonrpc": "2.0",
            "id": 1,  # Simple ID for now
            "method": "tools/call",  # MCP protocol: all tools are called with this method
            "params": {
                "name": tool,  # The actual tool name goes here
                "arguments": input_data  # The arguments go under 'arguments'
            }
        }

        print(f"DEBUG: Sending request: {request}")

        # Send the request and get response in one operation
        request_json = json.dumps(request) + "\n"
        stdout_data, stderr_data = proc.communicate(input=request_json, timeout=10)

        response_line = stdout_data.strip()
        print(f"DEBUG: Received response line: {response_line}")

        if not response_line:
            raise RuntimeError("No response received from MCP server")

        response = json.loads(response_line)
        print(f"DEBUG: Parsed response: {response}")

        if "error" in response:
            raise RuntimeError(f"MCP tool error: {response['error']}")

        result = response.get("result", {})
        print(f"DEBUG: Returning result: {result}")
        return result

    except subprocess.TimeoutExpired:
        print("DEBUG: Timeout waiting for MCP server response")
        if proc.poll() is None:  # Process still running
            proc.kill()
            proc.wait()
        raise RuntimeError("Timeout waiting for MCP server response")
    except Exception as e:
        print(f"DEBUG: Error in MCP tool call: {str(e)}")
        if 'stderr_data' in locals() and stderr_data:
            print(f"DEBUG: stderr output: {stderr_data}")
        raise

# Convenience functions for specific tools
async def add_task(user_id: str, title: str, description: str = None) -> Dict[str, Any]:
    """Call the add_task MCP tool"""
    return await call_mcp_tool("add_task", {
        "user_id": user_id,
        "title": title,
        "description": description
    })

async def list_tasks(user_id: str, status: str = "all") -> Dict[str, Any]:
    """Call the list_tasks MCP tool"""
    return await call_mcp_tool("list_tasks", {
        "user_id": user_id,
        "status": status
    })

async def complete_task(user_id: str, task_id: int) -> Dict[str, Any]:
    """Call the complete_task MCP tool"""
    return await call_mcp_tool("complete_task", {
        "user_id": user_id,
        "task_id": task_id
    })

async def delete_task(user_id: str, task_id: int) -> Dict[str, Any]:
    """Call the delete_task MCP tool"""
    return await call_mcp_tool("delete_task", {
        "user_id": user_id,
        "task_id": task_id
    })

async def update_task(user_id: str, task_id: int, title: str = None, description: str = None) -> Dict[str, Any]:
    """Call the update_task MCP tool"""
    params = {
        "user_id": user_id,
        "task_id": task_id
    }
    if title is not None:
        params["title"] = title
    if description is not None:
        params["description"] = description

    return await call_mcp_tool("update_task", params)
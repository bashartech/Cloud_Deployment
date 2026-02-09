# AI Agent Specification for Todo AI Chatbot

## Overview
This document specifies the behavior and capabilities of the AI agent used in the Todo AI Chatbot system.

## Agent Configuration
- **Model**: Gemini 2.0 Flash or compatible LLM
- **Integration**: OpenAI Agent SDK with MCP tools
- **Authentication**: JWT-based user identification

## Supported Natural Language Commands

### Task Creation
- **Triggers**: "add", "create", "remember", "todo", "task to", "need to"
- **Example**: "Add a task to buy groceries"
- **MCP Tool**: `add_task`
- **Behavior**: Creates new task with provided title and optional description

### Task Listing
- **Triggers**: "show", "list", "see", "view", "display", "my tasks"
- **Example**: "Show me all my tasks"
- **MCP Tool**: `list_tasks`
- **Behavior**: Lists all tasks for the user with status filtering

### Task Completion
- **Triggers**: "done", "complete", "finish", "completed"
- **Example**: "Mark task #1 as complete"
- **MCP Tool**: `complete_task`
- **Behavior**: Marks specified task as completed

### Task Deletion
- **Triggers**: "delete", "remove", "cancel", "get rid of"
- **Example**: "Delete task #2"
- **MCP Tool**: `delete_task`
- **Behavior**: Deletes specified task permanently

### Task Updates
- **Triggers**: "change", "update", "rename", "modify"
- **Example**: "Update task #1 title to 'Buy organic groceries'"
- **MCP Tool**: `update_task`
- **Behavior**: Updates task title and/or description

## Agent Behavior Rules
1. Always confirm actions with friendly responses
2. Handle errors gracefully with informative messages
3. Maintain conversation context
4. Respect user privacy and data isolation
5. Provide helpful suggestions when appropriate

## Error Handling
- Invalid task IDs: Respond with "Task not found" message
- Authentication failures: Prompt for re-authentication
- Network errors: Inform user of temporary unavailability
- Ambiguous requests: Ask for clarification

## Tool Chain Support
The agent supports chaining multiple tools in sequence:
- Example: "List my tasks, then delete the first one"
- Handles multi-step workflows seamlessly
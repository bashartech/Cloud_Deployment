# MCP Tool Specification for Todo AI Chatbot

## Overview
This document specifies the Model Context Protocol (MCP) tools used by the AI agent for task management operations.

## Tool Contracts

### add_task
**Purpose**: Create a new task for the user
**Input Schema**:
```json
{
  "user_id": {
    "type": "string",
    "description": "The ID of the user creating the task",
    "required": true
  },
  "title": {
    "type": "string",
    "description": "The title of the task to create",
    "required": true
  },
  "description": {
    "type": "string",
    "description": "Optional description of the task",
    "required": false
  }
}
```
**Output Schema**:
```json
{
  "task_id": {
    "type": "integer",
    "description": "The ID of the created task"
  },
  "status": {
    "type": "string",
    "description": "The status of the operation (created)"
  },
  "title": {
    "type": "string",
    "description": "The title of the created task"
  }
}
```
**Backend Endpoint**: `POST /api/tasks`
**Authentication**: X-User-ID header or JWT token

### list_tasks
**Purpose**: Retrieve all tasks for the user
**Input Schema**:
```json
{
  "user_id": {
    "type": "string",
    "description": "The ID of the user retrieving tasks",
    "required": true
  },
  "status": {
    "type": "string",
    "description": "Filter by task status (all, pending, completed)",
    "required": false,
    "default": "all"
  }
}
```
**Output Schema**:
```json
{
  "tasks": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "id": {"type": "integer"},
        "title": {"type": "string"},
        "description": {"type": "string"},
        "completed": {"type": "boolean"},
        "created_at": {"type": "string"},
        "updated_at": {"type": "string"}
      }
    }
  }
}
```
**Backend Endpoint**: `GET /api/tasks`
**Authentication**: X-User-ID header or JWT token

### complete_task
**Purpose**: Mark a task as completed
**Input Schema**:
```json
{
  "user_id": {
    "type": "string",
    "description": "The ID of the user completing the task",
    "required": true
  },
  "task_id": {
    "type": "integer",
    "description": "The ID of the task to complete",
    "required": true
  }
}
```
**Output Schema**:
```json
{
  "task_id": {
    "type": "integer",
    "description": "The ID of the completed task"
  },
  "status": {
    "type": "string",
    "description": "The status of the operation (completed)"
  },
  "title": {
    "type": "string",
    "description": "The title of the completed task"
  }
}
```
**Backend Endpoint**: `PATCH /api/tasks/{task_id}/complete`
**Authentication**: X-User-ID header or JWT token

### delete_task
**Purpose**: Delete a task
**Input Schema**:
```json
{
  "user_id": {
    "type": "string",
    "description": "The ID of the user deleting the task",
    "required": true
  },
  "task_id": {
    "type": "integer",
    "description": "The ID of the task to delete",
    "required": true
  }
}
```
**Output Schema**:
```json
{
  "task_id": {
    "type": "integer",
    "description": "The ID of the deleted task"
  },
  "status": {
    "type": "string",
    "description": "The status of the operation (deleted)"
  },
  "title": {
    "type": "string",
    "description": "The title of the deleted task"
  }
}
```
**Backend Endpoint**: `DELETE /api/tasks/{task_id}`
**Authentication**: X-User-ID header or JWT token

### update_task
**Purpose**: Update a task's information
**Input Schema**:
```json
{
  "user_id": {
    "type": "string",
    "description": "The ID of the user updating the task",
    "required": true
  },
  "task_id": {
    "type": "integer",
    "description": "The ID of the task to update",
    "required": true
  },
  "title": {
    "type": "string",
    "description": "New title for the task (optional)",
    "required": false
  },
  "description": {
    "type": "string",
    "description": "New description for the task (optional)",
    "required": false
  }
}
```
**Output Schema**:
```json
{
  "task_id": {
    "type": "integer",
    "description": "The ID of the updated task"
  },
  "status": {
    "type": "string",
    "description": "The status of the operation (updated)"
  },
  "title": {
    "type": "string",
    "description": "The updated title of the task"
  }
}
```
**Backend Endpoint**: `PUT /api/tasks/{task_id}`
**Authentication**: X-User-ID header or JWT token

## MCP Server Configuration
- **Protocol**: HTTP-based MCP
- **Authentication**: X-User-ID header for direct user identification
- **Fallback**: JWT token authentication
- **Stateless**: Server maintains no in-memory state between requests
- **Database**: All operations use SQLModel with Neon PostgreSQL

## Security Considerations
- All operations are scoped by user_id
- Cross-user access is prevented
- MCP tools validate user permissions
- Authentication is verified before each operation
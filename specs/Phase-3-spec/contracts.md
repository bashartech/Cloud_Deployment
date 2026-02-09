# API Contracts for Phase 3 - Todo AI Chatbot

## Overview
This document defines the API contracts for the MCP tools that connect the OpenAI Agent to the Phase 2 backend services. These contracts ensure consistent communication between the AI agent and backend services.

## MCP Tool Contracts

### 1. add_task Tool

#### Description
Creates a new task for the authenticated user.

#### Tool Schema
```json
{
  "name": "add_task",
  "description": "Create a new task for the current user",
  "input_schema": {
    "type": "object",
    "properties": {
      "title": {
        "type": "string",
        "description": "The title of the task to create"
      },
      "description": {
        "type": "string",
        "description": "Optional description of the task"
      },
      "due_date": {
        "type": "string",
        "format": "date",
        "description": "Optional due date in YYYY-MM-DD format"
      }
    },
    "required": ["title"]
  }
}
```

#### MCP Server Implementation
- Validates input parameters against schema
- Attaches JWT token to backend request
- Makes POST request to `/api/tasks/` endpoint
- Returns normalized response with task ID and confirmation

#### Backend Endpoint
- Method: `POST`
- Path: `/api/tasks/`
- Headers: `Authorization: Bearer {token}`
- Request Body: `{ "title": "...", "description": "...", "due_date": "..." }`
- Response: `{ "id": "...", "title": "...", "completed": false, ... }`

#### Expected Response
```json
{
  "success": true,
  "task_id": "uuid-string",
  "message": "Task 'Buy groceries' created successfully"
}
```

### 2. list_tasks Tool

#### Description
Retrieves all tasks for the authenticated user.

#### Tool Schema
```json
{
  "name": "list_tasks",
  "description": "Retrieve all tasks for the current user",
  "input_schema": {
    "type": "object",
    "properties": {
      "status": {
        "type": "string",
        "enum": ["all", "pending", "completed"],
        "description": "Filter tasks by status, default is 'all'"
      },
      "due_date_filter": {
        "type": "string",
        "enum": ["today", "week", "month", "overdue"],
        "description": "Optional filter for due date range"
      }
    }
  }
}
```

#### MCP Server Implementation
- Validates input parameters against schema
- Attaches JWT token to backend request
- Makes GET request to `/api/tasks/` endpoint with query parameters
- Returns normalized response with filtered tasks

#### Backend Endpoint
- Method: `GET`
- Path: `/api/tasks/?status={status}&due_date_filter={filter}`
- Headers: `Authorization: Bearer {token}`
- Response: Array of task objects

#### Expected Response
```json
{
  "success": true,
  "count": 3,
  "tasks": [
    {
      "id": "uuid-string",
      "title": "Buy groceries",
      "completed": false,
      "due_date": "2024-01-15"
    }
  ]
}
```

### 3. update_task Tool

#### Description
Updates an existing task for the authenticated user.

#### Tool Schema
```json
{
  "name": "update_task",
  "description": "Update an existing task for the current user",
  "input_schema": {
    "type": "object",
    "properties": {
      "task_id": {
        "type": "string",
        "description": "The ID of the task to update"
      },
      "title": {
        "type": "string",
        "description": "New title for the task"
      },
      "description": {
        "type": "string",
        "description": "New description for the task"
      },
      "due_date": {
        "type": "string",
        "format": "date",
        "description": "New due date in YYYY-MM-DD format"
      }
    },
    "required": ["task_id"]
  }
}
```

#### MCP Server Implementation
- Validates input parameters against schema
- Attaches JWT token to backend request
- Makes PUT request to `/api/tasks/{task_id}` endpoint
- Returns normalized response with updated task info

#### Backend Endpoint
- Method: `PUT`
- Path: `/api/tasks/{task_id}`
- Headers: `Authorization: Bearer {token}`
- Request Body: `{ "title": "...", "description": "...", "due_date": "..." }`
- Response: Updated task object

#### Expected Response
```json
{
  "success": true,
  "task_id": "uuid-string",
  "message": "Task 'Buy groceries' updated successfully"
}
```

### 4. complete_task Tool

#### Description
Marks a task as completed for the authenticated user.

#### Tool Schema
```json
{
  "name": "complete_task",
  "description": "Mark a task as completed for the current user",
  "input_schema": {
    "type": "object",
    "properties": {
      "task_id": {
        "type": "string",
        "description": "The ID of the task to mark as completed"
      },
      "completed": {
        "type": "boolean",
        "description": "Whether to mark as completed (true) or pending (false), default is true"
      }
    },
    "required": ["task_id"]
  }
}
```

#### MCP Server Implementation
- Validates input parameters against schema
- Attaches JWT token to backend request
- Makes PATCH request to `/api/tasks/{task_id}/complete` endpoint
- Returns normalized response with completion status

#### Backend Endpoint
- Method: `PATCH`
- Path: `/api/tasks/{task_id}/complete`
- Headers: `Authorization: Bearer {token}`
- Request Body: `{ "completed": true/false }`
- Response: Updated task object

#### Expected Response
```json
{
  "success": true,
  "task_id": "uuid-string",
  "completed": true,
  "message": "Task 'Buy groceries' marked as completed"
}
```

### 5. delete_task Tool

#### Description
Deletes a task for the authenticated user.

#### Tool Schema
```json
{
  "name": "delete_task",
  "description": "Delete a task for the current user",
  "input_schema": {
    "type": "object",
    "properties": {
      "task_id": {
        "type": "string",
        "description": "The ID of the task to delete"
      }
    },
    "required": ["task_id"]
  }
}
```

#### MCP Server Implementation
- Validates input parameters against schema
- Attaches JWT token to backend request
- Makes DELETE request to `/api/tasks/{task_id}` endpoint
- Returns normalized response confirming deletion

#### Backend Endpoint
- Method: `DELETE`
- Path: `/api/tasks/{task_id}`
- Headers: `Authorization: Bearer {token}`
- Response: `{ "message": "Task deleted successfully" }`

#### Expected Response
```json
{
  "success": true,
  "task_id": "uuid-string",
  "message": "Task deleted successfully"
}
```

## Error Response Format

All MCP tools follow the same error response format:

```json
{
  "success": false,
  "error": {
    "type": "validation_error|authentication_error|not_found|server_error",
    "message": "Human-readable error message",
    "details": "Additional error details if available"
  }
}
```

## Security Requirements

### Authentication
- Every tool call must include a valid JWT token
- MCP server must validate token before making backend requests
- Backend must verify user ownership of resources

### Authorization
- All operations must be scoped to authenticated user
- MCP tools must verify user_id matches authenticated user
- Backend enforces user isolation for all operations

### Validation
- All input parameters must be validated against schema
- Invalid parameters must result in validation errors
- MCP server must not make backend requests with invalid data

## Performance Requirements

### Response Times
- Tool calls should respond within 5 seconds under normal conditions
- MCP server should implement reasonable timeouts for backend requests
- Retry logic should be implemented for transient failures

### Concurrency
- MCP server should handle concurrent tool calls appropriately
- Backend must handle concurrent requests without data corruption
- Database operations should be atomic where required

## Monitoring and Logging

### MCP Server Logging
- Log tool call initiation with sanitized parameters
- Log backend response status and timing
- Log errors with appropriate detail levels

### Error Tracking
- Track failed tool calls for debugging
- Monitor error rates and response times
- Alert on security-related failures
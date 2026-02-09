---
name: "Secure REST API Implementation & User-ID URL Enforcement"
description: "Implement fully documented REST API endpoints with strict JWT authentication, URL-based user enforcement, and query-based filtering and sorting, ensuring the backend API behaves exactly as specified in the docs, without shortcuts."
version: "1.0.0"
---

# Secure REST API Implementation & User-ID URL Enforcement

## When to Use This Skill

Use this skill when you need to:
- Implement fully documented REST API endpoints with strict JWT authentication
- Enforce URL-based user validation where user ID must be present in the URL
- Create secure API endpoints that verify JWT user matches URL user
- Build filtering and sorting capabilities for task lists
- Ensure backend API behaves exactly as specified in documentation
- Implement production-grade security with user isolation

This skill ensures the backend API behaves exactly as specified in the docs, without shortcuts.

## Process Steps

1. **Implement Exact REST Endpoints**
   - GET /api/{user_id}/tasks
   - POST /api/{user_id}/tasks
   - GET /api/{user_id}/tasks/{id}
   - PUT /api/{user_id}/tasks/{id}
   - DELETE /api/{user_id}/tasks/{id}
   - PATCH /api/{user_id}/tasks/{id}/complete
   - Ensure all endpoints are under `/api/` path
   - Validate user ID is present in URL path

2. **JWT Authentication Enforcement**
   - Extract JWT from `Authorization: Bearer <token>` header
   - Verify JWT signature using shared secret
   - Decode user ID from JWT token payload
   - Reject invalid or expired tokens with appropriate HTTP status codes

3. **URL ↔ JWT User Validation**
   - Compare `{user_id}` parameter in URL with decoded JWT user ID
   - Reject requests where URL user ID doesn't match JWT user ID with `403 Forbidden`
   - Never trust frontend-provided user IDs in request bodies
   - Implement proper validation middleware

4. **User-Scoped Query Enforcement**
   - Filter all database queries by authenticated user ID
   - Prevent horizontal privilege escalation attacks
   - Ensure users can only access their own data
   - Implement proper authorization checks

5. **Filtering & Sorting Support**
   - Implement query parameters for filtering: `status=all|pending|completed`
   - Implement query parameters for sorting: `sort=created|title|due_date`
   - Apply filters at database query level for performance
   - Validate query parameters to prevent injection

6. **Consistent API Responses**
   - Use Pydantic response models for consistent output
   - Return proper HTTP status codes (200, 201, 401, 403, 404, etc.)
   - Ensure no raw ORM objects are leaked in responses
   - Implement proper error response formatting

## Output Format

The skill will produce:
- Fully compliant REST API with specified endpoint paths
- JWT authentication enforced on all endpoints
- URL-user ID validation to prevent unauthorized access
- Filtering and sorting capabilities for task lists
- Consistent API response formats using Pydantic models
- Proper HTTP status codes and error handling
- Documentation for API endpoints and parameters

## Example

**Input:** Implement secure REST API with user ID in URL and filtering/sorting

**Process:**
```python
# main.py (FastAPI app)
from fastapi import FastAPI, Depends, HTTPException, Query
from typing import List, Optional
from enum import Enum
import schemas
import models
import auth

app = FastAPI()

# Define enums for query parameters
class StatusFilter(str, Enum):
    all = "all"
    pending = "pending"
    completed = "completed"

class SortField(str, Enum):
    created = "created"
    title = "title"
    due_date = "due_date"

# GET /api/{user_id}/tasks
@app.get("/api/{user_id}/tasks", response_model=List[schemas.Task])
async def get_user_tasks(
    user_id: int,
    current_user_id: int = Depends(auth.get_current_user_id),
    status: StatusFilter = Query(StatusFilter.all),
    sort: SortField = Query(SortField.created)
):
    """Get tasks for a specific user with filtering and sorting"""
    # Verify JWT user matches URL user
    if current_user_id != user_id:
        raise HTTPException(status_code=403, detail="User ID mismatch")

    # Apply filters and sorting
    filters = {"user_id": user_id}
    if status != StatusFilter.all:
        filters["completed"] = (status == StatusFilter.completed)

    # Apply sorting
    order_by = sort.value
    if sort == SortField.created:
        order_by = "created_at"

    return await models.Task.get_filtered_tasks(filters, order_by)

# POST /api/{user_id}/tasks
@app.post("/api/{user_id}/tasks", response_model=schemas.Task)
async def create_task(
    user_id: int,
    task: schemas.TaskCreate,
    current_user_id: int = Depends(auth.get_current_user_id)
):
    """Create a new task for a specific user"""
    # Verify JWT user matches URL user
    if current_user_id != user_id:
        raise HTTPException(status_code=403, detail="User ID mismatch")

    db_task = models.Task(
        title=task.title,
        description=task.description,
        completed=False,
        user_id=user_id
    )
    return await db_task.save()

# GET /api/{user_id}/tasks/{id}
@app.get("/api/{user_id}/tasks/{task_id}", response_model=schemas.Task)
async def get_task(
    user_id: int,
    task_id: int,
    current_user_id: int = Depends(auth.get_current_user_id)
):
    """Get a specific task for a user"""
    # Verify JWT user matches URL user
    if current_user_id != user_id:
        raise HTTPException(status_code=403, detail="User ID mismatch")

    task = await models.Task.get_by_id_and_user(task_id, user_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task

# PUT /api/{user_id}/tasks/{id}
@app.put("/api/{user_id}/tasks/{task_id}", response_model=schemas.Task)
async def update_task(
    user_id: int,
    task_id: int,
    task_update: schemas.TaskUpdate,
    current_user_id: int = Depends(auth.get_current_user_id)
):
    """Update a specific task for a user"""
    # Verify JWT user matches URL user
    if current_user_id != user_id:
        raise HTTPException(status_code=403, detail="User ID mismatch")

    existing_task = await models.Task.get_by_id_and_user(task_id, user_id)
    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update task fields
    for field, value in task_update.dict(exclude_unset=True).items():
        setattr(existing_task, field, value)

    return await existing_task.save()

# DELETE /api/{user_id}/tasks/{id}
@app.delete("/api/{user_id}/tasks/{task_id}")
async def delete_task(
    user_id: int,
    task_id: int,
    current_user_id: int = Depends(auth.get_current_user_id)
):
    """Delete a specific task for a user"""
    # Verify JWT user matches URL user
    if current_user_id != user_id:
        raise HTTPException(status_code=403, detail="User ID mismatch")

    deleted = await models.Task.delete_by_id_and_user(task_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")

    return {"message": "Task deleted successfully"}

# PATCH /api/{user_id}/tasks/{id}/complete
@app.patch("/api/{user_id}/tasks/{task_id}/complete", response_model=schemas.Task)
async def complete_task(
    user_id: int,
    task_id: int,
    current_user_id: int = Depends(auth.get_current_user_id)
):
    """Mark a specific task as completed for a user"""
    # Verify JWT user matches URL user
    if current_user_id != user_id:
        raise HTTPException(status_code=403, detail="User ID mismatch")

    existing_task = await models.Task.get_by_id_and_user(task_id, user_id)
    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")

    existing_task.completed = True
    return await existing_task.save()
```

**Output:** A fully secure REST API with user ID enforcement in URLs, JWT authentication, filtering and sorting capabilities, and proper user isolation ensuring users can only access their own tasks.

## Implementation Rules

- Do NOT create `/api/tasks` shortcuts (all endpoints must include user_id in path)
- Do NOT infer user without URL match (always validate URL user matches JWT user)
- Do NOT expose data across users (implement strict user isolation)
- Do NOT skip query filtering (always filter by authenticated user)
- Do NOT trust frontend-provided user IDs in request bodies
- Do NOT allow URL-user ID mismatches (reject with 403 Forbidden)
- Ensure all database queries include proper user ID validation
- Implement proper validation for query parameters
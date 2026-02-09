from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List
try:
    from ..models.task import Task, TaskCreate, TaskRead, TaskUpdate
    from ..db import get_session
    from ..auth import get_user_id_from_token
    from ..crud.task import (
        create_task as crud_create_task,
        get_tasks_by_user,
        get_task_by_id_and_user,
        get_task_by_id,
        update_task as crud_update_task,
        toggle_task_completion,
        delete_task as crud_delete_task
    )
    from ..utils.event_publisher import (
        publish_task_created_event,
        publish_reminder_set_event,
        publish_task_updated_event,
        publish_task_completed_event,
        publish_task_deleted_event
    )
except ImportError:
    from models.task import Task, TaskCreate, TaskRead, TaskUpdate
    from db import get_session
    from auth import get_user_id_from_token
    from crud.task import (
        create_task as crud_create_task,
        get_tasks_by_user,
        get_task_by_id_and_user,
        get_task_by_id,
        update_task as crud_update_task,
        toggle_task_completion,
        delete_task as crud_delete_task
    )
    from utils.event_publisher import (
        publish_task_created_event,
        publish_reminder_set_event,
        publish_task_updated_event,
        publish_task_completed_event,
        publish_task_deleted_event
    )
import os
from datetime import datetime

router = APIRouter(tags=["tasks"])

@router.post("/tasks", response_model=TaskRead)
def create_task(
    task: TaskCreate,
    user_id: str = Depends(get_user_id_from_token),
    session: Session = Depends(get_session)
):
    """
    Create a new task for the authenticated user.

    The user_id is extracted from the JWT token, not from the request body,
    ensuring users can only create tasks for themselves.
    """
    db_task = crud_create_task(session, task, user_id)
    
    # Publish task created event with metadata
    import asyncio
    try:
        # Convert task data to dict for the event
        task_dict = db_task.model_dump()
        
        # Add event metadata
        event_metadata = {
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "task-service"
        }
        
        # Include event metadata in the published event
        task_with_metadata = {**task_dict, **event_metadata}
        asyncio.run(publish_task_created_event(db_task.id, task_with_metadata, user_id))
        
        # If the task has a due date or reminder, publish a reminder event
        if db_task.reminder_at:
            asyncio.run(
                publish_reminder_set_event(
                    task_id=db_task.id,
                    title=db_task.title,
                    remind_at=db_task.reminder_at,
                    user_id=user_id,
                    due_at=db_task.due_date
                )
            )
    except Exception as e:
        # Log the error but don't fail the task creation if event publishing fails
        print(f"Error publishing task created event: {str(e)}")
    
    return db_task


@router.get("/tasks", response_model=List[TaskRead])
def read_tasks(
    user_id: str = Depends(get_user_id_from_token),
    session: Session = Depends(get_session),
    completed: str = None,  # "all", "pending", "completed"
    priority: str = None,   # "low", "medium", "high"
    search: str = None,     # search term for title/description
    sort: str = "created_at",  # field to sort by
    order: str = "desc",      # sort order: "asc" or "desc"
    tags: str = None        # tag to filter by
):
    """
    Retrieve all tasks for the authenticated user with optional filtering, search, and sorting.

    Query parameters:
    - completed: Filter by completion status ("pending", "completed", "all")
    - priority: Filter by priority level ("low", "medium", "high")
    - search: Search term to match in title or description
    - sort: Field to sort by ("created_at", "due_date", "priority", "title")
    - order: Sort order ("asc", "desc")
    - tags: Filter by a specific tag
    """
    tasks = get_tasks_by_user(
        session,
        user_id,
        completed=completed,
        priority=priority,
        search=search,
        sort=sort,
        order=order,
        tags=tags
    )
    return tasks


@router.get("/tasks/{task_id}", response_model=TaskRead)
def read_task(
    task_id: int,
    user_id: str = Depends(get_user_id_from_token),
    session: Session = Depends(get_session)
):
    """
    Retrieve a specific task by ID.

    Users can only access their own tasks. If a task doesn't exist
    a 404 error is returned. If the task exists but belongs to another user,
    a 403 error is returned.
    """
    # First check if the task exists (without checking ownership)
    task_exists = get_task_by_id(session, task_id)

    if not task_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Now check if the task belongs to the authenticated user
    task = get_task_by_id_and_user(session, task_id, user_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You don't have permission to access this task"
        )

    return task


@router.put("/tasks/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    user_id: str = Depends(get_user_id_from_token),
    session: Session = Depends(get_session)
):
    """
    Update a specific task by ID.

    Users can only update their own tasks. The update can include
    title, description, and completion status.
    """
    # First check if the task exists (without checking ownership)
    task_exists = get_task_by_id(session, task_id)

    if not task_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Now try to update the task (ownership check happens in the CRUD function)
    updated_task = crud_update_task(session, task_id, user_id, task_update)

    if not updated_task:
        # If the task exists but wasn't updated, it means the user doesn't own it
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You don't have permission to update this task"
        )

    # Publish task updated event
    import asyncio
    try:
        # Convert task data to dict for the event
        task_dict = updated_task.model_dump()
        asyncio.run(publish_task_updated_event(updated_task.id, task_dict, user_id))
    except Exception as e:
        # Log the error but don't fail the task update if event publishing fails
        print(f"Error publishing task updated event: {str(e)}")

    return updated_task


@router.patch("/tasks/{task_id}/complete", response_model=TaskRead)
def update_task_completion(
    task_id: int,
    user_id: str = Depends(get_user_id_from_token),
    session: Session = Depends(get_session)
):
    """
    Toggle the completion status of a task.

    Users can only update their own tasks.
    """
    # First check if the task exists (without checking ownership)
    task_exists = get_task_by_id(session, task_id)

    if not task_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Now try to toggle the task completion (ownership check happens in the CRUD function)
    updated_task = toggle_task_completion(session, task_id, user_id)

    if not updated_task:
        # If the task exists but wasn't updated, it means the user doesn't own it
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You don't have permission to update this task"
        )

    # Publish task completed event if the task is being marked as completed
    import asyncio
    try:
        # Check if the task was marked as completed (not toggled back to incomplete)
        if updated_task.completed:
            # Convert task data to dict for the event
            task_dict = updated_task.model_dump()
            asyncio.run(publish_task_completed_event(updated_task.id, task_dict, user_id))
    except Exception as e:
        # Log the error but don't fail the task completion if event publishing fails
        print(f"Error publishing task completed event: {str(e)}")

    return updated_task


@router.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    user_id: str = Depends(get_user_id_from_token),
    session: Session = Depends(get_session)
):
    """
    Delete a specific task by ID.

    Users can only delete their own tasks.
    """
    # First check if the task exists (without checking ownership)
    task_exists = get_task_by_id(session, task_id)

    if not task_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Get the task before deletion to include in the event
    task_to_delete = get_task_by_id_and_user(session, task_id, user_id)
    if not task_to_delete:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You don't have permission to delete this task"
        )

    # Now try to delete the task (ownership check happens in the CRUD function)
    success = crud_delete_task(session, task_id, user_id)

    if not success:
        # If the task exists but wasn't deleted, it means the user doesn't own it
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You don't have permission to delete this task"
        )

    # Publish task deleted event
    import asyncio
    try:
        # Convert task data to dict for the event
        task_dict = task_to_delete.model_dump()
        asyncio.run(publish_task_deleted_event(task_to_delete.id, task_dict, user_id))
    except Exception as e:
        # Log the error but don't fail the task deletion if event publishing fails
        print(f"Error publishing task deleted event: {str(e)}")

    return {"message": "Task deleted successfully"}
from sqlmodel import Session, select, case
from typing import List, Optional
import json
try:
    from ..models.task import Task, TaskCreate, TaskUpdate, TaskRead
except ImportError:
    from models.task import Task, TaskCreate, TaskUpdate, TaskRead
def create_task(session: Session, task: TaskCreate, user_id: str) -> TaskRead:
    """
    Create a new task in the database.

    Args:
        session: Database session
        task: TaskCreate object with task data
        user_id: ID of the user creating the task

    Returns:
        Created Task object converted to TaskRead format
    """
    # Convert tags list to JSON string for storage, ensuring it's always a valid JSON array
    tags_json = json.dumps(task.tags) if task.tags is not None else "[]"

    # Convert priority enum to string for database storage
    priority_str = task.priority.value if hasattr(task.priority, 'value') else task.priority

    db_task = Task(
        title=task.title,
        description=task.description,
        completed=task.completed,
        user_id=user_id,
        priority=priority_str,
        tags=tags_json,
        due_date=task.due_date,
        is_recurring=task.is_recurring,
        recurrence_type=task.recurrence_type,
        recurrence_interval=task.recurrence_interval,
        next_run_at=task.next_run_at,
        reminder_at=task.reminder_at
    )

    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    # Return the task in TaskRead format to properly handle the tags field
    return convert_task_to_read(db_task)


def get_tasks_by_user(
    session: Session,
    user_id: str,
    completed: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None,
    sort: Optional[str] = "created_at",
    order: Optional[str] = "desc",
    tags: Optional[str] = None
) -> List[TaskRead]:
    """
    Retrieve all tasks for a specific user.

    Args:
        session: Database session
        user_id: ID of the user whose tasks to retrieve
        completed: Optional filter for completion status ("pending", "completed", "all")
        priority: Optional filter for priority ("low", "medium", "high")
        search: Optional search term to search in title and description
        sort: Field to sort by ("created_at", "due_date", "priority", "title")
        order: Sort order ("asc", "desc")
        tags: Optional tag to filter by

    Returns:
        List of Task objects converted to TaskRead format
    """
    query = select(Task).where(Task.user_id == user_id)

    # Apply filters
    if completed == "pending":
        query = query.where(Task.completed == False)
    elif completed == "completed":
        query = query.where(Task.completed == True)

    if priority:
        # Convert priority enum to string for database query if needed
        priority_str = priority.value if hasattr(priority, 'value') else priority
        query = query.where(Task.priority == priority_str)

    if search:
        # Search in both title and description using ILIKE for case-insensitive matching
        search_pattern = f"%{search}%"
        query = query.where((Task.title.ilike(search_pattern)) | (Task.description.ilike(search_pattern)))

    if tags:
        # Filter by tag - check if the tag exists in the JSON array
        # Use PostgreSQL's JSON contains operator to check if the tag is in the tags array
        query = query.where(Task.tags.op('::jsonb').contains('["' + tags + '"]'))

    # Apply sorting
    if sort == "due_date":
        if order == "asc":
            query = query.order_by(Task.due_date.asc(), Task.created_at.desc())
        else:
            query = query.order_by(Task.due_date.desc(), Task.created_at.desc())
    elif sort == "priority":
        # Sort by priority: high, medium, low
        priority_order = case(
            (Task.priority == "high", 1),
            (Task.priority == "medium", 2),
            (Task.priority == "low", 3),
            else_=4
        )
        if order == "asc":
            query = query.order_by(priority_order.asc(), Task.created_at.desc())
        else:
            query = query.order_by(priority_order.asc(), Task.created_at.desc())
    elif sort == "title":
        if order == "asc":
            query = query.order_by(Task.title.asc())
        else:
            query = query.order_by(Task.title.desc())
    else:  # Default to created_at
        if order == "asc":
            query = query.order_by(Task.created_at.asc())
        else:
            query = query.order_by(Task.created_at.desc())

    tasks = session.exec(query).all()
    # Convert all tasks to TaskRead format before returning
    return [convert_task_to_read(task) for task in tasks]




def convert_task_to_read(task: Task) -> TaskRead:
    """
    Convert a Task object to a TaskRead object.
    This properly handles the tags field conversion from JSON string to list.
    """
    if task:
        # Safely parse the tags JSON, with fallback to empty list if invalid
        tags_list = []
        if task.tags:
            try:
                tags_list = json.loads(task.tags)
                # Ensure tags_list is always a list
                if not isinstance(tags_list, list):
                    tags_list = []
            except json.JSONDecodeError:
                # If JSON is malformed, return empty list
                tags_list = []

        return TaskRead(
            id=task.id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            user_id=task.user_id,
            created_at=task.created_at,
            updated_at=task.updated_at,
            priority=task.priority,
            tags=tags_list,
            due_date=task.due_date,
            is_recurring=task.is_recurring,
            recurrence_type=task.recurrence_type,
            recurrence_interval=task.recurrence_interval,
            next_run_at=task.next_run_at,
            reminder_at=task.reminder_at
        )
    return None

def get_task_by_id_and_user(session: Session, task_id: int, user_id: str) -> Optional[TaskRead]:
    """
    Retrieve a specific task by ID and user ID.

    Args:
        session: Database session
        task_id: ID of the task to retrieve
        user_id: ID of the user who owns the task

    Returns:
        Task object converted to TaskRead format if found and owned by user, None otherwise
    """
    task = session.get(Task, task_id)
    if task and task.user_id == user_id:
        return convert_task_to_read(task)
    return None


def update_task(
    session: Session,
    task_id: int,
    user_id: str,
    task_update: TaskUpdate
) -> Optional[TaskRead]:
    """
    Update a specific task.

    Args:
        session: Database session
        task_id: ID of the task to update
        user_id: ID of the user who owns the task
        task_update: TaskUpdate object with update data

    Returns:
        Updated Task object converted to TaskRead format if successful, None if task not found or not owned by user
    """
    db_task = session.get(Task, task_id)

    if not db_task or db_task.user_id != user_id:
        return None

    # Update only the fields that are provided in the request
    if task_update.title is not None:
        db_task.title = task_update.title
    if task_update.description is not None:
        db_task.description = task_update.description
    if task_update.completed is not None:
        db_task.completed = task_update.completed
    if task_update.priority is not None:
        # Convert priority enum to string for database storage
        db_task.priority = task_update.priority.value if hasattr(task_update.priority, 'value') else task_update.priority
    if task_update.tags is not None:
        # Convert tags list to JSON string for storage, ensuring it's always a valid JSON array
        db_task.tags = json.dumps(task_update.tags) if task_update.tags is not None else "[]"
    if task_update.due_date is not None:
        db_task.due_date = task_update.due_date
    if task_update.is_recurring is not None:
        db_task.is_recurring = task_update.is_recurring
    if task_update.recurrence_type is not None:
        db_task.recurrence_type = task_update.recurrence_type
    if task_update.recurrence_interval is not None:
        db_task.recurrence_interval = task_update.recurrence_interval
    if task_update.next_run_at is not None:
        db_task.next_run_at = task_update.next_run_at
    if task_update.reminder_at is not None:
        db_task.reminder_at = task_update.reminder_at

    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    return convert_task_to_read(db_task)


from datetime import datetime, timedelta
import calendar

def toggle_task_completion(session: Session, task_id: int, user_id: str) -> Optional[TaskRead]:
    """
    Toggle the completion status of a task.

    Args:
        session: Database session
        task_id: ID of the task to update
        user_id: ID of the user who owns the task

    Returns:
        Updated Task object converted to TaskRead format if successful, None if task not found or not owned by user
    """
    db_task = session.get(Task, task_id)

    if not db_task or db_task.user_id != user_id:
        return None

    # Store the original completion status to determine if it's being completed now
    was_completed = db_task.completed
    # Toggle the completion status
    db_task.completed = not db_task.completed

    # If the task is being marked as completed and it's a recurring task, create the next occurrence
    if not was_completed and db_task.completed and db_task.is_recurring:
        # Calculate next due date based on recurrence pattern
        next_due_date = calculate_next_occurrence(db_task.due_date, db_task.recurrence_type, db_task.recurrence_interval)

        # Create a new task with the same properties but for the next occurrence
        new_task = Task(
            title=db_task.title,
            description=db_task.description,
            completed=False,  # New task starts as incomplete
            user_id=db_task.user_id,
            priority=db_task.priority,
            tags=db_task.tags,
            due_date=next_due_date,
            is_recurring=db_task.is_recurring,
            recurrence_type=db_task.recurrence_type,
            recurrence_interval=db_task.recurrence_interval,
            next_run_at=next_due_date,
            reminder_at=db_task.reminder_at  # Keep the same reminder pattern
        )

        session.add(new_task)
        # No need to commit here as we'll commit after updating the original task

    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    return convert_task_to_read(db_task)


def calculate_next_occurrence(current_date, recurrence_type, recurrence_interval):
    """
    Calculate the next occurrence date based on recurrence pattern.

    Args:
        current_date: The current due date
        recurrence_type: 'daily', 'weekly', or 'monthly'
        recurrence_interval: The interval (e.g., every 2 weeks)

    Returns:
        datetime: The next occurrence date
    """
    if not current_date:
        # If no current date, use today
        current_date = datetime.utcnow()

    if recurrence_type == "daily":
        return current_date + timedelta(days=recurrence_interval)
    elif recurrence_type == "weekly":
        return current_date + timedelta(weeks=recurrence_interval)
    elif recurrence_type == "monthly":
        # For monthly recurrence, add the appropriate number of months
        # This handles month-end dates properly
        current_year = current_date.year
        current_month = current_date.month
        current_day = current_date.day

        # Calculate target month and year
        target_month = current_month + recurrence_interval
        target_year = current_year + (target_month - 1) // 12
        target_month = ((target_month - 1) % 12) + 1

        # Handle month-end dates (e.g., Jan 31 -> Feb 28/29)
        max_day_in_target_month = calendar.monthrange(target_year, target_month)[1]
        target_day = min(current_day, max_day_in_target_month)

        return current_date.replace(year=target_year, month=target_month, day=target_day)
    else:
        # Default to daily if invalid recurrence type
        return current_date + timedelta(days=recurrence_interval)


def delete_task(session: Session, task_id: int, user_id: str) -> bool:
    """
    Delete a specific task.

    Args:
        session: Database session
        task_id: ID of the task to delete
        user_id: ID of the user who owns the task

    Returns:
        True if task was deleted, False if task not found or not owned by user
    """
    db_task = session.get(Task, task_id)

    if not db_task or db_task.user_id != user_id:
        return False

    session.delete(db_task)
    session.commit()

    return True


def get_task_by_id(session: Session, task_id: int) -> Optional[Task]:
    """
    Retrieve a task by ID without checking user ownership.
    This is used internally when user ownership has already been verified.

    Args:
        session: Database session
        task_id: ID of the task to retrieve

    Returns:
        Task object if found, None otherwise
    """
    task = session.get(Task, task_id)
    return task
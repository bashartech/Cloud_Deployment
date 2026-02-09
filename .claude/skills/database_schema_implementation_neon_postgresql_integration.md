---
name: "Database Schema Implementation & Neon PostgreSQL Integration"
description: "Implement a persistent, production-grade data layer using Neon Serverless PostgreSQL and SQLModel, fully aligned with the documented database schema and multi-user requirements, replacing all in-memory storage and guaranteeing data persistence, integrity, and user isolation."
version: "1.0.0"
---

# Database Schema Implementation & Neon PostgreSQL Integration

## When to Use This Skill

Use this skill when you need to:
- Implement persistent, production-grade data storage using Neon Serverless PostgreSQL
- Connect a FastAPI backend to Neon PostgreSQL with SQLModel ORM
- Establish secure database connections with proper credential handling
- Create user-scoped data models that ensure multi-user task isolation
- Replace all in-memory storage with persistent database storage
- Implement proper database models with relationships, constraints, and indexes
- Ensure data persistence, integrity, and user isolation

This skill replaces all in-memory storage and guarantees data persistence, integrity, and user isolation.

## Process Steps

1. **Configure Secure Database Connection**
   - Use `DATABASE_URL` from environment variables
   - Support Neon PostgreSQL connection pooling
   - Fail fast if DB config is missing
   - Ensure secure connection handling

2. **Implement SQLModel Database Models**
   - Create `User` model (managed externally by Better Auth, referenced by ID)
   - Create `Task` model with:
     - `id` (primary key)
     - `user_id` (foreign key → users.id)
     - `title` (required, 1–200 chars)
     - `description` (optional, max 1000 chars)
     - `completed` (boolean, default false)
     - `created_at`
     - `updated_at`
   - Use SQLModel as the mandatory ORM
   - Implement proper relationships and constraints

3. **Enforce Database Constraints & Indexes**
   - Create index on `tasks.user_id`
   - Create index on `tasks.completed`
   - Enforce non-null constraints
   - Ensure schema matches documented structure exactly
   - Implement proper validation rules

4. **Implement Schema Initialization**
   - Create tables safely on startup
   - Avoid destructive migrations
   - Ensure idempotent setup
   - Validate schema creation process

5. **Replace In-Memory Logic Completely**
   - All task operations must persist to DB
   - Remove all in-memory task lists
   - DB is the single source of truth
   - Ensure no in-memory storage remains

6. **Validate Persistence and Schema Compliance**
   - Test that tasks persist across restarts
   - Verify each task is linked to exactly one user
   - Confirm database schema matches docs exactly
   - Validate user data isolation works correctly

## Output Format

The skill will produce:
- Connected Neon Serverless PostgreSQL database
- SQLModel-backed persistent storage
- Schema matching documented DB spec exactly
- Database connection using environment variables
- Properly indexed and constrained database tables
- Updated backend endpoints using database persistence
- Environment configuration for database credentials
- Documentation for database schema and access patterns

## Example

**Input:** Integrate Neon Serverless PostgreSQL database with SQLModel for the existing FastAPI backend

**Process:**
```python
# models.py
from sqlmodel import SQLModel, Field, create_engine, Session
from datetime import datetime
from typing import Optional
import os

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)  # Foreign key to Better Auth user ID
    title: str = Field(min_length=1, max_length=200)  # Required, 1-200 chars
    description: str = Field(default="", max_length=1000)  # Optional, max 1000 chars
    completed: bool = Field(default=False, index=True)  # Boolean with index
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

# database.py
from sqlmodel import create_engine
import os

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

engine = create_engine(
    DATABASE_URL,
    # Support Neon connection pooling
    pool_pre_ping=True,
    pool_recycle=300,
)

def create_db_and_tables():
    """Create database tables safely on startup"""
    SQLModel.metadata.create_all(engine)

# crud.py
from sqlmodel import Session, select
from typing import List

def create_task(session: Session, user_id: int, title: str, description: str = "") -> Task:
    """Create a new task for a specific user"""
    task = Task(
        user_id=user_id,
        title=title,
        description=description,
        completed=False
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

def get_user_tasks(session: Session, user_id: int) -> List[Task]:
    """Get all tasks for a specific user"""
    statement = select(Task).where(Task.user_id == user_id)
    return session.exec(statement).all()

def update_task(session: Session, task_id: int, user_id: int, **kwargs) -> Optional[Task]:
    """Update a task, ensuring it belongs to the user"""
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()
    if task:
        for key, value in kwargs.items():
            setattr(task, key, value)
        task.updated_at = datetime.utcnow()
        session.add(task)
        session.commit()
        session.refresh(task)
    return task

def delete_task(session: Session, task_id: int, user_id: int) -> bool:
    """Delete a task, ensuring it belongs to the user"""
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()
    if task:
        session.delete(task)
        session.commit()
        return True
    return False
```

**Output:** A fully integrated database layer using SQLModel with Neon Serverless PostgreSQL, where all tasks are stored persistently with proper user isolation, exact schema compliance, and required indexes ensuring users only see their own tasks.

## Implementation Rules

- Do NOT use raw SQL (use SQLModel exclusively)
- Do NOT store user data manually outside JWT (Better Auth manages users)
- Do NOT bypass ORM relationships (use SQLModel relationships)
- Do NOT hardcode credentials (use environment variables)
- Do NOT store data in memory (all data must be in DB)
- Do NOT expose database directly to frontend
- Do NOT allow cross-user access to tasks
- Do NOT skip data validation and sanitization
- Do NOT implement direct SQL queries without ORM protection
- Do NOT allow schema mismatches with documented structure
- Ensure all database operations are properly secured against injection
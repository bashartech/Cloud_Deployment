from sqlmodel import SQLModel, Field
from typing import Optional, List
from datetime import datetime
import json
from enum import Enum

class PriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)

class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)  # User ID from JWT token
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    # New fields for advanced features
    priority: str = Field(default="medium", max_length=20)  # low, medium, high
    tags: str = Field(default="[]", max_length=1000)  # JSON string for tags array
    due_date: Optional[datetime] = Field(default=None)  # Optional due date
    is_recurring: bool = Field(default=False)  # Whether task repeats
    recurrence_type: Optional[str] = Field(default=None, max_length=20)  # daily, weekly, monthly
    recurrence_interval: int = Field(default=1)  # Interval for recurrence
    next_run_at: Optional[datetime] = Field(default=None)  # Next occurrence date
    reminder_at: Optional[datetime] = Field(default=None)  # Time to trigger reminder

class TaskCreate(TaskBase):
    priority: PriorityEnum = Field(default=PriorityEnum.medium)  # low, medium, high
    tags: Optional[List[str]] = []  # Array of tags
    due_date: Optional[datetime] = None  # Optional due date
    is_recurring: bool = False  # Whether task repeats
    recurrence_type: Optional[str] = None  # daily, weekly, monthly
    recurrence_interval: int = 1  # Interval for recurrence
    next_run_at: Optional[datetime] = None  # Next occurrence date
    reminder_at: Optional[datetime] = None  # Time to trigger reminder

class TaskRead(TaskBase):
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime
    # New fields for advanced features
    priority: PriorityEnum
    tags: List[str]
    due_date: Optional[datetime]
    is_recurring: bool
    recurrence_type: Optional[str]
    recurrence_interval: int
    next_run_at: Optional[datetime]
    reminder_at: Optional[datetime]

class TaskUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: Optional[bool] = None
    # New fields for advanced features
    priority: Optional[PriorityEnum] = Field(default=None)  # low, medium, high
    tags: Optional[List[str]] = None  # Array of tags
    due_date: Optional[datetime] = None  # Optional due date
    is_recurring: Optional[bool] = None  # Whether task repeats
    recurrence_type: Optional[str] = None  # daily, weekly, monthly
    recurrence_interval: Optional[int] = None  # Interval for recurrence
    next_run_at: Optional[datetime] = None  # Next occurrence date
    reminder_at: Optional[datetime] = None  # Time to trigger reminder
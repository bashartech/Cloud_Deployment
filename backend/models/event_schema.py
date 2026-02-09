"""
Event Schema Definitions for Todo Chatbot Event-Driven Architecture

This module defines the standardized event schemas used across all services
in the event-driven architecture with Kafka and Dapr.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Enumeration of all possible event types in the system."""
    TASK_CREATED = "TASK_CREATED"
    TASK_UPDATED = "TASK_UPDATED"
    TASK_COMPLETED = "TASK_COMPLETED"
    TASK_DELETED = "TASK_DELETED"
    TASK_DUE_SET = "TASK_DUE_SET"
    TASK_REMINDER_SET = "TASK_REMINDER_SET"
    REMINDER_TRIGGERED = "REMINDER_TRIGGERED"
    TASK_RECURRED = "TASK_RECURRED"


class EventMetadata(BaseModel):
    """Metadata that accompanies every event."""
    source: str = Field(description="Service that generated the event")
    version: str = Field(default="v1", description="Event schema version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the event occurred")


class BaseEvent(BaseModel):
    """Base event schema that all events inherit from."""
    event_id: str = Field(description="Unique identifier for the event")
    event_type: EventType = Field(description="Type of event")
    user_id: str = Field(description="ID of the user associated with the event")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the event occurred")
    metadata: EventMetadata = Field(default_factory=lambda: EventMetadata(source="unknown", version="v1"))


class TaskEvent(BaseModel):
    """Event schema for task-related events."""
    event_type: EventType
    task_id: int
    task_data: Dict[str, Any]
    user_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TaskCreatedEvent(TaskEvent):
    """Specific schema for task creation events."""
    event_type: EventType = EventType.TASK_CREATED


class TaskUpdatedEvent(TaskEvent):
    """Specific schema for task update events."""
    event_type: EventType = EventType.TASK_UPDATED


class TaskCompletedEvent(TaskEvent):
    """Specific schema for task completion events."""
    event_type: EventType = EventType.TASK_COMPLETED


class TaskDeletedEvent(TaskEvent):
    """Specific schema for task deletion events."""
    event_type: EventType = EventType.TASK_DELETED


class ReminderEvent(BaseModel):
    """Event schema for reminder-related events."""
    task_id: int
    title: str
    due_at: Optional[datetime] = None
    remind_at: datetime
    user_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class RecurrenceEvent(BaseModel):
    """Event schema for recurrence-related events."""
    original_task_id: int
    new_task_id: int
    recurrence_type: str
    user_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AuditEvent(BaseModel):
    """Event schema for audit trail events."""
    event_type: str
    entity_id: int
    entity_type: str
    user_id: str
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default={})
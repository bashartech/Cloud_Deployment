"""
Event Publishing Utilities for Todo Chatbot

This module provides utility functions to publish events via Dapr pub/sub
to the Kafka topics used in the event-driven architecture.
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum

import httpx
from fastapi import HTTPException

try:
    from ..models.event_schema import (
        BaseEvent,
        EventType,
        TaskEvent,
        ReminderEvent,
        RecurrenceEvent,
        AuditEvent
    )
except (ImportError, ValueError):
    from models.event_schema import (
        BaseEvent,
        EventType,
        TaskEvent,
        ReminderEvent,
        RecurrenceEvent,
        AuditEvent
    )


class EventPublisher:
    """Utility class for publishing events via Dapr pub/sub."""
    
    def __init__(self, dapr_http_port: int = 3500):
        """
        Initialize the event publisher with Dapr HTTP port.
        
        Args:
            dapr_http_port: The HTTP port for Dapr sidecar (default 3500)
        """
        self.dapr_http_port = dapr_http_port
        self.base_url = f"http://localhost:{dapr_http_port}"
        self.http_client = httpx.AsyncClient(timeout=30.0)

    async def publish_event(self, topic: str, event_data: Dict[str, Any]) -> bool:
        """
        Publish an event to a specific Kafka topic via Dapr.
        
        Args:
            topic: The Kafka topic name to publish to
            event_data: The event data to publish
            
        Returns:
            bool: True if publication was successful, False otherwise
        """
        try:
            url = f"{self.base_url}/v1.0/publish/kafka-pubsub/{topic}"
            
            # Add event metadata
            payload = {
                "event_id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                **event_data
            }
            
            response = await self.http_client.post(url, json=payload)
            
            if response.status_code in [200, 204]:
                return True
            else:
                print(f"Failed to publish event to {topic}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Error publishing event to {topic}: {str(e)}")
            return False

    async def publish_task_event(
        self, 
        event_type: EventType, 
        task_id: int, 
        task_data: Dict[str, Any], 
        user_id: str
    ) -> bool:
        """
        Publish a task-related event to the task-events topic.
        
        Args:
            event_type: The type of task event
            task_id: The ID of the task
            task_data: The task data
            user_id: The user ID associated with the task
            
        Returns:
            bool: True if publication was successful, False otherwise
        """
        event_data = {
            "event_type": event_type.value,
            "task_id": task_id,
            "task_data": task_data,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await self.publish_event("task-events", event_data)

    async def publish_reminder_event(
        self,
        task_id: int,
        title: str,
        remind_at: datetime,
        user_id: str,
        due_at: Optional[datetime] = None
    ) -> bool:
        """
        Publish a reminder event to the reminders topic.
        
        Args:
            task_id: The ID of the task
            title: The task title
            remind_at: When to send the reminder
            user_id: The user ID associated with the task
            due_at: When the task is due (optional)
            
        Returns:
            bool: True if publication was successful, False otherwise
        """
        event_data = {
            "task_id": task_id,
            "title": title,
            "due_at": due_at.isoformat() if due_at else None,
            "remind_at": remind_at.isoformat(),
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await self.publish_event("reminders", event_data)

    async def publish_task_update_event(
        self,
        task_id: int,
        task_data: Dict[str, Any],
        user_id: str,
        action: str = "updated"
    ) -> bool:
        """
        Publish a task update event to the task-updates topic for real-time sync.
        
        Args:
            task_id: The ID of the task
            task_data: The task data
            user_id: The user ID associated with the task
            action: The action that triggered the update
            
        Returns:
            bool: True if publication was successful, False otherwise
        """
        event_data = {
            "task_id": task_id,
            "task_data": task_data,
            "user_id": user_id,
            "action": action,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await self.publish_event("task-updates", event_data)

    async def publish_recurrence_event(
        self,
        original_task_id: int,
        new_task_id: int,
        recurrence_type: str,
        user_id: str
    ) -> bool:
        """
        Publish a recurrence event to the task-recurrence topic.
        
        Args:
            original_task_id: The ID of the original recurring task
            new_task_id: The ID of the new generated task
            recurrence_type: The type of recurrence (daily, weekly, monthly)
            user_id: The user ID associated with the task
            
        Returns:
            bool: True if publication was successful, False otherwise
        """
        event_data = {
            "original_task_id": original_task_id,
            "new_task_id": new_task_id,
            "recurrence_type": recurrence_type,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await self.publish_event("task-recurrence", event_data)

    async def publish_audit_event(
        self,
        event_type: str,
        entity_id: int,
        entity_type: str,
        user_id: str,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Publish an audit event to the task-audit topic.
        
        Args:
            event_type: The type of audit event
            entity_id: The ID of the entity
            entity_type: The type of entity (e.g., 'task')
            user_id: The user ID associated with the action
            old_values: Previous values (optional)
            new_values: New values (optional)
            
        Returns:
            bool: True if publication was successful, False otherwise
        """
        event_data = {
            "event_type": event_type,
            "entity_id": entity_id,
            "entity_type": entity_type,
            "user_id": user_id,
            "old_values": old_values or {},
            "new_values": new_values or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await self.publish_event("task-audit", event_data)

    async def close(self):
        """Close the HTTP client."""
        await self.http_client.aclose()


# Global event publisher instance
_event_publisher: Optional[EventPublisher] = None


def get_event_publisher() -> EventPublisher:
    """
    Get the global event publisher instance.
    
    Returns:
        EventPublisher: The event publisher instance
    """
    global _event_publisher
    if _event_publisher is None:
        _event_publisher = EventPublisher()
    return _event_publisher


async def publish_task_created_event(task_id: int, task_data: Dict[str, Any], user_id: str) -> bool:
    """Publish a TASK_CREATED event."""
    publisher = get_event_publisher()
    return await publisher.publish_task_event(EventType.TASK_CREATED, task_id, task_data, user_id)


async def publish_task_updated_event(task_id: int, task_data: Dict[str, Any], user_id: str) -> bool:
    """Publish a TASK_UPDATED event."""
    publisher = get_event_publisher()
    return await publisher.publish_task_event(EventType.TASK_UPDATED, task_id, task_data, user_id)


async def publish_task_completed_event(task_id: int, task_data: Dict[str, Any], user_id: str) -> bool:
    """Publish a TASK_COMPLETED event."""
    publisher = get_event_publisher()
    return await publisher.publish_task_event(EventType.TASK_COMPLETED, task_id, task_data, user_id)


async def publish_task_deleted_event(task_id: int, task_data: Dict[str, Any], user_id: str) -> bool:
    """Publish a TASK_DELETED event."""
    publisher = get_event_publisher()
    return await publisher.publish_task_event(EventType.TASK_DELETED, task_id, task_data, user_id)


async def publish_reminder_set_event(
    task_id: int, 
    title: str, 
    remind_at: datetime, 
    user_id: str, 
    due_at: Optional[datetime] = None
) -> bool:
    """Publish a TASK_REMINDER_SET event."""
    publisher = get_event_publisher()
    return await publisher.publish_reminder_event(task_id, title, remind_at, user_id, due_at)


async def publish_task_update_sync_event(
    task_id: int, 
    task_data: Dict[str, Any], 
    user_id: str, 
    action: str = "updated"
) -> bool:
    """Publish a task update event for real-time sync."""
    publisher = get_event_publisher()
    return await publisher.publish_task_update_event(task_id, task_data, user_id, action)
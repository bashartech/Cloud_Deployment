
"""
Notification Service for Task Reminders
This service consumes reminder events and sends notifications to users
"""
import asyncio
import json
import logging
from datetime import datetime
import os

# Import Dapr components with correct import paths for modern Dapr SDK
try:
    from dapr.clients import DaprClient
    from dapr.clients.grpc._state import StateItem
    import grpc
except ImportError:
    # Fallback for cases where Dapr is not available during development
    print("Warning: Dapr not available. Using mock objects for development.")
    # Define mock classes for development
    class DaprClient:
        def __init__(self):
            pass
        def subscribe(self, pubsub_name, topic):
            def decorator(func):
                return func
            return decorator
        def method(self, name):
            def decorator(func):
                return func
            return decorator
        def run(self, port):
            print(f"Dapr app mock running on port {port}")

    class StateItem:
        def __init__(self, key, value):
            self.key = key
            self.value = value

# Import reminder state management
from reminder_state import (
    store_reminder, get_reminder, update_reminder, delete_reminder,
    mark_reminder_as_notified, is_reminder_notified
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Dapr client
dapr_client = DaprClient()

# For pub/sub, we'll use a separate listener approach
import asyncio
from concurrent import futures

# Environment variables
PUBSUB_NAME = os.getenv('DAPR_PUBSUB_NAME', 'pubsub-kafka')
TASK_REMINDERS_TOPIC = os.getenv('TASK_REMINDERS_TOPIC', 'task-reminders')

class NotificationDelivery:
    """
    Notification delivery mechanism with multiple channels
    """
    def __init__(self):
        self.channels = {
            'email': self._send_email,
            'push': self._send_push,
            'sms': self._send_sms,
            'log': self._send_log
        }
    
    async def send_notification(self, user_id: str, task_title: str, due_date: str, channels: list = None):
        """
        Send notification to user about upcoming task via specified channels
        """
        if channels is None:
            channels = ['log']  # Default to logging for MVP
            
        notification_message = f"Reminder: Task '{task_title}' is due on {due_date}"
        results = {}
        
        for channel in channels:
            if channel in self.channels:
                try:
                    result = await self.channels[channel](user_id, notification_message)
                    results[channel] = result
                    logger.info(f"Notification sent via {channel} to user {user_id}: {result}")
                except Exception as e:
                    logger.error(f"Failed to send notification via {channel}: {str(e)}")
                    results[channel] = {"status": "failed", "error": str(e)}
            else:
                logger.warning(f"Unknown notification channel: {channel}")
                results[channel] = {"status": "unknown_channel"}
        
        return results
    
    async def _send_log(self, user_id: str, message: str):
        """Log notification (MVP implementation)"""
        logger.info(f"NOTIFICATION for user {user_id}: {message}")
        return {"status": "logged", "user_id": user_id, "message_preview": message[:50]}

    async def _send_email(self, user_id: str, message: str):
        """Send email notification (placeholder for production)"""
        # Placeholder for email service integration
        # Would typically integrate with services like SendGrid, AWS SES, etc.
        logger.info(f"EMAIL to user {user_id}: {message}")
        return {"status": "email_sent", "user_id": user_id}

    async def _send_push(self, user_id: str, message: str):
        """Send push notification (placeholder for production)"""
        # Placeholder for push notification service
        # Would typically integrate with services like Firebase, OneSignal, etc.
        logger.info(f"PUSH to user {user_id}: {message}")
        return {"status": "push_sent", "user_id": user_id}

    async def _send_sms(self, user_id: str, message: str):
        """Send SMS notification (placeholder for production)"""
        # Placeholder for SMS service
        # Would typically integrate with services like Twilio, AWS SNS, etc.
        logger.info(f"SMS to user {user_id}: {message}")
        return {"status": "sms_sent", "user_id": user_id}


# Initialize notification delivery
notification_delivery = NotificationDelivery()


async def send_notification(user_id: str, task_title: str, due_date: str, channels: list = None):
    """
    Send notification to user about upcoming task
    """
    logger.info(f"Sending notification to user {user_id} for task '{task_title}' due on {due_date}")
    
    # Send notification via specified channels (defaults to logging for MVP)
    results = await notification_delivery.send_notification(user_id, task_title, due_date, channels)
    
    return {"status": "processed", "user_id": user_id, "task_title": task_title, "results": results}

# For the new Dapr SDK, we'll implement a subscription mechanism using a separate service
# This is a simplified approach for the notification service
async def reminder_handler(event_data: dict) -> None:
    """
    Handle incoming reminder events from the pub/sub system
    Expected event_data format:
    {
        "user_id": "string",
        "task_id": "int",
        "task_title": "string",
        "due_date": "datetime string",
        "event_type": "reminder_triggered",
        "timestamp": "datetime string"
    }
    """
    logger.info(f"Received reminder event: {event_data}")
    
    try:
        user_id = event_data.get('user_id')
        task_id = event_data.get('task_id')
        task_title = event_data.get('task_title')
        due_date = event_data.get('due_date')
        
        if not all([user_id, task_id, task_title, due_date]):
            logger.error(f"Missing required fields in reminder event: {event_data}")
            return
        
        # Create a unique reminder ID
        reminder_id = f"reminder_{user_id}_{task_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Store reminder in state to track notification status
        reminder_data = {
            "user_id": user_id,
            "task_id": task_id,
            "task_title": task_title,
            "due_date": due_date,
            "notified": False,
            "event_type": event_data.get('event_type'),
            "timestamp": event_data.get('timestamp', datetime.now().isoformat()),
            "created_at": datetime.now().isoformat()
        }
        
        # Store the reminder in state management
        await store_reminder(reminder_id, reminder_data)

        # Check if this reminder has already been processed to prevent duplicates
        is_notified = await is_reminder_notified(reminder_id)
        if is_notified:
            logger.info(f"Reminder {reminder_id} already processed, skipping notification")
            return

        # Send notification to user
        await send_notification(user_id, task_title, due_date)

        # Mark the reminder as notified
        await mark_reminder_as_notified(reminder_id)
        
        logger.info(f"Processed reminder for task {task_id} for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error processing reminder event: {str(e)}")

async def health_method(request) -> dict:
    """
    Health check endpoint
    """
    return {"status": "healthy", "service": "notification-service"}

if __name__ == '__main__':
    logger.info("Starting Notification Service...")
    logger.info(f"Listening for topic: {TASK_REMINDERS_TOPIC} on pubsub: {PUBSUB_NAME}")

    # In the new Dapr SDK, pub/sub is typically handled through HTTP endpoints
    # that Dapr invokes, rather than direct subscription in the code
    # This service would be invoked by Dapr when events arrive
    logger.info("Notification Service initialized and ready for Dapr invocations")
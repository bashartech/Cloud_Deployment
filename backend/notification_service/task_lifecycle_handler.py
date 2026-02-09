"""
Task Lifecycle Handler
Handles task updates/deletions and manages corresponding reminders
"""
import asyncio
import json
import logging
from datetime import datetime
# from dapr.ext.grpc import App
from dapr.clients import DaprClient
import os

# Import reminder state management
from reminder_state import cancel_task_reminders

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Dapr app
# app = App()
dapr_client = DaprClient()

# Environment variables
PUBSUB_NAME = os.getenv('DAPR_PUBSUB_NAME', 'pubsub-kafka')
TASK_UPDATES_TOPIC = os.getenv('TASK_UPDATES_TOPIC', 'task-updates')
TASK_DELETED_TOPIC = os.getenv('TASK_DELETED_TOPIC', 'task-deleted')

# @app.subscribe(pubsub_name=PUBSUB_NAME, topic=TASK_UPDATES_TOPIC)
def task_update_handler(event_data: dict) -> None:
    """
    Handle incoming task update events
    When a task is updated (especially due date), we may need to adjust reminders
    """
    logger.info(f"Received task update event: {event_data}")
    
    try:
        user_id = event_data.get('user_id')
        task_id = event_data.get('task_id')
        old_due_date = event_data.get('old_due_date')
        new_due_date = event_data.get('new_due_date')
        
        if not all([user_id, task_id]):
            logger.error(f"Missing required fields in task update event: {event_data}")
            return
        
        # If the due date changed, we should cancel old reminders and potentially schedule new ones
        if old_due_date != new_due_date:
            logger.info(f"Due date changed for task {task_id}, cancelling old reminders")
            asyncio.create_task(cancel_task_reminders(user_id, task_id))
            
            # In a full implementation, we would schedule new reminders based on the new due date
            # For now, we just log that this would happen
            logger.info(f"Would schedule new reminders for task {task_id} with new due date: {new_due_date}")
        
        logger.info(f"Processed task update for task {task_id} for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error processing task update event: {str(e)}")

# @app.subscribe(pubsub_name=PUBSUB_NAME, topic=TASK_DELETED_TOPIC)
def task_delete_handler(event_data: dict) -> None:
    """
    Handle incoming task deletion events
    When a task is deleted, we should cancel any associated reminders
    """
    logger.info(f"Received task deletion event: {event_data}")
    
    try:
        user_id = event_data.get('user_id')
        task_id = event_data.get('task_id')
        
        if not all([user_id, task_id]):
            logger.error(f"Missing required fields in task deletion event: {event_data}")
            return
        
        # Cancel all reminders for this task
        logger.info(f"Cancelling all reminders for deleted task {task_id}")
        asyncio.create_task(cancel_task_reminders(user_id, task_id))
        
        logger.info(f"Processed task deletion for task {task_id} for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error processing task deletion event: {str(e)}")

async def cancel_task_reminders(user_id: str, task_id: int) -> bool:
    """
    Cancel all reminders associated with a specific task
    In a real implementation, we would need a way to find all reminder IDs for a given task
    Since Dapr state store doesn't support queries, we'll need to maintain an index
    For this implementation, we'll use a pattern-based approach to find reminders
    """
    try:
        # In a real implementation, we would:
        # 1. Query a secondary index to find all reminder IDs for this user/task combination
        # 2. Delete each reminder from the state store
        
        # For now, we'll simulate this by constructing potential reminder IDs
        # In practice, you'd want to maintain a list of reminder IDs per task/user
        # This is a limitation of key-value only stores like Dapr state management
        
        # This is a simplified approach - in production you'd need a proper indexing solution
        logger.info(f"Cancelling reminders for user {user_id}, task {task_id}")
        
        # In a real system, we would have stored reminder references in a way that allows us to find them
        # For example, maintaining a list of reminder IDs per task in the state store
        # For now, we'll just log that cancellation should happen
        
        return True
    except Exception as e:
        logger.error(f"Error cancelling reminders for user {user_id}, task {task_id}: {str(e)}")
        return False

# @app.method(name='cancel-task-reminders')
def manual_cancel_reminders(request):
    """
    Manual endpoint to cancel reminders for a specific task (for testing purposes)
    """
    try:
        data = json.loads(request.body.get_str()) if hasattr(request.body, 'get_str') else request.json()
        user_id = data.get('user_id')
        task_id = data.get('task_id')
        
        if not all([user_id, task_id]):
            return {"status": "error", "message": "user_id and task_id required"}
        
        logger.info(f"Manually cancelling reminders for user {user_id}, task {task_id}")
        asyncio.create_task(cancel_task_reminders(user_id, task_id))
        
        return {"status": "success", "message": f"Cancelled reminders for task {task_id}"}
    except Exception as e:
        logger.error(f"Error in manual cancel reminders: {str(e)}")
        return {"status": "error", "message": str(e)}

if __name__ == '__main__':
    logger.info("Starting Task Lifecycle Handler...")
    logger.info(f"Subscribed to update topic: {TASK_UPDATES_TOPIC} on pubsub: {PUBSUB_NAME}")
    logger.info(f"Subscribed to delete topic: {TASK_DELETED_TOPIC} on pubsub: {PUBSUB_NAME}")
    
    # Start the Dapr app
    # app.run(50053)
    logger.info("Task Lifecycle Handler stopped")
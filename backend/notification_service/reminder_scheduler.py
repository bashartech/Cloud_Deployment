"""
Reminder Scheduler Service
This service uses Dapr cron bindings to periodically check for upcoming tasks
and emit reminder events to the pub/sub system
"""
import asyncio
import json
import logging
from datetime import datetime, timedelta
# from dapr.ext.grpc import App, BindingApp
from dapr.clients import DaprClient
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Dapr app
# app = App()
dapr_client = DaprClient()

# Environment variables
PUBSUB_NAME = os.getenv('DAPR_PUBSUB_NAME', 'pubsub-kafka')
TASK_REMINDERS_TOPIC = os.getenv('TASK_REMINDERS_TOPIC', 'task-reminders')
BINDING_NAME = os.getenv('DAPR_BINDING_NAME', 'cron-reminders')

# Global variable to track if we're already checking reminders
checking_reminders = False

# @app.binding(BINDING_NAME)
def reminder_check(data: dict):
    """
    Cron binding handler that triggers periodically to check for upcoming tasks
    """
    global checking_reminders
    
    # Prevent overlapping executions
    if checking_reminders:
        logger.info("Previous reminder check still running, skipping this execution")
        return
    
    checking_reminders = True
    logger.info(f"Running periodic reminder check at {datetime.now().isoformat()}")
    
    try:
        # Check for tasks due within the next hour
        asyncio.create_task(check_upcoming_tasks())
    except Exception as e:
        logger.error(f"Error in reminder check: {str(e)}")
    finally:
        checking_reminders = False

async def check_upcoming_tasks():
    """
    Check for tasks that are due soon and emit reminder events
    """
    try:
        # Call the main backend service to get tasks with due dates
        # This would typically call an endpoint that returns tasks due within a certain timeframe
        resp = dapr_client.invoke_method(
            app_id='todo-backend',
            method_name='get_due_tasks',
            data={'timeframe_minutes': 60}  # Check for tasks due in next 60 minutes
        )
        
        due_tasks = json.loads(resp.data.decode('utf-8'))
        logger.info(f"Found {len(due_tasks)} tasks due soon")
        
        # For each due task, publish a reminder event
        for task in due_tasks:
            reminder_event = {
                "user_id": task.get('user_id'),
                "task_id": task.get('id'),
                "task_title": task.get('title'),
                "due_date": task.get('due_date'),
                "event_type": "reminder_triggered",
                "timestamp": datetime.now().isoformat()
            }
            
            # Publish reminder event to pubsub
            dapr_client.publish_event(
                pubsub_name=PUBSUB_NAME,
                topic_name=TASK_REMINDERS_TOPIC,
                data=reminder_event
            )
            
            logger.info(f"Published reminder event for task {task.get('id')} to user {task.get('user_id')}")
        
    except Exception as e:
        logger.error(f"Error checking upcoming tasks: {str(e)}")

# @app.method(name='trigger-reminder-check')
def manual_trigger(request):
    """
    Manual endpoint to trigger reminder check for testing purposes
    """
    logger.info("Manual reminder check triggered")
    asyncio.create_task(check_upcoming_tasks())
    return {"status": "triggered"}

if __name__ == '__main__':
    logger.info("Starting Reminder Scheduler Service...")
    logger.info(f"Using binding: {BINDING_NAME}")
    logger.info(f"Publishing to topic: {TASK_REMINDERS_TOPIC} on pubsub: {PUBSUB_NAME}")
    
    # Start the Dapr app
    # app.run(50052)
    logger.info("Reminder Scheduler Service stopped")
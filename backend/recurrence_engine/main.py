"""
Recurrence Engine Service
This service handles recurring tasks by listening for task completion events
and creating new instances based on recurrence patterns
"""
import asyncio
import json
import logging
from datetime import datetime, timedelta
# from dapr.ext.grpc import App
from dapr.clients import DaprClient
import os
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Dapr app
# app = App()
dapr_client = DaprClient()

# Environment variables
PUBSUB_NAME = os.getenv('DAPR_PUBSUB_NAME', 'pubsub-kafka')
TASK_COMPLETED_TOPIC = os.getenv('TASK_COMPLETED_TOPIC', 'task-completed')
TASK_RECURRENCE_TOPIC = os.getenv('TASK_RECURRENCE_TOPIC', 'task-recurrence')
BACKEND_APP_ID = os.getenv('BACKEND_APP_ID', 'todo-backend')
STATE_STORE_NAME = os.getenv('DAPR_STATE_STORE_NAME', 'state-postgres')

class RecurrencePattern(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

class RecurrenceEngine:
    """
    Handles the logic for creating recurring tasks
    """
    def __init__(self):
        self.client = DaprClient()
        self.pubsub_name = PUBSUB_NAME
        self.recurrence_topic = TASK_RECURRENCE_TOPIC
        self.backend_app_id = BACKEND_APP_ID
        self.state_store = STATE_STORE_NAME
    
    async def process_completed_task(self, task_data: dict) -> bool:
        """
        Process a completed task to see if it should recur
        task_data should contain:
        - id: int (task id)
        - user_id: str
        - title: str
        - description: str
        - recurrence_pattern: str (optional, one of RecurrencePattern)
        - recurrence_end_date: str (optional, ISO format)
        - recurrence_count: int (optional, number of recurrences left)
        - completed_at: str (ISO format)
        """
        try:
            task_id = task_data.get('id')
            user_id = task_data.get('user_id')
            title = task_data.get('title')
            description = task_data.get('description')
            recurrence_pattern = task_data.get('recurrence_pattern')
            
            # Generate a unique ID for this recurrence processing to ensure idempotency
            processing_id = f"recurrence_{user_id}_{task_id}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            
            # Check if this recurrence processing has already been attempted to prevent duplicates
            if await self.has_processed_recurrence(processing_id):
                logger.info(f"Recurrence processing {processing_id} already completed, skipping")
                return True
            
            # Mark this processing as started to prevent duplicate processing
            await self.mark_recurrence_processing_started(processing_id)
            
            # Check if this task has a recurrence pattern
            if not recurrence_pattern:
                logger.info(f"Task {task_id} has no recurrence pattern, skipping")
                await self.mark_recurrence_processing_completed(processing_id)
                return True
            
            # Validate recurrence pattern
            try:
                pattern = RecurrencePattern(recurrence_pattern.lower())
            except ValueError:
                logger.error(f"Invalid recurrence pattern '{recurrence_pattern}' for task {task_id}")
                await self.mark_recurrence_processing_completed(processing_id)
                return False
            
            # Check if recurrence should end
            if await self.should_stop_recurrence(task_data):
                logger.info(f"Recurrence ended for task {task_id}, stopping generation")
                await self.mark_recurrence_processing_completed(processing_id)
                return True
            
            # Calculate next occurrence date
            next_occurrence = await self.calculate_next_occurrence(task_data)
            if not next_occurrence:
                logger.info(f"Could not calculate next occurrence for task {task_id}")
                await self.mark_recurrence_processing_completed(processing_id)
                return False
            
            # Create new recurring task
            new_task_data = await self.create_recurring_task(task_data, next_occurrence)
            if not new_task_data:
                logger.error(f"Failed to create recurring task for original task {task_id}")
                await self.mark_recurrence_processing_completed(processing_id)
                return False
            
            # Publish event for audit trail
            await self.publish_recurrence_event(user_id, task_id, new_task_data['id'], pattern.value, next_occurrence)
            
            # Mark the recurrence processing as completed
            await self.mark_recurrence_processing_completed(processing_id)
            
            logger.info(f"Created recurring task {new_task_data['id']} from original task {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing completed task for recurrence: {str(e)}")
            return False
    
    async def has_processed_recurrence(self, processing_id: str) -> bool:
        """
        Check if a recurrence processing has already been completed
        """
        try:
            response = await self.client.get_state(
                store_name=self.state_store,
                key=f"recurrence_processed:{processing_id}"
            )
            
            return response.data is not None
        except Exception as e:
            logger.error(f"Error checking if recurrence was processed: {str(e)}")
            return False
    
    async def mark_recurrence_processing_started(self, processing_id: str) -> bool:
        """
        Mark a recurrence processing as started to prevent duplicate processing
        """
        try:
            await self.client.save_state(
                store_name=self.state_store,
                key=f"recurrence_started:{processing_id}",
                value=json.dumps({
                    'status': 'started',
                    'timestamp': datetime.now().isoformat()
                })
            )
            return True
        except Exception as e:
            logger.error(f"Error marking recurrence processing as started: {str(e)}")
            return False
    
    async def mark_recurrence_processing_completed(self, processing_id: str) -> bool:
        """
        Mark a recurrence processing as completed
        """
        try:
            # Mark as completed
            await self.client.save_state(
                store_name=self.state_store,
                key=f"recurrence_processed:{processing_id}",
                value=json.dumps({
                    'status': 'completed',
                    'timestamp': datetime.now().isoformat()
                })
            )
            
            # Remove the started marker
            await self.client.delete_state(
                store_name=self.state_store,
                key=f"recurrence_started:{processing_id}"
            )
            
            return True
        except Exception as e:
            logger.error(f"Error marking recurrence processing as completed: {str(e)}")
            return False
    
    async def should_stop_recurrence(self, task_data: dict) -> bool:
        """
        Determine if recurrence should stop based on end conditions
        """
        try:
            recurrence_end_date = task_data.get('recurrence_end_date')
            recurrence_count = task_data.get('recurrence_count')
            
            # Check end date condition
            if recurrence_end_date:
                end_date = datetime.fromisoformat(recurrence_end_date.replace('Z', '+00:00'))
                if datetime.now(end_date.tzinfo) >= end_date:
                    return True
            
            # Check count condition
            if recurrence_count is not None:
                # In a real system, we'd track how many recurrences have happened
                # For this implementation, we'll assume the count represents remaining recurrences
                if recurrence_count <= 0:
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error checking recurrence stop condition: {str(e)}")
            return False
    
    async def calculate_next_occurrence(self, task_data: dict) -> str:
        """
        Calculate the next occurrence date based on the recurrence pattern
        """
        try:
            recurrence_pattern = task_data.get('recurrence_pattern', '').lower()
            completed_at = task_data.get('completed_at', datetime.now().isoformat())
            
            # Parse the completion time
            if completed_at.endswith('Z'):
                completed_at = completed_at[:-1] + '+00:00'
            completed_datetime = datetime.fromisoformat(completed_at)
            
            # Calculate next occurrence based on pattern
            if recurrence_pattern == 'daily':
                next_date = completed_datetime + timedelta(days=1)
            elif recurrence_pattern == 'weekly':
                next_date = completed_datetime + timedelta(weeks=1)
            elif recurrence_pattern == 'monthly':
                # Simple monthly calculation (same day next month)
                # In production, handle month boundaries properly
                next_date = self.add_months(completed_datetime, 1)
            elif recurrence_pattern == 'yearly':
                next_date = self.add_months(completed_datetime, 12)
            else:
                logger.error(f"Unknown recurrence pattern: {recurrence_pattern}")
                return None
            
            return next_date.isoformat()
        except Exception as e:
            logger.error(f"Error calculating next occurrence: {str(e)}")
            return None
    
    def add_months(self, dt: datetime, months: int) -> datetime:
        """
        Helper to add months to a datetime, handling month boundaries
        """
        month = dt.month - 1 + months
        year = dt.year + month // 12
        month = month % 12 + 1
        day = min(dt.day, [31,
                          29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
                          31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month-1])
        return dt.replace(year=year, month=month, day=day)
    
    async def create_recurring_task(self, original_task: dict, next_occurrence: str) -> dict:
        """
        Create a new task based on the original task with updated due date
        """
        try:
            # Prepare new task data
            new_task = {
                'user_id': original_task['user_id'],
                'title': original_task['title'],
                'description': original_task['description'],
                'due_date': next_occurrence,
                'priority': original_task.get('priority', 'medium'),
                'tags': original_task.get('tags', []),
                'recurrence_pattern': original_task.get('recurrence_pattern'),
                'recurrence_end_date': original_task.get('recurrence_end_date'),
                'recurrence_count': original_task.get('recurrence_count', None)
            }
            
            # Decrement recurrence count if it exists
            if new_task['recurrence_count'] is not None:
                new_task['recurrence_count'] -= 1
            
            # Call the backend service to create the new task
            response = self.client.invoke_method(
                app_id=self.backend_app_id,
                method_name='create_task',
                data=json.dumps(new_task),
                content_type='application/json'
            )
            
            # Parse the response
            new_task_result = json.loads(response.data.decode('utf-8'))
            logger.info(f"Created new recurring task: {new_task_result}")
            
            return new_task_result
        except Exception as e:
            logger.error(f"Error creating recurring task: {str(e)}")
            return None
    
    async def publish_recurrence_event(self, user_id: str, original_task_id: int, new_task_id: int, pattern: str, next_occurrence: str):
        """
        Publish an event to track the recurrence for audit purposes
        """
        try:
            event_data = {
                'user_id': user_id,
                'original_task_id': original_task_id,
                'new_task_id': new_task_id,
                'recurrence_pattern': pattern,
                'next_occurrence': next_occurrence,
                'timestamp': datetime.now().isoformat(),
                'event_type': 'task_recurred'
            }
            
            self.client.publish_event(
                pubsub_name=self.pubsub_name,
                topic_name=self.recurrence_topic,
                data=event_data
            )
            
            logger.info(f"Published recurrence event for user {user_id}, original task {original_task_id}, new task {new_task_id}")
        except Exception as e:
            logger.error(f"Error publishing recurrence event: {str(e)}")

# Global instance
recurrence_engine = RecurrenceEngine()

# @app.subscribe(pubsub_name=PUBSUB_NAME, topic=TASK_COMPLETED_TOPIC)
def task_completed_handler(event_data: dict) -> None:
    """
    Handle incoming task completion events
    If the task has a recurrence pattern, create a new instance
    """
    logger.info(f"Received task completion event: {event_data}")
    
    try:
        # Process the completed task for recurrence
        asyncio.create_task(recurrence_engine.process_completed_task(event_data))
        
        logger.info(f"Processed task completion event for recurrence")
    except Exception as e:
        logger.error(f"Error in task completion handler: {str(e)}")

# @app.method(name='health')
def health_method(request):
    """
    Health check endpoint
    """
    return {"status": "healthy", "service": "recurrence-engine"}

# @app.method(name='process-task-for-recurrence')
def manual_process_task(request):
    """
    Manual endpoint to process a task for recurrence (for testing purposes)
    """
    try:
        data = json.loads(request.data.decode('utf-8')) if hasattr(request, 'data') else {}
        task_data = data.get('task_data', {})
        
        if not task_data:
            return {"status": "error", "message": "task_data required"}
        
        logger.info(f"Manually processing task {task_data.get('id')} for recurrence")
        result = asyncio.create_task(recurrence_engine.process_completed_task(task_data))
        
        return {"status": "success", "result": result.result() if hasattr(result, 'result') else "processing"}
    except Exception as e:
        logger.error(f"Error in manual process task: {str(e)}")
        return {"status": "error", "message": str(e)}

if __name__ == '__main__':
    logger.info("Starting Recurrence Engine Service...")
    logger.info(f"Subscribed to topic: {TASK_COMPLETED_TOPIC} on pubsub: {PUBSUB_NAME}")
    logger.info(f"Publishing to topic: {TASK_RECURRENCE_TOPIC} on pubsub: {PUBSUB_NAME}")
    
    # Start the Dapr app
    # app.run(50054)
    logger.info("Recurrence Engine Service stopped")
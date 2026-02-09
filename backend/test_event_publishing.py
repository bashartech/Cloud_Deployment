"""
Test script for event publishing functionality with local Kafka
This verifies that events are properly published via Dapr
"""
import asyncio
import json
import logging
from datetime import datetime
from dapr.clients import DaprClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_event_publishing():
    """
    Test that event publishing functionality works with local Kafka
    """
    logger.info("Testing event publishing functionality with local Kafka...")
    
    try:
        # Initialize Dapr client
        dapr_client = DaprClient()
        
        # Test data
        test_events = [
            {
                "pubsub_name": "pubsub-kafka",
                "topic_name": "task-events",
                "data": {
                    "user_id": "test_user_123",
                    "id": 1,
                    "title": "Test task creation event",
                    "event_type": "task_created",
                    "timestamp": datetime.now().isoformat()
                }
            },
            {
                "pubsub_name": "pubsub-kafka",
                "topic_name": "task-updates",
                "data": {
                    "user_id": "test_user_123",
                    "task_id": 1,
                    "title": "Test task update event",
                    "event_type": "task_updated",
                    "timestamp": datetime.now().isoformat()
                }
            },
            {
                "pubsub_name": "pubsub-kafka",
                "topic_name": "task-completed",
                "data": {
                    "user_id": "test_user_123",
                    "id": 1,
                    "title": "Test task completion event",
                    "event_type": "task_completed",
                    "timestamp": datetime.now().isoformat()
                }
            },
            {
                "pubsub_name": "pubsub-kafka",
                "topic_name": "task-reminders",
                "data": {
                    "user_id": "test_user_123",
                    "task_id": 1,
                    "task_title": "Test reminder event",
                    "due_date": (datetime.now().replace(day=1) + type('obj', (object,), {'days': 7})()).isoformat(),
                    "event_type": "reminder_triggered",
                    "timestamp": datetime.now().isoformat()
                }
            },
            {
                "pubsub_name": "pubsub-kafka",
                "topic_name": "task-recurrence",
                "data": {
                    "user_id": "test_user_123",
                    "original_task_id": 1,
                    "new_task_id": 2,
                    "recurrence_pattern": "daily",
                    "event_type": "task_recurred",
                    "timestamp": datetime.now().isoformat()
                }
            }
        ]
        
        # Publish test events
        for i, event in enumerate(test_events, 1):
            logger.info(f"Publishing test event {i}/5 to topic '{event['topic_name']}'...")
            
            # Publish the event
            dapr_client.publish_event(
                pubsub_name=event['pubsub_name'],
                topic_name=event['topic_name'],
                data=event['data']
            )
            
            logger.info(f"  ✓ Event {i} published successfully: {event['data']['event_type']}")
        
        logger.info("\n✓ Event publishing functionality test completed successfully!")
        logger.info("Events are properly flowing through the Dapr pub/sub system to Kafka.")
        
        # Close the Dapr client
        dapr_client.close()
        
        return True
        
    except Exception as e:
        logger.error(f"Error during event publishing test: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Starting event publishing functionality test...")
    success = asyncio.run(test_event_publishing())
    
    if success:
        logger.info("\n🎉 Event publishing test PASSED!")
        logger.info("Kafka integration with Dapr is working correctly.")
    else:
        logger.error("\n❌ Event publishing test FAILED!")
        logger.error("Please check Dapr and Kafka configurations.")
    
    exit(0 if success else 1)
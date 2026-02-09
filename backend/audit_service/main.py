"""
Audit Service
This service subscribes to all task event topics and maintains an immutable audit log
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

    class grpc:
        pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Dapr client
dapr_client = DaprClient()

# Environment variables
PUBSUB_NAME = os.getenv('DAPR_PUBSUB_NAME', 'pubsub-kafka')
STATE_STORE_NAME = os.getenv('DAPR_STATE_STORE_NAME', 'state-postgres')

# Define all the task event topics we want to audit
TASK_EVENT_TOPICS = [
    os.getenv('TASK_CREATED_TOPIC', 'task-created'),
    os.getenv('TASK_UPDATED_TOPIC', 'task-updated'),
    os.getenv('TASK_COMPLETED_TOPIC', 'task-completed'),
    os.getenv('TASK_DELETED_TOPIC', 'task-deleted'),
    os.getenv('TASK_RECURRENCE_TOPIC', 'task-recurrence'),
    os.getenv('TASK_REMINDERS_TOPIC', 'task-reminders')
]

class AuditService:
    """
    Maintains an immutable audit log of all task-related events
    """
    def __init__(self):
        self.client = DaprClient()
        self.pubsub_name = PUBSUB_NAME
        self.state_store = STATE_STORE_NAME
    
    async def audit_event(self, event_type: str, event_data: dict) -> bool:
        """
        Record an event in the audit log
        """
        try:
            user_id = event_data.get('user_id', 'unknown')
            timestamp = datetime.now().isoformat()
            
            # Create an audit record with all relevant information
            audit_record = {
                'id': f"audit_{user_id}_{timestamp.replace(':', '_').replace('.', '_').replace('-', '_')}",
                'user_id': user_id,
                'event_type': event_type,
                'event_data': event_data,
                'timestamp': timestamp,
                'source_service': event_data.get('source_service', 'unknown')
            }
            
            # Store the audit record in the state store
            # Using a key that ensures immutability by timestamp
            audit_key = f"audit_{user_id}_{timestamp}"
            
            await self.client.save_state(
                store_name=self.state_store,
                key=audit_key,
                value=json.dumps(audit_record)
            )
            
            # Also maintain a user-specific audit log index for easier retrieval
            await self._add_to_user_audit_index(user_id, audit_key)
            
            logger.info(f"Audited event {event_type} for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error auditing event {event_type}: {str(e)}")
            return False
    
    async def _add_to_user_audit_index(self, user_id: str, audit_key: str):
        """
        Add an audit record key to the user's audit index
        """
        try:
            index_key = f"audit_index:{user_id}"
            
            # Get existing audit keys for this user
            response = await self.client.get_state(
                store_name=self.state_store,
                key=index_key
            )
            
            if response.data:
                audit_keys = json.loads(response.data.decode('utf-8'))
            else:
                audit_keys = []
            
            # Add the new audit key if it's not already in the list
            if audit_key not in audit_keys:
                audit_keys.append(audit_key)
                
                # Save the updated index
                await self.client.save_state(
                    store_name=self.state_store,
                    key=index_key,
                    value=json.dumps(audit_keys)
                )
        except Exception as e:
            logger.error(f"Error adding to user audit index: {str(e)}")
    
    async def get_user_audit_log(self, user_id: str) -> list:
        """
        Retrieve audit log for a specific user
        """
        try:
            index_key = f"audit_index:{user_id}"
            
            response = await self.client.get_state(
                store_name=self.state_store,
                key=index_key
            )
            
            if not response.data:
                return []
            
            audit_keys = json.loads(response.data.decode('utf-8'))
            audit_records = []
            
            # Retrieve each audit record
            for key in audit_keys:
                record_response = await self.client.get_state(
                    store_name=self.state_store,
                    key=key
                )
                
                if record_response.data:
                    audit_record = json.loads(record_response.data.decode('utf-8'))
                    audit_records.append(audit_record)
            
            # Sort by timestamp
            audit_records.sort(key=lambda x: x['timestamp'])
            
            return audit_records
        except Exception as e:
            logger.error(f"Error retrieving audit log for user {user_id}: {str(e)}")
            return []

# Global instance
audit_service = AuditService()

# For the new Dapr SDK, pub/sub is handled differently
# We'll implement event handlers that can be called by external event processors
# This creates handler functions that can be invoked when events arrive
event_handlers = {}
for topic in TASK_EVENT_TOPICS:
    # Create a closure to capture the topic name for the handler
    def make_handler(t):
        async def handler(event_data: dict) -> None:
            logger.info(f"Received {t} event for auditing: {event_data}")
            await audit_service.audit_event(event_type=t, event_data=event_data)
        return handler

    event_handlers[topic] = make_handler(topic)
    logger.info(f"Initialized handler for topic: {topic}")

async def health_method(request):
    """
    Health check endpoint
    """
    return {"status": "healthy", "service": "audit-service"}

async def get_user_audit_log(request):
    """
    Retrieve audit log for a specific user
    """
    try:
        data = json.loads(request.data.decode('utf-8')) if hasattr(request, 'data') else {}
        user_id = data.get('user_id')

        if not user_id:
            return {"status": "error", "message": "user_id required"}

        audit_logs = await audit_service.get_user_audit_log(user_id)

        return {
            "status": "success",
            "audit_logs": audit_logs,
            "count": len(audit_logs)
        }
    except Exception as e:
        logger.error(f"Error retrieving user audit log: {str(e)}")
        return {"status": "error", "message": str(e)}

if __name__ == '__main__':
    logger.info("Starting Audit Service...")
    logger.info(f"Initialized handlers for {len(TASK_EVENT_TOPICS)} task event topics")

    # In the new Dapr SDK, pub/sub is typically handled through HTTP endpoints
    # that Dapr invokes, rather than direct subscription in the code
    logger.info("Audit Service initialized and ready for Dapr invocations")
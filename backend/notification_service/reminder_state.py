"""
Reminder State Management
Handles storing and retrieving reminder information using Dapr state store
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dapr.clients import DaprClient
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
STATE_STORE_NAME = os.getenv('DAPR_STATE_STORE_NAME', 'state-postgres')

class ReminderStateManager:
    """
    Manages reminder state using Dapr state store
    """
    def __init__(self):
        self.client = DaprClient()
        self.state_store = STATE_STORE_NAME
    
    async def store_reminder(self, reminder_id: str, reminder_data: Dict) -> bool:
        """
        Store a reminder in the state store
        reminder_data should contain:
        - user_id: str
        - task_id: int
        - task_title: str
        - due_date: str (ISO format)
        - notified: bool (whether notification was sent)
        - cancelled: bool (whether reminder was cancelled)
        - created_at: str (ISO format)
        """
        try:
            reminder_data['updated_at'] = datetime.now().isoformat()
            
            # Store the reminder in Dapr state store
            await self.client.save_state(
                store_name=self.state_store,
                key=reminder_id,
                value=json.dumps(reminder_data)
            )
            
            # Also maintain an index of reminders by user and task
            await self._add_to_user_task_index(reminder_data['user_id'], reminder_data['task_id'], reminder_id)
            
            logger.info(f"Stored reminder {reminder_id} for user {reminder_data.get('user_id')}")
            return True
        except Exception as e:
            logger.error(f"Error storing reminder {reminder_id}: {str(e)}")
            return False
    
    async def get_reminder(self, reminder_id: str) -> Optional[Dict]:
        """
        Retrieve a reminder from the state store
        """
        try:
            response = await self.client.get_state(
                store_name=self.state_store,
                key=reminder_id
            )
            
            if response.data:
                reminder_data = json.loads(response.data.decode('utf-8'))
                
                # Check if reminder is cancelled
                if reminder_data.get('cancelled', False):
                    logger.info(f"Reminder {reminder_id} is cancelled")
                
                logger.info(f"Retrieved reminder {reminder_id}")
                return reminder_data
            else:
                logger.info(f"No reminder found with ID {reminder_id}")
                return None
        except Exception as e:
            logger.error(f"Error retrieving reminder {reminder_id}: {str(e)}")
            return None
    
    async def update_reminder(self, reminder_id: str, updates: Dict) -> bool:
        """
        Update a reminder in the state store
        """
        try:
            # Get current reminder data
            current_data = await self.get_reminder(reminder_id)
            if not current_data:
                logger.warning(f"Cannot update reminder {reminder_id}: not found")
                return False
            
            # Apply updates
            current_data.update(updates)
            current_data['updated_at'] = datetime.now().isoformat()
            
            # Save updated data
            await self.client.save_state(
                store_name=self.state_store,
                key=reminder_id,
                value=json.dumps(current_data)
            )
            
            logger.info(f"Updated reminder {reminder_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating reminder {reminder_id}: {str(e)}")
            return False
    
    async def delete_reminder(self, reminder_id: str) -> bool:
        """
        Delete a reminder from the state store
        """
        try:
            # First get the reminder to remove it from indexes
            reminder = await self.get_reminder(reminder_id)
            if reminder:
                await self._remove_from_user_task_index(reminder['user_id'], reminder['task_id'], reminder_id)
            
            await self.client.delete_state(
                store_name=self.state_store,
                key=reminder_id
            )
            
            logger.info(f"Deleted reminder {reminder_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting reminder {reminder_id}: {str(e)}")
            return False
    
    async def get_user_reminders(self, user_id: str) -> List[Dict]:
        """
        Get all reminders for a specific user
        Note: This requires maintaining an index of user reminders
        """
        try:
            # Get the user's reminder index
            index_key = f"user_reminders:{user_id}"
            response = await self.client.get_state(
                store_name=self.state_store,
                key=index_key
            )
            
            if response.data:
                reminder_ids = json.loads(response.data.decode('utf-8'))
                reminders = []
                
                for rid in reminder_ids:
                    reminder = await self.get_reminder(rid)
                    if reminder:
                        reminders.append(reminder)
                
                logger.info(f"Retrieved {len(reminders)} reminders for user {user_id}")
                return reminders
            else:
                logger.info(f"No reminders found for user {user_id}")
                return []
        except Exception as e:
            logger.error(f"Error getting reminders for user {user_id}: {str(e)}")
            return []
    
    async def get_task_reminders(self, user_id: str, task_id: int) -> List[Dict]:
        """
        Get all reminders for a specific task
        """
        try:
            # Get the task's reminder index
            index_key = f"task_reminders:{user_id}:{task_id}"
            response = await self.client.get_state(
                store_name=self.state_store,
                key=index_key
            )
            
            if response.data:
                reminder_ids = json.loads(response.data.decode('utf-8'))
                reminders = []
                
                for rid in reminder_ids:
                    reminder = await self.get_reminder(rid)
                    if reminder:
                        reminders.append(reminder)
                
                logger.info(f"Retrieved {len(reminders)} reminders for task {task_id} for user {user_id}")
                return reminders
            else:
                logger.info(f"No reminders found for task {task_id} for user {user_id}")
                return []
        except Exception as e:
            logger.error(f"Error getting reminders for task {task_id} for user {user_id}: {str(e)}")
            return []
    
    async def mark_reminder_as_notified(self, reminder_id: str) -> bool:
        """
        Mark a reminder as notified to prevent duplicate notifications
        """
        return await self.update_reminder(reminder_id, {'notified': True})
    
    async def is_reminder_notified(self, reminder_id: str) -> bool:
        """
        Check if a reminder has already been notified
        """
        reminder = await self.get_reminder(reminder_id)
        return reminder.get('notified', False) if reminder else False
    
    async def cancel_reminder(self, reminder_id: str) -> bool:
        """
        Mark a reminder as cancelled
        """
        return await self.update_reminder(reminder_id, {'cancelled': True})
    
    async def is_reminder_cancelled(self, reminder_id: str) -> bool:
        """
        Check if a reminder has been cancelled
        """
        reminder = await self.get_reminder(reminder_id)
        return reminder.get('cancelled', False) if reminder else False
    
    async def cancel_task_reminders(self, user_id: str, task_id: int) -> bool:
        """
        Cancel all reminders for a specific task
        """
        try:
            task_reminders = await self.get_task_reminders(user_id, task_id)
            
            cancelled_count = 0
            for reminder in task_reminders:
                reminder_id = reminder.get('id', '') or list(reminder.keys())[0] if reminder else ''
                if reminder and await self.cancel_reminder(reminder['id'] if 'id' in reminder else reminder_id):
                    cancelled_count += 1
            
            logger.info(f"Cancelled {cancelled_count} reminders for task {task_id} for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error cancelling reminders for task {task_id} for user {user_id}: {str(e)}")
            return False
    
    async def _add_to_user_task_index(self, user_id: str, task_id: int, reminder_id: str):
        """
        Add a reminder ID to the user and task indexes
        """
        try:
            # Add to user index
            user_index_key = f"user_reminders:{user_id}"
            user_response = await self.client.get_state(
                store_name=self.state_store,
                key=user_index_key
            )
            
            if user_response.data:
                user_reminders = json.loads(user_response.data.decode('utf-8'))
            else:
                user_reminders = []
            
            if reminder_id not in user_reminders:
                user_reminders.append(reminder_id)
                await self.client.save_state(
                    store_name=self.state_store,
                    key=user_index_key,
                    value=json.dumps(user_reminders)
                )
            
            # Add to task index
            task_index_key = f"task_reminders:{user_id}:{task_id}"
            task_response = await self.client.get_state(
                store_name=self.state_store,
                key=task_index_key
            )
            
            if task_response.data:
                task_reminders = json.loads(task_response.data.decode('utf-8'))
            else:
                task_reminders = []
            
            if reminder_id not in task_reminders:
                task_reminders.append(reminder_id)
                await self.client.save_state(
                    store_name=self.state_store,
                    key=task_index_key,
                    value=json.dumps(task_reminders)
                )
        except Exception as e:
            logger.error(f"Error adding reminder {reminder_id} to indexes: {str(e)}")
    
    async def _remove_from_user_task_index(self, user_id: str, task_id: int, reminder_id: str):
        """
        Remove a reminder ID from the user and task indexes
        """
        try:
            # Remove from user index
            user_index_key = f"user_reminders:{user_id}"
            user_response = await self.client.get_state(
                store_name=self.state_store,
                key=user_index_key
            )
            
            if user_response.data:
                user_reminders = json.loads(user_response.data.decode('utf-8'))
                if reminder_id in user_reminders:
                    user_reminders.remove(reminder_id)
                    await self.client.save_state(
                        store_name=self.state_store,
                        key=user_index_key,
                        value=json.dumps(user_reminders)
                    )
            
            # Remove from task index
            task_index_key = f"task_reminders:{user_id}:{task_id}"
            task_response = await self.client.get_state(
                store_name=self.state_store,
                key=task_index_key
            )
            
            if task_response.data:
                task_reminders = json.loads(task_response.data.decode('utf-8'))
                if reminder_id in task_reminders:
                    task_reminders.remove(reminder_id)
                    await self.client.save_state(
                        store_name=self.state_store,
                        key=task_index_key,
                        value=json.dumps(task_reminders)
                    )
        except Exception as e:
            logger.error(f"Error removing reminder {reminder_id} from indexes: {str(e)}")

# Global instance
reminder_state_manager = ReminderStateManager()

# Convenience functions
async def store_reminder(reminder_id: str, reminder_data: Dict) -> bool:
    return await reminder_state_manager.store_reminder(reminder_id, reminder_data)

async def get_reminder(reminder_id: str) -> Optional[Dict]:
    return await reminder_state_manager.get_reminder(reminder_id)

async def update_reminder(reminder_id: str, updates: Dict) -> bool:
    return await reminder_state_manager.update_reminder(reminder_id, updates)

async def delete_reminder(reminder_id: str) -> bool:
    return await reminder_state_manager.delete_reminder(reminder_id)

async def mark_reminder_as_notified(reminder_id: str) -> bool:
    return await reminder_state_manager.mark_reminder_as_notified(reminder_id)

async def is_reminder_notified(reminder_id: str) -> bool:
    return await reminder_state_manager.is_reminder_notified(reminder_id)

async def cancel_reminder(reminder_id: str) -> bool:
    return await reminder_state_manager.cancel_reminder(reminder_id)

async def is_reminder_cancelled(reminder_id: str) -> bool:
    return await reminder_state_manager.is_reminder_cancelled(reminder_id)

async def cancel_task_reminders(user_id: str, task_id: int) -> bool:
    return await reminder_state_manager.cancel_task_reminders(user_id, task_id)
"""
WebSocket Service
This service handles real-time updates for task changes using WebSocket connections
"""
import asyncio
import json
import logging
from datetime import datetime
# from dapr.ext.grpc import App
from dapr.clients import DaprClient
import os
import websockets
from websockets.exceptions import ConnectionClosed
from typing import Dict, Set

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Dapr client
dapr_client = DaprClient()

# Environment variables
PUBSUB_NAME = os.getenv('DAPR_PUBSUB_NAME', 'pubsub-kafka')
TASK_UPDATES_TOPIC = os.getenv('TASK_UPDATES_TOPIC', 'task-updates')
WEBSOCKET_HOST = os.getenv('WEBSOCKET_HOST', '0.0.0.0')
WEBSOCKET_PORT = int(os.getenv('WEBSOCKET_PORT', 8765))

class WebSocketManager:
    """
    Manages WebSocket connections and broadcasts messages to clients
    """
    def __init__(self):
        self.active_connections: Dict[str, Set[websockets.WebSocketServerProtocol]] = {}
        self.user_connection_map: Dict[websockets.WebSocketServerProtocol, str] = {}
    
    async def connect(self, websocket: websockets.WebSocketServerProtocol, user_id: str):
        """
        Add a new WebSocket connection for a user
        """
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        
        self.active_connections[user_id].add(websocket)
        self.user_connection_map[websocket] = user_id
        logger.info(f"User {user_id} connected. Total connections: {len(self.active_connections[user_id])}")
    
    def disconnect(self, websocket: websockets.WebSocketServerProtocol):
        """
        Remove a WebSocket connection
        """
        if websocket in self.user_connection_map:
            user_id = self.user_connection_map[websocket]
            if user_id in self.active_connections:
                self.active_connections[user_id].discard(websocket)
                if len(self.active_connections[user_id]) == 0:
                    del self.active_connections[user_id]
            del self.user_connection_map[websocket]
            logger.info(f"User {user_id} disconnected")
    
    async def broadcast_to_user(self, user_id: str, message: dict):
        """
        Broadcast a message to all WebSocket connections for a specific user
        """
        if user_id in self.active_connections:
            connections_to_remove = []
            
            for connection in self.active_connections[user_id].copy():
                try:
                    await connection.send(json.dumps(message))
                except ConnectionClosed:
                    connections_to_remove.append(connection)
                except Exception as e:
                    logger.error(f"Error sending message to user {user_id}: {str(e)}")
                    connections_to_remove.append(connection)
            
            # Clean up closed connections
            for connection in connections_to_remove:
                self.disconnect(connection)
    
    async def broadcast_to_all(self, message: dict):
        """
        Broadcast a message to all connected clients
        """
        for user_id in self.active_connections.copy():
            await self.broadcast_to_user(user_id, message)

# Global WebSocket manager
ws_manager = WebSocketManager()

async def websocket_handler(websocket, path):
    """
    Handle incoming WebSocket connections
    Expected path format: /ws/{user_id}
    """
    try:
        # Extract user_id from path
        path_parts = path.strip('/').split('/')
        if len(path_parts) < 2 or path_parts[0] != 'ws':
            logger.error(f"Invalid WebSocket path: {path}")
            await websocket.close(code=1008, reason="Invalid path format. Use /ws/{user_id}")
            return
        
        user_id = path_parts[1]
        logger.info(f"WebSocket connection attempt for user {user_id}")
        
        # Register the connection
        await ws_manager.connect(websocket, user_id)
        
        # Send welcome message
        welcome_msg = {
            "type": "connection_established",
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
        await websocket.send(json.dumps(welcome_msg))
        
        # Keep the connection alive
        async for message in websocket:
            # Handle incoming messages from client if needed
            try:
                data = json.loads(message)
                msg_type = data.get('type')
                
                if msg_type == 'ping':
                    # Respond to ping
                    await websocket.send(json.dumps({'type': 'pong'}))
                else:
                    logger.info(f"Received message from user {user_id}: {data}")
            except json.JSONDecodeError:
                logger.warning(f"Received non-JSON message from user {user_id}: {message}")
            except Exception as e:
                logger.error(f"Error processing message from user {user_id}: {str(e)}")
    
    except ConnectionClosed:
        logger.info(f"WebSocket connection closed for user {user_id}")
    except Exception as e:
        logger.error(f"Error in WebSocket handler: {str(e)}")
    finally:
        ws_manager.disconnect(websocket)

# @app.subscribe(pubsub_name=PUBSUB_NAME, topic=TASK_UPDATES_TOPIC)
def task_updates_handler(event_data: dict) -> None:
    """
    Handle incoming task update events and broadcast to relevant users
    """
    logger.info(f"Received task update event: {event_data}")
    
    try:
        user_id = event_data.get('user_id')
        if not user_id:
            logger.error(f"No user_id in task update event: {event_data}")
            return
        
        # Prepare the update message
        update_message = {
            "type": "task_update",
            "event_type": event_data.get('event_type', 'update'),
            "task_data": event_data,
            "timestamp": datetime.now().isoformat()
        }
        
        # Broadcast to the specific user
        asyncio.create_task(ws_manager.broadcast_to_user(user_id, update_message))
        
        logger.info(f"Broadcast task update to user {user_id}")
    except Exception as e:
        logger.error(f"Error in task updates handler: {str(e)}")

# @app.method(name='health')
def health_method(request):
    """
    Health check endpoint
    """
    return {"status": "healthy", "service": "websocket-service", "active_users": len(ws_manager.active_connections)}

# @app.method(name='broadcast-test-message')
def broadcast_test_message(request):
    """
    Manual endpoint to broadcast a test message to a user (for testing purposes)
    """
    try:
        data = json.loads(request.data.decode('utf-8')) if hasattr(request, 'data') else {}
        user_id = data.get('user_id')
        message = data.get('message', 'Test message')
        
        if not user_id:
            return {"status": "error", "message": "user_id required"}
        
        test_message = {
            "type": "test_message",
            "content": message,
            "timestamp": datetime.now().isoformat()
        }
        
        asyncio.run(ws_manager.broadcast_to_user(user_id, test_message))
        
        return {"status": "success", "message": f"Test message sent to user {user_id}"}
    except Exception as e:
        logger.error(f"Error in broadcast test message: {str(e)}")
        return {"status": "error", "message": str(e)}

async def start_websocket_server():
    """
    Start the WebSocket server
    """
    logger.info(f"Starting WebSocket server on {WEBSOCKET_HOST}:{WEBSOCKET_PORT}")
    
    server = await websockets.serve(
        websocket_handler,
        WEBSOCKET_HOST,
        WEBSOCKET_PORT
    )
    
    logger.info(f"WebSocket server started on {WEBSOCKET_HOST}:{WEBSOCKET_PORT}")
    
    await server.wait_closed()

if __name__ == '__main__':
    logger.info("Starting WebSocket Service...")
    logger.info(f"Subscribed to topic: {TASK_UPDATES_TOPIC} on pubsub: {PUBSUB_NAME}")
    
    # Start both the Dapr app and WebSocket server concurrently
    import threading
    
    # Run Dapr app in a separate thread
    def run_dapr():
        dapr_client.run(50056)  # Different port than other services
    
    dapr_thread = threading.Thread(target=run_dapr)
    dapr_thread.daemon = True
    dapr_thread.start()
    
    # Run WebSocket server in main thread
    try:
        asyncio.run(start_websocket_server())
    except KeyboardInterrupt:
        logger.info("WebSocket Service stopped by user")
    except Exception as e:
        logger.error(f"Error running WebSocket service: {str(e)}")
    
    logger.info("WebSocket Service stopped")
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import time
try:
    from ..models.conversation import Conversation
    from ..models.chat_message import ChatMessage
    from ..db import get_session
    from ..auth import get_user_id_from_token
    from ..services.chat_service import process_chat
except (ImportError, ValueError):
    from models.conversation import Conversation
    from models.chat_message import ChatMessage
    from db import get_session
    from auth import get_user_id_from_token
    from services.chat_service import process_chat

# Simple in-memory rate limiting (for demo purposes)
# In production, use Redis or database-backed rate limiting
user_request_times = {}
RATE_LIMIT_WINDOW = 60  # seconds
MAX_REQUESTS_PER_WINDOW = 10

import os
import json
from datetime import datetime

# Pydantic models for request/response validation
from pydantic import BaseModel

class ChatRequest(BaseModel):
    conversation_id: Optional[int] = None
    message: str


class ChatResponse(BaseModel):
    conversation_id: int
    response: str
    tool_calls: List[Dict[str, Any]]


router = APIRouter(tags=["chat"])


@router.post("/api/{user_id}/chat", response_model=ChatResponse)
def chat_endpoint(
    user_id: str,
    chat_request: ChatRequest,
    authenticated_user_id: str = Depends(get_user_id_from_token),
    session: Session = Depends(get_session)
):
    """
    Chat endpoint that handles conversation with AI agent.

    Request body: {"conversation_id": number?, "message": string}
    Response body: {"conversation_id": number, "response": string, "tool_calls": []}

    This endpoint orchestrates the chat flow using the chat service:
    1. Validate request
    2. Process chat through service (handles all orchestration steps)
    3. Return response to client
    4. Server holds no state (ready for next request)
    """
    # Verify that the user_id in the path matches the authenticated user
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only access your own chat conversations"
        )
    # Rate limiting check
    current_time = time.time()

    # Initialize user request record if not exists
    if user_id not in user_request_times:
        user_request_times[user_id] = []

    # Clean old requests outside the window
    user_request_times[user_id] = [
        req_time for req_time in user_request_times[user_id]
        if current_time - req_time < RATE_LIMIT_WINDOW
    ]

    # Check if user exceeded rate limit
    if len(user_request_times[user_id]) >= MAX_REQUESTS_PER_WINDOW:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Maximum {MAX_REQUESTS_PER_WINDOW} requests per {RATE_LIMIT_WINDOW} seconds."
        )

    # Record this request
    user_request_times[user_id].append(current_time)
    try:
        # Validate request data
        if not chat_request.message or not chat_request.message.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message cannot be empty"
            )

        # Process the chat through the service which handles the complete orchestration
        conversation_id, response_text, tool_calls_result = process_chat(
            user_id=user_id,
            conversation_id=chat_request.conversation_id,
            message=chat_request.message,
            session=session
        )

        # Return response to client (step 8 in spec flow)
        response = ChatResponse(
            conversation_id=conversation_id,
            response=response_text,
            tool_calls=tool_calls_result
        )

        # Server holds no state (ready for next request) (step 9 in spec flow)
        return response

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except ValueError as e:
        # Handle value errors (like access denied)
        if "Access denied" in str(e):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
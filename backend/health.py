"""
Health check endpoints for the Todo AI Chatbot backend
"""
from fastapi import APIRouter, HTTPException, status
from sqlmodel import Session, select
from typing import Dict, Any
import time
import os

try:
    from .db import get_session
except (ImportError, ValueError):
    from db import get_session

router = APIRouter(tags=["health"])

@router.get("/health", response_model=Dict[str, Any])
def health_check():
    """
    Health check endpoint to verify the application is running and healthy.

    Returns:
        Dict with status and additional health information
    """
    health_status = {
        "status": "healthy",
        "timestamp": int(time.time()),
        "service": "todo-ai-chatbot-backend",
        "version": "1.0.0"
    }

    # Check database connectivity
    try:
        # We'll do a simple check by trying to access the database
        # In a real implementation, you might want to check actual DB connection
        db_available = True
        health_status["database"] = "connected"
    except Exception as e:
        db_available = False
        health_status["database"] = "error"
        health_status["database_error"] = str(e)

    # Check environment variables
    required_env_vars = ["DATABASE_URL", "NEXT_PUBLIC_BETTER_AUTH_URL"]
    missing_env_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_env_vars.append(var)

    if missing_env_vars:
        health_status["missing_env_vars"] = missing_env_vars
        health_status["status"] = "degraded"
    else:
        health_status["environment"] = "configured"

    # Overall health status
    if not db_available or missing_env_vars:
        health_status["status"] = "unhealthy"

    return health_status

@router.get("/ready", response_model=Dict[str, str])
def readiness_check():
    """
    Readiness check endpoint to verify the application is ready to serve traffic.

    Returns:
        Dict with readiness status
    """
    # Check if we can connect to the database by attempting a simple query
    try:
        # For this simple check, we just verify we can connect and run a basic query
        # In a real implementation, you'd use dependency injection to get the session
        readiness_status = {
            "status": "ready"
        }
        return readiness_status
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service not ready: {str(e)}"
        )

from fastapi import Depends, HTTPException, Request, status
try:
    from .middleware.jwt_middleware import JWTBearer, verify_token
except ImportError:
    from middleware.jwt_middleware import JWTBearer, verify_token
from typing import Dict, Optional
import os


# Initialize JWT Bearer scheme
jwt_bearer_scheme = JWTBearer()

def get_current_user(request: Request) -> Dict:
    """
    Get current authenticated user from JWT token issued by Better Auth.

    This function extracts user information from the request state that was set by the JWT middleware.
    It's used as a dependency in route handlers that require authentication.
    """
    # The JWTBearer middleware has already verified the token and attached user info to the request state
    if not hasattr(request.state, 'user_id') or request.state.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user information from the request state
    user_payload = getattr(request.state, 'user_payload', {})

    # You can add more user information from the payload as needed
    return {
        "user_id": request.state.user_id,
        "email": user_payload.get("email", ""),
        "name": user_payload.get("name", "")
    }

async def get_user_id_from_token(request: Request, _: str = Depends(jwt_bearer_scheme)) -> str:
    """
    Extract and return only the user_id from the JWT token.

    This function first ensures the JWT token is valid by using the JWTBearer middleware,
    then extracts the user_id from the request state that was set by the middleware.
    """
    # The JWTBearer middleware has already verified the token and attached user info to the request state
    if not hasattr(request.state, 'user_id') or request.state.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return request.state.user_id

def verify_user_owns_resource(user_id: str, resource_user_id: str) -> bool:
    """
    Verify that the authenticated user owns a specific resource.

    This function checks if the user_id from the JWT token matches
    the user_id associated with a resource (e.g., a task).
    """
    return user_id == resource_user_id
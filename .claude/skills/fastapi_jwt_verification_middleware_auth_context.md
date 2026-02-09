---
name: "FastAPI JWT Verification Middleware & Auth Context"
description: "Implement a FastAPI authentication layer that verifies JWT tokens issued by Better Auth, extracts authenticated user identity, and makes it available to all protected API routes, enabling stateless, secure, multi-user backend access."
version: "1.0.0"
---

# FastAPI JWT Verification Middleware & Auth Context

## When to Use This Skill

Use this skill when you need to:
- Implement FastAPI-specific JWT verification middleware
- Verify JWT tokens issued by Better Auth independently in the backend
- Extract authenticated user identity from JWT tokens
- Make authenticated user context available to all protected API routes
- Create a stateless authentication system for FastAPI backend
- Protect all API routes with JWT verification
- Implement secure token handling with shared secrets

This skill enables stateless, secure, multi-user backend access.

## Process Steps

1. **JWT Middleware Implementation**
   - Create FastAPI middleware to extract token from `Authorization: Bearer <token>` header
   - Reject missing or malformed tokens with appropriate HTTP status codes
   - Verify JWT signature using shared secret with Better Auth
   - Implement proper error handling for verification failures

2. **Token Decoding**
   - Decode JWT payload securely using appropriate library
   - Extract user ID and email from token payload
   - Validate token expiration to prevent usage of expired tokens
   - Implement proper validation of token claims

3. **Auth Context Injection**
   - Attach authenticated user information to request state in FastAPI
   - Make user ID accessible to route handlers via dependency injection
   - Create dependency functions to retrieve authenticated user context
   - Ensure context is available across all protected routes

4. **Global API Protection**
   - Apply JWT middleware to all `/api/*` routes in FastAPI
   - Configure route protection globally or per-route as needed
   - Return `401 Unauthorized` for requests with invalid or missing tokens
   - Implement consistent authentication enforcement

5. **Error Handling**
   - Distinguish between authentication errors and permission errors
   - Return consistent error responses for different failure scenarios
   - Implement proper logging for authentication failures without exposing secrets
   - Create appropriate HTTP status code responses

## Output Format

The skill will produce:
- FastAPI JWT verification middleware implementation
- Secure token extraction and validation from Authorization header
- Authenticated user context available to all protected routes
- Global API protection with consistent authentication enforcement
- Proper error handling and response formatting
- Documentation for middleware configuration and usage

## Example

**Input:** Implement FastAPI JWT verification middleware for Better Auth tokens

**Process:**
```python
# auth/middleware.py
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from typing import Dict, Optional
import os

# Security scheme for OpenAPI docs
security = HTTPBearer()

class JWTAuth:
    def __init__(self):
        self.secret = os.getenv("BETTER_AUTH_SECRET")
        if not self.secret:
            raise ValueError("BETTER_AUTH_SECRET environment variable is required")
        if len(self.secret) < 32:
            raise ValueError("BETTER_AUTH_SECRET must be at least 32 characters long")

    async def verify_token(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
        """
        Verify JWT token and return user information
        """
        token = credentials.credentials

        try:
            # Decode the JWT token
            payload = jwt.decode(
                token,
                self.secret,
                algorithms=["HS256"]  # Adjust algorithm as needed
            )

            # Validate token expiration
            if "exp" in payload and payload["exp"] < time.time():
                raise HTTPException(status_code=401, detail="Token expired")

            # Extract user information
            user_id = payload.get("sub") or payload.get("user_id")
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token: missing user ID")

            return {
                "user_id": user_id,
                "email": payload.get("email"),
                "token": token
            }

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
        except Exception as e:
            raise HTTPException(status_code=401, detail="Authentication failed")

# auth/dependencies.py
from fastapi import Depends
from .middleware import JWTAuth

auth_handler = JWTAuth()

async def get_current_user(credentials=Depends(auth_handler.verify_token)):
    """
    Dependency to get current authenticated user
    """
    return credentials

# main.py (FastAPI app)
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
import os
from auth.dependencies import get_current_user

app = FastAPI()

# Add CORS middleware as needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/protected")
async def protected_route(current_user: Dict = Depends(get_current_user)):
    """
    Example protected route that requires authentication
    """
    return {
        "message": "This is a protected route",
        "user_id": current_user["user_id"],
        "email": current_user.get("email")
    }

@app.get("/api/tasks")
async def get_user_tasks(current_user: Dict = Depends(get_current_user)):
    """
    Example route that uses authenticated user context
    """
    user_id = current_user["user_id"]
    # Use user_id to fetch user-specific tasks from database
    return {"tasks": [], "user_id": user_id}

# For applying authentication globally, you can create a base dependency
# or use middleware to protect all routes under /api/*
```

**Output:** A fully secured FastAPI backend with JWT verification middleware that independently validates tokens issued by Better Auth, extracts user identity, and makes authenticated context available to all protected API routes.

## Implementation Rules

- Do NOT trust frontend headers blindly (always verify JWT signature)
- Do NOT skip verification for any route (ensure all API routes are protected)
- Do NOT store sessions server-side (maintain stateless authentication)
- Do NOT log secrets or tokens (prevent sensitive information exposure)
- Do NOT accept tokens from sources other than Authorization header
- Do NOT bypass authentication for development shortcuts
- Ensure proper token expiration validation
- Implement secure secret management with environment variables
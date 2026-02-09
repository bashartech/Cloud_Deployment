---
name: "JWT Authentication & Authorization Enforcement"
description: "Implement secure authentication and authorization using Better Auth and JWTs, ensuring that every API request is verified and user-scoped, guaranteeing a real multi-user system."
version: "1.0.0"
---

# JWT Authentication & Authorization Enforcement

## When to Use This Skill

Use this skill when you need to:
- Implement secure authentication using Better Auth and JWTs
- Protect backend API routes requiring authentication
- Ensure user-scoped data access and prevent unauthorized access
- Enforce proper authorization checks on all sensitive operations
- Establish secure token handling between frontend and backend
- Create a true multi-user system where users can only access their own data

This skill guarantees that Project 2 becomes a real multi-user system, not a demo app.

## Process Steps

1. **Integrate Better Auth**
   - Configure Better Auth provider in the backend
   - Set up proper secret management for JWT signing
   - Implement login and signup flows
   - Configure JWT generation on successful authentication
   - Ensure secure secret handling and storage

2. **Implement JWT Verification Middleware**
   - Create middleware to validate JWT signature
   - Extract authenticated user ID from token payload
   - Implement proper token expiration handling
   - Reject invalid, expired, or malformed tokens
   - Log authentication failures for security monitoring

3. **Protect Backend Routes**
   - Apply JWT verification middleware to all sensitive routes
   - Require JWT for task-related API endpoints
   - Enforce user identity verification on every request
   - Return appropriate HTTP status codes for auth failures
   - Document protected endpoints clearly

4. **Enforce User-Scoped Authorization**
   - Match JWT user ID with database queries
   - Implement authorization checks to prevent horizontal privilege escalation
   - Ensure users can only access their own data
   - Validate user permissions for each operation
   - Implement proper error handling for authorization failures

5. **Implement Frontend JWT Handling**
   - Securely store JWT in browser storage (consider httpOnly cookies for higher security)
   - Implement token attachment to every protected API request
   - Create interceptors to automatically add Authorization headers
   - Handle authentication failures gracefully (redirect to login)
   - Implement token refresh mechanisms if needed

6. **Test Security Implementation**
   - Verify unauthorized requests fail appropriately
   - Confirm authenticated users access only their data
   - Test token expiration scenarios
   - Validate that user IDs cannot be spoofed
   - Conduct security testing for common vulnerabilities

## Output Format

The skill will produce:
- Better Auth integration with JWT configuration
- JWT verification middleware for FastAPI
- Protected API endpoints requiring authentication
- Frontend components for secure token handling
- Authorization logic enforcing user-scoped data access
- Security testing procedures and validation checks
- Documentation for authentication flow and security measures

## Example

**Input:** Secure the task management API with JWT authentication

**Process:**
```python
# auth.py
from fastapi import Depends, HTTPException, Request
from better_auth import get_current_user
from typing import Dict, Optional

async def get_current_user_id(request: Request) -> int:
    """Extract and verify user ID from JWT in request"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = auth_header.split(" ")[1]
    # Verify token and extract user ID
    user_data = verify_jwt_token(token)
    if not user_data or "user_id" not in user_data:
        raise HTTPException(status_code=401, detail="Invalid token")

    return user_data["user_id"]

# routes/tasks.py
from fastapi import APIRouter, Depends

router = APIRouter()

@router.get("/tasks")
async def get_user_tasks(current_user_id: int = Depends(get_current_user_id)):
    """Get tasks for the authenticated user only"""
    tasks = await get_tasks_by_user_id(current_user_id)
    return {"tasks": tasks}

@router.post("/tasks")
async def create_task(task_data: TaskCreate, current_user_id: int = Depends(get_current_user_id)):
    """Create a task for the authenticated user"""
    task = await create_task_for_user(task_data, current_user_id)
    return task
```

**Output:** A fully secured API where all task operations require valid JWT authentication, ensuring users can only access their own tasks.

## Implementation Rules

- Do NOT allow unauthenticated access to protected endpoints
- Do NOT trust user IDs passed manually from frontend
- Do NOT skip token verification on any protected route
- Do NOT expose authentication secrets in client-side code
- Do NOT store sensitive tokens in local storage if security requirements are high (prefer httpOnly cookies)
- Do NOT implement authorization by trusting frontend claims alone
- Ensure all authentication failures return appropriate HTTP status codes
- Implement proper logging for security events
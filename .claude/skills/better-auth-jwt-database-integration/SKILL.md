# Better Auth with JWT and Database Integration Skill

## Overview

This skill provides a comprehensive authentication workflow using Better Auth for user management, JWT tokens for authentication, and database integration for both frontend and backend operations. It ensures secure user authentication and user-scoped data access across full-stack applications.

## Purpose

The purpose of this skill is to:
- Implement secure user authentication using Better Auth
- Integrate JWT tokens for stateless authentication
- Connect to databases for user management and data storage
- Provide backend JWT verification for protected resources
- Ensure user-isolated data access with proper authorization

## Components

### 1. Frontend Better Auth Configuration

#### Core Configuration
```typescript
import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { schema } from "../db/schema";
import { nextCookies } from "better-auth/next-js";
import { db } from "../db/drizzle";

export const auth = betterAuth({
  // Social provider configuration
  socialProviders: {
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID as string,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET as string,
    },
  },

  // Email and password authentication
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false, // Set to true in production
  },

  // Database adapter configuration
  database: drizzleAdapter(db, {
    provider: "pg", // PostgreSQL provider
    schema       // Drizzle schema for Better Auth tables
  }),

  // Security configuration
  secret: process.env.NEXT_PUBLIC_BETTER_AUTH_SECRET || "fallback_secret_key_change_in_production",

  // Plugins for enhanced functionality
  plugins: [
    jwt({}),          // Enable JWT token issuance
    nextCookies()     // Enable cookie management
  ],
});
```

#### API Route Handler
```typescript
import { toNextJsHandler } from "better-auth/next-js"
import { auth } from "@/lib/auth"

export const runtime = "nodejs" // Required on Vercel

export const { GET, POST } = toNextJsHandler(auth)
```

### 2. Environment Variables

```bash
# Better Auth Configuration
NEXT_PUBLIC_BETTER_AUTH_SECRET=your_secret_key_here
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000

# Database Configuration
DATABASE_URL=postgresql://username:password@host:port/database

# Social Provider Configuration
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

## Database Schema and Drizzle ORM

### Drizzle Database Connection
```typescript
import { drizzle } from "drizzle-orm/neon-http";
import { neon } from "@neondatabase/serverless";
import { config } from "dotenv";

config({ path: ".env" });

export const db = drizzle(process.env.DATABASE_URL!);
```

### Authentication Schema
```typescript
import { relations } from "drizzle-orm";
import { pgTable, text, timestamp, boolean, index } from "drizzle-orm/pg-core";

// User table for authentication
export const user = pgTable("user", {
  id: text("id").primaryKey(),
  name: text("name").notNull(),
  email: text("email").notNull().unique(),
  emailVerified: boolean("email_verified").default(false).notNull(),
  image: text("image"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at")
    .defaultNow()
    .$onUpdate(() => new Date())
    .notNull(),
});

// Session table for managing user sessions
export const session = pgTable(
  "session",
  {
    id: text("id").primaryKey(),
    expiresAt: timestamp("expires_at").notNull(),
    token: text("token").notNull().unique(),
    createdAt: timestamp("created_at").defaultNow().notNull(),
    updatedAt: timestamp("updated_at")
      .$onUpdate(() => new Date())
      .notNull(),
    ipAddress: text("ip_address"),
    userAgent: text("user_agent"),
    userId: text("user_id")
      .notNull()
      .references(() => user.id, { onDelete: "cascade" }),
  },
  (table) => [index("session_userId_idx").on(table.userId)],
);

// Account table for social provider accounts
export const account = pgTable(
  "account",
  {
    id: text("id").primaryKey(),
    accountId: text("account_id").notNull(),
    providerId: text("provider_id").notNull(),
    userId: text("user_id")
      .notNull()
      .references(() => user.id, { onDelete: "cascade" }),
    accessToken: text("access_token"),
    refreshToken: text("refresh_token"),
    idToken: text("id_token"),
    accessTokenExpiresAt: timestamp("access_token_expires_at"),
    refreshTokenExpiresAt: timestamp("refresh_token_expires_at"),
    scope: text("scope"),
    password: text("password"),
    createdAt: timestamp("created_at").defaultNow().notNull(),
    updatedAt: timestamp("updated_at")
      .$onUpdate(() => new Date())
      .notNull(),
  },
  (table) => [index("account_userId_idx").on(table.userId)],
);

// Verification table for email verification
export const verification = pgTable(
  "verification",
  {
    id: text("id").primaryKey(),
    identifier: text("identifier").notNull(),
    value: text("value").notNull(),
    expiresAt: timestamp("expires_at").notNull(),
    createdAt: timestamp("created_at").defaultNow().notNull(),
    updatedAt: timestamp("updated_at")
      .defaultNow()
      .$onUpdate(() => new Date())
      .notNull(),
  },
  (table) => [index("verification_identifier_idx").on(table.identifier)],
);

// JWKS table for public/private key pairs
export const jwks = pgTable("jwks", {
  id: text("id").primaryKey(),
  publicKey: text("public_key").notNull(),
  privateKey: text("private_key").notNull(),
  createdAt: timestamp("created_at").notNull(),
  expiresAt: timestamp("expires_at"),
});

// Table relations
export const userRelations = relations(user, ({ many }) => ({
  sessions: many(session),
  accounts: many(account),
}));

export const schema = {
  user,
  session,
  account,
  verification,
  jwks
};
```

## JWT Token Issuance and Storage

### Token Generation Process
1. **User Authentication**: When a user successfully authenticates, Better Auth generates a JWT token
2. **Token Content**: The JWT contains user information including:
   - `sub`: User ID (subject identifier)
   - `email`: User's email address
   - `name`: User's name
   - `iat`: Issued at timestamp
   - `exp`: Expiration timestamp
   - `kid`: Key ID for identifying the signing key

### Token Storage
- **Frontend**: JWT tokens are stored as HTTP-only cookies for security
- **Backend**: Tokens are validated through Authorization header
- **Cookie Security**: HTTP-only cookies prevent XSS attacks

### Token Algorithms
- **Symmetric (HS256)**: Uses shared secret for signing/verification
- **Asymmetric (EdDSA)**: Uses public/private key pairs for enhanced security

## Backend JWT Verification Middleware

### JWT Middleware Implementation
```python
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from jose import JWTError
from typing import Dict, Optional
import os
import requests
import json
from jose.utils import base64url_decode

def get_jwt_secret():
    """Get JWT secret from environment, prioritizing the same variable Better Auth uses"""
    # Better Auth typically uses BETTER_AUTH_SECRET for both frontend and backend
    secret = os.getenv("NEXT_PUBLIC_BETTER_AUTH_SECRET")
    if not secret or secret == "":
        secret = os.getenv("BETTER_AUTH_SECRET")
    if not secret or secret == "":
        # Fallback - but this should not be used in production
        print("WARNING: Using fallback JWT secret. This should not happen in production!")
        secret = "e8QDSIu8QZtOENR8tRcsdwYMmwC4Uom0"  # Same as in .env
    return secret

JWT_SECRET = get_jwt_secret()
SUPPORTED_ALGORITHMS = ["EdDSA", "RS256", "RS384", "RS512", "HS256", "HS384", "HS512", "ES256", "ES384", "ES512", "PS256", "PS384", "PS512"]

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)

        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication scheme."
                )
            token = credentials.credentials
            payload = self.verify_jwt(token)
            if not payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token or expired token."
                )

            # Extract user_id from the payload (Better Auth uses 'sub' claim)
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing user ID."
                )

            request.state.user_id = user_id
            request.state.user_payload = payload  # Store full payload for additional user info if needed
            return credentials.credentials
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header."
            )

    def verify_jwt(self, token: str) -> Optional[Dict]:
        """
        Verify Better Auth JWT token.
        Try JWKS-based verification first (for EdDSA/RS algorithms), then secret-based (for HS algorithms).
        """
        # Decode the token header to get the algorithm info first
        try:
            from jose import jwt as jose_jwt

            # Decode the token header to get the algorithm
            header_data = token.split('.')[0]
            # Add padding if needed
            header_data += '=' * (4 - len(header_data) % 4)
            header = json.loads(base64url_decode(header_data.encode()))
            alg = header.get('alg')

            # If algorithm is HS256/HS384/HS512, try secret-based verification first
            if alg and alg.startswith('HS'):
                try:
                    payload = jose_jwt.decode(token, JWT_SECRET, algorithms=[alg], options={"verify_exp": True})
                    return payload
                except jose_jwt.ExpiredSignatureError:
                    return None
                except jose_jwt.JWTError:
                    pass  # Try JWKS method
            else:
                print(f"Algorithm {alg} is asymmetric, skipping secret-based verification")
        except Exception:
            pass  # Try JWKS method

        # For asymmetric algorithms (EdDSA, RS*, ES*), use JWKS-based verification
        try:
            from jose import jwk

            # Get the Better Auth JWKS endpoint
            better_auth_url = os.getenv("NEXT_PUBLIC_BETTER_AUTH_URL", "http://localhost:3000")
            jwks_url = f"{better_auth_url}/api/auth/jwks"

            # Fetch the JWKS
            jwks_response = requests.get(jwks_url, timeout=10)
            if not jwks_response.text:
                return None

            jwks = jwks_response.json()

            # Decode the token header to get the kid
            header_data = token.split('.')[0]
            header_data += '=' * (4 - len(header_data) % 4)
            header = json.loads(base64url_decode(header_data.encode()))

            kid = header.get('kid')
            if not kid:
                return None

            # Find the matching key in JWKS
            rsa_key = None
            for key in jwks.get('keys', []):
                if key.get('kid') == kid:
                    rsa_key = key
                    break

            if rsa_key is None:
                return None

            # Determine the algorithm from the key or header
            alg = rsa_key.get('alg') or header.get('alg')
            if alg and alg not in SUPPORTED_ALGORITHMS:
                return None

            # Handle different key types properly
            if rsa_key.get('kty') == 'OKP' and rsa_key.get('crv') == 'Ed25519':
                # This is an Ed25519 key used with EdDSA
                try:
                    # Decode the token components
                    header, payload, signature = token.split('.')

                    # Decode header and payload
                    header_data = base64url_decode(header.encode())
                    payload_data = base64url_decode(payload.encode())
                    signature_data = base64url_decode(signature.encode())

                    # Get the public key component
                    x_b64 = rsa_key['x']
                    if len(x_b64) % 4:
                        x_b64 += '=' * (4 - len(x_b64) % 4)
                    x_bytes = base64.urlsafe_b64decode(x_b64.encode())

                    # Use cryptography library for Ed25519 verification
                    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
                    from cryptography.exceptions import InvalidSignature

                    # Create the public key
                    public_key_crypto = Ed25519PublicKey.from_public_bytes(x_bytes)

                    # Verify the signature
                    message = f"{header}.{payload}".encode()
                    try:
                        public_key_crypto.verify(signature_data, message)

                        # If verification succeeds, decode the payload to get user info
                        payload_dict = json.loads(payload_data.decode())
                        return payload_dict
                    except InvalidSignature:
                        return None

                except Exception:
                    # Fallback to original approach
                    try:
                        public_key = jwk.construct(rsa_key)
                        payload = jose_jwt.decode(
                            token,
                            public_key.to_dict(),
                            algorithms=[alg] if alg else SUPPORTED_ALGORITHMS,
                            options={"verify_aud": False, "verify_exp": True}
                        )
                    except Exception:
                        return None
            elif rsa_key.get('kty') == 'RSA':
                public_key = jwk.construct(rsa_key, algorithm=alg)
                payload = jose_jwt.decode(
                    token,
                    public_key.to_dict(),
                    algorithms=[alg] if alg else SUPPORTED_ALGORITHMS,
                    options={"verify_aud": False, "verify_exp": True}
                )
            elif rsa_key.get('kty') == 'EC':
                public_key = jwk.construct(rsa_key, algorithm=alg)
                payload = jose_jwt.decode(
                    token,
                    public_key.to_dict(),
                    algorithms=[alg] if alg else SUPPORTED_ALGORITHMS,
                    options={"verify_aud": False, "verify_exp": True}
                )
            else:
                public_key = jwk.construct(rsa_key)
                payload = jose_jwt.decode(
                    token,
                    public_key.to_dict(),
                    algorithms=[alg] if alg else SUPPORTED_ALGORITHMS,
                    options={"verify_aud": False, "verify_exp": True}
                )

            return payload

        except jose_jwt.ExpiredSignatureError:
            return None
        except jose_jwt.JWTError:
            return None
        except requests.exceptions.RequestException:
            return None
        except Exception:
            return None
```

### Authentication Helper
```python
from fastapi import Depends, HTTPException, Request, status
from .middleware.jwt_middleware import JWTBearer, verify_token
from typing import Dict, Optional

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
```

## User-Scoped Data Access Patterns

### Protected Routes Example
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List
from ..models.task import Task, TaskCreate, TaskRead, TaskUpdate
from ..db import get_session
from ..auth import get_user_id_from_token
from ..crud.task import (
    create_task as crud_create_task,
    get_tasks_by_user,
    get_task_by_id_and_user,
    get_task_by_id,
    update_task as crud_update_task,
    toggle_task_completion,
    delete_task as crud_delete_task
)

router = APIRouter(tags=["tasks"])

@router.post("/tasks", response_model=TaskRead)
def create_task(
    task: TaskCreate,
    user_id: str = Depends(get_user_id_from_token),
    session: Session = Depends(get_session)
):
    """
    Create a new task for the authenticated user.

    The user_id is extracted from the JWT token, not from the request body,
    ensuring users can only create tasks for themselves.
    """
    db_task = crud_create_task(session, task, user_id)
    return db_task

@router.get("/tasks", response_model=List[TaskRead])
def read_tasks(
    user_id: str = Depends(get_user_id_from_token),
    session: Session = Depends(get_session),
    completed: str = None,  # "all", "pending", "completed"
    priority: str = None,   # "low", "medium", "high"
    search: str = None,     # search term for title/description
    sort: str = "created_at",  # field to sort by
    order: str = "desc",      # sort order: "asc" or "desc"
    tags: str = None        # tag to filter by
):
    """
    Retrieve all tasks for the authenticated user with optional filtering, search, and sorting.

    Query parameters:
    - completed: Filter by completion status ("pending", "completed", "all")
    - priority: Filter by priority level ("low", "medium", "high")
    - search: Search term to match in title or description
    - sort: Field to sort by ("created_at", "due_date", "priority", "title")
    - order: Sort order ("asc", "desc")
    - tags: Filter by a specific tag
    """
    tasks = get_tasks_by_user(
        session,
        user_id,
        completed=completed,
        priority=priority,
        search=search,
        sort=sort,
        order=order,
        tags=tags
    )
    return tasks

@router.get("/tasks/{task_id}", response_model=TaskRead)
def read_task(
    task_id: int,
    user_id: str = Depends(get_user_id_from_token),
    session: Session = Depends(get_session)
):
    """
    Retrieve a specific task by ID.

    Users can only access their own tasks. If a task doesn't exist
    a 404 error is returned. If the task exists but belongs to another user,
    a 403 error is returned.
    """
    # First check if the task exists (without checking ownership)
    task_exists = get_task_by_id(session, task_id)

    if not task_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Now check if the task belongs to the authenticated user
    task = get_task_by_id_and_user(session, task_id, user_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You don't have permission to access this task"
        )

    return task
```

## Frontend Usage Examples

### Authentication Client Usage
```typescript
// In your frontend components, you can use the auth client
import { authClient } from '@/lib/auth-client';

// Sign up example
const signUp = async (email: string, password: string) => {
  const result = await authClient.signUp.email({
    email,
    password,
    name: "User Name"
  });

  if (result.error) {
    console.error("Sign up failed:", result.error);
    return null;
  }

  return result.data;
};

// Sign in example
const signIn = async (email: string, password: string) => {
  const result = await authClient.signIn.email({
    email,
    password
  });

  if (result.error) {
    console.error("Sign in failed:", result.error);
    return null;
  }

  return result.data;
};

// Get current session
const getSession = async () => {
  const session = await authClient.getSession();
  return session.data;
};
```

## Backend Application Integration

### Main Application Setup
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Load environment variables explicitly
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv is not installed, environment variables should be loaded by the system
    pass

# Import JWT authentication middleware
try:
    from .middleware.jwt_middleware import JWTBearer
except ImportError:
    from middleware.jwt_middleware import JWTBearer

app = FastAPI(title="Secure Backend API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Secure Backend API!"}

# Include protected routes
try:
    from .routes import tasks
except ImportError:
    from routes import tasks

app.include_router(tasks.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Security Best Practices

### Secret Management
- Use strong, unique secrets for production
- Never commit secrets to version control
- Use environment variables for secret management

### Token Security
- Use HTTPS in production
- Set appropriate token expiration times
- Implement proper token refresh mechanisms

### Database Security
- Use parameterized queries to prevent SQL injection
- Implement proper access controls
- Regularly update and patch database systems

## Performance Considerations

### Token Verification
- Cache JWKS keys to avoid repeated HTTP requests
- Consider token introspection for high-traffic applications
- Implement proper error handling for network failures

### Database Optimization
- Use proper indexing on user_id fields
- Implement connection pooling
- Consider database read replicas for high availability

## Troubleshooting Common Issues

### Token Verification Failures
- Ensure the same secret is used in both frontend and backend
- Check that the JWKS endpoint is accessible from the backend
- Verify that the algorithm matches between frontend and backend

### Database Connection Issues
- Ensure the DATABASE_URL is correctly configured
- Check that the database is accessible from both frontend and backend
- Verify that the schema matches the expected structure

### CORS Issues
- Configure CORS middleware properly
- Ensure the frontend URL is in the allowed origins list
- Check that credentials are properly handled

## Implementation Checklist

### Frontend Setup
- [ ] Configure Better Auth with database adapter
- [ ] Set up JWT plugin for token issuance
- [ ] Create API route handler at `/api/auth/*`
- [ ] Configure environment variables
- [ ] Set up Drizzle ORM connection
- [ ] Define authentication schema

### Backend Setup
- [ ] Implement JWT verification middleware
- [ ] Create authentication helper functions
- [ ] Set up protected routes with user ID extraction
- [ ] Implement user-scoped data access patterns
- [ ] Configure CORS middleware
- [ ] Set up database connections

### Security Configuration
- [ ] Use HTTPS in production
- [ ] Set strong secrets
- [ ] Implement proper token expiration
- [ ] Add proper error handling
- [ ] Validate input data
- [ ] Sanitize outputs

### Testing
- [ ] Test authentication flow
- [ ] Verify JWT token validation
- [ ] Test user-scoped data access
- [ ] Validate error handling
- [ ] Check security measures
- [ ] Performance testing

## Architecture Decision Records

### ADR-001: Choice of Better Auth over Custom Authentication
- **Context**: Need for secure, scalable user authentication with social login support
- **Decision**: Use Better Auth for authentication management
- **Rationale**:
  - Provides battle-tested authentication with multiple providers
  - Handles JWT token issuance and management
  - Integrates well with database systems
  - Maintains security best practices
- **Consequences**:
  - Positive: Reduced development time, security features built-in
  - Negative: Dependency on external library, learning curve

### ADR-002: JWT-based Authentication over Session Cookies
- **Context**: Need for stateless authentication across frontend and backend
- **Decision**: Use JWT tokens for authentication
- **Rationale**:
  - Stateless (no server-side session storage)
  - Works across domains (CORS-friendly)
  - Mobile-app compatible
  - Scales horizontally (no session affinity)
- **Consequences**:
  - Positive: Scalability, cross-platform compatibility
  - Negative: Cannot revoke tokens before expiry, larger payload size

## Migration Path

### From Session-based to JWT-based
1. Implement JWT middleware in backend
2. Update frontend to store tokens in cookies/local storage
3. Modify authentication routes to issue JWT tokens
4. Update protected routes to validate JWT tokens
5. Implement token refresh mechanisms

### From Different Auth Libraries
1. Migrate user data to Better Auth schema
2. Update authentication endpoints
3. Implement JWT token validation
4. Update frontend authentication calls
5. Test user migration and authentication flow

## Testing Strategy

### Unit Tests
- JWT token generation and validation
- Database adapter functionality
- Authentication middleware
- User-scoped data access

### Integration Tests
- End-to-end authentication flow
- Token refresh mechanisms
- Protected route access
- Database integration

### Security Tests
- Token tampering attempts
- Invalid token handling
- User impersonation attempts
- Database injection attempts

## Monitoring and Observability

### Key Metrics
- Authentication success/failure rates
- Token validation performance
- Database connection health
- User session duration

### Logging Strategy
- Structured logging with correlation IDs
- Authentication event logging
- Token validation failures
- Security-related events

### Health Checks
- Database connectivity
- JWT verification service
- Authentication endpoints
- Token refresh endpoints

## Performance Optimization

### Token Caching
- Cache JWKS keys to reduce HTTP requests
- Implement token validation caching
- Use connection pooling for database

### Database Optimization
- Index user_id fields for fast lookups
- Optimize query patterns for user-scoped data
- Use connection pooling and connection reuse

### Network Optimization
- Minimize token size
- Use efficient serialization formats
- Implement proper compression

## Error Handling Strategy

### Authentication Errors
- Invalid credentials
- Expired tokens
- Invalid tokens
- Revoked tokens

### Database Errors
- Connection failures
- Query timeouts
- Constraint violations
- Transaction failures

### Network Errors
- JWKS endpoint unavailable
- Token validation timeouts
- Database connection timeouts
- API rate limits

## Security Considerations

### Token Security
- Use HTTPS in production
- Implement short token lifetimes
- Use strong signing algorithms
- Regular key rotation

### Input Validation
- Validate all user inputs
- Sanitize data before storage
- Prevent injection attacks
- Implement rate limiting

### Access Control
- User-scoped data access
- Role-based permissions
- Audit trail for sensitive operations
- Session management

## Best Practices Summary

### For Developers
- Use environment variables for configuration
- Implement proper error handling
- Follow security best practices
- Test authentication flows thoroughly

### For DevOps
- Monitor authentication metrics
- Implement proper logging
- Set up alerting for failures
- Regular security audits

### For Security
- Regular secret rotation
- Security scanning
- Penetration testing
- Compliance verification

This skill provides a complete, production-ready authentication system using Better Auth, JWT tokens, and database integration. It ensures secure, scalable, and maintainable user authentication across full-stack applications.
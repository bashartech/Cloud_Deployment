# Better Auth JWT to Database Workflow Skill

## Overview
This skill documents the complete workflow for implementing JWT-based authentication with Better Auth, connecting frontend token retrieval to backend verification and database operations. This addresses common integration challenges and provides a robust solution for full-stack applications.

## Complete Workflow

### 1. Frontend Token Retrieval
- **Configuration**: Set up Better Auth client with JWT plugin
- **Token Extraction**: Use `authClient.token()` method to retrieve JWT
- **Header Formation**: Add `Authorization: Bearer <token>` to API requests
- **Client Setup**: Include `jwtClient()` plugin in auth client configuration

### 2. Backend JWT Verification
- **Middleware**: Implement JWTBearer middleware for token validation
- **Algorithm Detection**: Identify token algorithm (HS256, EdDSA, etc.)
- **Verification Methods**:
  - For HS algorithms: Use shared secret verification
  - For asymmetric algorithms: Use JWKS-based verification
- **Token Validation**: Verify signature, expiration, and claims

### 3. Database Integration
- **User Scoping**: Extract user ID from JWT payload ('sub' claim)
- **Request State**: Inject user_id into request.state for route handlers
- **Data Access**: Scope database queries to authenticated user only
- **Authorization**: Verify user ownership before data operations

## Common Issues and Solutions

### Issue 1: JWKS Endpoint Configuration
**Problem**: JWKS endpoint returning HTML instead of JSON
**Solution**:
- Changed endpoint from `/.well-known/jwks.json` to `/api/auth/jwks`
- This aligns with Better Auth's actual JWKS endpoint location

### Issue 2: EdDSA Algorithm Verification
**Problem**: "Unable to find an algorithm for key" error with EdDSA tokens
**Solution**:
- Implemented manual Ed25519 signature verification using cryptography library
- Added fallback to jose library if manual verification fails
- Proper handling of OKP (Octet Key Pair) key types

### Issue 3: Token Algorithm Detection
**Problem**: "The specified alg value is not allowed" error
**Solution**:
- Expanded SUPPORTED_ALGORITHMS to include all possible JWT algorithms
- Added algorithm-specific verification logic
- Prioritize symmetric (HS) verification for HS algorithms

### Issue 4: Variable Scoping in JWT Verification
**Problem**: "cannot access local variable 'jwt' where it is not associated with a value"
**Solution**:
- Import JWT library as `jose_jwt` to avoid variable shadowing
- Proper scoping of import statements within functions

### Issue 5: JWKS Key Construction
**Problem**: "Unable to find an algorithm for key" during key construction
**Solution**:
- Added special handling for different key types (OKP, RSA, EC)
- Implemented proper Ed25519 key construction with base64 decoding
- Added error handling with fallback approaches

## Implementation Details

### Frontend Configuration
```typescript
// auth-client.ts
import { createAuthClient } from "better-auth/client";
import { jwtClient } from "better-auth/client/plugins";

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || "http://localhost:3000",
  plugins: [jwtClient()]
});
```

### API Client Integration
```typescript
// api.ts
const tokenResult = await authClient.token();
if (tokenResult && 'data' in tokenResult && tokenResult.data?.token) {
  token = tokenResult.data.token;
}
// Add to headers: Authorization: Bearer ${token}
```

### Backend Middleware
```python
# jwt_middleware.py
class JWTBearer(HTTPBearer):
    def verify_jwt(self, token: str) -> Optional[Dict]:
        # Algorithm detection and verification logic
        # Manual Ed25519 verification for OKP keys
        # JWKS-based verification for other algorithms
```

### Database Integration
```python
# auth.py
def get_user_id_from_token(request: Request, _: str = Depends(jwt_bearer_scheme)):
    # Extract user_id from request.state injected by middleware
    return request.state.user_id

# routes/tasks.py
@router.get("/tasks", response_model=List[TaskRead])
def read_tasks(
    user_id: str = Depends(get_user_id_from_token),
    session: Session = Depends(get_session)
):
    # Scope tasks to authenticated user only
```

## Security Considerations

1. **Token Validation**: Always validate JWT signature, expiration, and claims
2. **User Scoping**: Ensure all database operations are scoped to authenticated user
3. **Secret Management**: Use environment variables for JWT secrets
4. **Error Handling**: Return appropriate HTTP status codes (401, 403)
5. **CORS Configuration**: Properly configure CORS for cross-origin requests

## Testing and Validation

1. **Token Flow**: Verify JWT retrieval → transmission → validation → database access
2. **Error Cases**: Test invalid tokens, expired tokens, wrong user access
3. **Authorization**: Ensure users can only access their own data
4. **Algorithm Support**: Test both symmetric and asymmetric algorithm tokens

## Best Practices

1. **JWT Configuration**: Use appropriate algorithms (EdDSA recommended for security)
2. **Key Rotation**: Implement key rotation if using JWKS-based verification
3. **Caching**: Cache JWKS for performance (keys don't change frequently)
4. **Monitoring**: Log authentication failures for security monitoring
5. **Fallbacks**: Implement fallback verification methods for reliability

## Troubleshooting

### Common Error Messages:
- "Unable to find an algorithm for key": Check key type and algorithm support
- "The specified alg value is not allowed": Verify SUPPORTED_ALGORITHMS includes token algorithm
- "Invalid token or expired token": Validate token format and expiration
- JWKS endpoint returning HTML: Verify endpoint URL and server configuration

### Debugging Steps:
1. Enable detailed logging for JWT verification process
2. Verify JWKS endpoint is accessible and returns proper JSON
3. Check that Better Auth server is running and configured correctly
4. Confirm JWT secret matches between frontend and backend
5. Validate token algorithm and key type compatibility

This skill provides a complete reference for implementing JWT-based authentication with Better Auth, handling the common integration challenges and ensuring a secure, robust authentication workflow.
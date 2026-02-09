from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from jose import JWTError
from typing import Dict, Optional
import os

# JWT configuration - must match Better Auth's secret
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
# Better Auth supports multiple algorithms - include more common ones
SUPPORTED_ALGORITHMS = ["EdDSA", "RS256", "RS384", "RS512", "HS256", "HS384", "HS512", "ES256", "ES384", "ES512", "PS256", "PS384", "PS512"]

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        # First, check for X-User-ID header as a fallback for development
        user_id_header = request.headers.get("X-User-ID")
        if user_id_header:
            print(f"DEBUG: Using X-User-ID header for user: {user_id_header}")
            request.state.user_id = user_id_header
            request.state.user_payload = {"sub": user_id_header, "user_id_header_used": True}
            return user_id_header

        # If no X-User-ID header, proceed with JWT token authentication
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
        # Print for debugging - only log token presence, not the full token to avoid sensitive data exposure
        print(f"DEBUG: Attempting to verify Better Auth JWT - token present: {bool(token)}")

        # Decode the token header to get the algorithm info first
        try:
            from jose import jwt as jose_jwt
            from jose.utils import base64url_decode
            import json

            # Decode the token header to get the algorithm
            header_data = token.split('.')[0]
            # Add padding if needed
            header_data += '=' * (4 - len(header_data) % 4)
            header = json.loads(base64url_decode(header_data.encode()))
            alg = header.get('alg')

            print(f"DEBUG: Token algorithm detected: {alg}")

            # If algorithm is HS256/HS384/HS512, try secret-based verification first
            if alg and alg.startswith('HS'):
                try:
                    payload = jose_jwt.decode(token, JWT_SECRET, algorithms=[alg], options={"verify_exp": True})
                    print(f"DEBUG: Successfully decoded JWT with secret for user: {payload.get('sub', 'unknown')}")
                    return payload
                except jose_jwt.ExpiredSignatureError:
                    print("DEBUG: JWT token has expired - token rejected")
                    return None
                except jose_jwt.JWTError as e:
                    print(f"DEBUG: Secret-based verification failed: {str(e)} - trying JWKS method")
                except Exception as secret_error:
                    print(f"DEBUG: Unexpected error in secret-based verification: {str(secret_error)}")
            else:
                print(f"DEBUG: Algorithm {alg} is asymmetric, skipping secret-based verification")
        except Exception as header_error:
            print(f"DEBUG: Error decoding token header: {str(header_error)} - trying JWKS method")

        # For asymmetric algorithms (EdDSA, RS*, ES*), use JWKS-based verification
        try:
            # Import JWKS client for proper public key verification
            from jose import jwk
            import requests
            import json

            # Get the Better Auth JWKS endpoint - in Kubernetes, use internal service name
            better_auth_url = os.getenv("BETTER_AUTH_INTERNAL_URL", os.getenv("NEXT_PUBLIC_BETTER_AUTH_URL", "http://todo-chatbot-frontend:3000"))
            jwks_url = f"{better_auth_url}/api/auth/jwks"

            # Fetch the JWKS with proper error handling
            print(f"DEBUG: Attempting to fetch JWKS from: {jwks_url}")
            jwks_response = requests.get(jwks_url, timeout=10)

            # Check if response is empty or invalid
            print(f"DEBUG: JWKS response status: {jwks_response.status_code}")
            print(f"DEBUG: JWKS response headers: {dict(jwks_response.headers)}")
            if not jwks_response.text:
                print(f"DEBUG: JWKS endpoint returned empty response - token rejected")
                return None

            # Try to parse the response as JSON
            try:
                jwks = jwks_response.json()
                print(f"DEBUG: JWKS response keys: {list(jwks.keys()) if isinstance(jwks, dict) else 'Not a dict'}")
                print(f"DEBUG: JWKS keys count: {len(jwks.get('keys', []))}")
                for i, key in enumerate(jwks.get('keys', [])):
                    print(f"DEBUG: JWKS key {i}: {key.get('kty', 'unknown')} {key.get('alg', 'unknown')} {key.get('use', 'unknown')}")
            except json.JSONDecodeError as json_error:
                print(f"DEBUG: JWKS response is not valid JSON: {jwks_response.text[:200]}... - token rejected")
                return None

            # Decode the token header to get the kid
            header_data = token.split('.')[0]
            # Add padding if needed
            header_data += '=' * (4 - len(header_data) % 4)
            header = json.loads(base64url_decode(header_data.encode()))

            kid = header.get('kid')
            if not kid:
                print(f"DEBUG: No kid found in token header - token rejected")
                return None

            # Find the matching key in JWKS
            rsa_key = None
            for key in jwks.get('keys', []):
                if key.get('kid') == kid:
                    rsa_key = key
                    break

            if rsa_key is None:
                print(f"DEBUG: No matching key found for kid: {kid} - token rejected")
                return None

            # Determine the algorithm from the key or header
            alg = rsa_key.get('alg') or header.get('alg')
            if alg and alg not in SUPPORTED_ALGORITHMS:
                print(f"DEBUG: Algorithm {alg} not supported - token rejected")
                return None

            # For EdDSA, we need to handle it specially as it's not well supported by jwk.construct in some versions
            from jose import jwk
            from jose.backends import RSAKey, ECKey, HMACKey
            from jose.constants import ALGORITHMS
            import base64
            import json
            from jose.utils import base64url_decode

            # Handle different key types properly
            if rsa_key.get('kty') == 'OKP' and rsa_key.get('crv') == 'Ed25519':
                # This is an Ed25519 key used with EdDSA
                # For this specific case, let's try to manually decode and verify
                try:
                    # Decode the token components
                    header, payload, signature = token.split('.')

                    # Decode header and payload
                    header_data = base64url_decode(header.encode())
                    payload_data = base64url_decode(payload.encode())
                    signature_data = base64url_decode(signature.encode())

                    # Get the public key component
                    x_b64 = rsa_key['x']
                    # Add padding if needed
                    if len(x_b64) % 4:
                        x_b64 += '=' * (4 - len(x_b64) % 4)
                    x_bytes = base64.urlsafe_b64decode(x_b64.encode())

                    # Try to use cryptography library for Ed25519 verification
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
                        print(f"DEBUG: Successfully verified Ed25519 JWT for user: {payload_dict.get('sub', 'unknown')}")
                        return payload_dict
                    except InvalidSignature:
                        print(f"DEBUG: Ed25519 signature verification failed - token rejected")
                        return None

                except Exception as e:
                    print(f"DEBUG: Failed to verify Ed25519 key manually: {str(e)} - trying fallback")
                    # Fallback to original approach
                    try:
                        public_key = jwk.construct(rsa_key)
                        # If fallback succeeds, continue to normal verification
                        payload = jose_jwt.decode(
                            token,
                            public_key.to_dict(),
                            algorithms=[alg] if alg else SUPPORTED_ALGORITHMS,
                            options={"verify_aud": False, "verify_exp": True}  # Disable audience verification but verify expiration
                        )
                    except Exception as fallback_error:
                        print(f"DEBUG: Fallback key construction also failed: {str(fallback_error)} - token rejected")
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

            if 'payload' in locals():
                print(f"DEBUG: Successfully verified JWT with JWKS for user: {payload.get('sub', 'unknown')}")
                return payload

        except jose_jwt.ExpiredSignatureError:
            print("DEBUG: JWT token has expired - token rejected")
            return None
        except jose_jwt.JWTError as e:
            print(f"DEBUG: JWT error during JWKS verification: {str(e)} - token rejected")
            return None
        except requests.exceptions.RequestException as e:
            print(f"DEBUG: Error fetching JWKS from Better Auth: {str(e)} - token rejected")
            return None
        except Exception as e:
            print(f"DEBUG: General error in JWT verification: {str(e)} - token rejected")
            return None

def verify_token(token: str, request: Request = None) -> Optional[Dict]:
    """Verify Better Auth JWT token."""

    # First, if a request is provided, check for X-User-ID header as a fallback for development
    if request and hasattr(request, 'headers'):
        user_id_header = request.headers.get("X-User-ID")
        if user_id_header:
            print(f"DEBUG verify_token: Using X-User-ID header for user: {user_id_header}")
            return {"sub": user_id_header, "user_id_header_used": True}

    # If no X-User-ID header or no request, proceed with JWT token verification
    # Print for debugging - only log token presence, not the full token to avoid sensitive data exposure
    print(f"DEBUG verify_token: Attempting to verify Better Auth JWT - token present: {bool(token)}")

    # Decode the token header to get the algorithm info first
    try:
        from jose import jwt as jose_jwt
        from jose.utils import base64url_decode
        import json

        # Decode the token header to get the algorithm
        header_data = token.split('.')[0]
        # Add padding if needed
        header_data += '=' * (4 - len(header_data) % 4)
        header = json.loads(base64url_decode(header_data.encode()))
        alg = header.get('alg')

        print(f"DEBUG verify_token: Token algorithm detected: {alg}")

        # If algorithm is HS256/HS384/HS512, try secret-based verification first
        if alg and alg.startswith('HS'):
            try:
                payload = jose_jwt.decode(token, JWT_SECRET, algorithms=[alg], options={"verify_exp": True})
                print(f"DEBUG verify_token: Successfully decoded JWT with secret for user: {payload.get('sub', 'unknown')}")
                return payload
            except jose_jwt.ExpiredSignatureError:
                print("DEBUG verify_token: JWT token has expired - token rejected")
                return None
            except jose_jwt.JWTError as e:
                print(f"DEBUG verify_token: Secret-based verification failed: {str(e)} - trying JWKS method")
            except Exception as secret_error:
                print(f"DEBUG verify_token: Unexpected error in secret-based verification: {str(secret_error)}")
        else:
            print(f"DEBUG verify_token: Algorithm {alg} is asymmetric, skipping secret-based verification")
    except Exception as header_error:
        print(f"DEBUG verify_token: Error decoding token header: {str(header_error)} - trying JWKS method")

    # For asymmetric algorithms (EdDSA, RS*, ES*), use JWKS-based verification
    try:
        # Import JWKS client for proper public key verification
        from jose import jwk
        import requests
        import json

        # Get the Better Auth JWKS endpoint - in Kubernetes, use internal service name
        better_auth_url = os.getenv("BETTER_AUTH_INTERNAL_URL", os.getenv("NEXT_PUBLIC_BETTER_AUTH_URL", "http://todo-chatbot-frontend:3000"))
        jwks_url = f"{better_auth_url}/api/auth/jwks"

        # Fetch the JWKS with proper error handling
        print(f"DEBUG verify_token: Attempting to fetch JWKS from: {jwks_url}")
        jwks_response = requests.get(jwks_url, timeout=10)

        # Check if response is empty or invalid
        print(f"DEBUG verify_token: JWKS response status: {jwks_response.status_code}")
        print(f"DEBUG verify_token: JWKS response headers: {dict(jwks_response.headers)}")
        if not jwks_response.text:
            print(f"DEBUG verify_token: JWKS endpoint returned empty response - token rejected")
            return None

        # Try to parse the response as JSON
        try:
            jwks = jwks_response.json()
            print(f"DEBUG verify_token: JWKS response keys: {list(jwks.keys()) if isinstance(jwks, dict) else 'Not a dict'}")
            print(f"DEBUG verify_token: JWKS keys count: {len(jwks.get('keys', []))}")
            for i, key in enumerate(jwks.get('keys', [])):
                print(f"DEBUG verify_token: JWKS key {i}: {key.get('kty', 'unknown')} {key.get('alg', 'unknown')} {key.get('use', 'unknown')}")
        except json.JSONDecodeError as json_error:
            print(f"DEBUG verify_token: JWKS response is not valid JSON: {jwks_response.text[:200]}... - token rejected")
            return None

        # Decode the token header to get the kid
        header_data = token.split('.')[0]
        # Add padding if needed
        header_data += '=' * (4 - len(header_data) % 4)
        header = json.loads(base64url_decode(header_data.encode()))

        kid = header.get('kid')
        if not kid:
            print(f"DEBUG verify_token: No kid found in token header - token rejected")
            return None

        # Find the matching key in JWKS
        rsa_key = None
        for key in jwks.get('keys', []):
            if key.get('kid') == kid:
                rsa_key = key
                break

        if rsa_key is None:
            print(f"DEBUG verify_token: No matching key found for kid: {kid} - token rejected")
            return None

        # Determine the algorithm from the key or header
        alg = rsa_key.get('alg') or header.get('alg')
        if alg and alg not in SUPPORTED_ALGORITHMS:
            print(f"DEBUG verify_token: Algorithm {alg} not supported - token rejected")
            return None

        # For EdDSA, we need to handle it specially as it's not well supported by jwk.construct in some versions
        from jose import jwk
        from jose.backends import RSAKey, ECKey, HMACKey
        from jose.constants import ALGORITHMS
        import base64
        import json
        from jose.utils import base64url_decode

        # Handle different key types properly
        if rsa_key.get('kty') == 'OKP' and rsa_key.get('crv') == 'Ed25519':
            # This is an Ed25519 key used with EdDSA
            # For this specific case, let's try to manually decode and verify
            try:
                # Decode the token components
                header, payload, signature = token.split('.')

                # Decode header and payload
                header_data = base64url_decode(header.encode())
                payload_data = base64url_decode(payload.encode())
                signature_data = base64url_decode(signature.encode())

                # Get the public key component
                x_b64 = rsa_key['x']
                # Add padding if needed
                if len(x_b64) % 4:
                    x_b64 += '=' * (4 - len(x_b64) % 4)
                x_bytes = base64.urlsafe_b64decode(x_b64.encode())

                # Try to use cryptography library for Ed25519 verification
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
                    print(f"DEBUG verify_token: Successfully verified Ed25519 JWT for user: {payload_dict.get('sub', 'unknown')}")
                    return payload_dict
                except InvalidSignature:
                    print(f"DEBUG verify_token: Ed25519 signature verification failed - token rejected")
                    return None

            except Exception as e:
                print(f"DEBUG verify_token: Failed to verify Ed25519 key manually: {str(e)} - trying fallback")
                # Fallback to original approach
                payload = None
                try:
                    public_key = jwk.construct(rsa_key)
                    # If fallback succeeds, continue to normal verification
                    payload = jose_jwt.decode(
                        token,
                        public_key.to_dict(),
                        algorithms=[alg] if alg else SUPPORTED_ALGORITHMS,
                        options={"verify_aud": False, "verify_exp": True}  # Disable audience verification but verify expiration
                    )
                except Exception as fallback_error:
                    print(f"DEBUG verify_token: Fallback key construction also failed: {str(fallback_error)} - token rejected")
                    return None
        elif rsa_key.get('kty') == 'RSA':
            public_key = jwk.construct(rsa_key, algorithm=alg)
            payload = jose_jwt.decode(
                token,
                public_key.to_dict(),
                algorithms=[alg] if alg else SUPPORTED_ALGORITHMS,
                options={"verify_aud": False, "verify_exp": True}
            )
            print(f"DEBUG verify_token: Successfully verified JWT with JWKS for user: {payload.get('sub', 'unknown')}")
            return payload
        elif rsa_key.get('kty') == 'EC':
            public_key = jwk.construct(rsa_key, algorithm=alg)
            payload = jose_jwt.decode(
                token,
                public_key.to_dict(),
                algorithms=[alg] if alg else SUPPORTED_ALGORITHMS,
                options={"verify_aud": False, "verify_exp": True}
            )
            print(f"DEBUG verify_token: Successfully verified JWT with JWKS for user: {payload.get('sub', 'unknown')}")
            return payload
        else:
            public_key = jwk.construct(rsa_key)
            payload = jose_jwt.decode(
                token,
                public_key.to_dict(),
                algorithms=[alg] if alg else SUPPORTED_ALGORITHMS,
                options={"verify_aud": False, "verify_exp": True}
            )
            print(f"DEBUG verify_token: Successfully verified JWT with JWKS for user: {payload.get('sub', 'unknown')}")
            return payload

    except jose_jwt.ExpiredSignatureError:
        print("DEBUG verify_token: JWT token has expired - token rejected")
        return None
    except jose_jwt.JWTError as e:
        print(f"DEBUG verify_token: JWT error during JWKS verification: {str(e)} - token rejected")
        return None
    except requests.exceptions.RequestException as e:
        print(f"DEBUG verify_token: Error fetching JWKS from Better Auth: {str(e)} - token rejected")
        return None
    except Exception as e:
        print(f"DEBUG verify_token: General error in JWT verification: {str(e)} - token rejected")
        return None
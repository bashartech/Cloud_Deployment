---
name: "Environment Configuration, CORS & Production Readiness"
description: "Implement environment-based configuration, secure CORS handling, and production readiness checks, ensuring the application runs correctly across development and deployment environments, preventing common deployment and security failures."
version: "1.0.0"
---

# Environment Configuration, CORS & Production Readiness

## When to Use This Skill

Use this skill when you need to:
- Configure environment-specific variables for different deployment stages
- Implement secure CORS policies for frontend-backend communication
- Ensure application security and stability across development and production environments
- Set up proper environment variable management to prevent hardcoded secrets
- Validate application readiness for deployment
- Establish secure defaults and fail-safe configurations

This skill prevents common deployment and security failures.

## Process Steps

1. **Environment Variable Configuration**
   - Define required environment variables for database credentials, JWT secrets, API URLs
   - Implement secure loading of environment variables in both frontend and backend
   - Create .env.example files to document required variables
   - Implement validation to ensure required variables are present at startup
   - Set up proper variable scoping to prevent secrets from being exposed

2. **CORS Configuration**
   - Configure explicit frontend origin allowances in backend
   - Implement secure CORS policies that allow authenticated requests
   - Block unauthorized origins while maintaining functionality
   - Set appropriate CORS headers for credentials and authentication
   - Test CORS configuration across different environments

3. **Production Safety Checks**
   - Implement startup validation for required environment variables
   - Create fail-fast mechanisms for misconfiguration
   - Ensure no debug-only behavior persists in production
   - Implement proper logging and error handling for production
   - Set up health checks for production monitoring

4. **Deployment Readiness Validation**
   - Verify frontend and backend can run independently
   - Remove localhost assumptions in production configurations
   - Ensure secure defaults are enforced across all environments
   - Test cross-environment compatibility
   - Validate that all dependencies are properly configured

5. **Security Hardening**
   - Implement secure defaults for all configurations
   - Ensure secrets are not exposed in client-side code
   - Validate that sensitive data is properly protected
   - Implement proper access controls for configuration
   - Set up audit trails for configuration changes

6. **Testing and Validation**
   - Test environment variable loading in different stages
   - Verify CORS behavior across environments
   - Validate production readiness with security scans
   - Test application behavior without hardcoded values
   - Confirm deployment configurations work as expected

## Output Format

The skill will produce:
- Properly configured environment variables for all deployment stages
- Secure CORS configuration allowing only authorized origins
- Production-ready application with proper safety checks
- Configuration validation and error handling
- Documentation for environment setup and deployment
- Security measures to prevent hardcoded secrets
- Testing procedures for environment and CORS validation

## Example

**Input:** Configure environment variables, CORS, and production readiness for a Next.js/FastAPI application

**Process:**
```python
# backend/main.py (FastAPI)
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get environment-specific variables
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
DATABASE_URL = os.getenv("DATABASE_URL")
JWT_SECRET = os.getenv("JWT_SECRET")

# Validate required environment variables
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")
if not JWT_SECRET:
    raise ValueError("JWT_SECRET environment variable is required")

app = FastAPI()

# Configure CORS based on environment
if ENVIRONMENT == "development":
    # Allow all origins in development (with credentials)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # Production: only allow specific frontend origin
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[FRONTEND_URL],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=["*"],
        # Allow credentials for JWT
        allow_credentials=True,
    )

# Example protected endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "environment": ENVIRONMENT}

# backend/.env.example
DATABASE_URL=postgresql://user:password@localhost/dbname
JWT_SECRET=your-super-secret-jwt-key-here
ENVIRONMENT=development
```

```typescript
// frontend/next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    // These will be available at build time
    NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
  },
  // For API routes
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.NEXT_PUBLIC_API_BASE_URL ? `${process.env.NEXT_PUBLIC_API_BASE_URL}/:path*` : 'http://localhost:8000/:path*',
      },
    ]
  }
}

module.exports = nextConfig

// frontend/.env.example
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_ENVIRONMENT=development

// frontend/lib/config.ts
export const config = {
  apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
  environment: process.env.NEXT_PUBLIC_ENVIRONMENT || 'development',
  isDevelopment: process.env.NEXT_PUBLIC_ENVIRONMENT === 'development',
  isProduction: process.env.NEXT_PUBLIC_ENVIRONMENT === 'production',
};

// frontend/pages/_app.tsx
import { config } from '../lib/config';

function MyApp({ Component, pageProps }) {
  // Validate critical configuration on app startup
  if (!config.apiBaseUrl) {
    console.error('API base URL is not configured');
    // In production, you might want to show an error page
  }

  return <Component {...pageProps} />;
}

export default MyApp;
```

**Output:** A properly configured application with secure environment variable handling, appropriate CORS settings for each environment, and production-ready safety checks that prevent common deployment failures.

## Implementation Rules

- Do NOT allow wildcard CORS in production environments (specify explicit origins)
- Do NOT hardcode secrets or URLs in source code (use environment variables)
- Do NOT disable security measures for convenience (maintain security by default)
- Do NOT commit actual environment variable files to version control
- Do NOT expose sensitive backend environment variables to frontend
- Do NOT assume localhost URLs in production configurations
- Ensure proper validation of required environment variables at startup
- Implement secure defaults that work safely across all environments
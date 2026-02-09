---
name: "Docker Compose & Local-to-Cloud Deployment Enablement"
description: "Enable consistent local development and cloud deployment using Docker and environment-based configuration, ensuring frontend, backend, and database integration works identically across environments."
version: "1.0.0"
---

# Docker Compose & Local-to-Cloud Deployment Enablement

## When to Use This Skill

Use this skill when you need to:
- Set up Docker Compose for consistent local development environment
- Enable cloud deployment with containerized services
- Ensure frontend and backend can run together in containers
- Externalize configuration through environment variables
- Create cloud-ready architecture with stateless services
- Establish environment parity between local and cloud deployments
- Implement proper secret management for containerized applications

## Process Steps

1. **Docker Compose Setup**
   - Create docker-compose.yml file defining frontend service
   - Define backend service with appropriate configurations
   - Set up proper port mappings for service access
   - Configure service dependencies and networking
   - Ensure services can communicate with each other

2. **Environment Variable Management**
   - Externalize `DATABASE_URL` as environment variable
   - Externalize `BETTER_AUTH_SECRET` for authentication
   - Externalize API base URLs for service communication
   - Create .env.example files for documentation
   - Implement proper environment validation

3. **Local Development Parity**
   - Ensure same configuration works locally and in cloud
   - Avoid environment-specific code paths in applications
   - Use consistent service names and networking
   - Implement volume mounts for development convenience
   - Set up hot-reloading for efficient development

4. **Cloud Deployment Readiness**
   - Design stateless backend services for scalability
   - Configure external database connections (Neon PostgreSQL)
   - Ensure frontend can be deployed independently
   - Implement proper health checks and readiness probes
   - Set up resource limits and scaling configurations

5. **Security and Best Practices**
   - Avoid baking secrets into Docker images
   - Use multi-stage builds for optimized images
   - Implement proper logging and monitoring
   - Set up secure networking between services
   - Configure appropriate security contexts

## Output Format

The skill will produce:
- Docker Compose configuration for local development
- Containerized frontend and backend services
- Proper environment variable management
- Cloud-compatible service configurations
- Documentation for deployment procedures
- One-command local startup capability

## Example

**Input:** Set up Docker Compose for a full-stack Todo application with Next.js frontend and FastAPI backend

**Process:**
```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - BETTER_AUTH_SECRET=${BETTER_AUTH_SECRET}
      - ENVIRONMENT=development
    env_file:
      - .env
    depends_on:
      - db
    networks:
      - app-network
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_BASE_URL=http://backend:8000
      - NEXT_PUBLIC_ENVIRONMENT=development
    env_file:
      - .env
    depends_on:
      - backend
    networks:
      - app-network
    restart: unless-stopped

  db:
    image: postgres:15
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=todo_app
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app-network
    restart: unless-stopped

volumes:
  postgres_data:

networks:
  app-network:
    driver: bridge

# .env.example
DATABASE_URL=postgresql://user:password@host:port/database
BETTER_AUTH_SECRET=your-super-secure-jwt-secret-key-here-make-it-long-and-random
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# ./backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ./frontend/Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

RUN npm run build

FROM node:18-alpine

WORKDIR /app

COPY --from=builder /app/package*.json ./
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/next.config.js ./next.config.js

EXPOSE 3000

CMD ["npm", "start"]
```

**Alternative Dockerfile for backend with production optimization:**
```dockerfile
# ./backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

EXPOSE 8000

# Use gunicorn for production
CMD ["gunicorn", "main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

**Alternative Dockerfile for frontend with production optimization:**
```dockerfile
# ./frontend/Dockerfile
FROM node:18-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --only=production

FROM node:18-alpine AS builder
WORKDIR /app
COPY . .
COPY --from=deps /app/node_modules ./node_modules
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/package.json ./package.json

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME=0.0.0.0

CMD ["node", "server.js"]
```

**Usage commands:**
```bash
# Copy environment variables
cp .env.example .env
# Edit .env with actual values

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and start
docker-compose up --build -d
```

**Output:** A properly configured Docker Compose setup that enables one-command local startup with frontend and backend services communicating properly, and cloud-compatible services ready for deployment.

## Implementation Rules

- Do NOT bake secrets into Docker images (use environment variables)
- Do NOT rely on local-only configurations (ensure cloud compatibility)
- Do NOT hardcode ports or URLs in the application code
- Do NOT commit actual .env files to version control
- Do NOT use default passwords or secrets in production
- Ensure proper service dependencies and startup order
- Implement health checks for containerized services
- Use multi-stage builds to optimize image sizes
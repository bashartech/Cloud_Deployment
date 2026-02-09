---
name: "Full-Stack Project Initialization & Monorepo Setup"
description: "Initialize a production-ready full-stack monorepo containing a Next.js frontend and FastAPI backend, structured to support authentication, database access, and secure API communication."
version: "1.0.0"
---

# Full-Stack Project Initialization & Monorepo Setup

## When to Use This Skill

Use this skill when starting a new full-stack web application project that requires:
- A monorepo structure with separate frontend and backend services
- Next.js for the frontend (TypeScript)
- FastAPI for the backend (Python)
- Future integration with Neon PostgreSQL database
- Authentication with Better Auth and JWT
- A multi-user system
- Deployment-ready architecture

This skill ensures Claude Code starts Project 2 with the correct architecture, not an ad-hoc setup.

## Process Steps

1. **Initialize Monorepo Structure**
   - Create root project directory with appropriate name
   - Create `/frontend` and `/backend` directories
   - Set up root-level configuration files (package.json, etc.)

2. **Initialize Frontend Service**
   - Create Next.js application with TypeScript
   - Configure essential files (next.config.js, tsconfig.json)
   - Set up directory structure for pages, components, and API routes
   - Prepare authentication integration points
   - Configure environment variables support

3. **Initialize Backend Service using uv**
   - Create FastAPI project structure with uv
   - Set up main application entry point
   - Configure routing structure and middleware support
   - Prepare for future database and authentication integration
   - Set up environment variable handling

4. **Configure Shared Elements**
   - Root-level package management (if using npm workspaces)
   - Shared configuration files
   - Development scripts for running both services
   - Environment variable structure

5. **Validate Setup**
   - Verify both services can start independently
   - Confirm no runtime errors occur
   - Test basic service functionality

## Output Format

The skill will produce:
- A complete monorepo directory structure
- A functional Next.js frontend ready for development
- A functional FastAPI backend ready for development
- Proper configuration files for both services
- Scripts to run the services independently or together
- Documentation of the project structure

## Example

**Input:** Initialize a full-stack todo application monorepo

**Process:**
```
todo-app-monorepo/
├── package.json (root)
├── pnpm-workspace.yaml (or yarn.lock)
├── .gitignore
├── frontend/
│   ├── package.json
│   ├── next.config.js
│   ├── tsconfig.json
│   ├── .env.example
│   ├── pages/
│   │   ├── _app.tsx
│   │   ├── index.tsx
│   │   └── api/
│   ├── components/
│   ├── public/
│   └── styles/
└── backend/
    ├── requirements.txt
    ├── main.py
    ├── .env.example
    ├── app/
    │   ├── __init__.py
    │   ├── main.py
    │   ├── routers/
    │   └── middleware/
    └── tests/
```

**Output:** A fully configured monorepo with both services ready to start independently, following all architectural requirements specified.

## Implementation Rules

- Do NOT implement authentication logic yet
- Do NOT connect database yet
- Do NOT mix frontend and backend code
- Do NOT add sample users or tasks
- Do NOT implement Phase III+ features
- Do NOT hardcode secrets
- Maintain clean separation of concerns
- Prepare structure to support future Phase II features
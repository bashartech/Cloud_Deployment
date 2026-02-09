---
name: "Monorepo Structure & Spec-Kit–Compatible Project Layout"
description: "Organize the full-stack project into a Spec-Kit–compatible monorepo that allows Claude Code to reason across frontend, backend, and specifications in a single context, ensuring scalability, clarity, and spec-driven automation."
version: "1.0.0"
---

# Monorepo Structure & Spec-Kit–Compatible Project Layout

## When to Use This Skill

Use this skill when you need to:
- Organize a full-stack project into a Spec-Kit-compatible monorepo structure
- Enable Claude Code to reason across frontend, backend, and specifications in a single context
- Create a scalable project architecture with clear separation of concerns
- Implement spec-driven development with organized documentation
- Set up cross-layer visibility for efficient development
- Establish a clean monorepo structure with proper domain separation

This skill ensures scalability, clarity, and spec-driven automation.

## Process Steps

1. **Monorepo Folder Structure Setup**
   - Create root-level frontend and backend folders for clear separation
   - Establish dedicated `/specs` directory for all specifications
   - Create `.spec-kit/config.yaml` configuration file for Spec-Kit
   - Set up proper root-level configuration files

2. **Spec Organization**
   - Create `/specs/features` directory for feature specifications
   - Create `/specs/api` directory for API specifications
   - Create `/specs/database` directory for database specifications
   - Create `/specs/ui` directory for UI specifications
   - Organize specifications by domain and functionality

3. **CLAUDE.md Context Files Creation**
   - Create root CLAUDE.md for overall project overview and context
   - Create frontend CLAUDE.md for UI-specific rules and guidelines
   - Create backend CLAUDE.md for API and server-specific rules
   - Ensure context files provide clear guidance for each layer

4. **Cross-Layer Visibility Configuration**
   - Ensure frontend and backend code are readable in the same workspace
   - Enable cross-cutting edits across different layers of the application
   - Set up proper configuration for tooling to work across the monorepo
   - Create documentation that links related components across layers

5. **Monorepo Configuration**
   - Set up root-level package management (package.json, pyproject.toml, etc.)
   - Configure build tools to work across frontend and backend
   - Establish consistent linting and formatting rules
   - Set up proper dependency management across services

## Output Format

The skill will produce:
- Claude Code–friendly monorepo structure
- Spec-driven navigation with organized specifications
- Clean separation of concerns between frontend and backend
- Properly configured CLAUDE.md context files
- Spec-Kit compatible project layout
- Documentation for project structure and navigation

## Example

**Input:** Organize a full-stack Todo application into a Spec-Kit-compatible monorepo

**Process:**
```
todo-app-monorepo/
├── CLAUDE.md                           # Root project overview
├── package.json                        # Root package management
├── pnpm-workspace.yaml                 # Workspace configuration
├── .gitignore
├── frontend/                          # Frontend service
│   ├── CLAUDE.md                      # Frontend-specific context
│   ├── package.json
│   ├── next.config.js
│   ├── tsconfig.json
│   ├── .env.example
│   ├── pages/
│   ├── components/
│   ├── lib/
│   └── public/
├── backend/                           # Backend service
│   ├── CLAUDE.md                      # Backend-specific context
│   ├── requirements.txt
│   ├── main.py
│   ├── .env.example
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models/
│   │   ├── routers/
│   │   └── auth/
│   └── tests/
├── specs/                             # Specifications directory
│   ├── features/                      # Feature specifications
│   │   ├── authentication.md
│   │   ├── task-management.md
│   │   └── user-management.md
│   ├── api/                           # API specifications
│   │   ├── auth-api.md
│   │   ├── task-api.md
│   │   └── user-api.md
│   ├── database/                      # Database specifications
│   │   ├── schema.md
│   │   ├── migrations.md
│   │   └── indexes.md
│   └── ui/                            # UI specifications
│       ├── components.md
│       ├── layout.md
│       └── user-flows.md
├── .spec-kit/                         # Spec-Kit configuration
│   └── config.yaml
└── docs/                              # Additional documentation
    ├── architecture.md
    └── deployment.md
```

**Root CLAUDE.md:**
```markdown
# Todo App Monorepo

This is a full-stack Todo application monorepo with frontend, backend, and specifications organized for Claude Code.

## Structure
- `frontend/` - Next.js frontend application
- `backend/` - FastAPI backend service
- `specs/` - All project specifications
- `.spec-kit/` - Spec-Kit configuration

## Development
- Frontend: `cd frontend && npm run dev`
- Backend: `cd backend && uvicorn main:app --reload`
```

**Frontend CLAUDE.md:**
```markdown
# Frontend Context

Next.js frontend built with TypeScript and React.

## Tech Stack
- Next.js 14+
- TypeScript
- Tailwind CSS
- Better Auth for authentication

## UI Guidelines
- Use consistent component patterns
- Follow accessibility standards
- Maintain responsive design
```

**Backend CLAUDE.md:**
```markdown
# Backend Context

FastAPI backend with PostgreSQL database and JWT authentication.

## Tech Stack
- FastAPI
- SQLModel ORM
- PostgreSQL (Neon)
- Better Auth integration

## API Guidelines
- Follow REST conventions
- Use consistent error responses
- Implement proper authentication
```

**.spec-kit/config.yaml:**
```yaml
project:
  name: "Todo App"
  type: "full-stack"
  languages:
    - "TypeScript"
    - "Python"
  frameworks:
    - "Next.js"
    - "FastAPI"

specs:
  base_path: "./specs"
  categories:
    - "features"
    - "api"
    - "database"
    - "ui"
```

**Output:** A properly structured Spec-Kit-compatible monorepo that enables Claude Code to reason across frontend, backend, and specifications in a single context with clear separation of concerns and organized specifications.

## Implementation Rules

- Do NOT split the repository into separate repos (maintain monorepo structure)
- Do NOT flatten specifications (keep organized by domain)
- Do NOT mix frontend and backend code in the same directories
- Do NOT create circular dependencies between layers
- Do NOT place configuration files in inappropriate locations
- Ensure proper separation of concerns across all layers
- Maintain consistent naming conventions across the monorepo
- Keep CLAUDE.md files updated with current project context
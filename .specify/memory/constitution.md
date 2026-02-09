<!-- SYNC IMPACT REPORT
Version change: 1.1.0 → 2.0.0
Modified principles:
- Principle 1: Phase Continuity Rule (updated to include Phase 5 continuity)
- Principle 2: Spec-Driven Development (Mandatory) (updated for Phase 5)
- Principle 3: Stateless Architecture (updated for event-driven architecture)
- Principle 4: Separation of Responsibilities (updated for Dapr and Kafka)
- Principle 5: Database Usage Rules (updated for event-driven patterns)
- Principle 6: Authentication & User Isolation (maintained)
Added sections: Event-Driven Architecture, Dapr Integration, Kafka Integration, Advanced Features, Cloud Deployment
Removed sections: None
Templates requiring updates:
- .specify/templates/plan-template.md ⚠ pending
- .specify/templates/spec-template.md ⚠ pending
- .specify/templates/tasks-template.md ⚠ pending
Follow-up TODOs: None
-->
# Todo AI Chatbot Constitution - Phases 2-5

## Core Principles

### Phase Continuity Rule
Phases 3, 4, and 5 are continuations and extensions of Phase 2 — NOT rewrites. Phase 2 codebase must be reused, existing database schema for tasks must not be recreated, authentication and authorization logic must remain unchanged, and features from previous phases are preserved. Do NOT create the application from scratch, duplicate task tables or models, or bypass existing auth logic. Instead, extend Phase 2 with AI, MCP, chatbot, event-driven architecture, and cloud deployment capabilities.

### Spec-Driven Development (Mandatory)
All work in Phases 3-5 must follow this strict order: 1. Write a specification, 2. Validate the specification, 3. Create an execution plan, 4. Break the plan into atomic tasks, 5. Inspect existing codebase (file & folder structure), 6. Implement changes, 7. Test and validate, 8. Fix errors before proceeding. No implementation is allowed without an approved spec. For Phase 5, all Kafka and Dapr integrations must be specified before implementation.

### Stateless Architecture with Event-Driven Extensions
Services remain stateless between requests where possible. Conversation context is persisted in the database. MCP tools are fully stateless. For event-driven operations, services publish events to Kafka and consume from Kafka for background processing. This guarantees scalability, resilience, and reproducibility while enabling advanced features like recurring tasks and reminders.

### Separation of Responsibilities
Frontend handles UI, ChatKit, and user interaction. FastAPI Backend manages auth, chat orchestration, and conversation storage. AI Agent performs reasoning and decision-making. MCP Server handles task operations only. Kafka handles event streaming and decoupling. Dapr provides distributed application runtime services (Pub/Sub, State, Bindings, Secrets, Service Invocation). Database provides persistent state.

### Database Usage Rules
A single Neon PostgreSQL database is used. Existing Task table from Phase 2 is reused with extended schema for advanced features (priority, tags, due_date, is_recurring, reminder_at, etc.). Phase 3 introduced Conversation and Message tables. Phase 5 maintains these schemas while supporting event-driven updates through Kafka and Dapr state management.

### Authentication & User Isolation
All requests are authenticated using JWT. user_id is extracted from verified tokens. AI and MCP tools act on behalf of the authenticated user. MCP tools must always scope DB queries by user_id. At no point may AI, MCP tools, or background services bypass authentication. Event-driven services maintain user isolation through proper event metadata.

## Additional Constraints

### MCP & AI Constraints
MCP Server must be stateless with no conversation memory, no authentication logic, and only task operations. AI Agent has no direct database access, uses MCP tools exclusively, and has behavior defined by spec. MCP tools must support all advanced features (due dates, priorities, tags, recurring tasks, reminders).

### Event-Driven Architecture
All task operations publish events to Kafka topics (task-events). Reminder system consumes from Kafka to send notifications at scheduled times. Recurring task engine consumes from Kafka to create next occurrences when tasks are completed. Real-time sync uses Kafka for broadcasting updates to connected clients. This enables loose coupling and scalable processing.

### Dapr Integration
Dapr provides distributed application runtime services: Pub/Sub for Kafka integration, State management for conversation persistence, Bindings for cron jobs (reminders), Secrets for credential management, and Service Invocation for inter-service communication. Applications interact with Dapr sidecars via HTTP/gRPC APIs rather than directly with infrastructure.

### Kafka Integration
Kafka topics: task-events (for all CRUD operations), reminders (for scheduled notifications), task-updates (for real-time sync). Events follow standardized schema with event_type, task_id, task_data, user_id, and timestamp. Services publish to Kafka via Dapr pub/sub component rather than direct Kafka clients.

### Advanced Features
Application supports: Recurring Tasks (with configurable intervals), Due Dates & Reminders (with notification system), Priorities (low/medium/high), Tags (for categorization), Search, Filter, and Sort capabilities. These features are accessible through MCP tools and exposed via the AI chat interface.

### Technology Stack
Frontend: OpenAI ChatKit, Next.js, Tailwind CSS. Backend: FastAPI, OpenAI Agents SDK, Official MCP SDK. Database & ORM: Neon Serverless PostgreSQL, SQLModel. Authentication: Better Auth, JWT. Event Streaming: Kafka/Redpanda. Distributed Runtime: Dapr. Container Orchestration: Kubernetes (Minikube/DOKS/GKE/AKS). Package Management: Helm.

### Cloud Deployment
Applications must be deployable to Kubernetes clusters with Dapr and Kafka integration. Deployment uses Helm charts with environment-specific configurations. CI/CD pipelines automate testing and deployment. Monitoring and logging are configured for production environments.

## Development Workflow

### Enforcement Rule
Any future spec, task, or code that violates this constitution must be rejected or refactored before proceeding. This constitution is binding for all Phase 3-5 development work. Phases 3-5 build intelligence, event-driven architecture, and cloud capabilities on top of a solid system, not beside it and not instead of it.

## Governance

This constitution defines the foundational rules, boundaries, and guiding principles for Phases 2-5 of the Hackathon II Todo Application. This document ensures that all future specifications, plans, tasks, and implementations remain consistent with prior work, do not re-implement or break previous phases, follow Spec-Driven Development (SDD), and adhere strictly to hackathon requirements. This file acts as the single source of truth for architectural and process decisions in Phases 2-5. All PRs/reviews must verify compliance.

**Version**: 2.0.0 | **Ratified**: 2026-01-07 | **Last Amended**: 2026-02-08
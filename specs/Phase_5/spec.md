# Phase 5 Specification: Advanced Cloud Deployment

## Overview
Phase 5 focuses on production-grade deployment and architectural evolution of the Todo Chatbot system. All functional features (basic, intermediate, and advanced task features) are already implemented in earlier phases. This phase upgrades the system to a cloud-native, event-driven microservices architecture using Kafka and Dapr, and deploys it to production Kubernetes. The goal is to demonstrate scalability, decoupling, reliability, and operational maturity, not feature development.

## Objectives
### Architectural Objectives
- Convert the system to a fully event-driven architecture
- Decouple services using Kafka-compatible messaging
- Abstract infrastructure using Dapr
- Separate responsibilities into independent services
- Enable horizontal scalability and fault isolation

### Deployment Objectives
- Deploy the complete system locally on Minikube
- Deploy the same system to production Kubernetes
- Use Redpanda Cloud as managed Kafka
- Ensure zero code changes between local and cloud environments

### Operational Objectives
- Introduce CI/CD using GitHub Actions
- Enable monitoring, logging, and health checks
- Secure secrets and credentials properly
- Ensure production readiness

## System Architecture
### Architectural Style
The system MUST follow:
- Microservices architecture
- Event-driven communication
- Sidecar-based runtime abstraction (Dapr)
- Each service runs as a separate Kubernetes deployment with its own Dapr sidecar.

### Communication Patterns
| Type | Usage |
|------|-------|
| Synchronous | Frontend → Chat API (via Dapr service invocation) |
| Asynchronous | Inter-service workflows via Kafka events |
| Real-time | WebSocket broadcasting using event streams |

## Event-Driven Architecture
### Core Rules
- Services MUST NOT call each other synchronously for background work
- Services MUST publish events instead of triggering logic directly
- Event producers MUST NOT depend on consumers
- Event consumers MUST be restartable and idempotent
- Events MUST be immutable

### Kafka Topics (Mandatory)
| Topic | Responsibility |
|-------|---------------|
| task-events | All task lifecycle events |
| reminders | Reminder scheduling and triggers |
| task-updates | Real-time client synchronization |

### Event Lifecycle
#### Task Lifecycle Events
- Published by Chat API
- Consumed by:
  - Recurring Task Service
  - Audit Service

#### Reminder Events
- Published when tasks include due/reminder metadata
- Consumed by Notification Service

#### Update Events
- Published on task changes
- Consumed by WebSocket / Realtime Service

## Event Schema Requirements
### General Rules
- All events MUST be JSON
- Events MUST include: event_type, entity identifier, user identifier, timestamp
- Schema evolution MUST be backward compatible

### Task Event Schema (task-events)
```json
{
  "event_type": "created | updated | completed | deleted",
  "task_id": 123,
  "task_data": { "...existing task fields..." },
  "user_id": "user_123",
  "timestamp": "2026-02-08T10:30:00Z"
}
```

### Reminder Event Schema (reminders)
```json
{
  "task_id": 123,
  "remind_at": "2026-02-10T17:30:00Z",
  "user_id": "user_123"
}
```

## Dapr Integration Requirements
All infrastructure dependencies MUST be handled via Dapr building blocks.

### Mandatory Dapr Building Blocks
| Block | Purpose |
|-------|---------|
| Pub/Sub | Kafka abstraction |
| State Management | Conversation & transient state |
| Bindings (Cron) | Scheduled reminder triggers |
| Service Invocation | Service-to-service HTTP |
| Secrets | Credential management |

### Pub/Sub Rules
- Kafka SDKs MUST NOT be imported in application code
- Publishing and consuming MUST occur via Dapr APIs
- Consumer groups MUST be service-specific

### State Management Rules
- State storage MUST be optional and replaceable
- State operations MUST be idempotent
- State keys MUST be user-scoped

### Cron Binding Rules
- All scheduled operations MUST use Dapr cron bindings
- No system cron jobs allowed
- Cron handlers MUST tolerate retries

### Secrets Management Rules
- Secrets MUST NOT be hardcoded
- Secrets MUST NOT be committed to Git
- Secrets MUST be accessed via Dapr secret store
- Kubernetes Secrets are the default backend

## Service Responsibilities
### Chat API Service
#### Responsibilities
- Handle user requests
- Persist task data
- Publish task-related events
- Interface with MCP tools

#### Restrictions
- MUST NOT perform notification logic
- MUST NOT handle recurring task generation

### Notification Service
#### Responsibilities
- Consume reminder events
- Send notifications (email, push, logs)

#### Restrictions
- MUST NOT access task database
- MUST rely exclusively on events

### Recurring Task Service
#### Responsibilities
- Consume task completion events
- Generate next task instance

#### Restrictions
- MUST operate asynchronously
- MUST be idempotent

### Audit Service
#### Responsibilities
- Consume all task events
- Store immutable audit logs

### Realtime / WebSocket Service (Recommended)
#### Responsibilities
- Consume task-update events
- Broadcast changes to connected clients

## Deployment Requirements
### Local Deployment (Minikube)
- Minikube MUST be the local Kubernetes runtime
- Dapr MUST be installed in Kubernetes mode
- Redpanda MUST run locally
- All services MUST be deployable via Helm

### Cloud Deployment
Must deploy to:
- DigitalOcean Kubernetes (DOKS), OR
- Google Kubernetes Engine (GKE), OR
- Azure Kubernetes Service (AKS)

- Redpanda Cloud MUST be used for Kafka
- No application code changes allowed between environments

## CI/CD Requirements
### GitHub Actions Pipeline
Pipeline MUST:
- Build Docker images
- Run lint and tests
- Push images to container registry
- Deploy to Kubernetes via Helm

Manual production deployments are discouraged.

## Observability Requirements
### Logging
- Structured logs preferred
- Log event publishing and consumption
- Log failures with correlation identifiers

### Monitoring
Minimum requirements:
- Pod health & readiness
- Service availability
- Kafka consumer activity

## Security Requirements
- Secure service communication
- Secret isolation via Dapr
- User-level data isolation in events
- No cross-tenant data leakage

## Constraints
- Existing APIs MUST remain unchanged
- Kafka MUST be used for asynchronous workflows
- Dapr MUST be used for infrastructure abstraction
- Helm MUST be used for deployment packaging

## Acceptance Criteria
Phase 5 is complete when:
- System runs on Minikube with Dapr + Kafka
- System runs on cloud Kubernetes without code changes
- Event-driven flows are demonstrable
- Services are decoupled and independently scalable
- CI/CD pipeline deploys successfully
- Logs and health checks are available

## Guiding Principle
"Phase 5 is about how the system runs, not what features it has."
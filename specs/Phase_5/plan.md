# Phase 5 Implementation Plan

## Overview
This plan outlines the implementation steps for converting the Todo Chatbot system to a cloud-native, event-driven architecture using Kafka and Dapr, and deploying it to production Kubernetes. The plan follows the detailed execution phases from the project documentation.

## Phase 5.1 – Architecture Finalization
### Goals
- Finalize event-driven service boundaries
- Define event contracts and ownership
- Define Dapr usage per service

### Tasks
- Identify participating services:
  - Task Service
  - Reminder Service
  - Recurrence Engine
  - Notification Service
  - WebSocket Gateway
  - Audit Service
- Define synchronous vs asynchronous flows
- Decide which events are fire-and-forget
- Decide which events require retries / DLQ

### Deliverables
- Architecture diagram (services + Kafka + Dapr)
- Event flow diagram
- Service responsibility document

## Phase 5.2 – Event Model & Kafka Setup
### Goals
- Standardize event schema
- Prepare Kafka topics on Redpanda Cloud

### Tasks
- Define base event schema:
```json
{
  "event_id": "uuid",
  "event_type": "TASK_CREATED | TASK_UPDATED | TASK_COMPLETED | TASK_DELETED",
  "task_id": "string",
  "user_id": "string",
  "payload": {},
  "metadata": {
    "source": "task-service",
    "version": "v1"
  },
  "timestamp": "ISO-8601"
}
```
- Define topics:
  - task-events
  - task-reminders
  - task-recurrence
  - task-updates
  - task-audit
- Create Redpanda Cloud cluster
- Store Kafka credentials in Kubernetes secrets

### Deliverables
- Event schema version v1
- Kafka topic list
- Secrets structure for Kafka auth

## Phase 5.3 – Dapr Integration Layer
### Goals
- Introduce Dapr sidecars without breaking existing APIs
- Use Dapr as the abstraction layer

### Tasks
- Install Dapr on Minikube
- Configure Dapr components:
  - Pub/Sub (Kafka)
  - State Store (Redis or Postgres)
  - Secret Store (Kubernetes)
  - Bindings (cron)
- Create Dapr component YAMLs:
  - kafka-pubsub.yaml
  - statestore.yaml
  - cron-reminder.yaml
- Update services to:
  - Publish events via Dapr
  - Subscribe to topics via Dapr

### Deliverables
- Working Dapr-enabled local environment
- All services running with sidecars
- Verified pub/sub message flow

## Phase 5.4 – Advanced Feature: Due Dates & Reminders
### Goals
- Fully async reminder system
- No blocking logic in task service

### Tasks
- On task create/update:
  - Publish TASK_DUE_SET or TASK_REMINDER_SET event
- Reminder Service:
  - Consume reminder events
  - Persist reminder state
- Cron Binding:
  - Periodically check upcoming reminders
  - Emit REMINDER_TRIGGERED events
- Notification Service:
  - Consume reminder-triggered events
  - Send notifications (email / in-app / push)

### Deliverables
- Reminder flow end-to-end
- Reliable retries
- Idempotent reminder handling

## Phase 5.5 – Advanced Feature: Recurring Tasks Engine
### Goals
- Automatic task regeneration
- Event-driven recurrence logic

### Tasks
- Extend task model:
  - recurrence_type (daily / weekly / monthly)
  - recurrence_interval
  - recurrence_end (optional)
- On task completion:
  - Publish TASK_COMPLETED
- Recurrence Engine:
  - Consume completion events
  - Calculate next occurrence
  - Create new task via service invocation
  - Publish TASK_RECURRED

### Deliverables
- Recurring tasks work without cron in core service
- Clear audit trail of generated tasks

## Phase 5.6 – Real-Time Sync & Audit
### Goals
- Real-time UI updates
- Immutable event history

### Tasks
- WebSocket Service:
  - Subscribe to task-updates
  - Push updates to connected clients
- Audit Service:
  - Subscribe to all task-related topics
  - Persist immutable event logs
  - Ensure user-level isolation

### Deliverables
- Live UI updates without polling
- Full task history available for debugging

## Phase 5.7 – Kubernetes & Helm Deployment
### Goals
- Production-grade deployment

### Tasks
- Write Helm charts:
  - Backend services
  - Dapr components
  - Ingress
- Configure:
  - Resource limits
  - Liveness/readiness probes
- Deploy to Minikube
- Validate scaling and failure recovery

### Deliverables
- One-command Helm deployment
- Fully working Minikube environment

## Phase 5.8 – Cloud Deployment
### Goals
- Production readiness

### Tasks
- Choose cloud provider (DO / GCP / Azure)
- Provision Kubernetes cluster
- Install Dapr
- Configure external secrets
- Deploy Helm charts
- Verify Redpanda Cloud connectivity

### Deliverables
- Publicly reachable production cluster
- Secure secret handling
- Stable event processing

## Phase 5.9 – CI/CD Pipeline
### Goals
- Automated, safe deployments

### Tasks
- GitHub Actions pipeline:
  - Lint & test
  - Build Docker images
  - Push to registry
  - Deploy via Helm
- Environment separation (dev / prod)

### Deliverables
- Fully automated deployment
- Rollback capability

## Phase 5.10 – Monitoring, Logging & Hardening
### Goals
- Observability and resilience

### Tasks
- Metrics:
  - Dapr metrics
  - Kafka lag
- Logging:
  - Centralized logs
- Alerts:
  - Failed reminders
  - Event processing errors
- Load & failure testing

### Deliverables
- Dashboards
- Alerts
- Documented failure scenarios

## Final Outputs
- Event-driven advanced feature system
- Fully Dapr-powered microservices
- Kubernetes + Helm deployment
- Cloud-ready production setup
- Observable, scalable, and resilient architecture
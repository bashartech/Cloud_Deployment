
✦ Detailed Steps for Phase 5 Implementation

    Phase 1: Code - Event-Driven Architecture with Kafka and Dapr

    Step 1.1: Infrastructure Setup
     1. Install Dapr CLI:
        - Download and install Dapr CLI for Windows
        - Verify installation with dapr --version
        - Initialize Dapr with dapr init for local development

     2. Set up Local Kafka/Redpanda:
        - Create docker-compose.kafka.yml with Redpanda container
        - Configure Redpanda with proper broker addresses
        - Create all required topics: task-events, reminders, task-updates, task-recurrence, task-audit
        - Test Kafka connectivity with rpk command-line tool

     3. Create Dapr Components Directory:
        - Create dapr-components/ directory
        - Set up proper file structure for Dapr component configurations

     4. Define Event Schema:
        - Create backend/models/event_schema.py
        - Define base event structure with required fields: event_type, task_id, user_id, timestamp, task_data
        - Create specific schemas for different event types (TASK_CREATED, TASK_UPDATED, etc.)

     5. Update Backend Dependencies:
        - Add Dapr SDK to backend/requirements.txt
        - Add Kafka client libraries if needed (though Dapr will abstract this)

    Step 1.2: Dapr Component Configuration (Full Dapr Capabilities)
     1. Pub/Sub Component:
        - Create dapr-components/pubsub-kafka.yaml
        - Configure Kafka brokers, consumer groups, and serialization
        - Set up proper metadata for Redpanda compatibility

     2. State Management Component:
        - Create dapr-components/state-postgres.yaml
        - Configure PostgreSQL connection string
        - Set up proper state store configuration for task caching and conversation state

     3. Cron Binding Component:
        - Create dapr-components/cron-reminders.yaml
        - Configure cron schedule for periodic reminder checks (e.g., "/5    *")
        - Set up proper binding configuration

     4. Secret Store Component:
        - Create dapr-components/secrets-k8s.yaml
        - Configure Kubernetes secret store for local development
        - Set up proper authentication and access controls

     5. Test and Deploy Dapr Components:
        - Test each component individually
        - Deploy components to Minikube with kubectl apply -f dapr-components/

    Step 1.3: Event Publishing Infrastructure
     1. Initialize Dapr Client:
        - Update backend/main.py to initialize Dapr client
        - Add proper error handling for Dapr initialization

     2. Create Event Publisher Utility:
        - Create backend/utils/event_publisher.py
        - Implement functions to publish events via Dapr pub/sub
        - Add proper error handling and retry logic

     3. Modify Task Routes:
        - Update backend/routes/tasks.py to publish events after each operation
        - TASK_CREATED after task creation
        - TASK_UPDATED after task updates
        - TASK_COMPLETED after task completion
        - TASK_DELETED after task deletion
        - Include proper metadata (user_id, timestamp, task_data)

     4. Test Event Publishing:
        - Verify events are published to Kafka topics via Dapr
        - Test error handling when Kafka is unavailable

    Step 1.4: Notification Service for Reminders (Advanced Feature: Due Dates & Reminders)
     1. Create Service Structure:
        - Create backend/notification_service/ directory
        - Create backend/notification_service/main.py
        - Set up FastAPI application with Dapr integration

     2. Implement Event Consumer:
        - Subscribe to reminders Kafka topic via Dapr
        - Process reminder events with proper user isolation
        - Implement idempotent processing to prevent duplicates

     3. Create Notification Mechanism:
        - Implement logging for MVP (can be extended to email/push later)
        - Add proper error handling for notification failures
        - Include correlation IDs for tracing

     4. Implement Cron Handler:
        - Create endpoint that Dapr cron binding can call
        - Check for upcoming reminders periodically
        - Publish reminder events to notification service

     5. Test Reminder Flow:
        - Create tasks with due dates and reminders
        - Verify reminder events are published and consumed
        - Test reminder cancellation when tasks are updated/deleted

    Step 1.5: Recurring Task Engine (Advanced Feature: Recurring Tasks)
     1. Create Service Structure:
        - Create backend/recurrence_engine/ directory
        - Create backend/recurrence_engine/main.py
        - Set up FastAPI application with Dapr integration

     2. Implement Event Consumer:
        - Subscribe to task-events Kafka topic via Dapr
        - Filter for TASK_COMPLETED events for recurring tasks
        - Process only tasks that have recurrence settings

     3. Implement Recurrence Logic:
        - Calculate next occurrence based on recurrence_type (daily/weekly/monthly)
        - Handle recurrence intervals and end conditions
        - Preserve original task properties for new instances

     4. Create New Task Generation:
        - Use Dapr service invocation to create new tasks
        - Publish TASK_RECURRED events for audit trail
        - Handle recurrence end conditions properly

     5. Test Recurring Tasks:
        - Create recurring tasks with different patterns
        - Complete recurring tasks and verify new instances are created
        - Test recurrence end conditions

    Step 1.6: Audit and Real-Time Sync Services
     1. Audit Service:
        - Create backend/audit_service/ directory and main application
        - Subscribe to all task event topics
        - Store immutable event logs with user isolation
        - Implement proper retention policies

     2. WebSocket Service:
        - Create backend/websocket_service/ directory and main application
        - Subscribe to task-updates Kafka topic
        - Manage WebSocket connections and broadcasting
        - Implement user-specific filtering for real-time updates

     3. Test Services:
        - Verify audit logs are created for all operations
        - Test real-time updates to connected clients
        - Validate user isolation in both services

    Step 1.7: MCP Tools Enhancement for Advanced Features
     1. Update MCP Tools:
        - Modify mcp-server/src/tools/task-tools.ts
        - Update add_task to accept advanced fields (due_date, priority, tags, recurrence)
        - Update update_task to modify advanced fields
        - Add list_tasks with filtering by priority/tags/due_date
        - Implement sort_tasks functionality

     2. Update Event Publishing:
        - Ensure MCP tools publish appropriate events via Dapr
        - Maintain backward compatibility with existing functionality

     3. Test Enhanced Tools:
        - Verify all advanced features work through MCP tools
        - Test event publishing from MCP tools

    Step 1.8: Integration and Testing
     1. Full Integration Test:
        - Test complete event-driven flow from task creation to all consumers
        - Verify user isolation across all services
        - Test error handling and retry mechanisms

     2. Load Testing:
        - Simulate concurrent users and tasks
        - Test event processing under load
        - Verify system stability

     3. Validation:
        - Ensure all existing functionality remains intact
        - Verify advanced features work correctly

    Phase 2: Local Deployment on Minikube with Full Dapr Capabilities

    Step 2.1: Kubernetes and Helm Preparation
     1. Update Helm Charts:
        - Modify helm-charts/todo-chatbot/ to include new services
        - Add deployments for notification, recurrence, audit, and WebSocket services
        - Add Dapr annotations to all service deployments
        - Configure resource limits and health checks

     2. Prepare Kubernetes Templates:
        - Create service definitions for new services
        - Set up proper networking and load balancing
        - Configure Dapr sidecar annotations

    Step 2.2: Local Deployment Execution
     1. Deploy to Minikube:
        - Install Dapr on Minikube cluster
        - Deploy Dapr components
        - Deploy all services using Helm
        - Verify all services are running

     2. Validate Functionality:
        - Test complete application functionality
        - Validate event-driven flows in Kubernetes
        - Verify Full Dapr capabilities: Pub/Sub, State, Bindings, Secrets, Service Invocation
        - Test scaling and failure recovery

    Phase 3: Cloud Deployment (DigitalOcean) with Full Dapr

    Step 3.1: Cloud Infrastructure Setup
     1. Choose and Provision Cloud:
        - Create DigitalOcean account and Kubernetes cluster (DOKS)
        - Configure kubectl to connect to DOKS
        - Set up Redpanda Cloud account and cluster
        - Configure Redpanda Cloud connection

     2. Set Up Security:
        - Create Kubernetes secrets for cloud credentials
        - Configure cloud-specific networking
        - Set up security policies

    Step 3.2: Cloud Deployment Execution
     1. Deploy to Cloud:
        - Create cloud-specific Helm values
        - Deploy all services to DigitalOcean Kubernetes
        - Configure external access and load balancing
        - Validate functionality in cloud environment

     2. Validate Full Dapr Capabilities:
        - Verify Pub/Sub works with Redpanda Cloud
        - Verify State management with cloud PostgreSQL
        - Verify Bindings (cron) functionality
        - Verify Secrets management
        - Verify Service Invocation

    Step 3.3: CI/CD Pipeline and Monitoring
     1. GitHub Actions Setup:
        - Create workflow for automated builds
        - Add Docker image building and pushing to registry
        - Implement automated testing
        - Set up deployment to DigitalOcean

     2. Monitoring and Logging:
        - Configure centralized logging
        - Set up monitoring and alerting
        - Document deployment procedures

    This detailed workflow ensures that every aspect of the requirements is met accurately, with proper attention to advanced features, event-driven architecture, Dapr    
    integration, and deployment to both local and cloud environments.

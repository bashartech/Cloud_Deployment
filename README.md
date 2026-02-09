# Todo AI Chatbot - Complete Project Documentation

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Frontend](#frontend)
- [Backend](#backend)
- [Event-Driven Services](#event-driven-services)
- [MCP Server](#mcp-server)
- [Deployment](#deployment)
- [Development Setup](#development-setup)
- [Production Deployment](#production-deployment)
- [Troubleshooting](#troubleshooting)

## Overview

The Todo AI Chatbot is a sophisticated task management application that combines natural language processing with event-driven architecture. It extends traditional todo applications with AI-powered task management capabilities, real-time synchronization, automated notifications, and recurring tasks.

### Key Features
- **Natural Language Processing**: AI-powered chat interface for task management
- **Event-Driven Architecture**: Scalable microservices with Dapr
- **Real-Time Updates**: WebSocket-based live synchronization
- **Automated Notifications**: Reminder system for task deadlines
- **Recurring Tasks**: Automated task generation based on patterns
- **Audit Trails**: Immutable logs of all task operations
- **Secure Authentication**: JWT-based user isolation

## Architecture

The application follows a modern microservices architecture with the following components:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   MCP Server     │    │   Backend       │
│   (Next.js)     │◄──►│   (Node.js)      │◄──►│   (FastAPI)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────────────┐
                    │   Event-Driven Services │
                    │   • Notification        │
                    │   • Recurrence Engine   │
                    │   • Audit Service       │
                    │   • WebSocket Service   │
                    └─────────────────────────┘
```

### Technology Stack
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS, ChatKit UI
- **Backend**: FastAPI, Python 3.11, SQLModel ORM
- **Database**: Neon PostgreSQL (cloud) / PostgreSQL (local)
- **Authentication**: Better Auth with JWT
- **AI Integration**: OpenAI Agent SDK with MCP tools
- **Event Streaming**: Apache Kafka / Redpanda
- **Service Mesh**: Dapr (Distributed Application Runtime)
- **Containerization**: Docker
- **Orchestration**: Kubernetes with Helm
- **Deployment**: Minikube (local), Cloud providers (production)

## Frontend

The frontend is built with Next.js 14 and provides a modern, responsive user interface with AI chat capabilities.

### Features
- **AI Chat Interface**: Natural language task management
- **Real-time Updates**: Live synchronization across devices
- **Responsive Design**: Works on desktop and mobile
- **Secure Authentication**: User login/logout with JWT
- **Task Management**: Create, update, delete, and complete tasks
- **Advanced Filtering**: Sort and filter tasks by priority, tags, due date

### Directory Structure
```
frontend/
├── app/                 # Next.js app router pages
├── components/          # Reusable UI components
├── lib/                # Utility functions
├── public/             # Static assets
├── services/           # API service wrappers
├── types/              # TypeScript type definitions
├── middleware.ts       # Authentication middleware
└── next.config.js      # Next.js configuration
```

### Environment Variables
```env
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_BETTER_AUTH_SECRET=your_auth_secret
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

## Backend

The backend is built with FastAPI and implements the core business logic with event-driven architecture.

### Features
- **RESTful API**: Task management endpoints
- **Dapr Integration**: Service mesh capabilities
- **Event Publishing**: Kafka-based event streaming
- **Database Operations**: CRUD operations with SQLModel
- **Authentication**: JWT-based user isolation
- **Health Checks**: Ready and liveness endpoints

### Directory Structure
```
backend/
├── models/             # SQLAlchemy/SQLModel models
├── crud/               # Database operations
├── routes/             # API route handlers
├── services/           # Business logic
├── middleware/         # Request/response middleware
├── notification_service/ # Notification service
├── recurrence_engine/   # Recurring task engine
├── audit_service/      # Audit logging service
├── websocket_service/  # Real-time sync service
├── chat_agents/        # AI agent implementations
├── db.py               # Database configuration
├── main.py             # Main application entrypoint
└── requirements.txt    # Python dependencies
```

### Environment Variables
```env
DATABASE_URL=postgresql://user:pass@localhost/db
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_BETTER_AUTH_SECRET=your_auth_secret
GEMINI_API_KEY=your_gemini_api_key
MCP_SERVER_URL=http://localhost:3001
```

## Event-Driven Services

The application includes four specialized services that operate independently but communicate via events:

### 1. Notification Service
- Handles task reminder notifications
- Supports multiple delivery channels (email, push, SMS)
- Implements idempotent processing to prevent duplicates
- Automatically cancels notifications when tasks are updated

### 2. Recurrence Engine
- Generates recurring tasks based on completion events
- Supports daily, weekly, monthly, and yearly patterns
- Handles end conditions (by date or count)
- Publishes audit events for transparency

### 3. Audit Service
- Maintains immutable logs of all task operations
- Provides user-isolated audit trails
- Ensures compliance and accountability
- Tracks all changes to task data

### 4. WebSocket Service
- Manages real-time connections for live updates
- Broadcasts task changes to relevant users
- Implements user-specific filtering
- Handles connection management and scaling

## MCP Server

The Model Context Protocol (MCP) server acts as an intermediary between the AI agents and the backend services.

### Features
- **Protocol Implementation**: MCP-compliant server
- **Tool Integration**: Custom tools for task management
- **Authentication**: Secure communication with backend
- **Event Forwarding**: Relays events to appropriate services

### Directory Structure
```
mcp-server/
├── src/
│   ├── tools/          # MCP tool implementations
│   └── server.js       # MCP server entrypoint
├── package.json        # Node.js dependencies
└── tsconfig.json       # TypeScript configuration
```

## Deployment

### Local Development Setup

#### Prerequisites
- Node.js 18+
- Python 3.9+
- Docker Desktop
- Minikube
- kubectl
- Helm
- Dapr CLI

#### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd todo-chatbot

# Start Minikube
minikube start --memory=8192 --cpus=4

# Install Dapr
dapr init -k --wait

# Set Docker environment to Minikube
eval $(minikube docker-env)

# Build Docker images
docker build -t todo-services -f Dockerfile.services --target backend .
docker build -t todo-frontend -f Dockerfile.frontend .

# Create secrets for Neon database
kubectl create secret generic todo-backend-env \
  --from-literal=DATABASE_URL="your_neon_db_url" \
  --from-literal=BETTER_AUTH_URL="http://localhost:3000" \
  --from-literal=BETTER_AUTH_SECRET="your_auth_secret" \
  --from-literal=GEMINI_API_KEY="your_gemini_api_key"

kubectl create secret generic todo-frontend-env \
  --from-literal=NEXT_PUBLIC_BETTER_AUTH_URL="http://localhost:3000" \
  --from-literal=NEXT_PUBLIC_BACKEND_URL="http://localhost:8000"

# Deploy Dapr components
kubectl apply -f dapr-components/

# Deploy infrastructure (Kafka)
kubectl apply -f k8s-kafka-only.yaml

# Wait for Kafka to be ready
kubectl wait --for=condition=ready pod -l app=kafka --timeout=300s

# Deploy application with Helm
helm upgrade --install todo-chatbot ./helm-charts/todo-chatbot/ --values ./helm-charts/todo-chatbot/values.yaml

# Expose services
kubectl expose deployment todo-chatbot-frontend --type=NodePort --port=3000 --name=frontend-service
kubectl expose deployment todo-chatbot-backend --type=NodePort --port=8000 --name=backend-service

# Get service URLs
minikube service frontend-service --url
minikube service backend-service --url
```

### Production Deployment

For production deployment, the application can be deployed to cloud platforms like AWS, Azure, or GCP with the following considerations:

#### AWS EKS Deployment
```bash
# Create EKS cluster
eksctl create cluster --name todo-chatbot-cluster --nodes 3

# Install Dapr on EKS
dapr init -k --runtime-version=1.9.0

# Deploy to EKS using the same Helm charts
helm upgrade --install todo-chatbot ./helm-charts/todo-chatbot/ \
  --values ./helm-charts/todo-chatbot/values-prod.yaml
```

#### Google Cloud Platform (GKE)
```bash
# Create GKE cluster
gcloud container clusters create todo-chatbot-cluster --num-nodes=3

# Get credentials
gcloud container clusters get-credentials todo-chatbot-cluster

# Install Dapr
dapr init -k

# Deploy application
helm upgrade --install todo-chatbot ./helm-charts/todo-chatbot/ \
  --values ./helm-charts/todo-chatbot/values-prod.yaml
```

#### Azure AKS
```bash
# Create AKS cluster
az aks create --resource-group myResourceGroup --name todoChatbotCluster --node-count 3

# Get credentials
az aks get-credentials --resource-group myResourceGroup --name todoChatbotCluster

# Install Dapr
dapr init -k

# Deploy application
helm upgrade --install todo-chatbot ./helm-charts/todo-chatbot/ \
  --values ./helm-charts/todo-chatbot/values-prod.yaml
```

### Dapr Configuration

The application leverages multiple Dapr building blocks:

#### Pub/Sub Component (Kafka)
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "kafka:9092"
  - name: consumerGroup
    value: "todo-chatbot"
```

#### State Store Component (PostgreSQL)
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.postgresql
  version: v1
  metadata:
  - name: connectionString
    secretKeyRef:
      name: postgresql-connection-string
```

#### Secret Store Component (Kubernetes)
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: secrets
spec:
  type: secretstores.kubernetes
  version: v1
  metadata: []
```

## Development Setup

### Setting Up Locally

1. **Clone the repository**
```bash
git clone <repository-url>
cd todo-chatbot
```

2. **Set up backend**
```bash
cd backend
pip install -r requirements.txt
# Set up environment variables
cp .env.example .env
# Edit .env with your configuration
uvicorn main:app --reload --port 8000
```

3. **Set up frontend**
```bash
cd frontend
npm install
# Set up environment variables
cp .env.example .env
# Edit .env with your configuration
npm run dev
```

4. **Set up MCP server**
```bash
cd mcp-server
npm install
npm start
```

### Running Tests

#### Backend Tests
```bash
cd backend
python -m pytest tests/
```

#### Frontend Tests
```bash
cd frontend
npm test
```

#### Integration Tests
```bash
cd backend
python integration_test.py
```

### Docker Compose (Alternative Setup)
```bash
# Build and run with Docker Compose
docker-compose up --build
```

## Production Deployment

### Environment-Specific Configuration

Production deployments require additional configuration:

#### Database Scaling
- Use managed PostgreSQL services (AWS RDS, Google Cloud SQL, Azure Database)
- Implement read replicas for high availability
- Set up automated backups and monitoring

#### Service Scaling
- Configure Horizontal Pod Autoscaling (HPA)
- Set up resource limits and requests
- Implement circuit breakers and retries

#### Monitoring and Logging
- Integrate with Prometheus and Grafana
- Set up centralized logging with ELK stack
- Implement distributed tracing with Jaeger

#### Security Hardening
- Enable TLS/SSL for all communications
- Implement network policies
- Regular security scanning of containers
- Use secrets management (HashiCorp Vault, AWS Secrets Manager)

### CI/CD Pipeline

The recommended CI/CD pipeline includes:

1. **Code Quality Checks**
   - Linting and formatting
   - Security scanning
   - Unit tests

2. **Build and Package**
   - Container image building
   - Vulnerability scanning
   - Image signing

3. **Testing**
   - Integration tests
   - Performance tests
   - Security tests

4. **Deployment**
   - Staging environment
   - Production deployment
   - Rollback procedures

## Troubleshooting

### Common Issues

#### Dapr Sidecar Issues
```bash
# Check Dapr sidecar status
kubectl get pods -l dapr.io/enabled=true

# Describe pod to see Dapr sidecar logs
kubectl describe pod <pod-name>

# Check Dapr logs
kubectl logs <pod-name> -c daprd
```

#### Kafka Connectivity Issues
```bash
# Check Kafka pods
kubectl get pods -l app=kafka

# Test Kafka connectivity
kubectl exec -it deployment/kafka -- kafka-topics --list --bootstrap-server localhost:9092
```

#### Database Connection Issues
```bash
# Test database connectivity from backend pod
kubectl exec -it deployment/todo-chatbot-backend -- python -c "
import psycopg2
conn = psycopg2.connect('your_database_url')
print('Connected successfully')
"
```

#### Frontend Connection Issues
- Verify `NEXT_PUBLIC_BACKEND_URL` is accessible
- Check CORS configuration
- Ensure authentication tokens are properly configured

#### MCP Server Issues
- Verify `MCP_SERVER_URL` is accessible
- Check authentication between MCP server and backend
- Review MCP tool configurations

### Performance Optimization

#### Database Optimization
- Index frequently queried columns
- Optimize complex queries
- Use connection pooling

#### Service Optimization
- Implement caching strategies
- Optimize resource allocation
- Use CDN for static assets

#### Event Processing Optimization
- Tune Kafka partitions
- Optimize consumer group configurations
- Implement batching for high-volume events

### Monitoring Commands

```bash
# Check all pods
kubectl get pods

# Check all services
kubectl get services

# Check Dapr status
dapr status -k

# View application logs
kubectl logs deployment/todo-chatbot-backend
kubectl logs deployment/todo-chatbot-frontend

# Monitor resource usage
kubectl top pods

# Check events
kubectl get events --sort-by='.lastTimestamp'
```

## Contributing

### Development Guidelines
- Follow the existing code style and patterns
- Write unit tests for new functionality
- Update documentation for new features
- Use feature branches for development
- Submit pull requests for review

### Architecture Decisions
- All services communicate via events (loose coupling)
- User data isolation is mandatory
- Audit trails for all operations
- Idempotent operations where possible
- Graceful degradation in case of service failures

## License

MIT License - See LICENSE file for details.

## Support

For support, please open an issue in the repository or contact the development team.
# Implementation Plan: Phase 4 - Kubernetes Deployment for Todo AI Chatbot

## Technical Context

### Overview
This plan implements the Kubernetes deployment for the Todo AI Chatbot system following the authoritative specifications in prompt.md, containerizing the existing frontend, backend, and MCP server components for local Minikube deployment using Docker, Helm, and kubectl. Corrected to use TWO separate images as specified in prompt.md.

### Architecture Components
- **Frontend**: Next.js application in separate container (port 3000)
- **Backend+MCP**: Combined container running FastAPI backend and MCP server (port 8000)
- **Services**: Separate K8s Services for frontend and backend communication
- **Helm Chart**: Single chart with multiple deployments for easy management
- **Minikube**: Local Kubernetes cluster for development

### System Flow
```
Developer → Helm/helm install → Minikube K8s → Docker containers (Frontend + Backend+MCP) → Neon PostgreSQL
Browser → Next.js (3000) → FastAPI (HTTP) → MCP Server (internal)
```

### Dependencies
- Docker Desktop with Gordon (NLP agent) enabled
- Minikube
- kubectl
- Helm
- Node.js 20+
- Python 3.11+

### Constraints
- Frontend and Backend+MCP must run in separate containers
- MCP server communicates internally within backend container
- Local Minikube only (no cloud deployment initially)
- FastAPI serves as backend entrypoint
- Gordon is NLP agent in Docker Desktop UI (not CLI tool)

## Constitution Check

Based on the constitution file (`/mnt/d/TODO_APP/skills/TODOCHATBOT/.specify/memory/constitution.md`):

✅ **Phase Continuity Rule**: Will reuse existing Phase 2/3 codebase and architecture
✅ **Spec-Driven Development**: Following this plan based on detailed specifications
✅ **Stateless Architecture**: MCP server remains stateless with no direct DB access
✅ **Separation of Responsibilities**: Clear separation between frontend, backend, and MCP
✅ **Database Usage Rules**: Reusing existing Neon PostgreSQL database
✅ **Authentication & User Isolation**: Using JWT from Phase 2 for user isolation

## Gates

### Gate 1: Prerequisites Validation
- [ ] Docker Desktop with Gordon (NLP agent) is installed and running
- [ ] Minikube is installed and available
- [ ] kubectl is installed and configured
- [ ] Helm is installed and available
- [ ] Node.js 20+ is installed
- [ ] Python 3.11+ is installed

### Gate 2: Architecture Compliance
- [ ] Frontend and Backend+MCP run in separate containers
- [ ] MCP server communicates internally with FastAPI
- [ ] Proper networking between frontend and backend
- [ ] Correct ports: Frontend (3000), Backend (8000)

### Gate 3: Security Validation
- [ ] Secrets are properly managed in K8s
- [ ] No sensitive data exposed in ConfigMaps
- [ ] Proper RBAC if needed

## Phase 0: Outline & Research

### 0.1 Unknowns Resolution
- [x] Container architecture - resolved from prompt.md (Frontend and Backend+MCP separate)
- [x] Dockerfile requirements - resolved from prompt.md
- [x] K8s deployment patterns - resolved from prompt.md
- [x] Helm chart structure - resolved from prompt.md

### 0.2 Technology Choices Research
- [x] Docker separate images for frontend and backend+MCP as required by prompt.md
- [x] Helm for deployment management (mandatory requirement)
- [x] Gordon as NLP agent in Docker Desktop UI (not CLI tool)
- [x] Minikube for local development

### 0.3 Integration Patterns
- [x] Internal container communication between FastAPI and MCP
- [x] Inter-service communication between frontend and backend
- [x] Environment variable injection via Helm values

## Phase 1: Design & Contracts

### 1.1 Data Model Design

#### K8s Configuration Objects
- **Deployment**: Separate deployments for frontend and backend+MCP
- **Service**: Separate services for frontend (3000) and backend (8000)
- **ConfigMap**: Non-sensitive configuration via Helm values
- **Secret**: Sensitive data like API keys

### 1.2 API Contract Design

#### K8s API Endpoints
- `todochatbot-frontend:3000` - Frontend Next.js application
- `todochatbot-backend:8000` - Backend API and MCP server
- `todochatbot-backend:8000/health` - Health check endpoint
- `todochatbot-backend:8000/api/*` - Backend API endpoints

#### Environment Variable Contracts
- `NEXT_PUBLIC_API_URL` - Frontend to backend communication
- `DATABASE_URL` - Backend database connection
- `JWT_SECRET_KEY` - Authentication secret
- `ENV` - Environment configuration

### 1.3 Quickstart Documentation

#### Local Development Setup
1. Install prerequisites: Docker, Minikube, kubectl, Helm, Node.js, Python
2. Start Minikube: `minikube start`
3. Set Docker env: `eval $(minikube docker-env)`
4. Build Docker images using Gordon (NLP agent)
5. Deploy with Helm chart

#### Running the System
1. Start Minikube cluster
2. Build Docker images locally using Gordon NLP
3. Deploy using Helm chart
4. Access frontend via Minikube service on port 3000

## Phase 2: Implementation Plan

### 2.1 Environment Verification
**Objective**: Verify all required tools are installed and available as specified in prompt.md

#### Tasks:

##### MANDATORY CLAUDE SKILL

- Claude Code MUST use:
**mcp-server-tools-skill**

###### Allowed:

- Verify Docker Desktop with Gordon enabled
- Verify Minikube, kubectl, Helm installations
- Confirm Node.js 20+ and Python 3.11+ availability

##### Forbidden:

- Attempt to use Gordon as CLI tool
- Proceed without verifying prerequisites

1. [ ] Verify Docker Desktop is running with Gordon enabled
2. [ ] Verify Minikube installation: `minikube version`
3. [ ] Verify kubectl installation: `kubectl version --client`
4. [ ] Verify Helm installation: `helm version`
5. [ ] Verify Node.js 20+: `node --version`
6. [ ] Verify Python 3.11+: `python --version`

### 2.2 Docker Implementation
**Objective**: Create separate Dockerfiles for frontend and backend+MCP as specified in prompt.md

#### Tasks:
1. [ ] Create `Dockerfile.backend` for combined backend+MCP container:
   - Use `python:3.11-slim` base
   - Install system dependencies (gcc, g++, curl)
   - Install Node.js 20
   - Copy backend and MCP server source
   - Install dependencies
   - Build MCP server
   - Expose port 8000
   - Start FastAPI
2. [ ] Create `Dockerfile.frontend` for Next.js container:
   - Use `node:20-alpine` base
   - Install dependencies
   - Build Next.js app
   - Run production server
   - Expose port 3000
3. [ ] Build images using Gordon (NLP agent in Docker Desktop):
   - Build backend: "Build Docker image using Dockerfile.backend, tag as todo-backend-mcp:phase4"
   - Build frontend: "Build Docker image using Dockerfile.frontend, tag as todo-frontend:phase4"
4. [ ] Verify images exist in Docker Desktop

### 2.3 Kubernetes Setup
**Objective**: Prepare Minikube cluster for deployment

#### Tasks:
1. [ ] Start Minikube cluster: `minikube start`
2. [ ] Verify cluster: `kubectl get nodes`
3. [ ] Configure Docker for Minikube: `eval $(minikube docker-env)`
4. [ ] Verify Docker context targets Minikube

### 2.4 Helm Chart Creation
**Objective**: Create Helm chart with separate deployments for frontend and backend

#### Tasks:
1. [ ] Create Helm chart: `helm create todochatbot`
2. [ ] Configure `todochatbot/values.yaml` with explicit configuration:
   ```yaml
   frontend:
     image: todo-frontend
     tag: phase4
     port: 3000
     env:
       NEXT_PUBLIC_API_URL: http://todo-backend:8000

   backend:
     image: todo-backend-mcp
     tag: phase4
     port: 8000
     env:
       ENV: production
       MCP_MODE: kubernetes
   ```
3. [ ] Create separate deployment templates:
   - `deployment-frontend.yaml`
   - `deployment-backend.yaml`
4. [ ] Create separate service templates:
   - `service-frontend.yaml`
   - `service-backend.yaml`
5. [ ] Test Helm chart: `helm lint todochatbot`

### 2.5 Deployment & Testing
**Objective**: Deploy application to Minikube using Helm and validate functionality

#### Tasks:
1. [ ] Install Helm chart: `helm install todochatbot ./todochatbot`
2. [ ] Verify deployments: `kubectl get pods`
3. [ ] Verify services: `kubectl get svc`
4. [ ] Wait for pods to reach Running state
5. [ ] Test frontend access: `minikube service todochatbot-frontend --url`
6. [ ] Test backend health: `curl http://<backend-service>:8000/health`
7. [ ] Check backend logs for MCP initialization

### 2.6 Integration & Validation
**Objective**: Test complete system functionality in K8s environment

#### Tasks:
1. [ ] End-to-end testing in K8s
2. [ ] Verify frontend-backend communication
3. [ ] Test task CRUD operations through API
4. [ ] Validate user authentication flow
5. [ ] Verify MCP server functionality

## Phase 3: Deployment & Validation

### 3.1 Local Production Deployment
- Deploy to Minikube using Helm
- Verify all components communicate properly
- Test AI chatbot functionality
- Validate user authentication and task management

### 3.2 Post-Deployment Validation
- Verify Phase 2/3 functionality remains operational
- Confirm AI chatbot works as expected in K8s
- Validate user data isolation
- Monitor system performance in K8s

## Success Criteria Validation

### Measurable Outcomes
- [ ] Two Docker images built successfully using Gordon (NLP agent)
- [ ] Separate deployments for frontend (port 3000) and backend+MCP (port 8000)
- [ ] Helm chart installs successfully with all components
- [ ] Pod status is Running for both frontend and backend
- [ ] Services are accessible via Minikube
- [ ] Frontend can communicate with backend API
- [ ] Health check endpoint `/health` returns 200
- [ ] MCP server initializes properly in backend container
- [ ] Database connections are stable in K8s environment
- [ ] Users can successfully create, read, update, and delete tasks in K8s

## Risk Mitigation

### High-Risk Areas
1. **Gordon Usage**: Proper use of Gordon as NLP agent in Docker Desktop UI (not CLI)
2. **Image Building**: Ensuring images are built for Minikube context
3. **Service Communication**: Frontend to backend communication in K8s
4. **MCP Integration**: MCP server initialization within backend container

### Contingency Plans
1. **Gordon Issues**: Alternative manual Docker build process
2. **Service Discovery**: Verify service names and ports in K8s
3. **Communication Failures**: Check environment variables and network policies
4. **MCP Startup Issues**: Review MCP server configuration and dependencies

## Timeline
- **Week 1**: Environment verification and Docker implementation
- **Week 2**: Kubernetes and Helm configuration
- **Week 3**: Deployment testing and validation

## Resources Required
- Local development environment with Docker, Minikube, Helm, Gordon (NLP agent)
- Time allocation for containerization and K8s deployment
- Access to existing database credentials for configuration
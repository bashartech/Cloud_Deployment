# Implementation Tasks: Phase 4 - Kubernetes Deployment for Todo AI Chatbot

## Phase 1: Environment Verification

### Task 1.1: Verify Required Tools
**Objective**: Confirm all required tools are installed and available

**Steps**:
- [ ] Run `docker version` and verify Docker Desktop is running
- [ ] Run `minikube version` and verify Minikube is installed
- [ ] Run `kubectl version --client` and verify kubectl is installed
- [ ] Run `helm version` and verify Helm is installed
- [ ] Run `node --version` and verify Node.js 20+
- [ ] Run `python --version` and verify Python 3.11+
- [ ] Open Docker Desktop → Settings → Beta Features and ensure Docker AI / Gordon is enabled or asks with instructor

**Acceptance Criteria**:
- All commands return versions without errors
- Docker Desktop is running with Gordon enabled

**Dependencies**: None

## Phase 2: Dockerfile Creation

### Task 2.1: Create Backend + MCP Dockerfile
**Objective**: Create Dockerfile for backend and MCP server

**Location**: `TODOCHATBOT/Dockerfile.backend`

**Steps**:
- [ ] Create `Dockerfile.backend` after checking complete file structure of mcp server and backend then build with:
  - Base image: `python:3.11-slim`
  - Install system dependencies: `gcc`, `g++`, `curl`
  - Install Node.js 20
  - Copy backend source code from `./backend`
  - Copy MCP server source code from `./mcp-server`
  - Install Python dependencies from `backend/requirements.txt`
  - Install TypeScript globally
  - Build MCP server if source exists
  - Expose port **8000**
  - Start FastAPI application

**Acceptance Criteria**:
- Dockerfile.backend is created with correct specifications
- No Hugging Face-specific ports or logic included
- MCP server runs internally and is not exposed as separate service

**Dependencies**: Task 1.1

### Task 2.2: Create Frontend Dockerfile
**Objective**: Create Dockerfile for Next.js frontend

**Location**: `TODOCHATBOT/Dockerfile.frontend`

**Steps**:
- [ ] Create `Dockerfile.frontend` after checking complete file structure of frontend folder then  with:
  - Base image: `node:20-alpine`
  - Install frontend dependencies
  - Build Next.js application
  - Run production server
  - Expose port **3000**

**Acceptance Criteria**:
- Dockerfile.frontend is created with correct specifications
- Builds and runs Next.js application properly

**Dependencies**: Task 1.1

## Phase 3: Minikube Setup

### Task 3.1: Start Local Kubernetes Cluster
**Objective**: Initialize local Kubernetes cluster with Minikube

**Steps**:
- [ ] Run `minikube start`
- [ ] Run `kubectl get nodes`
- [ ] Verify node status is `Ready`

**Acceptance Criteria**:
- Minikube cluster starts successfully
- Node status shows `Ready`

**Dependencies**: Task 1.1

### Task 3.2: Configure Docker for Minikube
**Objective**: Configure Docker to build images for Minikube cluster

**Steps**:
- [ ] Run `eval $(minikube docker-env)` but (Ensure Minikube Docker daemon is active before asking Gordon to build images, otherwise images will be built into Docker Desktop instead of Minikube.)
- [ ] Verify Docker context is pointing to Minikube
- [ ] Before building images with Gordon, ensure Docker Desktop is using the Minikube Docker daemon (via eval $(minikube docker-env) in terminal). Gordon then builds into that context.

**Acceptance Criteria**:
- Docker commands target Minikube cluster
- Images built are available to Minikube

**Dependencies**: Task 3.1

## Phase 4: Docker Image Creation

### Task 4.1: Build Docker Images Using Gordon (NLP) - AFTER Minikube Configuration
**Objective**: Build Docker images using Docker Desktop's Gordon AI agent in Minikube context

**Steps**:
- [ ] Open Docker Desktop → Ask Gordon or use **docker ai** with instruction
- [ ] Issue instruction: "Build a Docker image using Dockerfile.backend and tag it as `todo-backend-mcp:phase4`"
- [ ] Issue instruction: "Build a Docker image using Dockerfile.frontend and tag it as `todo-frontend:phase4`"
- [ ] Verify both images appear in Docker Desktop image list
- [ ] Verify no build errors occurred

**Acceptance Criteria**:
- Both images (`todo-backend-mcp:phase4` and `todo-frontend:phase4`) exist in Minikube Docker context
- No build errors occurred during image creation

**Dependencies**: Task 2.1, Task 2.2, Task 3.1, Task 3.2

## Phase 5: Helm Chart Implementation (MANDATORY)

### Task 5.1: Create Helm Chart
**Objective**: Create Helm chart for the application

**Steps**:
- [ ] Run `helm create todochatbot`
- [ ] Verify chart structure is created properly

**Acceptance Criteria**:
- Helm chart `todochatbot` is created successfully
- Chart structure follows Helm best practices

**Dependencies**: Task 1.1

### Task 5.2: Configure values.yaml
**Objective**: Define explicit configuration in values.yaml

**Steps**:
- [ ] Update `todochatbot/values.yaml` with:
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
- [ ] ckeck the env file of backend and folder then add all env variables and secrets in values.yaml
- [ ] ❌ Do NOT hardcode in values.yaml , ✅ Use: Kubernetes Secret Or sealed secrets later

**Acceptance Criteria**:
- values.yaml contains explicit configuration for both frontend and backend
- Environment variables are properly defined
- Image names and ports match Docker image tags

**Dependencies**: Task 5.1

### Task 5.3: Create Helm Templates
**Objective**: Create separate deployment and service templates for frontend and backend

**Steps**:
- [ ] Create `todochatbot/templates/deployment-frontend.yaml` for frontend deployment
- [ ] Create `todochatbot/templates/deployment-backend.yaml` for backend deployment
- [ ] Create `todochatbot/templates/service-frontend.yaml` for frontend service
- [ ] Create `todochatbot/templates/service-backend.yaml` for backend service
- [ ] Ensure:
  - One container per deployment
  - Image, ports, and env values come from `values.yaml`
  - Backend service name matches frontend API URL
- [ ] Run `helm lint todochatbot` to validate
- [ ] Frontend env vars must be injected at build time OR runtime using Kubernetes env: (not .env.local).Backend env vars must be injected via env: in deployment template.
Also clarify Next.js rule:
- [ ] Frontend Dockerfile must read NEXT_PUBLIC_API_URL at runtime (not hardcoded during build).
- [ ] Backend Kubernetes Service MUST be named todo-backend and expose port 8000.
- [ ] NEXT_PUBLIC_* → available in browser
  - Others → NOT exposed
  - 📌 Without this, frontend API calls can fail silently.
- [ ] Configure Kubernetes liveness and readiness probes for backend using `/health` endpoint:
  - livenessProbe → restart container if app is stuck
  - readinessProbe → control traffic only when backend is ready
- [ ] Confirm frontend code reads API URL from process.env.NEXT_PUBLIC_API_URL at runtime (not hardcoded during build)

**Acceptance Criteria**:
- All four templates are created with proper configurations
- Templates reference values from values.yaml
- Helm lint passes without errors

**Dependencies**: Task 5.2

## Phase 6: Deployment

### Task 6.1: Install Helm Chart
**Objective**: Deploy the application using Helm

**Steps**:
- [ ] Run `helm install todochatbot ./todochatbot`
- [ ] Run `` to check pod status
- [ ] Run `kubectl get svc` to check services
- [ ] Wait for pods to reach `Running` state

**Acceptance Criteria**:
- Helm install completes successfully
- Both frontend and backend pods reach `Running` state
- Services are created successfully

**Dependencies**: Task 5.3, Task 4.1

## Phase 7: Access & Validation

### Task 7.1: Access Frontend
**Objective**: Access the frontend application

**Steps**:
- [ ] Run `minikube service todochatbot-frontend --url`
- [ ] Open the returned URL in browser
- [ ] Verify frontend loads properly

**Acceptance Criteria**:
- Frontend is accessible via browser
- Page loads without errors

**Dependencies**: Task 6.1

### Task 7.2: Validate Backend & MCP
**Objective**: Test backend and MCP server functionality

**Steps**:
- [ ] Run `kubectl logs deploy/todochatbot-backend`
- [ ] Test health endpoint: `curl http://<backend-service>:8000/health`
- [ ] Verify logs show MCP server initialized

**Acceptance Criteria**:
- Health endpoint returns HTTP 200
- Application logs show MCP server initialized without errors
- Backend responds to requests properly

**Dependencies**: Task 6.1

## Phase 8: Final Checklist

### Task 8.1: Complete Validation
**Objective**: Verify all requirements from prompt.md are met

**Steps**:
- [ ] Verify Backend image builds successfully
- [ ] Verify Frontend image builds successfully
- [ ] Verify Helm install succeeds
- [ ] Verify Pods are running
- [ ] Verify Frontend loads in browser
- [ ] Verify Backend health endpoint works
- [ ] Verify MCP server initializes without errors (MCP server is started by the backend process (FastAPI) during container startup, not as a separate process or service.)

**Acceptance Criteria**:
- All checklist items are completed
- Application functions properly in Kubernetes

**Dependencies**: All previous tasks

## Overall Acceptance Criteria
- [ ] Two Docker images built using Gordon (NLP agent in Docker Desktop)
- [ ] Separate deployments for frontend (port 3000) and backend+MCP (port 8000)
- [ ] Application deploys to Minikube using Helm
- [ ] Both frontend and backend services are accessible
- [ ] MCP server initializes properly in backend container
- [ ] Health check endpoint returns 200
- [ ] All validation checklist items from prompt.md are satisfied
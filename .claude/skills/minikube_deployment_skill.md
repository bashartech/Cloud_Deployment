# Complete Guide: Deploying 3-Tier Applications on Minikube with Helm Charts

## Overview
This guide provides a comprehensive approach to deploying 3-tier applications (frontend, backend, database) on Minikube using Docker, Helm charts, and Kubernetes. It covers common pitfalls, solutions, and best practices learned from real-world deployment challenges.

## Prerequisites
- Docker Desktop with Kubernetes enabled or Minikube
- Helm 3.x
- kubectl
- Node.js (for frontend development)
- Python (for backend development)

## Common Issues and Solutions

### 1. LightningCSS Binary Issues
**Problem**: LightningCSS (used by Tailwind CSS v4) ships with prebuilt binaries for specific platforms. When building in Docker containers, the binary for the container's platform may not exist.

**Solution**:
```bash
# Install build tools in Dockerfile
RUN apt-get update && apt-get install -y \
    python3 \
    make \
    g++ \
    build-essential \
    curl \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.cargo/bin:${PATH}"

# Force rebuild of native modules
RUN npm rebuild lightningcss
```

### 2. Authentication Token Validation Issues
**Problem**: JWT tokens issued by auth systems may not be validated properly when services communicate internally vs externally.

**Solution**:
```bash
# In Kubernetes environment, use internal service names
NEXT_PUBLIC_BETTER_AUTH_URL=http://todo-chatbot-frontend:3000
NEXT_PUBLIC_BACKEND_URL=http://todo-chatbot-backend:8000

# Update JWT middleware to use internal service name for JWKS
BETTER_AUTH_INTERNAL_URL=http://todo-chatbot-frontend:3000
```

### 3. Port Binding and Service Discovery
**Problem**: Services running in containers need to communicate with each other using internal Kubernetes DNS names, not localhost.

**Solution**:
- Frontend service: `http://todo-chatbot-frontend:3000`
- Backend service: `http://todo-chatbot-backend:8000`
- Database: Internal PostgreSQL service name

### 4. Environment Variable Management
**Problem**: Hardcoding environment variables in values files leads to security issues and deployment inconsistencies.

**Solution**: Use Kubernetes secrets for sensitive data:
```bash
# Create secrets separately from Helm charts
kubectl create secret generic todo-frontend-env \
  --from-literal=NEXT_PUBLIC_BETTER_AUTH_URL="http://todo.local" \
  --from-literal=NEXT_PUBLIC_BETTER_AUTH_SECRET="your-secret" \
  --from-literal=GOOGLE_CLIENT_ID="your-google-client-id" \
  --from-literal=GOOGLE_CLIENT_SECRET="your-google-client-secret" \
  -n your-namespace

kubectl create secret generic todo-backend-env \
  --from-literal=BETTER_AUTH_URL="http://todo.local" \
  --from-literal=BETTER_AUTH_SECRET="your-secret" \
  --from-literal=DATABASE_URL="your-db-url" \
  --from-literal=GEMINI_API_KEY="your-api-key" \
  -n your-namespace
```

## Complete Deployment Process

### 1. Build Docker Images
```bash
# Build frontend image
docker build -f Dockerfile.frontend -t todo-frontend:1.0 .

# Build backend image
docker build -f Dockerfile.backend -t todo-backend:1.0 .
```

### 2. Start Minikube
```bash
# Start Minikube with sufficient resources
minikube start --cpus=4 --memory=8192 --disk-size=40g

# Set Docker environment to Minikube
eval $(minikube docker-env)  # On Linux/Mac
minikube docker-env | Invoke-Expression  # On Windows PowerShell
```

### 3. Create Kubernetes Namespace
```bash
kubectl create namespace todo-chatbot --dry-run=client -o yaml | kubectl apply -f -
```

### 4. Create Secrets
```bash
# Create frontend secrets
kubectl create secret generic todo-frontend-env \
  --from-literal=NEXT_PUBLIC_BETTER_AUTH_URL="http://todo.local" \
  --from-literal=NEXT_PUBLIC_BETTER_AUTH_SECRET="e8QDSIu8QZtOENR8tRcsdwYMmwC4Uom0" \
  --from-literal=NEXT_PUBLIC_FRONTEND_URL="http://todo.local" \
  --from-literal=NEXT_PUBLIC_BACKEND_URL="http://todo.local/api" \
  --from-literal=GOOGLE_CLIENT_ID="your-google-client-id" \
  --from-literal=GOOGLE_CLIENT_SECRET="your-google-client-secret" \
  --from-literal=NEXT_PUBLIC_MCP_SERVER_URL="http://todo.local/mcp" \
  -n todo-chatbot

# Create backend secrets
kubectl create secret generic todo-backend-env \
  --from-literal=BETTER_AUTH_URL="http://todo.local" \
  --from-literal=BETTER_AUTH_SECRET="e8QDSIu8QZtOENR8tRcsdwYMmwC4Uom0" \
  --from-literal=DATABASE_URL="your-db-url" \
  --from-literal=GEMINI_API_KEY="your-api-key" \
  --from-literal=GOOGLE_CLIENT_ID="your-google-client-id" \
  --from-literal=GOOGLE_CLIENT_SECRET="your-google-client-secret" \
  -n todo-chatbot
```

### 5. Create Helm Chart Structure
```bash
# Create Helm chart
helm create todo-chatbot

# Update Chart.yaml with proper information
apiVersion: v2
name: todo-chatbot
description: A 3-tier Todo Chatbot application
type: application
version: 0.1.0
appVersion: "1.0.0"
```

### 6. Configure Helm Templates

**Deployment for Frontend (templates/frontend-deployment.yaml)**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "todo-chatbot.fullname" . }}-frontend
  labels:
    {{- include "todo-chatbot.labels" . | nindent 4 }}
    app: frontend
spec:
  replicas: {{ .Values.frontend.replicaCount }}
  selector:
    matchLabels:
      {{- include "todo-chatbot.selectorLabels" . | nindent 6 }}
      app: frontend
  template:
    metadata:
      labels:
        {{- include "todo-chatbot.selectorLabels" . | nindent 8 }}
        app: frontend
    spec:
      containers:
      - name: {{ .Chart.Name }}-frontend
        image: "{{ .Values.frontend.image.repository }}:{{ .Values.frontend.image.tag | default .Chart.AppVersion }}"
        imagePullPolicy: {{ .Values.frontend.image.pullPolicy }}
        ports:
        - containerPort: 3000
          name: http
        envFrom:
        - secretRef:
            name: todo-frontend-env
        livenessProbe:
          httpGet:
            path: /
            port: http
        readinessProbe:
          httpGet:
            path: /
            port: http
        resources:
          {{- toYaml .Values.frontend.resources | nindent 10 }}
      {{- with .Values.frontend.nodeSelector }}
      nodeSelector:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.frontend.affinity }}
      affinity:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.frontend.tolerations }}
      tolerations:
        {{- toYaml . | nindent 8 }}
      {{- end }}
```

**Deployment for Backend (templates/backend-deployment.yaml)**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "todo-chatbot.fullname" . }}-backend
  labels:
    {{- include "todo-chatbot.labels" . | nindent 4 }}
    app: backend
spec:
  replicas: {{ .Values.backend.replicaCount }}
  selector:
    matchLabels:
      {{- include "todo-chatbot.selectorLabels" . | nindent 6 }}
      app: backend
  template:
    metadata:
      labels:
        {{- include "todo-chatbot.selectorLabels" . | nindent 8 }}
        app: backend
    spec:
      containers:
      - name: {{ .Chart.Name }}-backend
        image: "{{ .Values.backend.image.repository }}:{{ .Values.backend.image.tag | default .Chart.AppVersion }}"
        imagePullPolicy: {{ .Values.backend.image.pullPolicy }}
        ports:
        - containerPort: 8000
          name: http
        envFrom:
        - secretRef:
            name: todo-backend-env
        livenessProbe:
          httpGet:
            path: /health
            port: http
        readinessProbe:
          httpGet:
            path: /health
            port: http
        resources:
          {{- toYaml .Values.backend.resources | nindent 10 }}
      {{- with .Values.backend.nodeSelector }}
      nodeSelector:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.backend.affinity }}
      affinity:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.backend.tolerations }}
      tolerations:
        {{- toYaml . | nindent 8 }}
      {{- end }}
```

### 7. Install NGINX Ingress Controller
```bash
# Install NGINX Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml

# Wait for ingress controller to be ready
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=90s
```

### 8. Deploy with Helm
```bash
# Install the Helm chart
helm install todo-chatbot-release . \
  --namespace todo-chatbot \
  --create-namespace \
  --set frontend.image.tag="1.0" \
  --set backend.image.tag="1.0"

# Or upgrade if already installed
helm upgrade todo-chatbot-release . \
  --namespace todo-chatbot \
  --set frontend.image.tag="1.1" \
  --set backend.image.tag="1.1"
```

### 9. Verify Deployment
```bash
# Check pods status
kubectl get pods -n todo-chatbot

# Check services
kubectl get svc -n todo-chatbot

# Check ingress
kubectl get ingress -n todo-chatbot

# Check logs
kubectl logs -n todo-chatbot -l app=frontend
kubectl logs -n todo-chatbot -l app=backend
```

## Essential Commands for Management

### Building and Updating Images
```bash
# Build new images
docker build -f Dockerfile.frontend -t todo-frontend:1.1 .
docker build -f Dockerfile.backend -t todo-backend:1.1 .

# Update deployments with new images
kubectl set image deployment/todo-chatbot-frontend -n todo-chatbot todo-chatbot-frontend=todo-frontend:1.1
kubectl set image deployment/todo-chatbot-backend -n todo-chatbot todo-chatbot-backend=todo-backend:1.1

# Or use Helm upgrade
helm upgrade todo-chatbot-release . --namespace todo-chatbot --set frontend.image.tag="1.1" --set backend.image.tag="1.1"
```

### Rolling Updates and Rollbacks
```bash
# Check rollout status
kubectl rollout status deployment/todo-chatbot-frontend -n todo-chatbot
kubectl rollout status deployment/todo-chatbot-backend -n todo-chatbot

# View rollout history
kubectl rollout history deployment/todo-chatbot-frontend -n todo-chatbot

# Rollback if needed
kubectl rollout undo deployment/todo-chatbot-frontend -n todo-chatbot

# Restart deployment
kubectl rollout restart deployment/todo-chatbot-frontend -n todo-chatbot
kubectl rollout restart deployment/todo-chatbot-backend -n todo-chatbot
```

### Service Management
```bash
# Check services
kubectl get svc -n todo-chatbot

# Check endpoints
kubectl get endpoints -n todo-chatbot

# Describe service for details
kubectl describe svc todo-chatbot-frontend -n todo-chatbot
```

### Pod Management
```bash
# Get pods
kubectl get pods -n todo-chatbot

# Get pod details
kubectl describe pod -n todo-chatbot -l app=frontend

# Check logs
kubectl logs -n todo-chatbot -l app=frontend
kubectl logs -n todo-chatbot -l app=backend

# Exec into pod
kubectl exec -it -n todo-chatbot deployment/todo-chatbot-frontend -- /bin/sh
```

### Port Forwarding for Local Development
```bash
# Port forward frontend
kubectl port-forward -n todo-chatbot svc/todo-chatbot-frontend 3000:3000

# Port forward backend
kubectl port-forward -n todo-chatbot svc/todo-chatbot-backend 8000:8000

# Port forward both in background
kubectl port-forward -n todo-chatbot svc/todo-chatbot-frontend 3000:3000 &
kubectl port-forward -n todo-chatbot svc/todo-chatbot-backend 8000:8000 &
```

## Common Troubleshooting Commands

### Authentication Issues
```bash
# Check if auth endpoints are accessible
kubectl exec -it -n todo-chatbot deployment/todo-chatbot-frontend -- curl http://todo-chatbot-backend:8000/health

# Verify secrets are correctly set
kubectl get secret todo-frontend-env -n todo-chatbot -o yaml
kubectl get secret todo-backend-env -n todo-chatbot -o yaml

# Decode secrets to verify content
kubectl get secret todo-frontend-env -n todo-chatbot -o jsonpath='{.data.NEXT_PUBLIC_BETTER_AUTH_URL}' | base64 -d
```

### Networking Issues
```bash
# Test service connectivity from within cluster
kubectl run test-pod --image=curlimages/curl -it --rm --restart=Never -- curl -I http://todo-chatbot-frontend:3000
kubectl run test-pod --image=curlimages/curl -it --rm --restart=Never -- curl -I http://todo-chatbot-backend:8000

# Check ingress status
kubectl describe ingress todo-chatbot-ingress -n todo-chatbot
```

### Resource Issues
```bash
# Check resource usage
kubectl top pods -n todo-chatbot

# Check node resources
kubectl top nodes

# Check resource limits
kubectl describe pod -n todo-chatbot -l app=frontend
```

## Best Practices for 3-Tier Applications

1. **Separate Secrets from Code**: Never store secrets in values files or Helm charts
2. **Use Internal Service Names**: Services should communicate using internal DNS names like `service-name.namespace:port`
3. **Health Checks**: Implement proper liveness and readiness probes
4. **Resource Limits**: Set appropriate CPU and memory limits
5. **Environment Consistency**: Use same environment variables in dev, staging, and prod
6. **Image Pull Policy**: Use `Never` for local Minikube deployments
7. **Rolling Updates**: Configure proper update strategies to minimize downtime
8. **Monitoring**: Implement proper logging and monitoring from the start

## Common Pitfalls to Avoid

1. **Hardcoded URLs**: Don't hardcode localhost or external URLs in containerized applications
2. **Missing Build Tools**: Ensure Docker images have necessary build tools for native modules
3. **Inconsistent Secrets**: Make sure frontend and backend secrets are synchronized
4. **Port Conflicts**: Verify services are exposed on correct ports
5. **Ingress Configuration**: Ensure ingress rules properly route to services
6. **Database Connections**: Verify database URLs work in Kubernetes environment
7. **Authentication Flow**: Ensure auth tokens are properly handled between services

This comprehensive guide should help deploy any 3-tier application on Minikube with Helm charts while avoiding common pitfalls and issues.
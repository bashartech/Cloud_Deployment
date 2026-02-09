# Phase 2: Local Deployment on Minikube with Full Dapr Capabilities

## Current Status
- Phase 1 (Code - Event-Driven Architecture) is completed
- Phase 2 tasks are currently pending
- Need to deploy the complete event-driven architecture to Minikube with Dapr

## Deployment Prerequisites
Before starting the deployment, ensure the following tools are installed:
- Minikube
- kubectl
- Helm
- Dapr CLI
- Docker

## Detailed Deployment Steps

### Step 1: Prepare Neon Database Connection
Before deployment, you need to set up your Neon PostgreSQL connection:
1. Create a Neon account and PostgreSQL database
2. Get your connection string from the Neon dashboard
3. Create a local environment file with your Neon database credentials

### Step 2: Start Minikube and Install Dapr
```bash
# Start Minikube with sufficient resources
minikube start --memory=8192 --cpus=4

# Verify Minikube is running
minikube status

# Install Dapr to the cluster
dapr init -k --wait
```

### Step 3: Verify Dapr Installation
```bash
# Check Dapr system pods
kubectl get pods -n dapr-system

# Verify Dapr CLI works with cluster
dapr status -k
```

### Step 4: Verify Application Secrets
```bash
# Verify that the application secrets exist (created in Phase 4)
kubectl get secret todo-backend-env

# If the secrets don't exist, create them with your application configuration:
kubectl create secret generic todo-backend-env \
  --from-literal=DATABASE_URL="postg****equire&channel_binding=require" \
  --from-literal=BETTER_AUTH_URL="http://localhost:3000" \
  --from-literal=BETTER_AUTH_SECRET="e8QDSIu8QZtOENR8tRcsdwYMmwC4Uom0" \
  --from-literal=GEMINI_API_KEY="AIz*****8QxdyM" \
  --from-literal=GOOGLE_CLIENT_ID="109****b.apps.googleusercontent.com" \
  --from-literal=GOOGLE_CLIENT_SECRET="GO****NJ" \
  -n todo-chatbot
```

```bash
# Verify that the application secrets exist (created in Phase 4)
kubectl get secret todo-frontend-env

# If the secrets don't exist, create them with your application configuration:
kubectl create secret generic todo-frontend-env \
  --from-literal=DATABASE_URL="pos***g=require" \
  --from-literal=NEXT_PUBLIC_DATABASE_URL="postgresql://neondb_****mode=require&channel_binding=require" \
  --from-literal=NEXT_PUBLIC_BETTER_AUTH_URL="http://localhost:3000" \
  --from-literal=NEXT_PUBLIC_BACKEND_URL="http://localhost:8000/api" \
  --from-literal=NEXT_PUBLIC_BETTER_AUTH_SECRET="e8***om0" \
  --from-literal=GEMINI_API_KEY="AI***dyM" \
  --from-literal=GOOGLE_CLIENT_ID="10978***.apps.googleusercontent.com" \
  --from-literal=GOOGLE_CLIENT_SECRET="GO***NJ" \
  -n todo-chatbot
```




### Step 5: Build Docker Images
```bash
# Set Docker environment to Minikube
eval $(minikube docker-env)

# Build multi-service image using the shared Dockerfile
cd ..
docker build -t todo-services -f Dockerfile.services --target backend .

# Build frontend image
cd frontend
docker build -t todo-frontend -f ../Dockerfile.frontend .
```

### Step 6: Deploy Infrastructure Components
```bash
# Deploy Kafka for event streaming (using the Kubernetes manifest)
kubectl apply -f k8s-kafka-only.yaml

# Wait for Kafka to be ready
kubectl wait --for=condition=ready pod -l app=kafka --timeout=300s

# Note: We're using Neon PostgreSQL cloud database instead of local PostgreSQL
# The Neon database connection is handled via the Kubernetes secret created in Step 4
```

### Step 7: Deploy Dapr Components
```bash
# Apply Dapr component configurations
kubectl apply -f dapr-components/
```

### Step 8: Deploy Application Services
```bash
# Navigate to Helm charts directory
cd ../helm-charts/todo-chatbot/

# Deploy using Helm
helm upgrade --install todo-chatbot . --values values.yaml

# Wait for all pods to be ready
kubectl wait --for=condition=ready pod -l app=backend --timeout=300s
kubectl wait --for=condition=ready pod -l app=frontend --timeout=300s
kubectl wait --for=condition=ready pod -l app=notification-service --timeout=300s
kubectl wait --for=condition=ready pod -l app=recurrence-engine --timeout=300s
kubectl wait --for=condition=ready pod -l app=audit-service --timeout=300s
kubectl wait --for=condition=ready pod -l app=websocket-service --timeout=300s
```

### Step 9: Expose Services
```bash
# Expose frontend service
kubectl expose deployment todo-chatbot-frontend --type=NodePort --port=3000 --name=frontend-service

# Get the NodePort for frontend
FRONTEND_PORT=$(kubectl get service frontend-service -o jsonpath='{.spec.ports[0].nodePort}')
echo "Frontend NodePort: $FRONTEND_PORT"

# Expose backend service for API access
kubectl expose deployment todo-chatbot-backend --type=NodePort --port=8000 --name=backend-service
BACKEND_PORT=$(kubectl get service backend-service -o jsonpath='{.spec.ports[0].nodePort}')
echo "Backend NodePort: $BACKEND_PORT"
```

### Step 10: Verify Deployment
```bash
# Check all pods
kubectl get pods

# Check all services
kubectl get services

# Check Dapr sidecars
kubectl get pods -l dapr.io/enabled=true

# View logs for each service
kubectl logs deployment/todo-chatbot-backend
kubectl logs deployment/todo-chatbot-notification-service
kubectl logs deployment/todo-chatbot-recurrence-engine
kubectl logs deployment/todo-chatbot-audit-service
kubectl logs deployment/todo-chatbot-websocket-service
```

### Step 11: Access the Application
```bash
# Get Minikube IP
MINIKUBE_IP=$(minikube ip)

# Access the application
echo "Frontend: http://$MINIKUBE_IP:$FRONTEND_PORT"
echo "Backend API: http://$MINIKUBE_IP:$BACKEND_PORT"

# Or use minikube service to get the URL
minikube service frontend-service --url
minikube service backend-service --url
```

### Step 12: Test Event-Driven Functionality
```bash
# Test event publishing by creating a task via the API
curl -X POST "http://$(minikube ip):$BACKEND_PORT/api/tasks" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test task", "description": "Test description", "completed": false}'

# Monitor the Kafka topics to see events
kubectl exec -it deployment/kafka -- kafka-console-consumer --bootstrap-server localhost:9092 --topic task-events --from-beginning
```

## What Has Been Completed:
- [X] Phase 1: Code - Event-Driven Architecture with Kafka and Dapr
- [X] Created all service implementations (notification, recurrence, audit, websocket)
- [X] Created Dapr component configurations
- [X] Created Helm chart templates for all services
- [X] Created Kubernetes manifests for infrastructure
- [X] Created multi-service Dockerfile that supports all backend services
- [X] Configured Neon PostgreSQL database integration via Kubernetes secrets
- [X] Updated backend deployment to use Neon database connection

## What Needs to Be Done:
- [ ] Execute the deployment steps above
- [ ] Verify all services are running correctly
- [ ] Test event-driven functionality
- [ ] Validate Dapr building blocks are working
- [ ] Update tasks.md to reflect completed deployment

## Troubleshooting Commands:
```bash
# Check Dapr sidecar injection
kubectl describe pod <pod-name> | grep dapr

# Check Kafka connectivity
kubectl exec -it deployment/kafka -- kafka-topics --list --bootstrap-server localhost:9092

# Check Neon database connectivity (from backend pod)
kubectl exec -it deployment/todo-chatbot-backend -- python -c "import psycopg2; conn = psycopg2.connect('your_neon_connection_string'); print('Connected successfully')"

# Port forward for debugging
kubectl port-forward service/kafka 9092:9092
kubectl port-forward service/todo-chatbot-backend 8000:8000
```

## Cleanup (when needed):
```bash
# Uninstall Helm release
helm uninstall todo-chatbot

# Remove Dapr components
kubectl delete -f dapr-components/

# Remove infrastructure
kubectl delete -f k8s-kafka-postgres.yaml

# Remove secrets
kubectl delete secret neon-db-connection-string

# Uninstall Dapr
dapr uninstall -k

# Stop Minikube
minikube stop
```
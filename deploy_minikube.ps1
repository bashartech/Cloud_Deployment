# Deployment script for Todo Chatbot to Minikube with Dapr
# deploy_minikube.ps1 (PowerShell script for Windows)

Write-Host "🚀 Starting deployment of Todo Chatbot to Minikube with Dapr..." -ForegroundColor Green

# Check if Minikube is running
$isMinikubeRunning = $(minikube status --format="{{.Host}}" 2>$null) -eq "Running"
if (-not $isMinikubeRunning) {
    Write-Host "❌ Minikube is not running. Starting Minikube..." -ForegroundColor Yellow
    minikube start --memory=4096 --cpus=2
} else {
    Write-Host "✅ Minikube is already running" -ForegroundColor Green
}

# Check if Dapr is installed in the cluster
$daprPods = kubectl get pods -n dapr-system --no-headers 2>$null
if ($daprPods) {
    Write-Host "✅ Dapr is already installed in the cluster" -ForegroundColor Green
} else {
    Write-Host "📦 Installing Dapr to the cluster..." -ForegroundColor Yellow
    dapr init -k --wait
}

# Build Docker images in Minikube's Docker environment
Write-Host "🐳 Building Docker images in Minikube environment..." -ForegroundColor Cyan
minikube docker-env | Invoke-Expression
docker build -t todo-frontend -f ./frontend/Dockerfile ./frontend/
docker build -t todo-backend -f ./Dockerfile.backend .

# Build additional service images using the same base but different entrypoints
# We'll copy the necessary files for each service and create specific images
docker build -t todo-notification-service -f - . <<EOF
FROM todo-backend
COPY ./backend/notification_service/ /app/
CMD ["python", "notification_service/main.py"]
EOF

docker build -t todo-recurrence-engine -f - . <<EOF
FROM todo-backend
COPY ./backend/recurrence_engine/ /app/
CMD ["python", "recurrence_engine/main.py"]
EOF

docker build -t todo-audit-service -f - . <<EOF
FROM todo-backend
COPY ./backend/audit_service/ /app/
CMD ["python", "audit_service/main.py"]
EOF

docker build -t todo-websocket-service -f - . <<EOF
FROM todo-backend
COPY ./backend/websocket_service/ /app/
CMD ["python", "websocket_service/main.py"]
EOF

# Install Kafka and PostgreSQL to the cluster
Write-Host "📦 Installing Kafka and PostgreSQL to the cluster..." -ForegroundColor Cyan
kubectl apply -f ./docker-compose.kafka.yml

# Wait for Kafka and PostgreSQL to be ready
Write-Host "⏳ Waiting for Kafka and PostgreSQL to be ready..." -ForegroundColor Yellow
kubectl wait --for=condition=ready pod -l app=kafka --timeout=300s
kubectl wait --for=condition=ready pod -l app=postgres --timeout=300s

# Apply Dapr components
Write-Host "⚙️ Applying Dapr components..." -ForegroundColor Cyan
kubectl apply -f ./dapr-components/

# Deploy the application using Helm
Write-Host "🚢 Deploying application using Helm..." -ForegroundColor Cyan
helm upgrade --install todo-chatbot ./helm-charts/todo-chatbot/ --values ./helm-charts/todo-chatbot/values.yaml

# Wait for all deployments to be ready
Write-Host "⏳ Waiting for all deployments to be ready..." -ForegroundColor Yellow
kubectl wait --for=condition=ready pod -l app=frontend --timeout=300s
kubectl wait --for=condition=ready pod -l app=backend --timeout=300s
kubectl wait --for=condition=ready pod -l app=notification-service --timeout=300s
kubectl wait --for=condition=ready pod -l app=recurrence-engine --timeout=300s
kubectl wait --for=condition=ready pod -l app=audit-service --timeout=300s
kubectl wait --for=condition=ready pod -l app=websocket-service --timeout=300s

# Expose the frontend service
Write-Host "🌐 Exposing frontend service..." -ForegroundColor Cyan
kubectl expose deployment todo-chatbot-frontend --type=LoadBalancer --port=3000 --name=frontend-lb

# Get the Minikube IP and display access information
$minikubeIP = $(minikube ip)
Write-Host "✅ Deployment completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Access Information:" -ForegroundColor White
Write-Host "   Frontend: http://$minikubeIP:3000" -ForegroundColor White
Write-Host "   Backend API: http://$minikubeIP:8000" -ForegroundColor White
Write-Host ""
Write-Host "🔧 To access the services directly in the cluster:" -ForegroundColor White
Write-Host "   Frontend: todo-chatbot-frontend:3000" -ForegroundColor White
Write-Host "   Backend: todo-chatbot-backend:8000" -ForegroundColor White
Write-Host "   Notification Service: todo-chatbot-notification-service:50051" -ForegroundColor White
Write-Host "   Recurrence Engine: todo-chatbot-recurrence-engine:50054" -ForegroundColor White
Write-Host "   Audit Service: todo-chatbot-audit-service:50055" -ForegroundColor White
Write-Host "   WebSocket Service: todo-chatbot-websocket-service:8765" -ForegroundColor White
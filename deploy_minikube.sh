#!/bin/bash
# Deployment script for Todo Chatbot to Minikube with Dapr

set -e  # Exit on any error

echo "🚀 Starting deployment of Todo Chatbot to Minikube with Dapr..."

# Check if Minikube is running
if ! minikube status &>/dev/null; then
    echo "❌ Minikube is not running. Starting Minikube..."
    minikube start --memory=4096 --cpus=2
else
    echo "✅ Minikube is already running"
fi

# Check if Dapr is installed in the cluster
if kubectl get pods -n dapr-system &>/dev/null; then
    echo "✅ Dapr is already installed in the cluster"
else
    echo "📦 Installing Dapr to the cluster..."
    dapr init -k --wait
fi

# Build Docker images in Minikube's Docker environment
echo "🐳 Building Docker images in Minikube environment..."
eval $(minikube docker-env)
docker build -t todo-frontend ../frontend/ -f ../frontend/Dockerfile
docker build -t todo-backend ../backend/ -f ../backend/Dockerfile

# Build additional service images
docker build -t todo-notification-service ../backend/notification_service/ -f - <<EOF
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 50051
CMD ["python", "main.py"]
EOF

docker build -t todo-recurrence-engine ../backend/recurrence_engine/ -f - <<EOF
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 50054
CMD ["python", "main.py"]
EOF

docker build -t todo-audit-service ../backend/audit_service/ -f - <<EOF
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 50055
CMD ["python", "main.py"]
EOF

docker build -t todo-websocket-service ../backend/websocket_service/ -f - <<EOF
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8765
CMD ["python", "main.py"]
EOF

# Install Kafka and PostgreSQL to the cluster
echo "📦 Installing Kafka and PostgreSQL to the cluster..."
kubectl apply -f docker-compose.kafka.yml

# Wait for Kafka and PostgreSQL to be ready
echo "⏳ Waiting for Kafka and PostgreSQL to be ready..."
kubectl wait --for=condition=ready pod -l app=kafka --timeout=300s
kubectl wait --for=condition=ready pod -l app=postgres --timeout=300s

# Apply Dapr components
echo "⚙️ Applying Dapr components..."
kubectl apply -f ../dapr-components/

# Deploy the application using Helm
echo "🚢 Deploying application using Helm..."
helm upgrade --install todo-chatbot ../helm-charts/todo-chatbot/ --values ../helm-charts/todo-chatbot/values.yaml

# Wait for all deployments to be ready
echo "⏳ Waiting for all deployments to be ready..."
kubectl wait --for=condition=ready pod -l app=frontend --timeout=300s
kubectl wait --for=condition=ready pod -l app=backend --timeout=300s
kubectl wait --for=condition=ready pod -l app=notification-service --timeout=300s
kubectl wait --for=condition=ready pod -l app=recurrence-engine --timeout=300s
kubectl wait --for=condition=ready pod -l app=audit-service --timeout=300s
kubectl wait --for=condition=ready pod -l app=websocket-service --timeout=300s

# Expose the frontend service
echo "🌐 Exposing frontend service..."
kubectl expose deployment todo-chatbot-frontend --type=LoadBalancer --port=3000 --name=frontend-lb

# Get the Minikube IP and display access information
MINIKUBE_IP=$(minikube ip)
echo "✅ Deployment completed successfully!"
echo ""
echo "📋 Access Information:"
echo "   Frontend: http://$MINIKUBE_IP:3000"
echo "   Backend API: http://$MINIKUBE_IP:8000"
echo "   Dapr Dashboard: http://$MINIKUBE_IP:8080 (if enabled)"
echo ""
echo "🔧 To access the services directly in the cluster:"
echo "   Frontend: todo-chatbot-frontend:3000"
echo "   Backend: todo-chatbot-backend:8000"
echo "   Notification Service: todo-chatbot-notification-service:50051"
echo "   Recurrence Engine: todo-chatbot-recurrence-engine:50054"
echo "   Audit Service: todo-chatbot-audit-service:50055"
echo "   WebSocket Service: todo-chatbot-websocket-service:8765"
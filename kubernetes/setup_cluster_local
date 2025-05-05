#!/bin/bash
set -e

# Colors for better output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
CLUSTER_NAME="study-app-cluster"

echo -e "${GREEN}DevOps Study App - Kubernetes Deployment Helper${NC}"
echo -e "${YELLOW}This script will set up a k3d cluster and deploy the study app.${NC}"
echo ""

# Check for required tools
check_dependency() {
  if ! command -v "$1" &>/dev/null; then
    echo -e "${RED}Error: $1 is not installed. Please install it before proceeding.${NC}"
    exit 1
  fi
}

echo "Checking dependencies..."
check_dependency k3d
check_dependency kubectl
check_dependency docker
echo -e "${GREEN}All dependencies are installed.${NC}"
echo ""

# Check if cluster exists
if k3d cluster list | grep -q "$CLUSTER_NAME"; then
  echo -e "${YELLOW}Cluster $CLUSTER_NAME already exists.${NC}"
  read -p "Do you want to delete and recreate it? (y/n): " -r
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Deleting existing cluster..."
    k3d cluster delete "$CLUSTER_NAME"
  else
    echo "Using existing cluster."
  fi
fi

# Create cluster if it doesn't exist
if ! k3d cluster list | grep -q "$CLUSTER_NAME"; then
  echo "Creating k3d cluster using config file..."
  k3d cluster create --config "$SCRIPT_DIR/k3d-config.yaml"
  echo -e "${GREEN}Cluster created successfully!${NC}"
fi

# Configure kubectl to use the cluster
echo "Configuring kubectl to use the cluster..."
kubectl config use-context k3d-"$CLUSTER_NAME"

# Build Docker images
echo "Building Docker images..."
echo "Building backend image..."
docker build -t backend:dev -f "$BASE_DIR/src/backend/Dockerfile" "$BASE_DIR/src/backend"

echo "Building frontend image..."
docker build -t frontend:dev -f "$BASE_DIR/src/frontend/Dockerfile" "$BASE_DIR/src/frontend"

# Import images into k3d
echo "Importing images into k3d..."
k3d image import backend:dev -c "$CLUSTER_NAME"
k3d image import frontend:dev -c "$CLUSTER_NAME"

# Deploy the application using kustomize
echo "Deploying application using kustomize..."
kubectl apply -k "$SCRIPT_DIR/manifests/dev"

# Wait for pods to be ready
echo "Waiting for pods to be ready..."
kubectl wait --for=condition=Ready pods --all -n study-app --timeout=120s

# Get service info
echo -e "${GREEN}Application deployed successfully!${NC}"
echo "Getting service information..."
kubectl get services -n study-app

# Function to wait for LoadBalancer IP assignment and get URL
get_service_url() {
  local service_name=$1
  local max_attempts=30
  local attempt=1

  echo -e "Waiting for $service_name external IP..."

  while [ $attempt -le $max_attempts ]; do
    local ip
    local port

    ip=$(kubectl get svc "$service_name" -n study-app -o=jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)
    port=$(kubectl get svc "$service_name" -n study-app -o=jsonpath='{.spec.ports[0].port}' 2>/dev/null)

    if [ -n "$ip" ] && [ -n "$port" ]; then
      echo "http://$ip:$port"
      return 0
    fi

    echo -n "."
    sleep 2
    ((attempt++))
  done

  echo ""
  echo -e "${RED}Could not get external IP for $service_name after $max_attempts attempts${NC}"
  return 1
}

# Get frontend and backend service URLs
FRONTEND_URL=$(get_service_url "dev-frontend")
BACKEND_URL=$(get_service_url "dev-backend")

echo -e "\n${GREEN}Access your application via LoadBalancer external IPs:${NC}"
if [ -n "$FRONTEND_URL" ] && [ -n "$BACKEND_URL" ]; then
  echo -e "Frontend: ${YELLOW}$FRONTEND_URL${NC}"
  echo -e "Backend API: ${YELLOW}$BACKEND_URL${NC}"
  echo -e "Backend health check: ${YELLOW}$BACKEND_URL/health${NC}"
else
  echo -e "\n${RED}Could not determine service URLs. Please check the service status:${NC}"
  echo -e "${YELLOW}kubectl get svc -n study-app${NC}"
fi

# Extract service ports for port-forwarding instructions
FRONTEND_PORT=$(kubectl get svc dev-frontend -n study-app -o=jsonpath='{.spec.ports[0].port}' 2>/dev/null)
BACKEND_PORT=$(kubectl get svc dev-backend -n study-app -o=jsonpath='{.spec.ports[0].port}' 2>/dev/null)

echo -e "\n${GREEN}Alternative access via port-forwarding (for local development):${NC}"
echo -e "To access via port-forwarding, run these commands in separate terminals:"
echo -e "${YELLOW}kubectl port-forward svc/dev-frontend -n study-app $FRONTEND_PORT:$FRONTEND_PORT${NC}"
echo -e "${YELLOW}kubectl port-forward svc/dev-backend -n study-app $BACKEND_PORT:$BACKEND_PORT${NC}"
echo -e "Then access the application at:"
echo -e "Frontend: ${YELLOW}http://localhost:$FRONTEND_PORT${NC}"
echo -e "Backend API: ${YELLOW}http://localhost:$BACKEND_PORT${NC}"
echo -e "Backend health check: ${YELLOW}http://localhost:$BACKEND_PORT/health${NC}"

echo -e "\nTo delete the cluster when finished:"
echo -e "${YELLOW}k3d cluster delete $CLUSTER_NAME${NC}"

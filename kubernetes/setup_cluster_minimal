#!/bin/bash
set -e

# Colors for better output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLUSTER_NAME="study-app-cluster"

echo -e "${GREEN}DevOps Study App - Minimal Kubernetes Cluster Setup${NC}"
echo -e "${YELLOW}This script will set up a k3d cluster without deploying any applications.${NC}"
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

echo -e "\n${GREEN}Cluster is now ready!${NC}"
echo -e "You can deploy applications manually or use one of the other setup scripts to deploy the study app."

echo -e "\nTo check your cluster nodes:"
echo -e "${YELLOW}kubectl get nodes${NC}"

echo -e "\nTo create the application namespace:"
echo -e "${YELLOW}kubectl create namespace study-app${NC}"

echo -e "\nTo delete the cluster when finished:"
echo -e "${YELLOW}k3d cluster delete $CLUSTER_NAME${NC}"

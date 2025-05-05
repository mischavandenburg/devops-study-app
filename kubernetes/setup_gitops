#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Check for required environment variables
required_vars=("DEVPOD_WORKSPACE_ID" "GITUSER" "GITOPS_REPO")
missing_vars=()

for var in "${required_vars[@]}"; do
  if [ -z "${!var}" ]; then
    missing_vars+=("$var")
  fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
  echo "Error: The following required environment variables are not set:"
  for var in "${missing_vars[@]}"; do
    echo "  - $var"
  done
  echo "Please set these variables before running this script."
  exit 1
fi

KEY_DIR="/workspaces/$DEVPOD_WORKSPACE_ID/dev-keys"

# Check if key exists
if [ ! -f "$KEY_DIR/study_app_gitops_deploy_key" ]; then
  echo "Error: Deploy key not found at $KEY_DIR/study_app_gitops_deploy_key"
  exit 1
fi

flux bootstrap git \
  --url=ssh://git@github.com/"$GITUSER"/"$GITOPS_REPO" \
  --branch=main \
  --private-key-file="$KEY_DIR"/study_app_gitops_deploy_key \
  --path=clusters/dev

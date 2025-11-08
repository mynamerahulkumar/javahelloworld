#!/bin/bash

# Restart script for Trading API (AWS EC2 PRODUCTION)
# This script stops and then starts the FastAPI server

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "🔄 Restarting Trading API server (Production)..."

# Stop the server
./aws-deploy/backend/stop.sh

# Wait for processes to fully stop
sleep 3

# Start the server
./aws-deploy/backend/start.sh





#!/bin/bash

# Restart script for both Frontend and Backend (AWS EC2 PRODUCTION)
# This script stops and then starts both services

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🔄 Restarting Full Stack Application (Production)..."
echo ""

# Stop all services
./aws-deploy/stop-all.sh

# Wait for processes to fully stop
echo ""
echo "⏳ Waiting for services to stop..."
sleep 5

# Start all services
./aws-deploy/start-all.sh





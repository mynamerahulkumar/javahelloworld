#!/bin/bash

# Restart script for both Frontend and Backend
# This script stops and then starts both services

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔄 Restarting Full Stack Application..."
echo ""

# Stop all services
./stop-all.sh

# Wait a moment for processes to fully stop
echo ""
echo "⏳ Waiting for services to stop..."
sleep 3

# Start all services
./start-all.sh


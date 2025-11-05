#!/bin/bash

# Restart script for Trading API
# This script stops and then starts the FastAPI server

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔄 Restarting Trading API server..."

# Stop the server
./stop.sh

# Wait a moment for processes to fully stop
sleep 2

# Start the server
./start.sh


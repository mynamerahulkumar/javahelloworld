#!/bin/bash

# Restart script for Frontend only
# This script stops and then starts the Next.js development server

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🔄 Restarting Frontend server..."

# Stop the server
./scripts/stop-frontend.sh

# Wait a moment for processes to fully stop
echo ""
echo "⏳ Waiting for server to stop..."
sleep 3

# Start the server
./scripts/start-frontend.sh


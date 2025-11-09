#!/bin/bash

# Stop script for Trading API (AWS EC2 PRODUCTION)
# This script stops the FastAPI server running on port 8501

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/common.sh"
cd "$BACKEND_DIR"

echo "🛑 Stopping Trading API server (Production)..."

# Kill process by PID file if it exists
if [ -f "logs/bot.pid" ]; then
    PID=$(cat logs/bot.pid)
    kill_process $PID
    rm logs/bot.pid
fi

# Kill any processes listening on port 8501
kill_port 8501 "backend"

# Kill any uvicorn processes related to this project
UVICORN_PIDS=$(pgrep -f "uvicorn.*main:app" 2>/dev/null)
if [ ! -z "$UVICORN_PIDS" ]; then
    echo "🔍 Found uvicorn processes: $UVICORN_PIDS"
    for PID in $UVICORN_PIDS; do
        kill_process "$PID" "uvicorn"
    done
fi

echo "✅ Trading API server stopped!"





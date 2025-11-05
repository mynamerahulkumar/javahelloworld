#!/bin/bash

# Stop script for Backend API only
# This script stops the FastAPI server running on port 8501

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT/backend"

echo "🛑 Stopping Backend API server..."

# Kill process by PID file if it exists
if [ -f logs/bot.pid ]; then
    PID=$(cat logs/bot.pid)
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID
        echo "✅ Stopped process $PID"
    else
        echo "⚠️  Process $PID not found (may have already stopped)"
    fi
    rm logs/bot.pid
fi

# Also kill any processes listening on port 8501
PIDS=$(lsof -ti :8501 2>/dev/null)
if [ ! -z "$PIDS" ]; then
    echo "🔍 Found processes on port 8501: $PIDS"
    for PID in $PIDS; do
        kill -9 $PID 2>/dev/null
        echo "✅ Killed process $PID"
    done
else
    echo "✅ No processes found on port 8501"
fi

# Kill any uvicorn processes related to this project
UVICORN_PIDS=$(pgrep -f "uvicorn.*main:app" 2>/dev/null)
if [ ! -z "$UVICORN_PIDS" ]; then
    echo "🔍 Found uvicorn processes: $UVICORN_PIDS"
    for PID in $UVICORN_PIDS; do
        kill -9 $PID 2>/dev/null
        echo "✅ Killed uvicorn process $PID"
    done
fi

echo "✅ Backend API server stopped!"


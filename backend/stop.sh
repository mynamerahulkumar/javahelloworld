#!/bin/bash

# Stop script for Trading API
# This script stops the FastAPI server running on port 8501

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🛑 Stopping Trading API server..."

# Kill process by PID file if it exists
if [ -f bot.pid ]; then
    PID=$(cat bot.pid)
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID
        echo "✅ Stopped process $PID"
    else
        echo "⚠️  Process $PID not found (may have already stopped)"
    fi
    rm bot.pid
fi

# Also kill any processes listening on port 8501
PIDS=$(lsof -ti :8501)
if [ ! -z "$PIDS" ]; then
    echo "🔍 Found processes on port 8501: $PIDS"
    for PID in $PIDS; do
        kill -9 $PID 2>/dev/null
        echo "✅ Killed process $PID"
    done
else
    echo "✅ No processes found on port 8501"
fi

echo "✅ Trading API server stopped!"


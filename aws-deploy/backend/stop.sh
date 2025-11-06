#!/bin/bash

# Stop script for Trading API (AWS EC2 PRODUCTION)
# This script stops the FastAPI server running on port 8501

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT/backend"

echo "🛑 Stopping Trading API server (Production)..."

# Function to kill process by PID
kill_process() {
    local pid=$1
    if [ ! -z "$pid" ] && ps -p $pid > /dev/null 2>&1; then
        kill $pid 2>/dev/null
        sleep 2
        if ps -p $pid > /dev/null 2>&1; then
            kill -9 $pid 2>/dev/null
        fi
        echo "✅ Stopped process $pid"
        return 0
    fi
    return 1
}

# Function to kill processes on port (works on Linux)
kill_port() {
    local port=$1
    
    # Try using ss
    if command -v ss &> /dev/null; then
        PIDS=$(ss -tlnp | grep ":$port " | grep -oP 'pid=\K[0-9]+' | sort -u)
    # Try using netstat
    elif command -v netstat &> /dev/null; then
        PIDS=$(netstat -tlnp 2>/dev/null | grep ":$port " | grep -oP '[0-9]+/[^ ]+' | cut -d'/' -f1 | sort -u)
    # Try using lsof
    elif command -v lsof &> /dev/null; then
        PIDS=$(lsof -ti :$port 2>/dev/null)
    else
        echo "⚠️  Warning: Cannot kill processes on port $port"
        return 1
    fi
    
    if [ ! -z "$PIDS" ]; then
        echo "🔍 Found processes on port $port: $PIDS"
        for PID in $PIDS; do
            kill_process $PID
        done
        return 0
    fi
    return 1
}

# Kill process by PID file if it exists
if [ -f "logs/bot.pid" ]; then
    PID=$(cat logs/bot.pid)
    kill_process $PID
    rm logs/bot.pid
fi

# Kill any processes listening on port 8501
kill_port 8501

# Kill any uvicorn processes related to this project
UVICORN_PIDS=$(pgrep -f "uvicorn.*main:app" 2>/dev/null)
if [ ! -z "$UVICORN_PIDS" ]; then
    echo "🔍 Found uvicorn processes: $UVICORN_PIDS"
    for PID in $UVICORN_PIDS; do
        kill_process $PID
    done
fi

echo "✅ Trading API server stopped!"


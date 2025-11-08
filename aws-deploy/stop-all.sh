#!/bin/bash

# Stop script for both Frontend and Backend (AWS EC2 PRODUCTION)
# This script stops both the FastAPI backend and Next.js frontend

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🛑 Stopping Full Stack Application (Production)..."
echo ""

# Function to kill process by PID
kill_process() {
    local pid=$1
    local name=$2
    if [ ! -z "$pid" ] && ps -p $pid > /dev/null 2>&1; then
        kill $pid 2>/dev/null
        sleep 2
        if ps -p $pid > /dev/null 2>&1; then
            kill -9 $pid 2>/dev/null
        fi
        echo "✅ Stopped $name process $pid"
        return 0
    fi
    return 1
}

# Function to kill processes on port (works on Linux)
kill_port() {
    local port=$1
    local name=$2
    
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
        echo "⚠️  Warning: Cannot kill processes on port $port (ss, netstat, or lsof not found)"
        return 1
    fi
    
    if [ ! -z "$PIDS" ]; then
        echo "🔍 Found processes on port $port: $PIDS"
        for PID in $PIDS; do
            kill_process $PID "$name"
        done
        return 0
    fi
    return 1
}

# Stop Backend
echo "📦 Stopping Backend API..."

# Method 1: Kill by PID file
if [ -f "logs/backend.pid" ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    kill_process $BACKEND_PID "backend"
    rm logs/backend.pid
fi

# Method 2: Kill processes on port 8501
kill_port 8501 "backend"

# Method 3: Kill uvicorn processes
UVICORN_PIDS=$(pgrep -f "uvicorn.*main:app" 2>/dev/null)
if [ ! -z "$UVICORN_PIDS" ]; then
    echo "🔍 Found uvicorn processes: $UVICORN_PIDS"
    for PID in $UVICORN_PIDS; do
        kill_process $PID "uvicorn"
    done
fi

# Stop Frontend
echo "🎨 Stopping Frontend..."

# Method 1: Kill by PID file
if [ -f "logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    kill_process $FRONTEND_PID "frontend"
    rm logs/frontend.pid
fi

# Method 2: Kill processes on port 3000
kill_port 3000 "frontend"

# Method 3: Kill Next.js processes
NEXT_PIDS=$(pgrep -f "next.*start\|next.*dev" 2>/dev/null)
if [ ! -z "$NEXT_PIDS" ]; then
    echo "🔍 Found Next.js processes: $NEXT_PIDS"
    for PID in $NEXT_PIDS; do
        kill_process $PID "Next.js"
    done
fi

# Clean up Next.js lock files
if [ -d "frontend/.next" ]; then
    echo "🧹 Cleaning up Next.js lock files..."
    find frontend/.next -name "lock" -type f -delete 2>/dev/null || true
    find frontend/.next -name "*.lock" -type f -delete 2>/dev/null || true
    echo "✅ Lock files cleaned"
fi

echo ""
echo "✅ Full Stack Application Stopped!"





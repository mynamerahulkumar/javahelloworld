#!/bin/bash

# Stop script for both Frontend and Backend (AWS EC2 PRODUCTION)
# This script stops both the FastAPI backend and Next.js frontend

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/common.sh"
cd "$PROJECT_ROOT"

echo "🛑 Stopping Full Stack Application (Production)..."
echo ""

# Stop Backend
echo "📦 Stopping Backend API..."

# Method 1: Kill by PID file
if [ -f "logs/backend.pid" ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    kill_process "$BACKEND_PID" "backend"
    rm logs/backend.pid
fi

# Method 2: Kill processes on port 8501
kill_port 8501 "backend"

# Method 3: Kill uvicorn processes
UVICORN_PIDS=$(pgrep -f "uvicorn.*main:app" 2>/dev/null)
if [ ! -z "$UVICORN_PIDS" ]; then
    echo "🔍 Found uvicorn processes: $UVICORN_PIDS"
    for PID in $UVICORN_PIDS; do
        kill_process "$PID" "uvicorn"
    done
fi

# Stop Frontend
echo "🎨 Stopping Frontend..."

# Method 1: Kill by PID file
if [ -f "logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    kill_process "$FRONTEND_PID" "frontend"
    rm logs/frontend.pid
fi

# Method 2: Kill processes on port 3000
kill_port 3000 "frontend"

# Method 3: Kill Next.js processes
NEXT_PIDS=$(pgrep -f "next.*start\|next.*dev" 2>/dev/null)
if [ ! -z "$NEXT_PIDS" ]; then
    echo "🔍 Found Next.js processes: $NEXT_PIDS"
    for PID in $NEXT_PIDS; do
        kill_process "$PID" "Next.js"
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





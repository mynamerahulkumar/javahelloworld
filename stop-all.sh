#!/bin/bash

# Stop script for both Frontend and Backend (LOCAL DEVELOPMENT)
# This script stops both the FastAPI backend and Next.js frontend

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🛑 Stopping Full Stack Application..."
echo ""

# Stop Backend
echo "📦 Stopping Backend API..."

# Method 1: Use backend's stop script
if [ -f "backend/stop.sh" ]; then
    cd backend
    ./stop.sh
    cd ..
fi

# Method 2: Kill by PID file
if [ -f "logs/backend.pid" ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        kill $BACKEND_PID 2>/dev/null
        echo "✅ Stopped backend process $BACKEND_PID"
    fi
    rm logs/backend.pid
fi

# Method 3: Kill any processes on port 8501
PIDS=$(lsof -ti :8501 2>/dev/null)
if [ ! -z "$PIDS" ]; then
    echo "🔍 Found processes on port 8501: $PIDS"
    for PID in $PIDS; do
        kill -9 $PID 2>/dev/null
        echo "✅ Killed backend process $PID"
    done
fi

# Stop Frontend
echo "🎨 Stopping Frontend..."

# Kill by PID file
if [ -f "logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        kill $FRONTEND_PID 2>/dev/null
        echo "✅ Stopped frontend process $FRONTEND_PID"
    fi
    rm logs/frontend.pid
fi

# Kill any processes on port 3000
PIDS=$(lsof -ti :3000 2>/dev/null)
if [ ! -z "$PIDS" ]; then
    echo "🔍 Found processes on port 3000: $PIDS"
    for PID in $PIDS; do
        kill -9 $PID 2>/dev/null
        echo "✅ Killed frontend process $PID"
    done
fi

# Kill any Next.js processes
NEXT_PIDS=$(pgrep -f "next dev" 2>/dev/null)
if [ ! -z "$NEXT_PIDS" ]; then
    echo "🔍 Found Next.js processes: $NEXT_PIDS"
    for PID in $NEXT_PIDS; do
        kill -9 $PID 2>/dev/null
        echo "✅ Killed Next.js process $PID"
    done
fi

# Clean up Next.js lock files
if [ -d "frontend/.next" ]; then
    echo "🧹 Cleaning up Next.js lock files..."
    find frontend/.next -name "lock" -type f -delete 2>/dev/null
    find frontend/.next -name "*.lock" -type f -delete 2>/dev/null
    echo "✅ Lock files cleaned"
fi

echo ""
echo "✅ Full Stack Application Stopped!"

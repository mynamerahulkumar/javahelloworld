#!/bin/bash

# Stop script for Frontend only
# This script stops the Next.js development server running on port 3000

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🛑 Stopping Frontend server..."

# Kill process by PID file if it exists
if [ -f logs/frontend.pid ]; then
    PID=$(cat logs/frontend.pid)
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID
        echo "✅ Stopped process $PID"
    else
        echo "⚠️  Process $PID not found (may have already stopped)"
    fi
    rm logs/frontend.pid
fi

# Also kill any processes listening on port 3000
PIDS=$(lsof -ti :3000 2>/dev/null)
if [ ! -z "$PIDS" ]; then
    echo "🔍 Found processes on port 3000: $PIDS"
    for PID in $PIDS; do
        kill -9 $PID 2>/dev/null
        echo "✅ Killed process $PID"
    done
else
    echo "✅ No processes found on port 3000"
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

# Kill any node processes related to Next.js
NODE_PIDS=$(pgrep -f "node.*next-server" 2>/dev/null)
if [ ! -z "$NODE_PIDS" ]; then
    echo "🔍 Found Next.js node processes: $NODE_PIDS"
    for PID in $NODE_PIDS; do
        kill -9 $PID 2>/dev/null
        echo "✅ Killed Next.js node process $PID"
    done
fi

# Clean up Next.js lock files
if [ -d "frontend/.next" ]; then
    echo "🧹 Cleaning up Next.js lock files..."
    find frontend/.next -name "lock" -type f -delete 2>/dev/null
    find frontend/.next -name "*.lock" -type f -delete 2>/dev/null
    echo "✅ Lock files cleaned"
fi

echo "✅ Frontend server stopped!"


#!/bin/bash

# Cleanup script for Frontend
# This script cleans up stale lock files and processes

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT/frontend"

echo "🧹 Cleaning up Frontend..."

# Clean up Next.js lock files
if [ -d ".next" ]; then
    echo "🧹 Removing Next.js lock files..."
    find .next -name "lock" -type f -delete 2>/dev/null
    find .next -name "*.lock" -type f -delete 2>/dev/null
    echo "✅ Lock files removed"
else
    echo "ℹ️  No .next directory found"
fi

# Kill any processes on port 3000
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
else
    echo "✅ No Next.js processes found"
fi

# Remove PID file if it exists
if [ -f "../logs/frontend.pid" ]; then
    rm ../logs/frontend.pid
    echo "✅ Removed PID file"
fi

echo "✅ Frontend cleanup completed!"


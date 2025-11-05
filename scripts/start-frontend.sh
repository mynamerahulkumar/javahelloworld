#!/bin/bash

# Start script for Frontend only
# This script starts the Next.js development server on port 3000

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT/frontend"

# Check if frontend port is already in use
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 3000 is already in use. Attempting to stop existing processes..."
    cd "$PROJECT_ROOT"
    ./scripts/stop-frontend.sh
    sleep 2
fi

echo "🎨 Starting Frontend..."
echo ""

# Clean up Next.js lock files if they exist
if [ -d ".next" ]; then
    echo "🧹 Cleaning up stale Next.js lock files..."
    find .next -name "lock" -type f -delete 2>/dev/null
    find .next -name "*.lock" -type f -delete 2>/dev/null
    echo "✅ Lock files cleaned"
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "⚠️  node_modules not found. Installing dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
fi

# Create logs directory if it doesn't exist
mkdir -p ../logs

# Start the development server in the background
nohup npm run dev > ../logs/frontend.log 2>&1 &

# Save the process ID
FRONTEND_PID=$!
echo $FRONTEND_PID > ../logs/frontend.pid

echo "✅ Frontend server started!"
echo "📌 PID: $FRONTEND_PID"
echo "🌐 Server running at: http://localhost:3000"
echo ""
echo "📝 View logs: tail -f logs/frontend.log"
echo "🛑 To stop the server, run: ./scripts/stop-frontend.sh"


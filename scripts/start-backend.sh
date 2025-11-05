#!/bin/bash

# Start script for Backend API only
# This script starts the FastAPI server on port 8501

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT/backend"

# Check if backend port is already in use
if lsof -Pi :8501 -sTCP:LISTEN -t >/dev/null ; then
    echo "❌ Port 8501 is already in use. Please stop the existing server first."
    echo "   Run: ./scripts/stop-backend.sh"
    exit 1
fi

echo "📦 Starting Backend API..."
echo "📝 Logs will be written to: backend/logs/bot.log"
echo ""

# Create logs directory if it doesn't exist
mkdir -p logs

# Start the server in the background
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8501 --reload > logs/bot.log 2>&1 &

# Save the process ID
BACKEND_PID=$!
echo $BACKEND_PID > logs/bot.pid

echo "✅ Backend API server started!"
echo "📌 PID: $BACKEND_PID"
echo "🌐 Server running at: http://localhost:8501"
echo "📚 API docs at: http://localhost:8501/docs"
echo ""
echo "📝 View logs: tail -f backend/logs/bot.log"
echo "🛑 To stop the server, run: ./scripts/stop-backend.sh"


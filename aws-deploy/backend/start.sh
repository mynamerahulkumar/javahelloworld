#!/bin/bash

# Start script for Trading API (AWS EC2 PRODUCTION)
# This script starts the FastAPI server on port 8501 in production mode

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT/backend"

# Function to check if port is in use (works on Linux)
check_port() {
    local port=$1
    if command -v ss &> /dev/null; then
        ss -tuln | grep -q ":$port " && return 0 || return 1
    elif command -v netstat &> /dev/null; then
        netstat -tuln | grep -q ":$port " && return 0 || return 1
    elif command -v lsof &> /dev/null; then
        lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 && return 0 || return 1
    else
        echo "⚠️  Warning: Cannot check port $port"
        return 1
    fi
}

# Check if server is already running
if check_port 8501; then
    echo "❌ Port 8501 is already in use. Please stop the existing server first."
    echo "   Run: ./aws-deploy/backend/stop.sh"
    exit 1
fi

echo "🚀 Starting Trading API server (Production Mode - AWS EC2)..."
echo "📝 Logs will be written to: logs/bot.log"
echo "📊 View logs with: tail -f logs/bot.log"
echo ""

# Create logs directory if it doesn't exist
mkdir -p logs

# Start the server in production mode (no reload, with workers)
if command -v uv &> /dev/null; then
    # Use uv run for production (no reload, with workers)
    nohup uv run python -m uvicorn main:app --host 0.0.0.0 --port 8501 --workers 4 > logs/bot.log 2>&1 &
    PID=$!
elif [ -d ".venv" ]; then
    # Use virtual environment
    nohup .venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8501 --workers 4 > logs/bot.log 2>&1 &
    PID=$!
else
    # Use system Python
    nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8501 --workers 4 > logs/bot.log 2>&1 &
    PID=$!
fi

# Save the process ID
echo $PID > logs/bot.pid

# Wait a moment and verify the process is running
sleep 3
if ! ps -p $PID > /dev/null 2>&1; then
    echo "❌ Server failed to start. Check logs/bot.log for details"
    tail -20 logs/bot.log
    exit 1
fi

echo "✅ Trading API server started!"
echo "📌 PID: $PID"
echo "🌐 Server running at: http://0.0.0.0:8501"
echo "📚 API docs at: http://0.0.0.0:8501/docs"
echo ""
echo "📝 View logs: tail -f logs/bot.log"
echo "🛑 To stop the server, run: ./aws-deploy/backend/stop.sh"





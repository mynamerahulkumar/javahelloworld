#!/bin/bash

# Start script for Trading API (LOCAL DEVELOPMENT)
# This script starts the FastAPI server on port 8501 with hot-reload

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if server is already running
if lsof -Pi :8501 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "❌ Port 8501 is already in use. Please stop the existing server first."
    echo "   Run: ./stop.sh"
    exit 1
fi

echo "🚀 Starting Trading API server (Development Mode)..."
echo "📝 Logs will be written to: logs/bot.log"
echo "📊 View logs with: tail -f logs/bot.log"
echo ""

# Create logs directory if it doesn't exist
mkdir -p logs

# Start the server in development mode (with reload)
if command -v uv &> /dev/null; then
    # Use uv run for development (with reload)
    nohup uv run python -m uvicorn main:app --host 0.0.0.0 --port 8501 --reload > logs/bot.log 2>&1 &
    PID=$!
else
    # Fallback to system Python
    nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8501 --reload > logs/bot.log 2>&1 &
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
echo "🌐 Server running at: http://localhost:8501"
echo "📚 API docs at: http://localhost:8501/docs"
echo ""
echo "📝 View logs: tail -f logs/bot.log"
echo "🛑 To stop the server, run: ./stop.sh"
echo ""
echo "💡 Note: Hot-reload is enabled for development"
echo "   For production, use scripts in ../aws-deploy/ folder"

#!/bin/bash

# Start script for Trading API
# This script starts the FastAPI server on port 8501

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if server is already running
if lsof -Pi :8501 -sTCP:LISTEN -t >/dev/null ; then
    echo "❌ Port 8501 is already in use. Please stop the existing server first."
    echo "   Run: ./stop.sh"
    exit 1
fi

echo "🚀 Starting Trading API server..."
echo "📝 Logs will be written to: logs/bot.log"
echo "📊 View logs with: tail -f logs/bot.log"
echo ""

# Start the server in the background
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8501 --reload > logs/bot.log 2>&1 &

# Save the process ID
echo $! > bot.pid

echo "✅ Trading API server started!"
echo "📌 PID: $(cat bot.pid)"
echo "🌐 Server running at: http://localhost:8501"
echo "📚 API docs at: http://localhost:8501/docs"
echo ""
echo "To stop the server, run: ./stop.sh"


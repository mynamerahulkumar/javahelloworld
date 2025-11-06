#!/bin/bash

# Start script for both Frontend and Backend (LOCAL DEVELOPMENT)
# This script starts both the FastAPI backend and Next.js frontend in development mode

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Starting Full Stack Application (Development Mode)..."
echo ""

# Check if backend port is already in use
if lsof -Pi :8501 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Backend port 8501 is already in use"
    echo "   Run: ./stop-all.sh to stop existing services"
    exit 1
fi

# Check if frontend port is already in use
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Frontend port 3000 is already in use"
    echo "   Run: ./stop-all.sh to stop existing services"
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs
mkdir -p backend/logs

# Start Backend
echo "📦 Starting Backend API (Development Mode)..."
cd backend

# Use backend's start script if it exists, otherwise start directly
if [ -f "./start.sh" ]; then
    ./start.sh > ../logs/backend.log 2>&1 &
    sleep 3
    # Get PID from backend's own PID file
    if [ -f "logs/bot.pid" ]; then
        BACKEND_PID=$(cat logs/bot.pid)
        if ! ps -p $BACKEND_PID > /dev/null 2>&1; then
            BACKEND_PID=$(pgrep -f "uvicorn.*main:app" | head -1)
        fi
    else
        BACKEND_PID=$(pgrep -f "uvicorn.*main:app" | head -1)
    fi
else
    # Fallback: start backend directly with reload for development
    if command -v uv &> /dev/null; then
        nohup uv run python -m uvicorn main:app --host 0.0.0.0 --port 8501 --reload > ../logs/backend.log 2>&1 &
        BACKEND_PID=$!
    else
        nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8501 --reload > ../logs/backend.log 2>&1 &
        BACKEND_PID=$!
    fi
fi

cd ..
if [ -z "$BACKEND_PID" ] || [ "$BACKEND_PID" = "" ]; then
    echo "❌ Failed to get backend PID"
    exit 1
fi
echo $BACKEND_PID > logs/backend.pid
echo "✅ Backend started (PID: $BACKEND_PID)"
echo "   Backend logs: logs/backend.log"

# Wait a moment for backend to start
sleep 3

# Start Frontend
echo "🎨 Starting Frontend (Development Mode)..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "⚠️  node_modules not found. Installing dependencies..."
    npm install
fi

nohup npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo $FRONTEND_PID > logs/frontend.pid
echo "✅ Frontend started (PID: $FRONTEND_PID)"
echo "   Frontend logs: logs/frontend.log"

# Wait a moment for frontend to start
sleep 3

# Check if processes are still running
if ! ps -p $BACKEND_PID > /dev/null 2>&1; then
    echo "❌ Backend failed to start. Check logs/backend.log for details"
    exit 1
fi

if ! ps -p $FRONTEND_PID > /dev/null 2>&1; then
    echo "❌ Frontend failed to start. Check logs/frontend.log for details"
    exit 1
fi

echo ""
echo "✅ Full Stack Application Started Successfully!"
echo ""
echo "📊 Services:"
echo "   Backend API:  http://localhost:8501"
echo "   Backend Docs: http://localhost:8501/docs"
echo "   Frontend:     http://localhost:3000"
echo ""
echo "📝 Logs:"
echo "   Backend:  tail -f logs/backend.log"
echo "   Frontend: tail -f logs/frontend.log"
echo ""
echo "🛑 To stop all services, run: ./stop-all.sh"
echo "🔄 To restart all services, run: ./restart-all.sh"
echo ""
echo "💡 Note: This is DEVELOPMENT mode with hot-reload enabled"
echo "   For production deployment, use scripts in aws-deploy/ folder"

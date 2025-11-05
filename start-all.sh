#!/bin/bash

# Start script for both Frontend and Backend
# This script starts both the FastAPI backend and Next.js frontend

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Starting Full Stack Application..."
echo ""

# Check if backend port is already in use
if lsof -Pi :8501 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Backend port 8501 is already in use"
    echo "   Run: ./stop-all.sh to stop existing services"
    exit 1
fi

# Check if frontend port is already in use
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Frontend port 3000 is already in use"
    echo "   Run: ./stop-all.sh to stop existing services"
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Start Backend
echo "📦 Starting Backend API..."
cd backend
if [ -f "./start.sh" ]; then
    # Use backend's start script
    ./start.sh > ../logs/backend.log 2>&1 &
    # Wait a moment for start.sh to create its PID file and start the process
    sleep 3
    # Get PID from backend's own PID file
    if [ -f "logs/bot.pid" ]; then
        BACKEND_PID=$(cat logs/bot.pid)
        # Verify the PID is valid
        if ! ps -p $BACKEND_PID > /dev/null 2>&1; then
            # Fallback: find the uvicorn process
            BACKEND_PID=$(pgrep -f "uvicorn.*main:app" | head -1)
        fi
    else
        # Fallback: find the uvicorn process
        BACKEND_PID=$(pgrep -f "uvicorn.*main:app" | head -1)
    fi
else
    # Fallback: start backend directly
    nohup python -m uvicorn main:app --host 0.0.0.0 --port 8501 --reload > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
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
echo "🎨 Starting Frontend..."
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


#!/bin/bash

# Start script for both Frontend and Backend (AWS EC2 PRODUCTION)
# This script starts both the FastAPI backend and Next.js frontend in production mode

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🚀 Starting Full Stack Application (Production Mode - AWS EC2)..."
echo ""

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
        echo "⚠️  Warning: Cannot check port $port (ss, netstat, or lsof not found)"
        return 1
    fi
}

# Check if backend port is already in use
if check_port 8501; then
    echo "⚠️  Backend port 8501 is already in use"
    echo "   Run: ./aws-deploy/stop-all.sh to stop existing services"
    exit 1
fi

# Check if frontend port is already in use
if check_port 3000; then
    echo "⚠️  Frontend port 3000 is already in use"
    echo "   Run: ./aws-deploy/stop-all.sh to stop existing services"
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs
mkdir -p backend/logs

# Start Backend
echo "📦 Starting Backend API (Production Mode)..."
cd backend

# Check if uv is available
if command -v uv &> /dev/null; then
    # Use uv run for production (no reload, with workers)
    nohup uv run python -m uvicorn main:app --host 0.0.0.0 --port 8501 --workers 4 > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
else
    # Fallback to system Python
    if [ -d ".venv" ]; then
        nohup .venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8501 --workers 4 > ../logs/backend.log 2>&1 &
        BACKEND_PID=$!
    else
        nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8501 --workers 4 > ../logs/backend.log 2>&1 &
        BACKEND_PID=$!
    fi
fi

cd ..
echo $BACKEND_PID > logs/backend.pid
echo "✅ Backend started (PID: $BACKEND_PID)"
echo "   Backend logs: logs/backend.log"

# Wait a moment for backend to start
sleep 5

# Verify backend is running
if ! ps -p $BACKEND_PID > /dev/null 2>&1; then
    echo "❌ Backend failed to start. Check logs/backend.log for details"
    tail -20 logs/backend.log
    exit 1
fi

# Start Frontend
echo "🎨 Starting Frontend (Production Mode)..."
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "⚠️  node_modules not found. Installing dependencies..."
    npm ci
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install frontend dependencies"
        exit 1
    fi
fi

# Check if production build exists and is valid
BUILD_NEEDED=false
if [ ! -d ".next" ]; then
    echo "⚠️  Production build directory not found. Building..."
    BUILD_NEEDED=true
elif [ ! -f ".next/BUILD_ID" ]; then
    echo "⚠️  Production build is incomplete (missing BUILD_ID). Rebuilding..."
    BUILD_NEEDED=true
else
    echo "✅ Production build found. Verifying..."
    # Check if build is recent (within last 7 days) or force rebuild if needed
    BUILD_AGE=$(find .next/BUILD_ID -mtime +7 2>/dev/null | wc -l)
    if [ "$BUILD_AGE" -gt 0 ]; then
        echo "⚠️  Production build is older than 7 days. Rebuilding..."
        BUILD_NEEDED=true
    fi
fi

# Build if needed
if [ "$BUILD_NEEDED" = true ]; then
    echo "🏗️  Building Next.js application for production..."
    npm run build
    if [ $? -ne 0 ]; then
        echo "❌ Failed to build frontend. Check the output above for errors."
        exit 1
    fi
    echo "✅ Frontend build completed successfully"
fi

# Verify build exists before starting
if [ ! -f ".next/BUILD_ID" ]; then
    echo "❌ Production build is still missing after build attempt. Cannot start frontend."
    echo "   Please check the build output above for errors."
    exit 1
fi

# Start in production mode
echo "🚀 Starting Next.js production server..."
NODE_ENV=production nohup npm run start > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!

cd ..
echo $FRONTEND_PID > logs/frontend.pid
echo "✅ Frontend started (PID: $FRONTEND_PID)"
echo "   Frontend logs: logs/frontend.log"

# Wait a moment for frontend to start
sleep 5

# Verify frontend is running
if ! ps -p $FRONTEND_PID > /dev/null 2>&1; then
    echo "❌ Frontend failed to start. Check logs/frontend.log for details"
    echo ""
    echo "Last 30 lines of frontend.log:"
    tail -30 logs/frontend.log
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
echo "🛑 To stop all services, run: ./aws-deploy/stop-all.sh"
echo "🔄 To restart all services, run: ./aws-deploy/restart-all.sh"


#!/bin/bash

# Start script for both Frontend and Backend (AWS EC2 PRODUCTION)
# This script starts both the FastAPI backend and Next.js frontend in production mode

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/common.sh"
cd "$PROJECT_ROOT"

echo "🚀 Starting Full Stack Application (Production Mode - AWS EC2)..."
echo ""

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
ensure_logs

# Start Backend
echo "📦 Starting Backend API (Production Mode)..."
cd backend

# Check if uv is available
if command -v uv &> /dev/null; then
    # Use uv run for production (no reload, with workers)
    nohup uv run python -m uvicorn main:app --host 0.0.0.0 --port 8501 --workers 4 > "$LOG_DIR/backend.log" 2>&1 &
    BACKEND_PID=$!
else
    # Fallback to system Python
    if [ -d ".venv" ]; then
        nohup .venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8501 --workers 4 > "$LOG_DIR/backend.log" 2>&1 &
        BACKEND_PID=$!
    else
        nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8501 --workers 4 > "$LOG_DIR/backend.log" 2>&1 &
        BACKEND_PID=$!
    fi
fi

cd ..
record_pid "$BACKEND_PID" "backend"
echo "✅ Backend started (PID: $BACKEND_PID)"
echo "   Backend logs: logs/backend.log"

# Wait a moment for backend to start
sleep 5

# Verify backend is running
if ! ps -p $BACKEND_PID > /dev/null 2>&1; then
    echo "❌ Backend failed to start. Check logs/backend.log for details"
    tail -20 "$LOG_DIR/backend.log"
    exit 1
fi

# Start Frontend
echo "🎨 Starting Frontend (Production Mode)..."
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "⚠️  node_modules not found. Installing dependencies..."
    npm ci --include=dev
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install frontend dependencies"
        exit 1
    fi
elif [ ! -d "node_modules/@tailwindcss/postcss" ] || [ ! -d "node_modules/tailwindcss" ]; then
    echo "⚠️  Required Tailwind dependencies missing. Re-installing with dev packages..."
    npm install --include=dev
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install required dev dependencies"
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
NODE_ENV=production nohup npm run start > "$LOG_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!

cd ..
record_pid "$FRONTEND_PID" "frontend"
echo "✅ Frontend started (PID: $FRONTEND_PID)"
echo "   Frontend logs: logs/frontend.log"

# Wait a moment for frontend to start
sleep 5

# Verify frontend is running
if ! ps -p $FRONTEND_PID > /dev/null 2>&1; then
    echo "❌ Frontend failed to start. Check logs/frontend.log for details"
    echo ""
    echo "Last 30 lines of frontend.log:"
    tail -30 "$LOG_DIR/frontend.log"
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


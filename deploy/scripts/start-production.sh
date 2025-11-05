#!/bin/bash

# Production Start Script for AWS EC2
# This script starts the application in production mode
# Usage: ./deploy/scripts/start-production.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
APP_NAME="trading-api"

echo "🚀 Starting Trading API in Production Mode..."
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  Running as root. Services will be managed by systemd."
    echo "   Use: sudo systemctl start ${APP_NAME}-backend ${APP_NAME}-frontend"
    exit 1
fi

# Set production environment
export ENVIRONMENT=production
export NODE_ENV=production

# Start backend (if systemd is not configured)
if ! systemctl is-active --quiet ${APP_NAME}-backend 2>/dev/null; then
    echo "📦 Starting Backend..."
    cd "$DEPLOY_DIR/backend"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d ".venv" ]; then
        echo "   Creating virtual environment..."
        python3 -m venv .venv
        source .venv/bin/activate
        pip install --upgrade pip
        if command -v uv &> /dev/null; then
            uv sync --no-dev
        else
            pip install -e .
        fi
    else
        source .venv/bin/activate
    fi
    
    # Start with uvicorn (production mode)
    nohup python -m uvicorn main:app \
        --host 0.0.0.0 \
        --port 8501 \
        --workers 4 \
        --log-level info \
        > /var/log/trading-api/backend.log 2>&1 &
    
    echo $! > /tmp/${APP_NAME}-backend.pid
    echo "✅ Backend started (PID: $(cat /tmp/${APP_NAME}-backend.pid))"
else
    echo "✅ Backend is already running (managed by systemd)"
fi

# Wait for backend to be ready
echo "⏳ Waiting for backend to be ready..."
sleep 5

# Start frontend (if systemd is not configured)
if ! systemctl is-active --quiet ${APP_NAME}-frontend 2>/dev/null; then
    echo "🎨 Starting Frontend..."
    cd "$DEPLOY_DIR/frontend"
    
    # Build if not already built
    if [ ! -d ".next" ]; then
        echo "   Building frontend..."
        npm run build
    fi
    
    # Start Next.js in production mode
    nohup npm start > /var/log/trading-api/frontend.log 2>&1 &
    
    echo $! > /tmp/${APP_NAME}-frontend.pid
    echo "✅ Frontend started (PID: $(cat /tmp/${APP_NAME}-frontend.pid))"
else
    echo "✅ Frontend is already running (managed by systemd)"
fi

echo ""
echo "✅ Production services started!"
echo ""
echo "📊 Services:"
echo "   Backend API:  http://localhost:8501"
echo "   Backend Docs: http://localhost:8501/docs"
echo "   Frontend:     http://localhost:3000"
echo ""
echo "📝 Logs:"
echo "   Backend:  tail -f /var/log/trading-api/backend.log"
echo "   Frontend: tail -f /var/log/trading-api/frontend.log"
echo ""
echo "🛑 To stop: ./deploy/scripts/stop-production.sh"
echo "   Or use systemd: sudo systemctl stop ${APP_NAME}-backend ${APP_NAME}-frontend"
echo ""


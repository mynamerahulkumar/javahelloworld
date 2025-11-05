#!/bin/bash

# Production Stop Script for AWS EC2
# This script stops the application in production mode
# Usage: ./deploy/scripts/stop-production.sh

set -e

APP_NAME="trading-api"

echo "🛑 Stopping Trading API in Production Mode..."
echo ""

# Stop systemd services if they exist
if systemctl is-active --quiet ${APP_NAME}-backend 2>/dev/null; then
    echo "🛑 Stopping backend (systemd)..."
    sudo systemctl stop ${APP_NAME}-backend
    echo "✅ Backend stopped"
elif [ -f "/tmp/${APP_NAME}-backend.pid" ]; then
    PID=$(cat /tmp/${APP_NAME}-backend.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "🛑 Stopping backend (PID: $PID)..."
        kill $PID
        rm /tmp/${APP_NAME}-backend.pid
        echo "✅ Backend stopped"
    else
        echo "⚠️  Backend process not found"
        rm /tmp/${APP_NAME}-backend.pid
    fi
else
    # Try to find and kill uvicorn processes
    PIDS=$(pgrep -f "uvicorn.*main:app" || true)
    if [ -n "$PIDS" ]; then
        echo "🛑 Stopping backend processes..."
        echo "$PIDS" | xargs kill
        echo "✅ Backend stopped"
    else
        echo "⚠️  No backend process found"
    fi
fi

# Stop frontend
if systemctl is-active --quiet ${APP_NAME}-frontend 2>/dev/null; then
    echo "🛑 Stopping frontend (systemd)..."
    sudo systemctl stop ${APP_NAME}-frontend
    echo "✅ Frontend stopped"
elif [ -f "/tmp/${APP_NAME}-frontend.pid" ]; then
    PID=$(cat /tmp/${APP_NAME}-frontend.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "🛑 Stopping frontend (PID: $PID)..."
        kill $PID
        rm /tmp/${APP_NAME}-frontend.pid
        echo "✅ Frontend stopped"
    else
        echo "⚠️  Frontend process not found"
        rm /tmp/${APP_NAME}-frontend.pid
    fi
else
    # Try to find and kill Next.js processes
    PIDS=$(pgrep -f "next.*start" || true)
    if [ -n "$PIDS" ]; then
        echo "🛑 Stopping frontend processes..."
        echo "$PIDS" | xargs kill
        echo "✅ Frontend stopped"
    else
        echo "⚠️  No frontend process found"
    fi
fi

echo ""
echo "✅ All services stopped!"
echo ""


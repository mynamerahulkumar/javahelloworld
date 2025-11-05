#!/bin/bash

# Stop Backend Service Script for AWS EC2
# Usage: ./deploy/scripts/stop-backend.sh

set -e

APP_NAME="trading-api"
SERVICE_NAME="${APP_NAME}-backend"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}🛑 Stopping Backend Service...${NC}"
echo ""

# Check if systemd service exists
if systemctl list-unit-files | grep -q "^${SERVICE_NAME}.service"; then
    # Check if service is running
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        echo -e "${YELLOW}Stopping ${SERVICE_NAME}...${NC}"
        sudo systemctl stop "$SERVICE_NAME"
        
        # Wait a moment for service to stop
        sleep 2
        
        # Check status
        if ! systemctl is-active --quiet "$SERVICE_NAME"; then
            echo -e "${GREEN}✅ Backend service stopped successfully${NC}"
        else
            echo -e "${RED}❌ Failed to stop backend service${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}⚠️  Backend service is not running${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Systemd service not found${NC}"
    echo "Attempting to stop backend manually..."
    
    # Try to stop using PID file
    if [ -f "/tmp/${APP_NAME}-backend.pid" ]; then
        PID=$(cat /tmp/${APP_NAME}-backend.pid)
        if ps -p $PID > /dev/null 2>&1; then
            echo "Stopping backend process (PID: $PID)..."
            kill $PID
            rm /tmp/${APP_NAME}-backend.pid
            echo -e "${GREEN}✅ Backend stopped${NC}"
        else
            echo -e "${YELLOW}⚠️  PID file exists but process is not running${NC}"
            rm /tmp/${APP_NAME}-backend.pid
        fi
    else
        # Try to find and kill uvicorn processes
        PIDS=$(pgrep -f "uvicorn.*main:app" || true)
        if [ -n "$PIDS" ]; then
            echo "Stopping backend processes..."
            echo "$PIDS" | xargs kill
            echo -e "${GREEN}✅ Backend stopped${NC}"
        else
            echo -e "${YELLOW}⚠️  No backend process found${NC}"
        fi
    fi
fi

echo ""
echo "Backend service stopped."


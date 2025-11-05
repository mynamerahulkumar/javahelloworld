#!/bin/bash

# Stop Frontend Service Script for AWS EC2
# Usage: ./deploy/scripts/stop-frontend.sh

set -e

APP_NAME="trading-api"
SERVICE_NAME="${APP_NAME}-frontend"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}🛑 Stopping Frontend Service...${NC}"
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
            echo -e "${GREEN}✅ Frontend service stopped successfully${NC}"
        else
            echo -e "${RED}❌ Failed to stop frontend service${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}⚠️  Frontend service is not running${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Systemd service not found${NC}"
    echo "Attempting to stop frontend manually..."
    
    # Try to stop using PID file
    if [ -f "/tmp/${APP_NAME}-frontend.pid" ]; then
        PID=$(cat /tmp/${APP_NAME}-frontend.pid)
        if ps -p $PID > /dev/null 2>&1; then
            echo "Stopping frontend process (PID: $PID)..."
            kill $PID
            rm /tmp/${APP_NAME}-frontend.pid
            echo -e "${GREEN}✅ Frontend stopped${NC}"
        else
            echo -e "${YELLOW}⚠️  PID file exists but process is not running${NC}"
            rm /tmp/${APP_NAME}-frontend.pid
        fi
    else
        # Try to find and kill Next.js processes
        PIDS=$(pgrep -f "next.*start" || true)
        if [ -n "$PIDS" ]; then
            echo "Stopping frontend processes..."
            echo "$PIDS" | xargs kill
            echo -e "${GREEN}✅ Frontend stopped${NC}"
        else
            echo -e "${YELLOW}⚠️  No frontend process found${NC}"
        fi
    fi
fi

echo ""
echo "Frontend service stopped."


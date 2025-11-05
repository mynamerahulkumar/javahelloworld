#!/bin/bash

# Start Frontend Service Script for AWS EC2
# Usage: ./deploy/scripts/start-frontend.sh

set -e

APP_NAME="trading-api"
SERVICE_NAME="${APP_NAME}-frontend"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🎨 Starting Frontend Service...${NC}"
echo ""

# Check if systemd service exists
if systemctl list-unit-files | grep -q "^${SERVICE_NAME}.service"; then
    # Check if service is already running
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        echo -e "${YELLOW}⚠️  Frontend service is already running${NC}"
        echo ""
        sudo systemctl status "$SERVICE_NAME" --no-pager | head -n 10
    else
        echo -e "${GREEN}Starting ${SERVICE_NAME}...${NC}"
        sudo systemctl start "$SERVICE_NAME"
        
        # Wait a moment for service to start
        sleep 2
        
        # Check status
        if systemctl is-active --quiet "$SERVICE_NAME"; then
            echo -e "${GREEN}✅ Frontend service started successfully${NC}"
            echo ""
            sudo systemctl status "$SERVICE_NAME" --no-pager | head -n 10
        else
            echo -e "${RED}❌ Failed to start frontend service${NC}"
            echo ""
            echo "Checking logs:"
            sudo journalctl -u "$SERVICE_NAME" -n 20 --no-pager
            exit 1
        fi
    fi
else
    echo -e "${YELLOW}⚠️  Systemd service not found${NC}"
    echo "Attempting to start frontend manually..."
    
    DEPLOY_DIR="/opt/trading-api"
    cd "$DEPLOY_DIR/frontend" 2>/dev/null || {
        echo -e "${RED}❌ Frontend directory not found at $DEPLOY_DIR/frontend${NC}"
        exit 1
    }
    
    # Check if already running
    if pgrep -f "next.*start" > /dev/null; then
        echo -e "${YELLOW}⚠️  Frontend process is already running${NC}"
        pgrep -f "next.*start"
        exit 0
    fi
    
    # Build if needed
    if [ ! -d ".next" ]; then
        echo "Building frontend..."
        npm run build
    fi
    
    # Start frontend
    export NODE_ENV=production
    export PORT=3000
    export HOSTNAME=0.0.0.0
    
    nohup npm start > /var/log/trading-api/frontend.log 2>&1 &
    echo $! > /tmp/${APP_NAME}-frontend.pid
    
    echo -e "${GREEN}✅ Frontend started (PID: $(cat /tmp/${APP_NAME}-frontend.pid))${NC}"
    echo "   Logs: /var/log/trading-api/frontend.log"
fi

echo ""
echo -e "${GREEN}Frontend: http://localhost:3000${NC}"
echo ""
echo "View logs: ./deploy/scripts/view-frontend-logs.sh"
echo "Check status: sudo systemctl status ${SERVICE_NAME}"


#!/bin/bash

# Start Backend Service Script for AWS EC2
# Usage: ./deploy/scripts/start-backend.sh

set -e

APP_NAME="trading-api"
SERVICE_NAME="${APP_NAME}-backend"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🚀 Starting Backend Service...${NC}"
echo ""

# Check if systemd service exists
if systemctl list-unit-files | grep -q "^${SERVICE_NAME}.service"; then
    # Check if service is already running
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        echo -e "${YELLOW}⚠️  Backend service is already running${NC}"
        echo ""
        sudo systemctl status "$SERVICE_NAME" --no-pager | head -n 10
    else
        echo -e "${GREEN}Starting ${SERVICE_NAME}...${NC}"
        sudo systemctl start "$SERVICE_NAME"
        
        # Wait a moment for service to start
        sleep 2
        
        # Check status
        if systemctl is-active --quiet "$SERVICE_NAME"; then
            echo -e "${GREEN}✅ Backend service started successfully${NC}"
            echo ""
            sudo systemctl status "$SERVICE_NAME" --no-pager | head -n 10
        else
            echo -e "${RED}❌ Failed to start backend service${NC}"
            echo ""
            echo "Checking logs:"
            sudo journalctl -u "$SERVICE_NAME" -n 20 --no-pager
            exit 1
        fi
    fi
else
    echo -e "${YELLOW}⚠️  Systemd service not found${NC}"
    echo "Attempting to start backend manually..."
    
    DEPLOY_DIR="/opt/trading-api"
    cd "$DEPLOY_DIR/backend" 2>/dev/null || {
        echo -e "${RED}❌ Backend directory not found at $DEPLOY_DIR/backend${NC}"
        exit 1
    }
    
    # Check if already running
    if pgrep -f "uvicorn.*main:app" > /dev/null; then
        echo -e "${YELLOW}⚠️  Backend process is already running${NC}"
        pgrep -f "uvicorn.*main:app"
        exit 0
    fi
    
    # Create virtual environment if needed
    if [ ! -d ".venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv .venv || python3.12 -m venv .venv || python3.11 -m venv .venv
    fi
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Start backend
    export ENVIRONMENT=production
    export PORT=8501
    export HOST=0.0.0.0
    export WORKERS=4
    
    nohup python -m uvicorn main:app --host 0.0.0.0 --port 8501 --workers 4 > /var/log/trading-api/backend.log 2>&1 &
    echo $! > /tmp/${APP_NAME}-backend.pid
    
    echo -e "${GREEN}✅ Backend started (PID: $(cat /tmp/${APP_NAME}-backend.pid))${NC}"
    echo "   Logs: /var/log/trading-api/backend.log"
fi

echo ""
echo -e "${GREEN}Backend API: http://localhost:8501${NC}"
echo -e "${GREEN}API Docs: http://localhost:8501/docs${NC}"
echo ""
echo "View logs: ./deploy/scripts/view-backend-logs.sh"
echo "Check status: sudo systemctl status ${SERVICE_NAME}"


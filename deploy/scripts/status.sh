#!/bin/bash

# Service Status Checker Script for AWS EC2
# Shows status of all services
# Usage: ./deploy/scripts/status.sh

set -e

APP_NAME="trading-api"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}📊 Trading API Service Status${NC}"
echo "=========================================="
echo ""

# Function to check service status
check_service() {
    local service=$1
    local service_name="${APP_NAME}-${service}"
    
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}${service_name}${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    if systemctl list-unit-files | grep -q "^${service_name}.service"; then
        # Systemd service exists
        if systemctl is-active --quiet "$service_name"; then
            echo -e "${GREEN}Status: ✅ Running${NC}"
        else
            echo -e "${RED}Status: ❌ Stopped${NC}"
        fi
        
        if systemctl is-enabled --quiet "$service_name"; then
            echo -e "${GREEN}Auto-start: ✅ Enabled${NC}"
        else
            echo -e "${YELLOW}Auto-start: ⚠️  Disabled${NC}"
        fi
        
        echo ""
        echo -e "${YELLOW}Details:${NC}"
        sudo systemctl status "$service_name" --no-pager | head -n 8
    else
        # Check if running manually
        if [ "$service" = "backend" ]; then
            PIDS=$(pgrep -f "uvicorn.*main:app" || true)
            if [ -n "$PIDS" ]; then
                echo -e "${GREEN}Status: ✅ Running (manual)${NC}"
                echo "PIDs: $PIDS"
            else
                echo -e "${RED}Status: ❌ Stopped${NC}"
            fi
        elif [ "$service" = "frontend" ]; then
            PIDS=$(pgrep -f "next.*start" || true)
            if [ -n "$PIDS" ]; then
                echo -e "${GREEN}Status: ✅ Running (manual)${NC}"
                echo "PIDs: $PIDS"
            else
                echo -e "${RED}Status: ❌ Stopped${NC}"
            fi
        fi
        
        echo -e "${YELLOW}⚠️  Systemd service not configured${NC}"
    fi
    
    echo ""
}

# Check backend
check_service "backend"

# Check frontend
check_service "frontend"

# Summary
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📋 Quick Commands${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Start all:     ./deploy/scripts/start-all.sh"
echo "Stop all:      ./deploy/scripts/stop-all.sh"
echo "Restart all:   ./deploy/scripts/restart-all.sh"
echo "View logs:     ./deploy/scripts/view-logs.sh"
echo ""


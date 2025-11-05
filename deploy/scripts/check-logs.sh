#!/bin/bash

# Comprehensive Log Checker Script
# Shows log file locations, service status, and recent log entries
# Usage: ./deploy/scripts/check-logs.sh [backend|frontend|all]

set -e

SERVICE="${1:-all}"
APP_NAME="trading-api"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Function to check service status
check_service() {
    local service=$1
    local service_name="${APP_NAME}-${service}"
    
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}📊 ${service_name} Status${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    if systemctl list-unit-files | grep -q "^${service_name}.service"; then
        # Service exists
        if systemctl is-active --quiet "$service_name"; then
            echo -e "${GREEN}✅ Service is running${NC}"
        else
            echo -e "${RED}❌ Service is not running${NC}"
        fi
        
        # Show status
        echo ""
        echo -e "${YELLOW}Service Status:${NC}"
        sudo systemctl status "$service_name" --no-pager -l | head -n 15
        
        # Log file locations
        echo ""
        echo -e "${YELLOW}Log Locations:${NC}"
        echo "  Systemd Journal: sudo journalctl -u ${service_name}"
        echo "  Log File: /var/log/trading-api/${service}.log"
        echo "  Error Log: /var/log/trading-api/${service}.error.log"
        
        # Recent log entries
        echo ""
        echo -e "${YELLOW}Recent Log Entries (last 10 lines):${NC}"
        sudo journalctl -u "$service_name" -n 10 --no-pager | tail -n 10
        
    else
        echo -e "${YELLOW}⚠️  Systemd service not found${NC}"
        
        # Check file-based logs
        LOG_FILE="/var/log/trading-api/${service}.log"
        ERROR_LOG="/var/log/trading-api/${service}.error.log"
        
        if [ -f "$LOG_FILE" ] || [ -f "$ERROR_LOG" ]; then
            echo -e "${YELLOW}File-based logs found:${NC}"
            if [ -f "$LOG_FILE" ]; then
                echo "  ✅ $LOG_FILE ($(du -h "$LOG_FILE" | cut -f1))"
                echo -e "${YELLOW}  Last 5 lines:${NC}"
                tail -n 5 "$LOG_FILE" | sed 's/^/    /'
            fi
            if [ -f "$ERROR_LOG" ]; then
                echo "  ✅ $ERROR_LOG ($(du -h "$ERROR_LOG" | cut -f1))"
                if [ -s "$ERROR_LOG" ]; then
                    echo -e "${YELLOW}  Last 5 lines:${NC}"
                    tail -n 5 "$ERROR_LOG" | sed 's/^/    /'
                fi
            fi
        else
            echo -e "${RED}❌ No log files found${NC}"
        fi
    fi
    
    echo ""
}

# Function to show quick commands
show_commands() {
    local service=$1
    
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}🔧 Quick Commands${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${YELLOW}View logs in real-time:${NC}"
    echo "  ./deploy/scripts/view-${service}-logs.sh"
    echo ""
    echo -e "${YELLOW}View last 100 lines:${NC}"
    echo "  ./deploy/scripts/view-${service}-logs.sh --last 100"
    echo ""
    echo -e "${YELLOW}Using systemd journalctl:${NC}"
    echo "  sudo journalctl -u ${APP_NAME}-${service} -f"
    echo "  sudo journalctl -u ${APP_NAME}-${service} -n 100"
    echo ""
    echo -e "${YELLOW}Check service status:${NC}"
    echo "  sudo systemctl status ${APP_NAME}-${service}"
    echo ""
}

# Main logic
case "$SERVICE" in
    backend)
        check_service "backend"
        show_commands "backend"
        ;;
    frontend)
        check_service "frontend"
        show_commands "frontend"
        ;;
    all|*)
        if [ "$SERVICE" != "all" ] && [ "$SERVICE" != "" ]; then
            echo -e "${RED}❌ Unknown service: $SERVICE${NC}"
            echo "Usage: $0 [backend|frontend|all]"
            exit 1
        fi
        
        echo -e "${GREEN}🔍 Trading API Log Checker${NC}"
        echo ""
        check_service "backend"
        check_service "frontend"
        
        echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${BLUE}📝 All Log Commands${NC}"
        echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo -e "${YELLOW}View all logs:${NC}"
        echo "  ./deploy/scripts/view-logs.sh"
        echo ""
        echo -e "${YELLOW}View backend logs:${NC}"
        echo "  ./deploy/scripts/view-logs.sh backend"
        echo ""
        echo -e "${YELLOW}View frontend logs:${NC}"
        echo "  ./deploy/scripts/view-logs.sh frontend"
        echo ""
        ;;
esac


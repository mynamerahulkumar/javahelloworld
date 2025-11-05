#!/bin/bash

# Log Viewer Script for Trading API
# View logs for backend, frontend, or both
# Usage: ./deploy/scripts/view-logs.sh [backend|frontend|all] [--tail|--last N]

set -e

APP_NAME="trading-api"
SERVICE="$1"
MODE="${2:---tail}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to show usage
show_usage() {
    echo "Usage: $0 [backend|frontend|all] [--tail|--last N]"
    echo ""
    echo "Options:"
    echo "  backend    - Show backend logs only"
    echo "  frontend   - Show frontend logs only"
    echo "  all        - Show both backend and frontend logs (default)"
    echo ""
    echo "Modes:"
    echo "  --tail     - Follow logs in real-time (default)"
    echo "  --last N   - Show last N lines (e.g., --last 100)"
    echo ""
    echo "Examples:"
    echo "  $0                    # Follow all logs"
    echo "  $0 backend            # Follow backend logs"
    echo "  $0 frontend --last 50 # Show last 50 lines of frontend logs"
    echo "  $0 all --last 200     # Show last 200 lines of all logs"
}

# Check if service is specified
if [ -z "$SERVICE" ]; then
    SERVICE="all"
fi

# Check if MODE is --last and extract number
if [[ "$MODE" == --last* ]]; then
    LINES=$(echo "$MODE" | cut -d' ' -f2)
    if [ -z "$LINES" ]; then
        LINES=100  # Default to 100 lines
    fi
    MODE="--last"
else
    MODE="--tail"
    LINES=100
fi

# Function to check if systemd service exists
service_exists() {
    systemctl list-unit-files | grep -q "^${APP_NAME}-$1.service"
}

# Function to view systemd logs
view_systemd_logs() {
    local service=$1
    local service_name="${APP_NAME}-${service}"
    
    if service_exists "$service"; then
        echo -e "${GREEN}📋 ${service_name} logs (systemd)${NC}"
        echo -e "${BLUE}========================================${NC}"
        
        if [ "$MODE" = "--tail" ]; then
            sudo journalctl -u "$service_name" -f
        else
            sudo journalctl -u "$service_name" -n "$LINES" --no-pager
        fi
    else
        echo -e "${YELLOW}⚠️  Systemd service $service_name not found${NC}"
        return 1
    fi
}

# Function to view file-based logs
view_file_logs() {
    local service=$1
    local log_file="/var/log/trading-api/${service}.log"
    local error_log="/var/log/trading-api/${service}.error.log"
    
    if [ -f "$log_file" ] || [ -f "$error_log" ]; then
        echo -e "${GREEN}📋 ${service} logs (file-based)${NC}"
        echo -e "${BLUE}========================================${NC}"
        
        if [ "$MODE" = "--tail" ]; then
            if [ -f "$log_file" ]; then
                echo -e "${YELLOW}Standard output:${NC}"
                tail -f "$log_file" &
                TAIL_PID=$!
            fi
            if [ -f "$error_log" ]; then
                echo -e "${YELLOW}Error output:${NC}"
                tail -f "$error_log" &
                TAIL_PID2=$!
            fi
            # Wait for interrupt
            trap "kill $TAIL_PID $TAIL_PID2 2>/dev/null; exit" INT TERM
            wait
        else
            if [ -f "$log_file" ]; then
                echo -e "${YELLOW}Standard output (last $LINES lines):${NC}"
                tail -n "$LINES" "$log_file"
            fi
            if [ -f "$error_log" ]; then
                echo -e "${YELLOW}Error output (last $LINES lines):${NC}"
                tail -n "$LINES" "$error_log"
            fi
        fi
    else
        echo -e "${YELLOW}⚠️  Log files not found at $log_file${NC}"
        return 1
    fi
}

# Function to view logs (try systemd first, then file-based)
view_logs() {
    local service=$1
    
    if service_exists "$service"; then
        view_systemd_logs "$service"
    else
        view_file_logs "$service"
    fi
}

# Main logic
case "$SERVICE" in
    backend)
        echo -e "${GREEN}🔍 Viewing Backend Logs${NC}"
        echo ""
        view_logs "backend"
        ;;
    frontend)
        echo -e "${GREEN}🔍 Viewing Frontend Logs${NC}"
        echo ""
        view_logs "frontend"
        ;;
    all|*)
        if [ "$SERVICE" != "all" ] && [ "$SERVICE" != "" ]; then
            echo -e "${RED}❌ Unknown service: $SERVICE${NC}"
            show_usage
            exit 1
        fi
        
        echo -e "${GREEN}🔍 Viewing All Logs${NC}"
        echo ""
        
        if [ "$MODE" = "--tail" ]; then
            echo -e "${YELLOW}⚠️  Following multiple services. Use Ctrl+C to stop.${NC}"
            echo -e "${YELLOW}   To view separately, use: $0 backend or $0 frontend${NC}"
            echo ""
            
            # Use journalctl to follow multiple services
            if service_exists "backend" && service_exists "frontend"; then
                sudo journalctl -u "${APP_NAME}-backend" -u "${APP_NAME}-frontend" -f
            elif service_exists "backend"; then
                view_logs "backend"
            elif service_exists "frontend"; then
                view_logs "frontend"
            else
                echo -e "${RED}❌ No services found. Are services running?${NC}"
                echo "   Check status: sudo systemctl status ${APP_NAME}-backend ${APP_NAME}-frontend"
                exit 1
            fi
        else
            # Show last N lines for all services
            if service_exists "backend"; then
                view_systemd_logs "backend"
                echo ""
            fi
            if service_exists "frontend"; then
                view_systemd_logs "frontend"
                echo ""
            fi
            
            # Also show file-based logs if systemd doesn't exist
            if ! service_exists "backend" && ! service_exists "frontend"; then
                view_file_logs "backend"
                echo ""
                view_file_logs "frontend"
            fi
        fi
        ;;
esac


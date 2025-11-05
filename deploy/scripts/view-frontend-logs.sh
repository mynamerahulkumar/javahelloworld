#!/bin/bash

# Frontend Log Viewer Script
# Quick script to view frontend logs
# Usage: ./deploy/scripts/view-frontend-logs.sh [--tail|--last N]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

MODE="${1:---tail}"
APP_NAME="trading-api"

echo -e "${GREEN}📋 Frontend Logs${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if systemd service exists
if systemctl list-unit-files | grep -q "^${APP_NAME}-frontend.service"; then
    if [ "$MODE" = "--tail" ]; then
        echo -e "${YELLOW}Following logs (Ctrl+C to stop)...${NC}"
        echo ""
        sudo journalctl -u "${APP_NAME}-frontend" -f
    else
        LINES=$(echo "$MODE" | cut -d' ' -f2)
        if [ -z "$LINES" ]; then
            LINES=100
        fi
        sudo journalctl -u "${APP_NAME}-frontend" -n "$LINES" --no-pager
    fi
else
    # Try file-based logs
    LOG_FILE="/var/log/trading-api/frontend.log"
    ERROR_LOG="/var/log/trading-api/frontend.error.log"
    
    if [ -f "$LOG_FILE" ] || [ -f "$ERROR_LOG" ]; then
        if [ "$MODE" = "--tail" ]; then
            echo -e "${YELLOW}Following logs (Ctrl+C to stop)...${NC}"
            echo ""
            if [ -f "$LOG_FILE" ]; then
                echo -e "${YELLOW}Standard output:${NC}"
                tail -f "$LOG_FILE"
            fi
            if [ -f "$ERROR_LOG" ]; then
                echo -e "${YELLOW}Error output:${NC}"
                tail -f "$ERROR_LOG"
            fi
        else
            LINES=$(echo "$MODE" | cut -d' ' -f2)
            if [ -z "$LINES" ]; then
                LINES=100
            fi
            if [ -f "$LOG_FILE" ]; then
                echo -e "${YELLOW}Standard output (last $LINES lines):${NC}"
                tail -n "$LINES" "$LOG_FILE"
            fi
            if [ -f "$ERROR_LOG" ]; then
                echo -e "${YELLOW}Error output (last $LINES lines):${NC}"
                tail -n "$LINES" "$ERROR_LOG"
            fi
        fi
    else
        echo -e "${YELLOW}⚠️  No frontend logs found.${NC}"
        echo "   Check if frontend service is running:"
        echo "   sudo systemctl status ${APP_NAME}-frontend"
        exit 1
    fi
fi


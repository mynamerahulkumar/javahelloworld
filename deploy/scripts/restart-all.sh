#!/bin/bash

# Restart All Services Script for AWS EC2
# Restarts both backend and frontend services
# Usage: ./deploy/scripts/restart-all.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔄 Restarting All Trading API Services${NC}"
echo "=========================================="
echo ""

# Stop all services
echo -e "${YELLOW}Stopping all services...${NC}"
"$SCRIPT_DIR/stop-all.sh"
echo ""

# Wait a moment
sleep 3

# Start all services
echo -e "${GREEN}Starting all services...${NC}"
"$SCRIPT_DIR/start-all.sh"
echo ""

echo -e "${GREEN}✅ All Services Restarted!${NC}"
echo ""
echo "Services:"
echo "  Backend API:  http://localhost:8501"
echo "  Backend Docs: http://localhost:8501/docs"
echo "  Frontend:     http://localhost:3000"
echo ""
echo "Check status: ./deploy/scripts/check-logs.sh"
echo ""


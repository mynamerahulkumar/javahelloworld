#!/bin/bash

# Start All Services Script for AWS EC2
# Starts both backend and frontend services
# Usage: ./deploy/scripts/start-all.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Starting All Trading API Services${NC}"
echo "=========================================="
echo ""

# Start backend
echo -e "${GREEN}📦 Starting Backend...${NC}"
"$SCRIPT_DIR/start-backend.sh"
echo ""

# Wait a moment for backend to be ready
sleep 3

# Start frontend
echo -e "${GREEN}🎨 Starting Frontend...${NC}"
"$SCRIPT_DIR/start-frontend.sh"
echo ""

echo -e "${GREEN}✅ All Services Started!${NC}"
echo ""
echo "Services:"
echo "  Backend API:  http://localhost:8501"
echo "  Backend Docs: http://localhost:8501/docs"
echo "  Frontend:     http://localhost:3000"
echo ""
echo "Commands:"
echo "  View logs:    ./deploy/scripts/view-logs.sh"
echo "  Stop all:     ./deploy/scripts/stop-all.sh"
echo "  Restart all:  ./deploy/scripts/restart-all.sh"
echo "  Check status: ./deploy/scripts/check-logs.sh"
echo ""


#!/bin/bash

# Restart Frontend Service Script for AWS EC2
# Usage: ./deploy/scripts/restart-frontend.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔄 Restarting Frontend Service...${NC}"
echo "=========================================="
echo ""

# Stop frontend
echo -e "${YELLOW}Stopping frontend...${NC}"
"$SCRIPT_DIR/stop-frontend.sh"
echo ""

# Wait a moment
sleep 2

# Start frontend
echo -e "${GREEN}Starting frontend...${NC}"
"$SCRIPT_DIR/start-frontend.sh"
echo ""

echo -e "${GREEN}✅ Frontend restarted successfully!${NC}"
echo ""


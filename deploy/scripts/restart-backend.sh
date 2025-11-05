#!/bin/bash

# Restart Backend Service Script for AWS EC2
# Usage: ./deploy/scripts/restart-backend.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔄 Restarting Backend Service...${NC}"
echo "=========================================="
echo ""

# Stop backend
echo -e "${YELLOW}Stopping backend...${NC}"
"$SCRIPT_DIR/stop-backend.sh"
echo ""

# Wait a moment
sleep 2

# Start backend
echo -e "${GREEN}Starting backend...${NC}"
"$SCRIPT_DIR/start-backend.sh"
echo ""

echo -e "${GREEN}✅ Backend restarted successfully!${NC}"
echo ""


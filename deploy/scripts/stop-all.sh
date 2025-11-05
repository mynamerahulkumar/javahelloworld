#!/bin/bash

# Stop All Services Script for AWS EC2
# Stops both backend and frontend services
# Usage: ./deploy/scripts/stop-all.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🛑 Stopping All Trading API Services${NC}"
echo "=========================================="
echo ""

# Stop backend
echo -e "${YELLOW}📦 Stopping Backend...${NC}"
"$SCRIPT_DIR/stop-backend.sh"
echo ""

# Stop frontend
echo -e "${YELLOW}🎨 Stopping Frontend...${NC}"
"$SCRIPT_DIR/stop-frontend.sh"
echo ""

echo -e "${GREEN}✅ All Services Stopped!${NC}"
echo ""
echo "To start services again:"
echo "  ./deploy/scripts/start-all.sh"
echo ""


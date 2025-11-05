#!/bin/bash

# AWS EC2 Deployment Script
# This script deploys the application to an AWS EC2 instance
# Usage: ./deploy/aws-deploy.sh [EC2_HOST] [EC2_USER]

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Configuration
EC2_HOST="${1:-${EC2_HOST}}"
EC2_USER="${2:-${EC2_USER:-ec2-user}}"  # Default to ec2-user for Amazon Linux
EC2_SSH_KEY="${EC2_SSH_KEY:-~/.ssh/id_rsa}"
DEPLOY_DIR="${DEPLOY_DIR:-/opt/trading-api}"
APP_NAME="trading-api"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if EC2_HOST is provided
if [ -z "$EC2_HOST" ]; then
    echo -e "${RED}Error: EC2_HOST is required${NC}"
    echo "Usage: $0 [EC2_HOST] [EC2_USER]"
    echo "Or set environment variables: EC2_HOST, EC2_USER, EC2_SSH_KEY"
    exit 1
fi

echo -e "${GREEN}🚀 Starting AWS EC2 Deployment${NC}"
echo "=========================================="
echo "EC2 Host: $EC2_HOST"
echo "EC2 User: $EC2_USER"
echo "Deploy Directory: $DEPLOY_DIR"
echo "=========================================="
echo ""

# Test SSH connection
echo -e "${YELLOW}📡 Testing SSH connection...${NC}"
if ! ssh -i "$EC2_SSH_KEY" -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$EC2_USER@$EC2_HOST" "echo 'Connection successful'" > /dev/null 2>&1; then
    echo -e "${RED}❌ Failed to connect to EC2 instance${NC}"
    echo "Please check:"
    echo "  1. EC2_HOST is correct: $EC2_HOST"
    echo "  2. SSH key path is correct: $EC2_SSH_KEY"
    echo "  3. Security group allows SSH (port 22)"
    echo "  4. EC2 instance is running"
    exit 1
fi
echo -e "${GREEN}✅ SSH connection successful${NC}"
echo ""

# Create deployment package (exclude unnecessary files)
echo -e "${YELLOW}📦 Creating deployment package...${NC}"
cd "$PROJECT_ROOT"
TEMP_DIR=$(mktemp -d)
DEPLOY_PACKAGE="$TEMP_DIR/${APP_NAME}.tar.gz"

# Create a clean copy for deployment
rsync -av \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='node_modules' \
    --exclude='.next' \
    --exclude='logs' \
    --exclude='*.log' \
    --exclude='*.pid' \
    --exclude='privatedata' \
    --exclude='.env' \
    --exclude='.DS_Store' \
    --exclude='deploy/.env.production' \
    --exclude='backup_code' \
    --exclude='.vscode' \
    --exclude='.idea' \
    "$PROJECT_ROOT/" "$TEMP_DIR/$APP_NAME/"

# Create tarball
cd "$TEMP_DIR"
tar -czf "$DEPLOY_PACKAGE" "$APP_NAME/"
echo -e "${GREEN}✅ Deployment package created: $(du -h "$DEPLOY_PACKAGE" | cut -f1)${NC}"
echo ""

# Upload to EC2
echo -e "${YELLOW}📤 Uploading to EC2 instance...${NC}"
scp -i "$EC2_SSH_KEY" "$DEPLOY_PACKAGE" "$EC2_USER@$EC2_HOST:/tmp/"
echo -e "${GREEN}✅ Upload complete${NC}"
echo ""

# Run deployment script on EC2
echo -e "${YELLOW}🔧 Running deployment on EC2 instance...${NC}"
ssh -i "$EC2_SSH_KEY" "$EC2_USER@$EC2_HOST" << 'ENDSSH'
    set -e
    
    APP_NAME="trading-api"
    DEPLOY_DIR="/opt/trading-api"
    DEPLOY_PACKAGE="/tmp/${APP_NAME}.tar.gz"
    
    # Extract deployment package
    echo "📦 Extracting deployment package..."
    sudo mkdir -p "$DEPLOY_DIR"
    sudo tar -xzf "$DEPLOY_PACKAGE" -C "$DEPLOY_DIR/" --strip-components=1
    
    # Set ownership
    sudo chown -R $USER:$USER "$DEPLOY_DIR"
    
    # Install/update dependencies
    echo "📥 Installing dependencies..."
    
    # Backend dependencies
    if [ -f "$DEPLOY_DIR/backend/pyproject.toml" ]; then
        cd "$DEPLOY_DIR/backend"
        # Use python3.12 if available, otherwise python3
        PYTHON_CMD="python3"
        if command -v python3.12 &> /dev/null; then
            PYTHON_CMD="python3.12"
        elif command -v python3.11 &> /dev/null; then
            PYTHON_CMD="python3.11"
        fi
        
        # Create virtual environment if it doesn't exist
        if [ ! -d ".venv" ]; then
            echo "📦 Creating virtual environment..."
            $PYTHON_CMD -m venv .venv
        fi
        
        # Activate virtual environment
        source .venv/bin/activate
        
        # Upgrade pip
        pip install --upgrade pip setuptools wheel
        
        # Install dependencies
        if command -v uv &> /dev/null; then
            uv sync --no-dev
        else
            pip install -e .
        fi
    fi
    
    # Frontend dependencies and build
    if [ -f "$DEPLOY_DIR/frontend/package.json" ]; then
        cd "$DEPLOY_DIR/frontend"
        if [ ! -d "node_modules" ]; then
            npm ci --production=false
        fi
        echo "🏗️  Building frontend..."
        npm run build
    fi
    
    # Create necessary directories
    mkdir -p "$DEPLOY_DIR/logs"
    mkdir -p "$DEPLOY_DIR/backend/logs"
    mkdir -p "$DEPLOY_DIR/backend/privatedata"
    
    # Set up systemd services (if not already done)
    if [ ! -f "/etc/systemd/system/${APP_NAME}-backend.service" ]; then
        echo "🔧 Setting up systemd services..."
        sudo "$DEPLOY_DIR/deploy/scripts/setup-systemd.sh"
    fi
    
    # Reload systemd and restart services
    sudo systemctl daemon-reload
    
    echo "✅ Deployment complete!"
ENDSSH

# Cleanup
rm -rf "$TEMP_DIR"

echo ""
echo -e "${GREEN}✅ Deployment Successful!${NC}"
echo ""
echo "Next steps:"
echo "  1. Copy environment files to EC2:"
echo "     scp -i $EC2_SSH_KEY deploy/.env.production $EC2_USER@$EC2_HOST:$DEPLOY_DIR/backend/.env"
echo "     scp -i $EC2_SSH_KEY deploy/.env.production $EC2_USER@$EC2_HOST:$DEPLOY_DIR/frontend/.env.local"
echo ""
echo "  2. Copy private data (if needed):"
echo "     scp -i $EC2_SSH_KEY -r privatedata/ $EC2_USER@$EC2_HOST:$DEPLOY_DIR/backend/"
echo ""
echo "  3. Start services on EC2:"
echo "     ssh -i $EC2_SSH_KEY $EC2_USER@$EC2_HOST 'sudo systemctl start ${APP_NAME}-backend ${APP_NAME}-frontend'"
echo ""
echo "  4. Check service status:"
echo "     ssh -i $EC2_SSH_KEY $EC2_USER@$EC2_HOST 'sudo systemctl status ${APP_NAME}-backend ${APP_NAME}-frontend'"
echo ""


#!/bin/bash

# Deployment script for AWS EC2 Linux
# This script sets up the application for production deployment
# It calls install-dependencies.sh to install all dependencies

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🚀 Setting up application for AWS EC2 Linux deployment..."
echo ""

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "⚠️  Warning: This script is optimized for Linux. Current OS: $OSTYPE"
fi

# Run the installation script
echo "📦 Installing all dependencies..."
if [ -f "$SCRIPT_DIR/install-dependencies.sh" ]; then
    chmod +x "$SCRIPT_DIR/install-dependencies.sh"
    "$SCRIPT_DIR/install-dependencies.sh"
else
    echo "❌ install-dependencies.sh not found in aws-deploy directory"
    exit 1
fi

# Set executable permissions on scripts
echo ""
echo "🔧 Setting executable permissions..."
chmod +x "$SCRIPT_DIR/start-all.sh" "$SCRIPT_DIR/stop-all.sh" "$SCRIPT_DIR/restart-all.sh"
chmod +x "$SCRIPT_DIR/backend/start.sh" "$SCRIPT_DIR/backend/stop.sh" "$SCRIPT_DIR/backend/restart.sh"
chmod +x "$SCRIPT_DIR/setup-systemd.sh" "$SCRIPT_DIR/deploy.sh"

echo ""
echo "✅ Deployment setup complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Configure environment variables:"
echo "      - Backend: nano backend/.env"
echo "      - Frontend: nano frontend/.env.local"
echo "   2. Start services:"
echo "      - Using scripts: ./aws-deploy/start-all.sh"
echo "      - Using systemd: sudo ./aws-deploy/setup-systemd.sh"


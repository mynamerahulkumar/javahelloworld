#!/bin/bash

# Deployment script for AWS EC2 Linux
# This script sets up the application for production deployment

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Setting up application for AWS EC2 Linux deployment..."
echo ""

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "⚠️  Warning: This script is optimized for Linux. Current OS: $OSTYPE"
fi

# Install system dependencies (if needed)
echo "📦 Checking system dependencies..."

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.12+"
    exit 1
fi

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+"
    exit 1
fi

# Check for uv (Python package manager)
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv (Python package manager)..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
if [ -f "pyproject.toml" ]; then
    uv sync
else
    echo "❌ pyproject.toml not found in backend directory"
    exit 1
fi
cd ..

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
if [ -f "package.json" ]; then
    npm ci --production=false
else
    echo "❌ package.json not found in frontend directory"
    exit 1
fi
cd ..

# Build frontend for production
echo "🏗️  Building frontend for production..."
cd frontend
npm run build
cd ..

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p backend/logs
chmod 755 logs backend/logs

# Set executable permissions on scripts
echo "🔧 Setting executable permissions..."
chmod +x start-all.sh stop-all.sh restart-all.sh
chmod +x backend/start.sh backend/stop.sh backend/restart.sh
chmod +x scripts/*.sh 2>/dev/null || true

echo ""
echo "✅ Deployment setup complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Configure environment variables in backend/.env"
echo "   2. Configure environment variables in frontend/.env.local"
echo "   3. Start services: ./start-all.sh"
echo "   4. Or use systemd services: sudo ./setup-systemd.sh"


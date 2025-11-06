#!/bin/bash

# Build script for Frontend (Production)
# This script builds the Next.js frontend for production

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT/frontend"

echo "🏗️  Building Frontend for Production..."
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "⚠️  node_modules not found. Installing dependencies..."
    npm ci
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
fi

# Clean previous build if it exists
if [ -d ".next" ]; then
    echo "🧹 Cleaning previous build..."
    rm -rf .next
fi

# Build for production
echo "📦 Building Next.js application..."
npm run build

# Verify build was successful
if [ $? -ne 0 ]; then
    echo "❌ Build failed. Check the output above for errors."
    exit 1
fi

# Verify build files exist
if [ ! -f ".next/BUILD_ID" ]; then
    echo "❌ Build completed but BUILD_ID file is missing. Build may have failed."
    exit 1
fi

BUILD_ID=$(cat .next/BUILD_ID 2>/dev/null || echo "N/A")
echo ""
echo "✅ Frontend built successfully!"
echo "   Build ID: $BUILD_ID"
echo "   Build directory: .next/"
echo ""
echo "📝 Next steps:"
echo "   - Start services: ./aws-deploy/start-all.sh"
echo "   - Or restart services: ./aws-deploy/restart-all.sh"


#!/bin/bash

# Simple build script for Frontend (Production)
# This script builds with increased memory and simpler output

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT/frontend"

echo "🏗️  Building Frontend for Production (Simple Mode)..."
echo ""

# Check system resources
echo "📊 System Resources:"
free -h
echo ""
df -h . | head -2
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "⚠️  Installing dependencies..."
    npm ci
fi

# Clean previous build
if [ -d ".next" ]; then
    echo "🧹 Cleaning previous build..."
    rm -rf .next
fi

# Build with increased memory allocation
echo "📦 Building Next.js application..."
echo "   Using increased memory allocation (4GB)"
echo "   This may take 5-10 minutes..."
echo ""

# Set Node.js memory limit and build
NODE_OPTIONS="--max-old-space-size=4096" npm run build

# Check result
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Build failed!"
    echo ""
    echo "💡 Try:"
    echo "   1. Check memory: free -h"
    echo "   2. Check disk space: df -h"
    echo "   3. Check frontend/.env.local for missing variables"
    exit 1
fi

# Verify build
if [ ! -f ".next/BUILD_ID" ]; then
    echo "❌ Build ID missing. Build may have failed."
    exit 1
fi

echo ""
echo "✅ Build completed successfully!"
echo "   Build ID: $(cat .next/BUILD_ID)"




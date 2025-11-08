#!/bin/bash

# Minimal dependency installation script
# This script installs only production dependencies to save space

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "📦 Installing Minimal Dependencies (Production Only)..."
echo ""

# Install Frontend dependencies (production only)
echo "🎨 Installing Frontend dependencies (production only)..."
cd frontend

# Clean previous installation
if [ -d "node_modules" ]; then
    echo "   Removing existing node_modules..."
    rm -rf node_modules
fi

# Install only production dependencies
echo "   Installing production dependencies..."
npm ci --production=false  # We need dev deps for build, but will clean after

# Build for production
echo "   Building for production..."
npm run build

# Remove dev dependencies after build
echo "   Removing development dependencies..."
npm prune --production

cd ..

# Install Backend dependencies
echo "📦 Installing Backend dependencies..."
cd backend

# Install with uv (already optimized)
if command -v uv &> /dev/null; then
    echo "   Installing with uv..."
    uv sync
else
    echo "   ⚠️  uv not found. Please install it first."
    exit 1
fi

cd ..

# Run optimization
echo ""
echo "🔧 Running optimization..."
"$SCRIPT_DIR/optimize-dependencies.sh"

echo ""
echo "✅ Minimal dependencies installed!"
echo ""
echo "📊 Final disk usage:"
du -sh frontend backend 2>/dev/null | awk '{print "   " $2 ": " $1}'




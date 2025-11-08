#!/bin/bash

# Safe remove dependencies script (keeps package-lock.json and config files)
# This script removes installed dependencies but keeps configuration files

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🗑️  Removing Dependencies (Safe Mode)..."
echo ""
echo "This will remove:"
echo "   - Frontend: node_modules, .next"
echo "   - Backend: .venv, __pycache__, *.pyc"
echo "   - Caches: npm, pip, uv"
echo ""
echo "This will KEEP:"
echo "   - package.json, package-lock.json"
echo "   - pyproject.toml, requirements files"
echo "   - Configuration files"
echo ""

# Remove Frontend dependencies
echo "🧹 Removing Frontend dependencies..."
cd frontend

# Remove node_modules
if [ -d "node_modules" ]; then
    echo "   Removing node_modules..."
    rm -rf node_modules
    echo "   ✅ node_modules removed"
fi

# Remove .next build directory
if [ -d ".next" ]; then
    echo "   Removing .next build directory..."
    rm -rf .next
    echo "   ✅ .next removed"
fi

# Clean npm cache (but keep package-lock.json)
echo "   Cleaning npm cache..."
npm cache clean --force 2>/dev/null || true
echo "   ✅ npm cache cleaned"

# Remove cache directories
rm -rf .next/cache 2>/dev/null || true
rm -rf node_modules/.cache 2>/dev/null || true

cd ..

# Remove Backend dependencies
echo ""
echo "🧹 Removing Backend dependencies..."
cd backend

# Remove .venv
if [ -d ".venv" ]; then
    echo "   Removing .venv virtual environment..."
    rm -rf .venv
    echo "   ✅ .venv removed"
fi

# Remove Python cache
echo "   Removing Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
echo "   ✅ Python cache removed"

# Clean caches
if command -v uv &> /dev/null; then
    echo "   Cleaning uv cache..."
    uv cache clean 2>/dev/null || true
    echo "   ✅ uv cache cleaned"
fi

if [ -d "$HOME/.cache/pip" ]; then
    echo "   Cleaning pip cache..."
    rm -rf "$HOME/.cache/pip" 2>/dev/null || true
    echo "   ✅ pip cache cleaned"
fi

cd ..

echo ""
echo "✅ Dependencies removed (configuration files preserved)!"
echo ""
echo "📝 Next steps:"
echo "   1. Reinstall: ./aws-deploy/install-dependencies.sh"
echo "   2. Or minimal: ./aws-deploy/install-dependencies-minimal.sh"




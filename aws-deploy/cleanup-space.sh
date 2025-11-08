#!/bin/bash

# Cleanup script to free up disk space
# Run this after installation to reduce disk usage

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🧹 Cleaning up disk space..."
echo ""

# Function to get directory size
get_size() {
    du -sh "$1" 2>/dev/null | cut -f1 || echo "0"
}

BEFORE_FRONTEND=$(get_size frontend)
BEFORE_BACKEND=$(get_size backend)

# Clean Frontend
echo "🎨 Cleaning Frontend..."
cd frontend

# Remove dev dependencies (keep only what's needed for production)
if [ -d "node_modules" ]; then
    echo "   Removing development dependencies..."
    npm prune --production 2>/dev/null || true
fi

# Clean Next.js cache
if [ -d ".next/cache" ]; then
    echo "   Removing Next.js cache..."
    rm -rf .next/cache
fi

# Remove source maps from production build
if [ -d ".next" ]; then
    echo "   Removing source maps..."
    find .next -name "*.map" -type f -delete 2>/dev/null || true
fi

# Clean npm cache
echo "   Cleaning npm cache..."
npm cache clean --force 2>/dev/null || true

# Remove unnecessary files from node_modules
echo "   Removing unnecessary files from node_modules..."
find node_modules -name "*.md" -type f -delete 2>/dev/null || true
find node_modules -name "*.txt" -type f -delete 2>/dev/null || true
find node_modules -name "CHANGELOG*" -type f -delete 2>/dev/null || true
find node_modules -name "LICENSE*" -type f -delete 2>/dev/null || true
find node_modules -name "*.map" -type f -delete 2>/dev/null || true
find node_modules -type d -name "__tests__" -exec rm -rf {} + 2>/dev/null || true
find node_modules -type d -name "test" -exec rm -rf {} + 2>/dev/null || true
find node_modules -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true
find node_modules -type d -name "docs" -exec rm -rf {} + 2>/dev/null || true
find node_modules -type d -name "examples" -exec rm -rf {} + 2>/dev/null || true

cd ..

# Clean Backend
echo "📦 Cleaning Backend..."
cd backend

# Clean Python cache
echo "   Removing Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

# Clean uv cache
if command -v uv &> /dev/null; then
    echo "   Cleaning uv cache..."
    uv cache clean 2>/dev/null || true
fi

# Clean pip cache
if [ -d "$HOME/.cache/pip" ]; then
    echo "   Removing pip cache..."
    rm -rf "$HOME/.cache/pip" 2>/dev/null || true
fi

# Remove test files from venv
if [ -d ".venv" ]; then
    echo "   Cleaning .venv..."
    find .venv -name "*.md" -type f -delete 2>/dev/null || true
    find .venv -name "*.txt" -type f -delete 2>/dev/null || true
    find .venv -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find .venv -type d -name "test" -exec rm -rf {} + 2>/dev/null || true
    find .venv -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true
fi

cd ..

# Clean logs
echo "🧹 Cleaning logs..."
rm -f logs/*.log 2>/dev/null || true
rm -f backend/logs/*.log 2>/dev/null || true
find . -name "*.log" -type f -delete 2>/dev/null || true

# Clean temporary files
echo "🧹 Cleaning temporary files..."
find . -name "*.tmp" -type f -delete 2>/dev/null || true
find . -name "*.temp" -type f -delete 2>/dev/null || true
find . -name ".DS_Store" -type f -delete 2>/dev/null || true
find . -name "Thumbs.db" -type f -delete 2>/dev/null || true

# Clean git files if not needed
if [ -d ".git" ] && [ "$SKIP_GIT_CLEAN" != "1" ]; then
    echo "🧹 Cleaning git files (optional)..."
    # Only clean if explicitly requested
    # rm -rf .git/hooks .git/objects/info 2>/dev/null || true
fi

AFTER_FRONTEND=$(get_size frontend)
AFTER_BACKEND=$(get_size backend)

echo ""
echo "✅ Cleanup completed!"
echo ""
echo "📊 Disk usage:"
echo "   Frontend: $BEFORE_FRONTEND → $AFTER_FRONTEND"
echo "   Backend:  $BEFORE_BACKEND → $AFTER_BACKEND"
echo ""
echo "💡 To free up more space, you can:"
echo "   1. Remove node_modules and reinstall: cd frontend && rm -rf node_modules && npm ci --production"
echo "   2. Remove .venv and reinstall: cd backend && rm -rf .venv && uv sync"
echo "   3. Use the minimal install script: ./aws-deploy/install-dependencies-minimal.sh"





#!/bin/bash

# Remove all dependencies script
# This script removes all installed dependencies for a clean reinstall

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🗑️  Removing All Dependencies..."
echo ""
echo "⚠️  WARNING: This will remove all installed dependencies!"
echo "   - Frontend: node_modules, .next, package-lock.json"
echo "   - Backend: .venv, __pycache__, *.pyc"
echo "   - Caches: npm, pip, uv"
echo ""
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "❌ Cancelled. No dependencies were removed."
    exit 0
fi

echo ""
echo "🧹 Removing Frontend dependencies..."

# Remove Frontend dependencies
cd frontend

# Remove node_modules
if [ -d "node_modules" ]; then
    echo "   Removing node_modules..."
    rm -rf node_modules
    echo "   ✅ node_modules removed"
else
    echo "   ⚠️  node_modules not found"
fi

# Remove .next build directory
if [ -d ".next" ]; then
    echo "   Removing .next build directory..."
    rm -rf .next
    echo "   ✅ .next removed"
else
    echo "   ⚠️  .next not found"
fi

# Remove package-lock.json (optional - comment out if you want to keep it)
if [ -f "package-lock.json" ]; then
    echo "   Removing package-lock.json..."
    rm -f package-lock.json
    echo "   ✅ package-lock.json removed"
else
    echo "   ⚠️  package-lock.json not found"
fi

# Remove npm cache
echo "   Cleaning npm cache..."
npm cache clean --force 2>/dev/null || true
echo "   ✅ npm cache cleaned"

# Remove other frontend files
echo "   Removing other frontend files..."
rm -rf .next/cache 2>/dev/null || true
rm -rf node_modules/.cache 2>/dev/null || true
find . -name "*.log" -type f -delete 2>/dev/null || true
find . -name ".DS_Store" -type f -delete 2>/dev/null || true

cd ..

echo ""
echo "🧹 Removing Backend dependencies..."

# Remove Backend dependencies
cd backend

# Remove .venv (virtual environment)
if [ -d ".venv" ]; then
    echo "   Removing .venv virtual environment..."
    rm -rf .venv
    echo "   ✅ .venv removed"
else
    echo "   ⚠️  .venv not found"
fi

# Remove Python cache files
echo "   Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "*.dist-info" -exec rm -rf {} + 2>/dev/null || true
echo "   ✅ Python cache files removed"

# Remove uv cache
if command -v uv &> /dev/null; then
    echo "   Cleaning uv cache..."
    uv cache clean 2>/dev/null || true
    echo "   ✅ uv cache cleaned"
fi

# Remove pip cache
if [ -d "$HOME/.cache/pip" ]; then
    echo "   Removing pip cache..."
    rm -rf "$HOME/.cache/pip" 2>/dev/null || true
    echo "   ✅ pip cache removed"
fi

# Remove backend logs
if [ -d "logs" ]; then
    echo "   Removing backend logs..."
    rm -rf logs/*.log 2>/dev/null || true
    echo "   ✅ backend logs removed"
fi

cd ..

# Remove project-level logs
echo ""
echo "🧹 Removing project logs..."
if [ -d "logs" ]; then
    rm -rf logs/*.log 2>/dev/null || true
    rm -f logs/*.pid 2>/dev/null || true
    echo "   ✅ project logs removed"
fi

# Remove temporary files
echo "🧹 Removing temporary files..."
find . -name "*.tmp" -type f -delete 2>/dev/null || true
find . -name "*.temp" -type f -delete 2>/dev/null || true
find . -name ".DS_Store" -type f -delete 2>/dev/null || true
find . -name "Thumbs.db" -type f -delete 2>/dev/null || true

echo ""
echo "✅ All dependencies removed!"
echo ""
echo "📊 Current disk usage:"
du -sh frontend backend 2>/dev/null | awk '{print "   " $2 ": " $1}' || echo "   (directories may be empty)"
echo ""
echo "📝 Next steps:"
echo "   1. Reinstall dependencies:"
echo "      ./aws-deploy/install-dependencies.sh"
echo ""
echo "   2. Or install minimal dependencies:"
echo "      ./aws-deploy/install-dependencies-minimal.sh"
echo ""
echo "   3. Then build frontend:"
echo "      ./aws-deploy/build-frontend.sh"


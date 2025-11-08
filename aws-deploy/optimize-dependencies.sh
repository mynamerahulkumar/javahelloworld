#!/bin/bash

# Optimize dependencies script
# This script reduces disk space usage by cleaning up unnecessary files and optimizing dependencies

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🔧 Optimizing Dependencies for Production..."
echo ""

# Function to get directory size
get_size() {
    du -sh "$1" 2>/dev/null | cut -f1
}

echo "📊 Current disk usage:"
echo "   Frontend: $(get_size frontend)"
echo "   Backend: $(get_size backend)"
echo ""

# Optimize Frontend
echo "🎨 Optimizing Frontend dependencies..."
cd frontend

# Clean npm cache
echo "   Cleaning npm cache..."
npm cache clean --force 2>/dev/null || true

# Remove dev dependencies from node_modules (keep only production)
if [ -d "node_modules" ]; then
    echo "   Removing development dependencies..."
    # Install only production dependencies
    npm prune --production 2>/dev/null || true
fi

# Clean Next.js cache
if [ -d ".next/cache" ]; then
    echo "   Cleaning Next.js cache..."
    rm -rf .next/cache
fi

# Remove unnecessary files
echo "   Removing unnecessary files..."
find . -name "*.log" -type f -delete 2>/dev/null || true
find . -name "*.map" -type f -delete 2>/dev/null || true
find . -name ".DS_Store" -type f -delete 2>/dev/null || true
find . -name "Thumbs.db" -type f -delete 2>/dev/null || true

# Remove test files
find . -name "__tests__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.test.*" -type f -delete 2>/dev/null || true
find . -name "*.spec.*" -type f -delete 2>/dev/null || true

# Remove documentation files
find node_modules -name "README.md" -type f -delete 2>/dev/null || true
find node_modules -name "CHANGELOG.md" -type f -delete 2>/dev/null || true
find node_modules -name "LICENSE" -type f -delete 2>/dev/null || true
find node_modules -name "*.md" -type f -delete 2>/dev/null || true

# Remove source maps from node_modules
find node_modules -name "*.map" -type f -delete 2>/dev/null || true

cd ..

# Optimize Backend
echo "📦 Optimizing Backend dependencies..."
cd backend

# Clean Python cache
echo "   Cleaning Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

# Clean uv cache if using uv
if command -v uv &> /dev/null; then
    echo "   Cleaning uv cache..."
    uv cache clean 2>/dev/null || true
fi

# Clean pip cache
if [ -d "$HOME/.cache/pip" ]; then
    echo "   Cleaning pip cache..."
    rm -rf "$HOME/.cache/pip" 2>/dev/null || true
fi

# Remove test files
find . -name "__tests__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "test_*.py" -type f -delete 2>/dev/null || true
find . -name "*_test.py" -type f -delete 2>/dev/null || true

# Remove documentation files
find .venv -name "*.md" -type f -delete 2>/dev/null || true
find .venv -name "*.txt" -type f -delete 2>/dev/null || true
find .venv -name "LICENSE" -type f -delete 2>/dev/null || true

cd ..

# Clean logs
echo "🧹 Cleaning logs..."
rm -f logs/*.log 2>/dev/null || true
rm -f backend/logs/*.log 2>/dev/null || true

# Clean temporary files
echo "🧹 Cleaning temporary files..."
find . -name "*.tmp" -type f -delete 2>/dev/null || true
find . -name "*.temp" -type f -delete 2>/dev/null || true
find . -name ".DS_Store" -type f -delete 2>/dev/null || true

echo ""
echo "📊 Disk usage after optimization:"
echo "   Frontend: $(get_size frontend)"
echo "   Backend: $(get_size backend)"
echo ""
echo "✅ Dependencies optimized!"




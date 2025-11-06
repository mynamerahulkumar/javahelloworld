#!/bin/bash

# Check build status script
# This script helps diagnose why the build might be hanging

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT/frontend"

echo "🔍 Checking Build Status and System Resources..."
echo ""

# Check if build is running
BUILD_PROCESSES=$(ps aux | grep -E "next build|node.*next" | grep -v grep | wc -l)
if [ "$BUILD_PROCESSES" -gt 0 ]; then
    echo "✅ Build process is running:"
    ps aux | grep -E "next build|node.*next" | grep -v grep
    echo ""
else
    echo "❌ No build process found"
    echo ""
fi

# Check system resources
echo "📊 System Resources:"
echo "   Memory:"
free -h
echo ""
echo "   Disk Space:"
df -h . | head -2
echo ""

# Check if .next directory exists
if [ -d ".next" ]; then
    echo "📁 .next directory exists:"
    ls -lah .next/ | head -10
    echo ""
    
    if [ -f ".next/BUILD_ID" ]; then
        echo "✅ BUILD_ID found: $(cat .next/BUILD_ID)"
    else
        echo "❌ BUILD_ID missing - build is incomplete"
    fi
else
    echo "❌ .next directory does not exist"
fi

echo ""
echo "💡 Recommendations:"
echo "   1. If build is stuck, kill it: pkill -f 'next build'"
echo "   2. Check memory: free -h (need at least 2GB free)"
echo "   3. Check disk space: df -h (need at least 1GB free)"
echo "   4. Try simple build: ./build-frontend-simple.sh"
echo "   5. Check environment: cat frontend/.env.local"


#!/bin/bash

# Build script for Frontend (Production)
# This script builds the Next.js frontend for production with timeout and monitoring

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT/frontend"

echo "🏗️  Building Frontend for Production..."
echo ""

# Check system resources
echo "📊 Checking system resources..."
FREE_MEM=$(free -m | awk 'NR==2{printf "%.0f", $3*100/$2}')
DISK_SPACE=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
echo "   Memory usage: ${FREE_MEM}%"
echo "   Disk usage: ${DISK_SPACE}%"

if [ "$DISK_SPACE" -gt 90 ]; then
    echo "   ⚠️  Warning: Disk usage is above 90%"
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo ""
    echo "⚠️  node_modules not found. Installing dependencies..."
    npm ci
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
fi

# Clean previous build if it exists
if [ -d ".next" ]; then
    echo ""
    echo "🧹 Cleaning previous build..."
    rm -rf .next
fi

# Set environment variables for build
export NODE_ENV=production
export NEXT_TELEMETRY_DISABLED=1

# Build for production with timeout (15 minutes = 900 seconds)
echo ""
echo "📦 Building Next.js application..."
echo "   This may take several minutes. Please wait..."
echo "   Build timeout: 15 minutes"
echo ""

# Create a temporary log file for build output
BUILD_LOG="/tmp/nextjs-build-$$.log"

# Function to show build progress
show_progress() {
    local pid=$1
    local timeout=900  # 15 minutes
    local elapsed=0
    local interval=30  # Check every 30 seconds
    
    while [ $elapsed -lt $timeout ]; do
        if ! ps -p $pid > /dev/null 2>&1; then
            return 0  # Process completed
        fi
        
        # Show progress every 30 seconds
        if [ $((elapsed % interval)) -eq 0 ]; then
            echo "   ⏳ Build in progress... (${elapsed}s elapsed)"
            # Show last few lines of build log if it exists
            if [ -f "$BUILD_LOG" ]; then
                tail -3 "$BUILD_LOG" 2>/dev/null | sed 's/^/      /'
            fi
        fi
        
        sleep 5
        elapsed=$((elapsed + 5))
    done
    
    # Timeout reached
    echo ""
    echo "   ⚠️  Build timeout reached (15 minutes)"
    return 1
}

# Start build in background and capture output
npm run build > "$BUILD_LOG" 2>&1 &
BUILD_PID=$!

echo "   Build process started (PID: $BUILD_PID)"
echo "   Build log: $BUILD_LOG"
echo ""

# Monitor build progress
show_progress $BUILD_PID &
MONITOR_PID=$!

# Wait for build to complete or timeout
wait $BUILD_PID 2>/dev/null
BUILD_EXIT_CODE=$?

# Stop monitor
kill $MONITOR_PID 2>/dev/null || true

# Show final build output
echo ""
echo "📋 Build output:"
echo "----------------------------------------"
tail -50 "$BUILD_LOG"
echo "----------------------------------------"
echo ""

# Clean up log file
rm -f "$BUILD_LOG"

# Check build result
if [ $BUILD_EXIT_CODE -ne 0 ]; then
    echo "❌ Build failed with exit code $BUILD_EXIT_CODE"
    echo ""
    echo "💡 Troubleshooting tips:"
    echo "   1. Check if you have enough memory (Next.js needs at least 2GB)"
    echo "   2. Check disk space: df -h"
    echo "   3. Check memory: free -h"
    echo "   4. Try building with more verbose output:"
    echo "      cd frontend && NODE_OPTIONS='--max-old-space-size=4096' npm run build"
    echo "   5. Check for environment variable issues in frontend/.env.local"
    exit 1
fi

# Verify build was successful
if [ ! -f ".next/BUILD_ID" ]; then
    echo "❌ Build completed but BUILD_ID file is missing. Build may have failed."
    echo ""
    echo "💡 Check the build output above for errors."
    exit 1
fi

BUILD_ID=$(cat .next/BUILD_ID 2>/dev/null || echo "N/A")
BUILD_SIZE=$(du -sh .next 2>/dev/null | cut -f1)

echo "✅ Frontend built successfully!"
echo "   Build ID: $BUILD_ID"
echo "   Build size: $BUILD_SIZE"
echo "   Build directory: .next/"
echo ""
echo "📝 Next steps:"
echo "   - Start services: ./aws-deploy/start-all.sh"
echo "   - Or restart services: ./aws-deploy/restart-all.sh"

#!/bin/bash

# Simple start script for AWS Linux hosts
# Starts backend (FastAPI) and frontend (Next.js) in production mode with minimal checks

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/common.sh"

check_command python3
check_command npm

if ! python3 -c "import uvicorn" >/dev/null 2>&1; then
    echo "❌ Python module 'uvicorn' not found. Install backend dependencies first."
    echo "   Example: cd \"$BACKEND_DIR\" && python3 -m pip install \"uvicorn[standard]\" fastapi ..."
    exit 1
fi

cd "$PROJECT_ROOT" || exit 1

ensure_logs

echo "Starting backend (simple mode)..."
cd "$BACKEND_DIR" || exit 1
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8501 > "$LOG_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
record_pid "$BACKEND_PID" "backend"
echo "Backend PID: $BACKEND_PID"

echo "Starting frontend (simple mode)..."
cd "$FRONTEND_DIR" || exit 1

if [ ! -f ".next/BUILD_ID" ]; then
    echo "❌ Production build missing (.next/BUILD_ID not found)."
    echo "   Run: npm run build"
    exit 1
fi

if [ ! -d "node_modules/@tailwindcss/postcss" ] || [ ! -d "node_modules/tailwindcss" ]; then
    echo "❌ Required frontend dependencies missing."
    echo "   Run: npm ci --include=dev"
    exit 1
fi

nohup npm run start > "$LOG_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
record_pid "$FRONTEND_PID" "frontend"
echo "Frontend PID: $FRONTEND_PID"

echo "Backend logs: $PROJECT_ROOT/logs/backend.log"
echo "Frontend logs: $PROJECT_ROOT/logs/frontend.log"
echo "Use aws-deploy/simple-stop-all.sh to stop both services."



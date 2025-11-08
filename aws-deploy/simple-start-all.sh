#!/bin/bash

# Simple start script for AWS Linux hosts
# Starts backend (FastAPI) and frontend (Next.js) in production mode with minimal checks

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT" || exit 1

mkdir -p logs
mkdir -p backend/logs

echo "Starting backend (simple mode)..."
cd backend || exit 1
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8501 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "$BACKEND_PID" > ../logs/backend.pid
echo "Backend PID: $BACKEND_PID"

cd "$PROJECT_ROOT" || exit 1

echo "Starting frontend (simple mode)..."
cd frontend || exit 1
nohup npm run start > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "$FRONTEND_PID" > ../logs/frontend.pid
echo "Frontend PID: $FRONTEND_PID"

cd "$PROJECT_ROOT" || exit 1

echo "Backend logs: $PROJECT_ROOT/logs/backend.log"
echo "Frontend logs: $PROJECT_ROOT/logs/frontend.log"
echo "Use aws-deploy/simple-stop-all.sh to stop both services."


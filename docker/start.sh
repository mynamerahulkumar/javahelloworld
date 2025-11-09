#!/bin/bash

set -euo pipefail

BACKEND_PORT="${BACKEND_PORT:-8501}"
BACKEND_WORKERS="${BACKEND_WORKERS:-4}"
FRONTEND_PORT="${PORT:-3000}"

cleanup() {
    local exit_code=$?
    if [ -n "${BACKEND_PID:-}" ] && ps -p "$BACKEND_PID" >/dev/null 2>&1; then
        kill "$BACKEND_PID" >/dev/null 2>&1 || true
        wait "$BACKEND_PID" 2>/dev/null || true
    fi
    if [ -n "${FRONTEND_PID:-}" ] && ps -p "$FRONTEND_PID" >/dev/null 2>&1; then
        kill "$FRONTEND_PID" >/dev/null 2>&1 || true
        wait "$FRONTEND_PID" 2>/dev/null || true
    fi
    exit "$exit_code"
}

trap cleanup EXIT INT TERM

echo "Starting backend on port ${BACKEND_PORT}..."
cd /app/backend
uvicorn main:app --host 0.0.0.0 --port "$BACKEND_PORT" --workers "$BACKEND_WORKERS" &
BACKEND_PID=$!

echo "Starting frontend on port ${FRONTEND_PORT}..."
cd /app/frontend
if [ ! -f ".next/BUILD_ID" ]; then
    echo "❌ Next.js build is missing. Ensure the frontend build stage completed successfully."
    exit 1
fi
NODE_ENV=production PORT="$FRONTEND_PORT" npm run start -- --hostname 0.0.0.0 &
FRONTEND_PID=$!

wait -n "$BACKEND_PID" "$FRONTEND_PID"
*** End Patch*** End Patch to=functions.apply_patch code execution reasoning code_only=False supervisory_signal=True


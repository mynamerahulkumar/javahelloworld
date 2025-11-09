#!/bin/bash

# Simple stop script for AWS Linux hosts
# Stops backend (FastAPI) and frontend (Next.js) processes using stored PIDs or fallbacks

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/common.sh"

cd "$PROJECT_ROOT" || exit 1

stop_with_pid_file() {
    local name=$1
    local pid_file=$2
    local fallback_pattern=$3

    if [ -f "$pid_file" ]; then
        local pid
        pid=$(cat "$pid_file")
        if ! kill_process "$pid" "$name"; then
            echo "$name PID $pid not running, attempting fallback."
            pkill -f "$fallback_pattern" >/dev/null 2>&1 && echo "Stopped $name via fallback pattern."
        fi
        rm -f "$pid_file"
    elif pkill -f "$fallback_pattern" >/dev/null 2>&1; then
        echo "Stopped $name via fallback pattern."
    else
        echo "No running process found for $name."
    fi
}

stop_with_pid_file "backend" "$LOG_DIR/backend.pid" "uvicorn.*main:app"
stop_with_pid_file "frontend" "$LOG_DIR/frontend.pid" "next start"

echo "Backend and frontend stop commands issued."



#!/bin/bash

# Shared helpers for AWS deployment scripts

# Resolve key directories once so sourced scripts can reuse them
LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$LIB_DIR/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
LOG_DIR="$PROJECT_ROOT/logs"
BACKEND_LOG_DIR="$BACKEND_DIR/logs"

export PROJECT_ROOT BACKEND_DIR FRONTEND_DIR LOG_DIR BACKEND_LOG_DIR

ensure_logs() {
    mkdir -p "$LOG_DIR" "$BACKEND_LOG_DIR"
}

check_command() {
    local binary=$1
    local friendly=${2:-$1}
    if ! command -v "$binary" >/dev/null 2>&1; then
        echo "❌ Required command '$friendly' not found."
        return 1
    else
        echo "⚠️  Warning: Cannot kill processes on port $port (ss, netstat, or lsof not found)"
    fi
}

check_port() {
    local port=$1
    if command -v ss >/dev/null 2>&1; then
        ss -tuln | grep -q ":$port " && return 0 || return 1
    elif command -v netstat >/dev/null 2>&1; then
        netstat -tuln | grep -q ":$port " && return 0 || return 1
    elif command -v lsof >/dev/null 2>&1; then
        lsof -Pi :"$port" -sTCP:LISTEN -t >/dev/null 2>&1 && return 0 || return 1
    else
        echo "⚠️  Warning: Cannot check port $port (ss, netstat, or lsof not found)"
        return 1
    fi
}

kill_process() {
    local pid=$1
    local name=$2
    if [ -n "$pid" ] && ps -p "$pid" >/dev/null 2>&1; then
        kill "$pid" 2>/dev/null || true
        sleep 2
        if ps -p "$pid" >/dev/null 2>&1; then
            kill -9 "$pid" 2>/dev/null || true
        fi
        echo "✅ Stopped $name process $pid"
        return 0
    fi
    return 1
}

kill_port() {
    local port=$1
    local name=$2
    local pids=""

    if command -v ss >/dev/null 2>&1; then
        pids=$(ss -tlnp 2>/dev/null | grep ":$port " | grep -oP 'pid=\K[0-9]+' | sort -u)
    elif command -v netstat >/dev/null 2>&1; then
        pids=$(netstat -tlnp 2>/dev/null | grep ":$port " | grep -oP '[0-9]+/[^ ]+' | cut -d'/' -f1 | sort -u)
    elif command -v lsof >/dev/null 2>&1; then
        pids=$(lsof -ti :"$port" 2>/dev/null)
    fi

    if [ -n "$pids" ]; then
        echo "🔍 Found processes on port $port: $pids"
        for pid in $pids; do
            kill_process "$pid" "$name"
        done
        return 0
    fi
    return 1
}

record_pid() {
    local pid=$1
    local name=$2
    echo "$pid" > "$LOG_DIR/$name.pid"
}

tail_log() {
    local path=$1
    if [ -f "$path" ]; then
        tail -20 "$path"
    fi
}


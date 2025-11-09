#!/bin/bash

# Service status helper for AWS EC2 Linux
# Checks backend/frontend processes, listening ports, and HTTP endpoints.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/common.sh"

HOST="${1:-localhost}"
BACKEND_PORT="${BACKEND_PORT:-8501}"
FRONTEND_PORT="${FRONTEND_PORT:-3000}"

HEADER="=============================="

echo "$HEADER"
echo "AWS Service Status Check"
echo "Project root: $PROJECT_ROOT"
echo "Target host:  $HOST"
echo "Backend port: $BACKEND_PORT"
echo "Frontend port:$FRONTEND_PORT"
echo "$HEADER"
echo ""

check_process() {
    local name=$1
    local pattern=$2

    if pgrep -f "$pattern" >/dev/null 2>&1; then
        echo "✅ $name process running (pattern: $pattern)"
        pgrep -af "$pattern"
    else
        echo "❌ $name process NOT found (pattern: $pattern)"
    fi
    echo ""
}

check_port_status() {
    local port=$1
    local label=$2

    if command -v ss >/dev/null 2>&1; then
        if ss -tulpn | grep -q ":$port"; then
            echo "✅ $label port $port is listening"
            ss -tulpn | grep ":$port"
        else
            echo "❌ $label port $port is NOT listening"
        fi
    elif command -v netstat >/dev/null 2>&1; then
        if netstat -tulpn | grep -q ":$port"; then
            echo "✅ $label port $port is listening"
            netstat -tulpn | grep ":$port"
        else
            echo "❌ $label port $port is NOT listening"
        fi
    else
        echo "⚠️  Neither ss nor netstat found; skipping port check for $label ($port)"
    fi
    echo ""
}

curl_check() {
    local label=$1
    local url=$2

    if command -v curl >/dev/null 2>&1; then
        echo "🔍 Curl check: $label ($url)"
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$url" || true)
        if [[ "$HTTP_CODE" =~ ^2|3 ]]; then
            echo "✅ $label reachable (HTTP $HTTP_CODE)"
        else
            echo "❌ $label not reachable (HTTP $HTTP_CODE)"
        fi
    else
        echo "⚠️  curl not installed; skipping HTTP check for $label"
    fi
    echo ""
}

echo "Process checks"
echo "--------------"
check_process "Backend (FastAPI)" "uvicorn.*main:app"
check_process "Frontend (Next.js)" "next start"

echo "Port checks"
echo "-----------"
check_port_status "$BACKEND_PORT" "Backend"
check_port_status "$FRONTEND_PORT" "Frontend"

echo "HTTP checks"
echo "-----------"
curl_check "Backend docs" "http://$HOST:$BACKEND_PORT/docs"
curl_check "Frontend login" "http://$HOST:$FRONTEND_PORT/login"

echo "$HEADER"
echo "Status check complete."
echo "$HEADER"


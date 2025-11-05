#!/bin/bash

# View logs script for Full Stack Application
# This script provides easy access to view logs

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

BACKEND_LOG="logs/backend.log"
FRONTEND_LOG="logs/frontend.log"

case "${1:-all}" in
    backend)
        if [ ! -f "$BACKEND_LOG" ]; then
            echo "⚠️  Backend log file not found: $BACKEND_LOG"
            exit 1
        fi
        echo "📝 Backend Logs:"
        echo ""
        case "${2:-tail}" in
            tail)
                tail -f "$BACKEND_LOG"
                ;;
            lines)
                LINES=${3:-50}
                tail -n "$LINES" "$BACKEND_LOG"
                ;;
            all)
                cat "$BACKEND_LOG"
                ;;
            *)
                echo "Usage: $0 backend [tail|lines|all] [number_of_lines]"
                exit 1
                ;;
        esac
        ;;
    frontend)
        if [ ! -f "$FRONTEND_LOG" ]; then
            echo "⚠️  Frontend log file not found: $FRONTEND_LOG"
            exit 1
        fi
        echo "📝 Frontend Logs:"
        echo ""
        case "${2:-tail}" in
            tail)
                tail -f "$FRONTEND_LOG"
                ;;
            lines)
                LINES=${3:-50}
                tail -n "$LINES" "$FRONTEND_LOG"
                ;;
            all)
                cat "$FRONTEND_LOG"
                ;;
            *)
                echo "Usage: $0 frontend [tail|lines|all] [number_of_lines]"
                exit 1
                ;;
        esac
        ;;
    all)
        echo "📝 All Logs (Backend + Frontend):"
        echo ""
        echo "=== BACKEND LOG ==="
        if [ -f "$BACKEND_LOG" ]; then
            tail -n 20 "$BACKEND_LOG"
        else
            echo "Backend log not found"
        fi
        echo ""
        echo "=== FRONTEND LOG ==="
        if [ -f "$FRONTEND_LOG" ]; then
            tail -n 20 "$FRONTEND_LOG"
        else
            echo "Frontend log not found"
        fi
        ;;
    *)
        echo "Usage: $0 [backend|frontend|all] [tail|lines|all] [number_of_lines]"
        echo ""
        echo "Examples:"
        echo "  $0                    # Show last 20 lines of all logs"
        echo "  $0 backend tail       # Follow backend logs in real-time"
        echo "  $0 frontend lines 100 # Show last 100 lines of frontend logs"
        echo "  $0 all                # Show last 20 lines of all logs"
        exit 1
        ;;
esac


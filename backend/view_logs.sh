#!/bin/bash

# View logs script for Trading API
# This script provides easy access to view logs

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

LOG_FILE="logs/bot.log"

if [ ! -f "$LOG_FILE" ]; then
    echo "⚠️  Log file not found: $LOG_FILE"
    exit 1
fi

echo "📋 Viewing logs: $LOG_FILE"
echo ""

case "${1:-tail}" in
    tail)
        echo "📝 Tailing logs (Ctrl+C to exit)..."
        tail -f "$LOG_FILE"
        ;;
    lines)
        LINES=${2:-50}
        echo "📝 Last $LINES lines:"
        tail -n "$LINES" "$LOG_FILE"
        ;;
    all)
        echo "📝 All logs:"
        cat "$LOG_FILE"
        ;;
    *)
        echo "Usage: $0 [tail|lines|all] [number_of_lines]"
        echo "  tail   - Follow logs in real-time (default)"
        echo "  lines  - Show last N lines (default: 50)"
        echo "  all    - Show all logs"
        exit 1
        ;;
esac


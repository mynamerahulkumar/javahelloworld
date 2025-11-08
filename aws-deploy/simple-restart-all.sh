#!/bin/bash

# Simple restart script for AWS Linux hosts

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

"$SCRIPT_DIR/simple-stop-all.sh"
sleep 2
"$SCRIPT_DIR/simple-start-all.sh"

echo "Restart sequence completed."


#!/bin/bash

# Setup systemd services for AWS EC2 Linux
# This script creates systemd service files for backend and frontend

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
USER=$(whoami)

echo "🔧 Setting up systemd services for AWS EC2 Linux..."
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  This script needs sudo privileges to create systemd services"
    echo "   Please run: sudo ./setup-systemd.sh"
    exit 1
fi

# Create systemd service directory if it doesn't exist
mkdir -p /etc/systemd/system

# Detect uv path
UV_PATH=$(which uv 2>/dev/null || echo "$HOME/.cargo/bin/uv")
if [ ! -f "$UV_PATH" ]; then
    UV_PATH="uv"  # Fallback to system PATH
fi

# Create backend service
cat > /etc/systemd/system/trading-backend.service << EOF
[Unit]
Description=Trading API Backend Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_ROOT/backend
Environment="PATH=$PROJECT_ROOT/backend/.venv/bin:/usr/local/bin:/usr/bin:/bin:$HOME/.cargo/bin"
ExecStart=$UV_PATH run python -m uvicorn main:app --host 0.0.0.0 --port 8501 --workers 4
Restart=always
RestartSec=10
StandardOutput=append:$PROJECT_ROOT/logs/backend.log
StandardError=append:$PROJECT_ROOT/logs/backend.log

[Install]
WantedBy=multi-user.target
EOF

# Create frontend service
cat > /etc/systemd/system/trading-frontend.service << EOF
[Unit]
Description=Trading Frontend Service
After=network.target trading-backend.service
Requires=trading-backend.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_ROOT/frontend
Environment="PATH=/usr/bin:/bin"
Environment="NODE_ENV=production"
ExecStart=/usr/bin/npm run start
Restart=always
RestartSec=10
StandardOutput=append:$PROJECT_ROOT/logs/frontend.log
StandardError=append:$PROJECT_ROOT/logs/frontend.log

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
systemctl daemon-reload

echo "✅ Systemd services created!"
echo ""
echo "📝 Service files created:"
echo "   - /etc/systemd/system/trading-backend.service"
echo "   - /etc/systemd/system/trading-frontend.service"
echo ""
echo "🚀 To start services:"
echo "   sudo systemctl start trading-backend"
echo "   sudo systemctl start trading-frontend"
echo ""
echo "🔄 To enable services on boot:"
echo "   sudo systemctl enable trading-backend"
echo "   sudo systemctl enable trading-frontend"
echo ""
echo "📊 To check status:"
echo "   sudo systemctl status trading-backend"
echo "   sudo systemctl status trading-frontend"
echo ""
echo "📝 To view logs:"
echo "   sudo journalctl -u trading-backend -f"
echo "   sudo journalctl -u trading-frontend -f"


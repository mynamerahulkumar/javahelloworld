#!/bin/bash

# Systemd Service Setup Script
# Creates systemd service files for backend and frontend
# Run with sudo: sudo ./deploy/scripts/setup-systemd.sh

set -e

APP_NAME="trading-api"
DEPLOY_DIR="/opt/trading-api"
SERVICE_USER="${SUDO_USER:-$USER}"

echo "🔧 Setting up systemd services for $APP_NAME..."
echo ""

# Create systemd service file for backend
echo "📝 Creating backend systemd service..."
sudo tee /etc/systemd/system/${APP_NAME}-backend.service > /dev/null <<EOF
[Unit]
Description=Trading API Backend (FastAPI)
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$DEPLOY_DIR/backend
Environment="PATH=$DEPLOY_DIR/backend/.venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="ENVIRONMENT=production"
Environment="PORT=8501"
Environment="HOST=0.0.0.0"
Environment="WORKERS=4"
Environment="LOG_LEVEL=info"
# Use python from venv, fallback to system python3 (try python3.12 first)
ExecStart=/bin/bash -c 'if [ -f "$DEPLOY_DIR/backend/.venv/bin/python" ]; then $DEPLOY_DIR/backend/.venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8501 --workers 4; elif command -v python3.12 &> /dev/null; then python3.12 -m uvicorn main:app --host 0.0.0.0 --port 8501 --workers 4; else python3 -m uvicorn main:app --host 0.0.0.0 --port 8501 --workers 4; fi'
Restart=always
RestartSec=10
StandardOutput=append:/var/log/trading-api/backend.log
StandardError=append:/var/log/trading-api/backend.error.log

# Security settings
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

# Create systemd service file for frontend
echo "📝 Creating frontend systemd service..."
sudo tee /etc/systemd/system/${APP_NAME}-frontend.service > /dev/null <<EOF
[Unit]
Description=Trading API Frontend (Next.js)
After=network.target ${APP_NAME}-backend.service
Requires=${APP_NAME}-backend.service

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$DEPLOY_DIR/frontend
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
Environment="NODE_ENV=production"
Environment="PORT=3000"
Environment="HOSTNAME=0.0.0.0"
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=10
StandardOutput=append:/var/log/trading-api/frontend.log
StandardError=append:/var/log/trading-api/frontend.error.log

# Security settings
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
echo "🔄 Reloading systemd daemon..."
sudo systemctl daemon-reload

# Enable services
echo "✅ Enabling services..."
sudo systemctl enable ${APP_NAME}-backend.service
sudo systemctl enable ${APP_NAME}-frontend.service

echo ""
echo "✅ Systemd services created successfully!"
echo ""
echo "Service management commands:"
echo "  Start:   sudo systemctl start ${APP_NAME}-backend ${APP_NAME}-frontend"
echo "  Stop:    sudo systemctl stop ${APP_NAME}-backend ${APP_NAME}-frontend"
echo "  Restart: sudo systemctl restart ${APP_NAME}-backend ${APP_NAME}-frontend"
echo "  Status:  sudo systemctl status ${APP_NAME}-backend ${APP_NAME}-frontend"
echo "  Logs:    sudo journalctl -u ${APP_NAME}-backend -f"
echo "           sudo journalctl -u ${APP_NAME}-frontend -f"
echo ""


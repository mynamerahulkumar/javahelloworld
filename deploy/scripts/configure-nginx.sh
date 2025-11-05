#!/bin/bash

# Nginx Configuration Script
# Sets up nginx configuration for Trading API
# Usage: sudo ./deploy/scripts/configure-nginx.sh

set -e

echo "🌐 Configuring Nginx for Trading API..."
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root (use sudo)"
    exit 1
fi

DEPLOY_DIR="/opt/trading-api"
NGINX_SITE="trading-api"
NGINX_CONF="/etc/nginx/sites-available/${NGINX_SITE}"

# Detect OS for nginx configuration path
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    OS="unknown"
fi

# Amazon Linux uses /etc/nginx/conf.d/ instead of sites-available/sites-enabled
if [ "$OS" = "amzn" ] || [ "$OS" = "amazon" ]; then
    NGINX_CONF="/etc/nginx/conf.d/trading-api.conf"
    echo "📝 Using Amazon Linux nginx configuration path: $NGINX_CONF"
else
    NGINX_CONF="/etc/nginx/sites-available/${NGINX_SITE}"
fi

# Copy nginx configuration
if [ -f "$DEPLOY_DIR/deploy/nginx.conf" ]; then
    echo "📝 Copying nginx configuration..."
    cp "$DEPLOY_DIR/deploy/nginx.conf" "$NGINX_CONF"
    echo "✅ Configuration copied to $NGINX_CONF"
else
    echo "⚠️  Nginx configuration file not found at $DEPLOY_DIR/deploy/nginx.conf"
    echo "   Creating default configuration..."
    
    # Create default configuration
    cat > "$NGINX_CONF" << 'EOF'
# Nginx Configuration for Trading API

upstream backend_api {
    server 127.0.0.1:8501;
    keepalive 64;
}

upstream frontend_app {
    server 127.0.0.1:3000;
    keepalive 64;
}

server {
    listen 80;
    listen [::]:80;
    server_name _;

    access_log /var/log/nginx/trading-api-access.log;
    error_log /var/log/nginx/trading-api-error.log;

    client_max_body_size 10M;

    # Backend API
    location /api/ {
        proxy_pass http://backend_api;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
    }

    # Backend Docs
    location /docs {
        proxy_pass http://backend_api;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }

    # Frontend
    location / {
        proxy_pass http://frontend_app;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF
    echo "✅ Default configuration created"
fi

# Create symlink if needed (not for Amazon Linux)
if [ "$OS" != "amzn" ] && [ "$OS" != "amazon" ]; then
    if [ ! -L "/etc/nginx/sites-enabled/${NGINX_SITE}" ]; then
        echo "🔗 Creating symlink..."
        ln -s "$NGINX_CONF" "/etc/nginx/sites-enabled/${NGINX_SITE}"
        echo "✅ Symlink created"
    else
        echo "✅ Symlink already exists"
    fi
    
    # Remove default site (optional)
    if [ -L "/etc/nginx/sites-enabled/default" ]; then
        echo "🗑️  Removing default nginx site..."
        rm /etc/nginx/sites-enabled/default
        echo "✅ Default site removed"
    fi
else
    echo "✅ Amazon Linux uses /etc/nginx/conf.d/ directly (no symlink needed)"
fi

# Test nginx configuration
echo "🧪 Testing nginx configuration..."
if nginx -t; then
    echo "✅ Nginx configuration is valid"
else
    echo "❌ Nginx configuration test failed"
    exit 1
fi

# Reload nginx
echo "🔄 Reloading nginx..."
systemctl reload nginx
echo "✅ Nginx reloaded"

echo ""
echo "✅ Nginx configuration complete!"
echo ""
echo "Nginx is now configured to proxy:"
echo "  - Backend API: /api/ -> http://localhost:8501"
echo "  - Backend Docs: /docs -> http://localhost:8501"
echo "  - Frontend: / -> http://localhost:3000"
echo ""
echo "Edit configuration: $NGINX_CONF"
echo "Test configuration: sudo nginx -t"
echo "Reload nginx: sudo systemctl reload nginx"
echo ""


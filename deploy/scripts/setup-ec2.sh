#!/bin/bash

# EC2 Instance Setup Script
# Run this script once on a fresh EC2 instance to set up the environment
# Usage: ./deploy/scripts/setup-ec2.sh

set -e

echo "🔧 Setting up EC2 instance for Trading API deployment..."
echo ""

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "❌ Cannot detect OS. Exiting."
    exit 1
fi

echo "📦 Detected OS: $OS"
echo ""

# Update system packages
echo "📥 Updating system packages..."
if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    sudo apt-get update
    sudo apt-get upgrade -y
elif [ "$OS" = "amzn" ] || [ "$OS" = "amazon" ]; then
    sudo yum update -y
elif [ "$OS" = "rhel" ] || [ "$OS" = "centos" ] || [ "$OS" = "fedora" ]; then
    sudo yum update -y
else
    echo "⚠️  Unsupported OS. Please install dependencies manually."
fi

# Install Python 3.12+ and pip
echo "🐍 Installing Python 3.12+..."
if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    sudo apt-get install -y python3.12 python3.12-venv python3-pip python3.12-dev build-essential
    # Install uv (modern Python package manager)
    if ! command -v uv &> /dev/null; then
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.cargo/bin:$PATH"
    fi
elif [ "$OS" = "amzn" ] || [ "$OS" = "amazon" ]; then
    # Amazon Linux 2 comes with Python 3.7, need to install Python 3.12+
    # Check if Python 3.12+ is available
    if ! command -v python3.12 &> /dev/null && ! command -v python3.11 &> /dev/null; then
        echo "📦 Installing Python 3.12 from source (Amazon Linux)..."
        # Install build dependencies
        sudo yum groupinstall -y "Development Tools"
        sudo yum install -y openssl-devel bzip2-devel libffi-devel zlib-devel readline-devel sqlite-devel wget
        # Install Python 3.12 from source
        cd /tmp
        wget https://www.python.org/ftp/python/3.12.0/Python-3.12.0.tgz
        tar xzf Python-3.12.0.tgz
        cd Python-3.12.0
        ./configure --enable-optimizations --prefix=/usr/local
        make altinstall
        cd /
        rm -rf /tmp/Python-3.12.0*
        # Create symlink
        sudo ln -sf /usr/local/bin/python3.12 /usr/bin/python3.12
        sudo ln -sf /usr/local/bin/pip3.12 /usr/bin/pip3.12
    fi
    # Install pip and build tools
    sudo yum install -y python3-pip python3-devel gcc make
    # Upgrade pip
    python3 -m pip install --upgrade pip setuptools wheel
elif [ "$OS" = "rhel" ] || [ "$OS" = "centos" ] || [ "$OS" = "fedora" ]; then
    sudo yum install -y python3 python3-pip python3-devel gcc make
    python3 -m pip install --upgrade pip setuptools wheel
fi

# Install Node.js 18+ (using NodeSource repository)
echo "📦 Installing Node.js 18+..."
if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    if ! command -v node &> /dev/null || [ "$(node --version | cut -d'v' -f2 | cut -d'.' -f1)" -lt 18 ]; then
        curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
        sudo apt-get install -y nodejs
    fi
elif [ "$OS" = "amzn" ] || [ "$OS" = "amazon" ]; then
    if ! command -v node &> /dev/null || [ "$(node --version | cut -d'v' -f2 | cut -d'.' -f1)" -lt 18 ] 2>/dev/null; then
        echo "📦 Installing Node.js 20.x from NodeSource (Amazon Linux)..."
        curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
        sudo yum install -y nodejs
        # Verify installation
        node --version
        npm --version
    else
        echo "✅ Node.js $(node --version) is already installed"
    fi
elif [ "$OS" = "rhel" ] || [ "$OS" = "centos" ] || [ "$OS" = "fedora" ]; then
    if ! command -v node &> /dev/null; then
        curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
        sudo yum install -y nodejs
    fi
fi

# Install nginx (for reverse proxy)
echo "🌐 Installing Nginx..."
if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    sudo apt-get install -y nginx
elif [ "$OS" = "amzn" ] || [ "$OS" = "amazon" ]; then
    # Amazon Linux uses amazon-linux-extras for nginx
    if ! command -v nginx &> /dev/null; then
        # Try amazon-linux-extras first (for Amazon Linux 2)
        if command -v amazon-linux-extras &> /dev/null; then
            sudo amazon-linux-extras install -y nginx1
        else
            # Fallback to yum
            sudo yum install -y nginx
        fi
        # Start and enable nginx
        sudo systemctl start nginx
        sudo systemctl enable nginx
    else
        echo "✅ Nginx is already installed"
    fi
elif [ "$OS" = "rhel" ] || [ "$OS" = "centos" ] || [ "$OS" = "fedora" ]; then
    sudo yum install -y nginx
fi

# Create application directory
echo "📁 Creating application directory..."
sudo mkdir -p /opt/trading-api
sudo chown -R $USER:$USER /opt/trading-api

# Create logs directory
sudo mkdir -p /var/log/trading-api
sudo chown -R $USER:$USER /var/log/trading-api

# Install PM2 for process management (optional, systemd is preferred)
if ! command -v pm2 &> /dev/null; then
    echo "📦 Installing PM2 (optional process manager)..."
    sudo npm install -g pm2
fi

# Configure firewall
echo "🔥 Configuring firewall..."
if command -v ufw &> /dev/null; then
    # Ubuntu/Debian uses ufw
    sudo ufw allow 22/tcp   # SSH
    sudo ufw allow 80/tcp   # HTTP
    sudo ufw allow 443/tcp  # HTTPS
    sudo ufw --force enable
elif command -v firewall-cmd &> /dev/null; then
    # RHEL/CentOS/Fedora/Amazon Linux 2023 uses firewalld
    sudo firewall-cmd --permanent --add-service=ssh
    sudo firewall-cmd --permanent --add-service=http
    sudo firewall-cmd --permanent --add-service=https
    sudo firewall-cmd --reload
    echo "✅ Firewall configured (firewalld)"
else
    echo "⚠️  No firewall manager found. Please configure Security Groups in AWS Console."
    echo "   Ensure ports 22 (SSH), 80 (HTTP), and 443 (HTTPS) are open."
fi

# Configure AWS CloudWatch Logs (optional)
echo "📊 CloudWatch Logs setup (optional)..."
echo "   To enable CloudWatch, install awscli and configure:"
echo "   aws configure"
echo ""

echo "✅ EC2 instance setup complete!"
echo ""
echo "Next steps:"
echo "  1. Run the deployment script: ./deploy/aws-deploy.sh [EC2_HOST]"
echo "  2. Configure environment variables"
echo "  3. Set up systemd services"
echo ""


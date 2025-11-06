#!/bin/bash

# Installation script for AWS EC2 Linux
# This script installs all system dependencies and project dependencies

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🚀 Installing all dependencies for AWS EC2 Linux..."
echo ""

# Detect Linux distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    OS_VERSION=$VERSION_ID
else
    echo "⚠️  Cannot detect Linux distribution"
    OS="unknown"
fi

echo "📋 Detected OS: $OS $OS_VERSION"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install Python 3.12+
install_python() {
    echo "📦 Installing Python 3.12+..."
    
    if [ "$OS" = "amzn" ] || [ "$OS" = "amazon" ]; then
        # Amazon Linux 2
        echo "   Detected Amazon Linux 2"
        sudo yum update -y
        sudo yum install -y python3.12 python3.12-pip python3.12-devel gcc
    elif [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
        # Ubuntu/Debian
        echo "   Detected Ubuntu/Debian"
        sudo apt-get update -y
        sudo apt-get install -y software-properties-common
        sudo add-apt-repository -y ppa:deadsnakes/ppa
        sudo apt-get update -y
        sudo apt-get install -y python3.12 python3.12-pip python3.12-venv python3.12-dev build-essential
    elif [ "$OS" = "rhel" ] || [ "$OS" = "centos" ]; then
        # RHEL/CentOS
        echo "   Detected RHEL/CentOS"
        sudo yum update -y
        sudo yum install -y python3.12 python3.12-pip python3.12-devel gcc
    else
        echo "   ⚠️  Unknown OS. Please install Python 3.12+ manually"
        return 1
    fi
    
    # Verify installation
    if command_exists python3.12; then
        PYTHON_VERSION=$(python3.12 --version)
        echo "   ✅ Python installed: $PYTHON_VERSION"
        return 0
    else
        echo "   ❌ Python 3.12 installation failed"
        return 1
    fi
}

# Function to install Node.js 18+
install_nodejs() {
    echo "📦 Installing Node.js 18+..."
    
    if [ "$OS" = "amzn" ] || [ "$OS" = "amazon" ]; then
        # Amazon Linux 2 - Use NodeSource repository
        echo "   Detected Amazon Linux 2"
        curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
        sudo yum install -y nodejs
    elif [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
        # Ubuntu/Debian - Use NodeSource repository
        echo "   Detected Ubuntu/Debian"
        curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
        sudo apt-get install -y nodejs
    elif [ "$OS" = "rhel" ] || [ "$OS" = "centos" ]; then
        # RHEL/CentOS - Use NodeSource repository
        echo "   Detected RHEL/CentOS"
        curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
        sudo yum install -y nodejs
    else
        echo "   ⚠️  Unknown OS. Please install Node.js 18+ manually"
        return 1
    fi
    
    # Verify installation
    if command_exists node; then
        NODE_VERSION=$(node --version)
        NPM_VERSION=$(npm --version)
        echo "   ✅ Node.js installed: $NODE_VERSION"
        echo "   ✅ npm installed: $NPM_VERSION"
        return 0
    else
        echo "   ❌ Node.js installation failed"
        return 1
    fi
}

# Function to install uv (Python package manager)
install_uv() {
    echo "📦 Installing uv (Python package manager)..."
    
    if command_exists uv; then
        UV_VERSION=$(uv --version)
        echo "   ✅ uv already installed: $UV_VERSION"
        return 0
    fi
    
    # Install uv using the official installer
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Add to PATH if not already there
    if [ -f "$HOME/.cargo/bin/uv" ]; then
        export PATH="$HOME/.cargo/bin:$PATH"
        echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
        echo "   ✅ uv installed and added to PATH"
        return 0
    else
        echo "   ❌ uv installation failed"
        return 1
    fi
}

# Function to install system build dependencies
install_build_dependencies() {
    echo "📦 Installing system build dependencies..."
    
    if [ "$OS" = "amzn" ] || [ "$OS" = "amazon" ]; then
        # Amazon Linux 2
        sudo yum groupinstall -y "Development Tools"
        sudo yum install -y openssl-devel bzip2-devel libffi-devel
    elif [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
        # Ubuntu/Debian
        sudo apt-get install -y build-essential libssl-dev libffi-dev python3-dev
    elif [ "$OS" = "rhel" ] || [ "$OS" = "centos" ]; then
        # RHEL/CentOS
        sudo yum groupinstall -y "Development Tools"
        sudo yum install -y openssl-devel bzip2-devel libffi-devel
    else
        echo "   ⚠️  Unknown OS. Skipping build dependencies"
    fi
    
    echo "   ✅ Build dependencies installed"
}

# Check and install Python
if ! command_exists python3.12 && ! command_exists python3; then
    install_python
elif command_exists python3.12; then
    PYTHON_VERSION=$(python3.12 --version)
    echo "✅ Python already installed: $PYTHON_VERSION"
elif command_exists python3; then
    PYTHON_VERSION=$(python3 --version)
    PYTHON_MAJOR=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1)
    PYTHON_MINOR=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f2)
    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 12 ]; then
        echo "✅ Python already installed: $PYTHON_VERSION"
    else
        echo "⚠️  Python version is $PYTHON_VERSION, but 3.12+ is required"
        install_python
    fi
else
    install_python
fi

# Check and install Node.js
if ! command_exists node; then
    install_nodejs
else
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -ge 18 ]; then
        echo "✅ Node.js already installed: $(node --version)"
    else
        echo "⚠️  Node.js version is $(node --version), but 18+ is required"
        install_nodejs
    fi
fi

# Check and install npm
if ! command_exists npm; then
    echo "❌ npm is not installed. Installing Node.js will install npm."
    install_nodejs
else
    echo "✅ npm already installed: $(npm --version)"
fi

# Install build dependencies
install_build_dependencies

# Install uv
if ! command_exists uv; then
    install_uv
    # Make sure uv is in PATH for this session
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Verify uv is accessible
if ! command_exists uv; then
    echo "⚠️  uv not found in PATH. Adding to PATH..."
    export PATH="$HOME/.cargo/bin:$PATH"
    if ! command_exists uv; then
        echo "❌ uv is still not accessible. Please install manually:"
        echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
fi

echo ""
echo "📦 Installing backend dependencies..."
cd backend

# Install backend dependencies using uv
if [ -f "pyproject.toml" ]; then
    echo "   Installing Python dependencies with uv..."
    uv sync
    echo "   ✅ Backend dependencies installed"
else
    echo "   ❌ pyproject.toml not found in backend directory"
    exit 1
fi

cd ..

echo ""
echo "📦 Installing frontend dependencies..."
cd frontend

# Install frontend dependencies
if [ -f "package.json" ]; then
    echo "   Installing Node.js dependencies..."
    npm ci
    echo "   ✅ Frontend dependencies installed"
else
    echo "   ❌ package.json not found in frontend directory"
    exit 1
fi

cd ..

echo ""
echo "🏗️  Building frontend for production..."
cd frontend

# Build frontend for production
if [ -f "package.json" ]; then
    echo "   Building Next.js application..."
    npm run build
    echo "   ✅ Frontend built successfully"
else
    echo "   ❌ package.json not found in frontend directory"
    exit 1
fi

cd ..

echo ""
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p backend/logs
chmod 755 logs backend/logs

echo ""
echo "✅ All dependencies installed successfully!"
echo ""
echo "📝 Next steps:"
echo "   1. Configure environment variables:"
echo "      - Backend: nano backend/.env"
echo "      - Frontend: nano frontend/.env.local"
echo "   2. Start services:"
echo "      - Using scripts: ./aws-deploy/start-all.sh"
echo "      - Using systemd: sudo ./aws-deploy/setup-systemd.sh"
echo ""
echo "📊 Installed versions:"
if command_exists python3.12; then
    echo "   Python: $(python3.12 --version)"
elif command_exists python3; then
    echo "   Python: $(python3 --version)"
fi
if command_exists node; then
    echo "   Node.js: $(node --version)"
    echo "   npm: $(npm --version)"
fi
if command_exists uv; then
    echo "   uv: $(uv --version)"
fi


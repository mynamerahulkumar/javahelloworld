# Installation Guide for AWS EC2 Linux

This guide explains how to install all dependencies for the Trading Application on AWS EC2 Linux.

## 🚀 Quick Installation

### Option 1: Automated Installation (Recommended)

```bash
cd aws-deploy
chmod +x install-dependencies.sh deploy.sh
./install-dependencies.sh
```

This will automatically:
- ✅ Install Python 3.12+ (if not installed)
- ✅ Install Node.js 18+ (if not installed)
- ✅ Install npm (comes with Node.js)
- ✅ Install uv (Python package manager)
- ✅ Install system build dependencies
- ✅ Install backend Python dependencies
- ✅ Install frontend Node.js dependencies
- ✅ Build frontend for production

### Option 2: Using Deploy Script

```bash
cd aws-deploy
chmod +x deploy.sh
./deploy.sh
```

This will run `install-dependencies.sh` automatically.

## 📋 Supported Operating Systems

The installation script supports:

- **Amazon Linux 2** (amzn/amazon)
- **Ubuntu** (ubuntu)
- **Debian** (debian)
- **RHEL/CentOS** (rhel/centos)

## 🔧 Manual Installation (If Automated Fails)

### 1. Install Python 3.12+

#### Amazon Linux 2
```bash
sudo yum update -y
sudo yum install -y python3.12 python3.12-pip python3.12-devel gcc
```

#### Ubuntu/Debian
```bash
sudo apt-get update -y
sudo apt-get install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update -y
sudo apt-get install -y python3.12 python3.12-pip python3.12-venv python3.12-dev build-essential
```

### 2. Install Node.js 18+

#### Amazon Linux 2 / RHEL/CentOS
```bash
curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
sudo yum install -y nodejs
```

#### Ubuntu/Debian
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### 3. Install uv (Python Package Manager)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.cargo/bin:$PATH"
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
```

### 4. Install System Build Dependencies

#### Amazon Linux 2 / RHEL/CentOS
```bash
sudo yum groupinstall -y "Development Tools"
sudo yum install -y openssl-devel bzip2-devel libffi-devel
```

#### Ubuntu/Debian
```bash
sudo apt-get install -y build-essential libssl-dev libffi-dev python3-dev
```

### 5. Install Backend Dependencies

```bash
cd backend
uv sync
cd ..
```

### 6. Install Frontend Dependencies

```bash
cd frontend
npm ci
npm run build
cd ..
```

## ✅ Verification

After installation, verify all dependencies:

```bash
# Check Python
python3.12 --version  # or python3 --version

# Check Node.js
node --version  # Should be v18.x or higher

# Check npm
npm --version

# Check uv
uv --version
```

## 🔍 Troubleshooting

### Python Installation Issues

If Python 3.12+ is not available in your distribution's repositories:

1. **Use pyenv** (recommended for flexibility):
   ```bash
   curl https://pyenv.run | bash
   export PATH="$HOME/.pyenv/bin:$PATH"
   pyenv install 3.12.0
   pyenv global 3.12.0
   ```

2. **Compile from source**:
   ```bash
   wget https://www.python.org/ftp/python/3.12.0/Python-3.12.0.tgz
   tar xzf Python-3.12.0.tgz
   cd Python-3.12.0
   ./configure --enable-optimizations
   make altinstall
   ```

### Node.js Installation Issues

If Node.js installation fails:

1. **Check NodeSource repository**:
   ```bash
   # For Amazon Linux 2 / RHEL/CentOS
   curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
   
   # For Ubuntu/Debian
   curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
   ```

2. **Use nvm** (Node Version Manager):
   ```bash
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
   export NVM_DIR="$HOME/.nvm"
   [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
   nvm install 20
   nvm use 20
   ```

### uv Installation Issues

If uv is not accessible after installation:

1. **Add to PATH manually**:
   ```bash
   export PATH="$HOME/.cargo/bin:$PATH"
   echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
   source ~/.bashrc
   ```

2. **Verify installation**:
   ```bash
   which uv
   uv --version
   ```

### Permission Issues

If you encounter permission errors:

```bash
# Make scripts executable
chmod +x aws-deploy/*.sh
chmod +x aws-deploy/backend/*.sh

# Check file ownership
ls -la aws-deploy/
```

### Build Dependencies Issues

If backend dependencies fail to install:

```bash
# Install additional build tools
# Amazon Linux 2 / RHEL/CentOS
sudo yum install -y gcc gcc-c++ make

# Ubuntu/Debian
sudo apt-get install -y gcc g++ make
```

## 📝 Post-Installation

After successful installation:

1. **Configure environment variables**:
   ```bash
   # Backend
   nano backend/.env
   
   # Frontend
   nano frontend/.env.local
   ```

2. **Start services**:
   ```bash
   # Using scripts
   ./aws-deploy/start-all.sh
   
   # Or using systemd
   sudo ./aws-deploy/setup-systemd.sh
   ```

## 🆘 Getting Help

If you encounter issues:

1. Check the installation logs
2. Verify all system dependencies are installed
3. Check file permissions
4. Review the troubleshooting section above
5. Check AWS EC2 security group settings (ports 8501, 3000)

## 📚 Related Documentation

- [AWS_EC2_DEPLOYMENT.md](./AWS_EC2_DEPLOYMENT.md) - Complete deployment guide
- [QUICK_START_EC2.md](./QUICK_START_EC2.md) - Quick reference
- [README.md](./README.md) - AWS deployment scripts overview


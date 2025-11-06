# AWS EC2 Deployment Scripts

This folder contains all scripts and documentation for deploying to AWS EC2 Linux.

## 📁 Folder Structure

```
aws-deploy/
├── README.md              # This file
├── deploy.sh              # Initial deployment setup
├── setup-systemd.sh       # Create systemd services
├── start-all.sh           # Start all services (production)
├── stop-all.sh            # Stop all services (production)
├── restart-all.sh         # Restart all services (production)
├── backend/
│   ├── start.sh           # Start backend (production)
│   ├── stop.sh            # Stop backend (production)
│   └── restart.sh         # Restart backend (production)
└── [Documentation files]
```

## 🚀 Quick Start

### 1. Initial Deployment

```bash
cd aws-deploy
chmod +x *.sh backend/*.sh
./deploy.sh
```

### 2. Start Services

```bash
# From project root
./aws-deploy/start-all.sh

# Or from aws-deploy folder
cd aws-deploy
./start-all.sh
```

### 3. Stop Services

```bash
./aws-deploy/stop-all.sh
```

### 4. Restart Services

```bash
./aws-deploy/restart-all.sh
```

## 📝 Viewing Logs

```bash
# Backend logs
tail -f logs/backend.log

# Frontend logs
tail -f logs/frontend.log

# Using systemd (if using systemd services)
sudo journalctl -u trading-backend -f
sudo journalctl -u trading-frontend -f
```

## 📚 Documentation

- **AWS_EC2_DEPLOYMENT.md** - Complete deployment guide
- **QUICK_START_EC2.md** - Quick reference
- **README_DEPLOYMENT.md** - Service management
- **HOW_TO_VIEW_LOGS.md** - Log viewing guide
- **DEPLOYMENT_SUMMARY.md** - Summary of optimizations

## ⚠️ Important Notes

- These scripts are for **PRODUCTION** deployment on AWS EC2
- They use **production mode** (no reload, with workers)
- For **local development**, use scripts in the root directory

## 🔄 Local vs AWS Scripts

- **Local scripts** (root directory): Development mode with hot-reload
- **AWS scripts** (aws-deploy/): Production mode with workers


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
├── simple-start-all.sh    # Minimal start script (no checks)
├── simple-stop-all.sh     # Minimal stop script
├── simple-restart-all.sh  # Minimal restart script
├── check-services.sh      # Verify backend/frontend status
├── backend/
│   ├── start.sh           # Start backend (production)
│   ├── stop.sh            # Stop backend (production)
│   └── restart.sh         # Restart backend (production)
└── [Documentation files]
```

## 🚀 Quick Start

### 0. Prerequisites on the EC2 instance

Run these once after pulling the repository (or whenever dependencies change):

```bash
# Backend Python dependencies
cd backend
python3 -m pip install -r requirements.txt

# Frontend Node dependencies (installs dev packages required for build)
cd ../frontend
npm ci --include=dev
npm run build

# Return to project root
cd ..
```

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

### 5. Simple Scripts (Minimal Checks)

Use these when you want lightweight process management without port or dependency checks:

```bash
./aws-deploy/simple-start-all.sh
./aws-deploy/simple-stop-all.sh
./aws-deploy/simple-restart-all.sh
```

> ℹ️ The minimal scripts now validate that required backend modules and Next.js build artifacts exist. If they exit early, re-run the prerequisite steps above.

### 6. Check Service Status

Run the diagnostic helper to verify processes, ports, and HTTP endpoints:

```bash
./aws-deploy/check-services.sh             # defaults to localhost
./aws-deploy/check-services.sh 127.0.0.1   # custom host/IP
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





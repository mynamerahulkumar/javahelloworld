# Deployment Guide - AWS EC2 Linux

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Viewing Logs](#viewing-logs)
3. [Managing Services](#managing-services)
4. [Troubleshooting](#troubleshooting)

## 🚀 Quick Start

### Initial Deployment

```bash
# 1. Make scripts executable
chmod +x deploy.sh setup-systemd.sh start-all.sh stop-all.sh restart-all.sh

# 2. Run deployment script
./deploy.sh

# 3. Configure environment variables
nano backend/.env
nano frontend/.env.local

# 4. Start services
./start-all.sh
```

## 📝 Viewing Logs

### Method 1: Direct Log Files

#### Backend Logs

```bash
# Real-time logs
tail -f logs/backend.log

# Last 50 lines
tail -n 50 logs/backend.log

# Last 100 lines
tail -n 100 logs/backend.log

# Search for errors
grep -i "error" logs/backend.log | tail -20

# Backend-specific log file
tail -f backend/logs/bot.log
```

#### Frontend Logs

```bash
# Real-time logs
tail -f logs/frontend.log

# Last 50 lines
tail -n 50 logs/frontend.log

# Search for errors
grep -i "error" logs/frontend.log | tail -20
```

### Method 2: Using view-logs.sh Script

```bash
# View all logs (last 20 lines)
./view-logs.sh

# Backend logs (real-time)
./view-logs.sh backend tail

# Backend logs (last 100 lines)
./view-logs.sh backend lines 100

# Frontend logs (real-time)
./view-logs.sh frontend tail

# Frontend logs (last 50 lines)
./view-logs.sh frontend lines 50
```

### Method 3: Using Journalctl (Systemd Services)

```bash
# Backend logs (real-time)
sudo journalctl -u trading-backend -f

# Frontend logs (real-time)
sudo journalctl -u trading-frontend -f

# Last 50 lines
sudo journalctl -u trading-backend -n 50

# Logs since today
sudo journalctl -u trading-backend --since today

# Logs with specific time range
sudo journalctl -u trading-backend --since "1 hour ago"
```

## 🛠️ Managing Services

### Start Services

```bash
# Start all services (scripts)
./start-all.sh

# Start backend only
cd backend && ./start.sh

# Start frontend only
cd frontend && npm run start

# Start using systemd
sudo systemctl start trading-backend
sudo systemctl start trading-frontend
```

### Stop Services

```bash
# Stop all services (scripts)
./stop-all.sh

# Stop backend only
cd backend && ./stop.sh

# Stop frontend only
./scripts/stop-frontend.sh

# Stop using systemd
sudo systemctl stop trading-backend
sudo systemctl stop trading-frontend
```

### Restart Services

```bash
# Restart all services (scripts)
./restart-all.sh

# Restart backend only
cd backend && ./restart.sh

# Restart using systemd
sudo systemctl restart trading-backend
sudo systemctl restart trading-frontend
```

### Check Service Status

```bash
# Check if processes are running
ps aux | grep uvicorn  # Backend
ps aux | grep next     # Frontend

# Check ports
ss -tuln | grep 8501   # Backend port
ss -tuln | grep 3000   # Frontend port

# Check systemd status
sudo systemctl status trading-backend
sudo systemctl status trading-frontend
```

## 🔍 Troubleshooting

### Services Not Starting

1. **Check Logs**
   ```bash
   tail -50 logs/backend.log
   tail -50 logs/frontend.log
   ```

2. **Check Environment Variables**
   ```bash
   cat backend/.env
   cat frontend/.env.local
   ```

3. **Check Dependencies**
   ```bash
   python3 --version  # Should be 3.12+
   node --version     # Should be 18+
   uv --version       # Should be installed
   ```

4. **Check Port Availability**
   ```bash
   sudo ss -tlnp | grep 8501
   sudo ss -tlnp | grep 3000
   ```

### Port Already in Use

```bash
# Find process using port
sudo ss -tlnp | grep 8501
sudo lsof -i :8501

# Kill process
sudo kill -9 <PID>
```

### Permission Issues

```bash
# Make scripts executable
chmod +x *.sh
chmod +x backend/*.sh
chmod +x scripts/*.sh

# Check file ownership
ls -la
```

### Log Files Not Found

```bash
# Create logs directory
mkdir -p logs
mkdir -p backend/logs

# Check log file locations
ls -la logs/
ls -la backend/logs/
```

## 📊 Log File Locations

### Script-based Deployment

- **Backend**: `logs/backend.log` and `backend/logs/bot.log`
- **Frontend**: `logs/frontend.log`
- **PID files**: `logs/backend.pid` and `logs/frontend.pid`

### Systemd Services

- **Backend**: `logs/backend.log` (configured in service file)
- **Frontend**: `logs/frontend.log` (configured in service file)
- **System logs**: Use `journalctl` commands

## 🔐 Security Notes

1. **Environment Variables**: Never commit `.env` files
2. **File Permissions**: Restrict access to sensitive files
   ```bash
   chmod 600 backend/.env frontend/.env.local
   ```
3. **Firewall**: Configure EC2 security group to allow only necessary ports
4. **Logs**: Regularly rotate logs to prevent disk space issues

## 📚 Additional Resources

- [AWS_EC2_DEPLOYMENT.md](./AWS_EC2_DEPLOYMENT.md) - Detailed deployment guide
- [QUICK_START_EC2.md](./QUICK_START_EC2.md) - Quick reference
- [HOW_TO_CHECK_BACKEND_LOGS.md](./HOW_TO_CHECK_BACKEND_LOGS.md) - Backend log details


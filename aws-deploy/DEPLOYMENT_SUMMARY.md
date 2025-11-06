# AWS EC2 Linux Deployment - Summary

## ✅ What's Been Optimized

### 1. Production-Ready Scripts

All scripts have been optimized for AWS EC2 Linux:

- **`deploy.sh`**: Initial deployment setup
- **`start-all.sh`**: Start both backend and frontend (production mode)
- **`stop-all.sh`**: Stop both services (EC2 Linux compatible)
- **`restart-all.sh`**: Restart both services
- **`setup-systemd.sh`**: Create systemd services for production

### 2. Backend Scripts

- **`backend/start.sh`**: Production mode (no reload, with workers)
- **`backend/stop.sh`**: EC2 Linux compatible (uses `ss`/`netstat`/`lsof`)
- **`backend/restart.sh`**: Restart backend service

### 3. Key Optimizations

#### Port Checking
- Uses `ss` (preferred on Linux)
- Falls back to `netstat` if `ss` not available
- Falls back to `lsof` if neither available

#### Production Mode
- Backend: Uses `--workers 4` instead of `--reload`
- Frontend: Uses `npm run start` (production) instead of `npm run dev`
- No hot-reload in production

#### Process Management
- Proper PID tracking
- Graceful shutdown (SIGTERM then SIGKILL)
- Process verification after startup

#### Logging
- All logs written to `logs/` directory
- Backend logs: `logs/backend.log` and `backend/logs/bot.log`
- Frontend logs: `logs/frontend.log`
- Systemd logs: `journalctl` commands

## 📝 How to View Logs

### Quick Commands

```bash
# Backend logs (real-time)
tail -f logs/backend.log

# Frontend logs (real-time)
tail -f logs/frontend.log

# Using view-logs script
./view-logs.sh backend tail
./view-logs.sh frontend tail

# Systemd logs (if using systemd)
sudo journalctl -u trading-backend -f
sudo journalctl -u trading-frontend -f
```

### Detailed Log Viewing

See [README_DEPLOYMENT.md](./README_DEPLOYMENT.md) for complete log viewing guide.

## 🚀 Deployment Steps

### 1. Initial Setup

```bash
chmod +x deploy.sh setup-systemd.sh start-all.sh stop-all.sh restart-all.sh
./deploy.sh
```

### 2. Configure Environment

```bash
# Backend
nano backend/.env

# Frontend
nano frontend/.env.local
```

### 3. Start Services

**Option A: Scripts**
```bash
./start-all.sh
```

**Option B: Systemd (Recommended)**
```bash
sudo ./setup-systemd.sh
sudo systemctl start trading-backend trading-frontend
sudo systemctl enable trading-backend trading-frontend
```

## 📊 Service Management

### Start
```bash
./start-all.sh                    # Scripts
sudo systemctl start trading-backend trading-frontend  # Systemd
```

### Stop
```bash
./stop-all.sh                     # Scripts
sudo systemctl stop trading-backend trading-frontend   # Systemd
```

### Restart
```bash
./restart-all.sh                  # Scripts
sudo systemctl restart trading-backend trading-frontend  # Systemd
```

### Status
```bash
ps aux | grep uvicorn             # Backend
ps aux | grep next                # Frontend
sudo systemctl status trading-backend   # Systemd
```

## 📚 Documentation Files

1. **AWS_EC2_DEPLOYMENT.md**: Complete deployment guide
2. **QUICK_START_EC2.md**: Quick reference guide
3. **README_DEPLOYMENT.md**: Log viewing and service management
4. **HOW_TO_CHECK_BACKEND_LOGS.md**: Detailed backend log guide

## 🔍 Log Locations

### Script-based Deployment
- Backend: `logs/backend.log`, `backend/logs/bot.log`
- Frontend: `logs/frontend.log`
- PID files: `logs/backend.pid`, `logs/frontend.pid`

### Systemd Services
- Backend: `logs/backend.log` + `journalctl -u trading-backend`
- Frontend: `logs/frontend.log` + `journalctl -u trading-frontend`

## ✅ All Scripts Are Working

All scripts have been tested and optimized for:
- ✅ AWS EC2 Linux (Amazon Linux 2, Ubuntu)
- ✅ Production mode (no reload, with workers)
- ✅ Proper process management
- ✅ Comprehensive logging
- ✅ Error handling
- ✅ Port checking (ss/netstat/lsof)
- ✅ Graceful shutdown

## 🎯 Next Steps

1. Deploy to EC2 instance
2. Run `./deploy.sh`
3. Configure environment variables
4. Start services with `./start-all.sh` or systemd
5. View logs using the commands above

For detailed instructions, see the documentation files listed above.


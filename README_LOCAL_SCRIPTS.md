# Local Development Scripts

This document explains the local development scripts in the root directory.

## 📁 Local Scripts (Root Directory)

These scripts are for **local development** with hot-reload enabled:

- `start-all.sh` - Start both backend and frontend (development mode)
- `stop-all.sh` - Stop both services
- `restart-all.sh` - Restart both services
- `backend/start.sh` - Start backend only (with --reload)
- `backend/stop.sh` - Stop backend only
- `backend/restart.sh` - Restart backend only
- `view-logs.sh` - View logs

## 🚀 Quick Start (Local Development)

### Start All Services

```bash
./start-all.sh
```

This will:
- Start backend with `--reload` (hot-reload enabled)
- Start frontend with `npm run dev` (development mode)
- Enable auto-reload on code changes

### Stop All Services

```bash
./stop-all.sh
```

### Restart All Services

```bash
./restart-all.sh
```

## 📝 Viewing Logs (Local)

```bash
# Backend logs
tail -f logs/backend.log

# Frontend logs
tail -f logs/frontend.log

# Using view-logs script
./view-logs.sh backend tail
./view-logs.sh frontend tail
```

## 🔄 Local vs AWS Scripts

| Feature | Local Scripts (Root) | AWS Scripts (aws-deploy/) |
|---------|---------------------|---------------------------|
| **Mode** | Development | Production |
| **Backend** | `--reload` (hot-reload) | `--workers 4` (no reload) |
| **Frontend** | `npm run dev` | `npm run start` (production build) |
| **Port Check** | `lsof` | `ss`/`netstat`/`lsof` |
| **Use Case** | Local development | AWS EC2 deployment |

## ⚠️ Important Notes

- Local scripts use **development mode** with hot-reload
- Changes to code will automatically reload
- For production deployment, use scripts in `aws-deploy/` folder




# Quick Start Guide

## 🚀 Starting the Full Stack Application

### Option 1: Start Both Services Together (Recommended)

```bash
# Start both backend and frontend
./start-all.sh

# Access the application:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8501
# - API Docs: http://localhost:8501/docs
```

### Option 2: Start Services Separately

#### Backend Only
```bash
cd backend
./start.sh
```

#### Frontend Only
```bash
cd frontend
npm run dev
```

## 🛑 Stopping the Application

### Stop Both Services
```bash
./stop-all.sh
```

### Stop Services Separately
```bash
# Stop backend
cd backend
./stop.sh

# Stop frontend (Ctrl+C in the terminal where it's running)
```

## 🔄 Restarting the Application

```bash
# Restart both services
./restart-all.sh
```

## 📝 Viewing Logs

```bash
# View all logs (last 20 lines)
./view-logs.sh

# Follow backend logs in real-time
./view-logs.sh backend tail

# View last 100 lines of frontend logs
./view-logs.sh frontend lines 100

# View all backend logs
./view-logs.sh backend all
```

## 📋 Prerequisites

Before starting, make sure you have:

1. **Backend Setup**:
   - Python 3.12+ installed
   - Dependencies installed: `cd backend && uv sync` or `pip install -e .`
   - `.env` file configured (copy from `.env.example`)
   - Client credentials in `backend/privatedata/srp_client_trading.csv`

2. **Frontend Setup**:
   - Node.js 18+ installed
   - Dependencies installed: `cd frontend && npm install`
   - `.env.local` file configured (copy from `.env.example`)

## 🔧 Troubleshooting

### Port Already in Use

If you see "Port already in use" errors:

```bash
# Stop all services
./stop-all.sh

# Or manually kill processes
lsof -ti :8501 | xargs kill -9  # Backend
lsof -ti :3000 | xargs kill -9  # Frontend
```

### Services Not Starting

1. Check logs:
   ```bash
   ./view-logs.sh backend
   ./view-logs.sh frontend
   ```

2. Verify prerequisites:
   - Backend: Check Python version and dependencies
   - Frontend: Check Node.js version and dependencies

3. Check environment variables:
   - Backend: Verify `backend/.env` file
   - Frontend: Verify `frontend/.env.local` file

## 📚 Additional Resources

- See `README.md` for detailed documentation
- Backend API docs: http://localhost:8501/docs (when running)
- Frontend README: `frontend/README.md`
- Backend README: `backend/README.md` (if exists)


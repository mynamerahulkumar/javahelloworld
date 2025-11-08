# Scripts Overview

## 📁 Script Organization

### Local Development Scripts (Root Directory)

These scripts are for **local development** with hot-reload:

- **`start-all.sh`** - Start both backend and frontend (development mode)
- **`stop-all.sh`** - Stop both services
- **`restart-all.sh`** - Restart both services
- **`view-logs.sh`** - View logs
- **`backend/start.sh`** - Start backend only (with --reload)
- **`backend/stop.sh`** - Stop backend only
- **`backend/restart.sh`** - Restart backend only

**Features:**
- ✅ Hot-reload enabled (auto-reload on code changes)
- ✅ Development mode
- ✅ Uses `lsof` for port checking (macOS/Linux compatible)

### AWS EC2 Production Scripts (aws-deploy/ folder)

These scripts are for **production deployment** on AWS EC2:

- **`aws-deploy/start-all.sh`** - Start both services (production mode)
- **`aws-deploy/stop-all.sh`** - Stop both services
- **`aws-deploy/restart-all.sh`** - Restart both services
- **`aws-deploy/deploy.sh`** - Initial deployment setup
- **`aws-deploy/setup-systemd.sh`** - Create systemd services
- **`aws-deploy/backend/start.sh`** - Start backend (production)
- **`aws-deploy/backend/stop.sh`** - Stop backend
- **`aws-deploy/backend/restart.sh`** - Restart backend

**Features:**
- ✅ Production mode (no reload, with workers)
- ✅ Optimized for AWS EC2 Linux
- ✅ Uses `ss`/`netstat`/`lsof` for port checking
- ✅ Systemd service support

## 🚀 Usage

### Local Development

```bash
# Start all services (development mode)
./start-all.sh

# Stop all services
./stop-all.sh

# Restart all services
./restart-all.sh

# View logs
./view-logs.sh backend tail
```

### AWS EC2 Production

```bash
# Initial deployment
cd aws-deploy
./deploy.sh

# Start all services (production mode)
./aws-deploy/start-all.sh

# Stop all services
./aws-deploy/stop-all.sh

# Restart all services
./aws-deploy/restart-all.sh
```

## 📝 Key Differences

| Feature | Local Scripts | AWS Scripts |
|---------|--------------|-------------|
| **Location** | Root directory | `aws-deploy/` folder |
| **Mode** | Development | Production |
| **Backend** | `--reload` | `--workers 4` |
| **Frontend** | `npm run dev` | `npm run start` |
| **Hot Reload** | ✅ Yes | ❌ No |
| **Port Check** | `lsof` | `ss`/`netstat`/`lsof` |
| **Use Case** | Local development | AWS EC2 deployment |

## ✅ All Scripts Are Working

Both local and AWS scripts are:
- ✅ Executable and ready to use
- ✅ Properly separated
- ✅ Optimized for their respective environments
- ✅ Fully documented




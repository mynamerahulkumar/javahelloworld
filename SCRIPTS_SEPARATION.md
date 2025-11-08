# Scripts Separation Guide

## 📁 Script Organization

Scripts are now separated into two distinct groups:

### 1. Local Development Scripts (Root Directory)

**Location**: Root directory of the project

**Purpose**: Local development with hot-reload

**Scripts**:
- `start-all.sh` - Start both services (development mode)
- `stop-all.sh` - Stop both services
- `restart-all.sh` - Restart both services
- `view-logs.sh` - View logs
- `backend/start.sh` - Start backend (with --reload)
- `backend/stop.sh` - Stop backend
- `backend/restart.sh` - Restart backend

**Features**:
- ✅ Development mode
- ✅ Hot-reload enabled (`--reload` for backend, `npm run dev` for frontend)
- ✅ Uses `lsof` for port checking (works on macOS and Linux)
- ✅ Auto-reload on code changes

### 2. AWS EC2 Production Scripts (aws-deploy/ folder)

**Location**: `aws-deploy/` folder

**Purpose**: Production deployment on AWS EC2 Linux

**Scripts**:
- `aws-deploy/start-all.sh` - Start both services (production mode)
- `aws-deploy/stop-all.sh` - Stop both services
- `aws-deploy/restart-all.sh` - Restart both services
- `aws-deploy/deploy.sh` - Initial deployment setup
- `aws-deploy/setup-systemd.sh` - Create systemd services
- `aws-deploy/backend/start.sh` - Start backend (production)
- `aws-deploy/backend/stop.sh` - Stop backend
- `aws-deploy/backend/restart.sh` - Restart backend

**Features**:
- ✅ Production mode
- ✅ No hot-reload (`--workers 4` for backend, `npm run start` for frontend)
- ✅ Optimized for AWS EC2 Linux
- ✅ Uses `ss`/`netstat`/`lsof` for port checking (Linux compatible)
- ✅ Systemd service support

## 🚀 Usage

### Local Development

```bash
# Start all services (development mode with hot-reload)
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
# or
cd aws-deploy && ./start-all.sh

# Stop all services
./aws-deploy/stop-all.sh

# Restart all services
./aws-deploy/restart-all.sh
```

## 📊 Key Differences

| Feature | Local Scripts | AWS Scripts |
|---------|--------------|-------------|
| **Location** | Root directory | `aws-deploy/` folder |
| **Mode** | Development | Production |
| **Backend Command** | `--reload` | `--workers 4` |
| **Frontend Command** | `npm run dev` | `npm run start` |
| **Hot Reload** | ✅ Yes | ❌ No |
| **Port Check** | `lsof` | `ss`/`netstat`/`lsof` |
| **Use Case** | Local development | AWS EC2 deployment |
| **Performance** | Optimized for development | Optimized for production |

## ✅ Verification

All scripts have been:
- ✅ Separated into local and AWS folders
- ✅ Syntax checked and verified
- ✅ Made executable
- ✅ Documented

## 📝 Documentation

- **SCRIPTS_OVERVIEW.md** - Overview of all scripts
- **README_LOCAL_SCRIPTS.md** - Local development scripts guide
- **aws-deploy/README.md** - AWS deployment scripts guide
- **aws-deploy/AWS_EC2_DEPLOYMENT.md** - Complete AWS deployment guide




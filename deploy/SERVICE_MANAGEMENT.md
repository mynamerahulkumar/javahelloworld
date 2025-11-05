# Service Management Guide for AWS EC2 Linux

Complete guide for managing Trading API services on Amazon Linux EC2.

## Quick Reference

### Start Services
```bash
# Start backend only
./deploy/scripts/start-backend.sh

# Start frontend only
./deploy/scripts/start-frontend.sh

# Start both services
./deploy/scripts/start-all.sh
```

### Stop Services
```bash
# Stop backend only
./deploy/scripts/stop-backend.sh

# Stop frontend only
./deploy/scripts/stop-frontend.sh

# Stop both services
./deploy/scripts/stop-all.sh
```

### Restart Services
```bash
# Restart backend only
./deploy/scripts/restart-backend.sh

# Restart frontend only
./deploy/scripts/restart-frontend.sh

# Restart both services
./deploy/scripts/restart-all.sh
```

### Check Status
```bash
# Check all services status
./deploy/scripts/status.sh
```

## Detailed Usage

### Start Scripts

#### `start-backend.sh`
Starts the backend FastAPI service.

```bash
./deploy/scripts/start-backend.sh
```

**Features:**
- Checks if service is already running
- Uses systemd service if available
- Falls back to manual start if systemd not configured
- Creates virtual environment if needed
- Shows service status after start

#### `start-frontend.sh`
Starts the frontend Next.js service.

```bash
./deploy/scripts/start-frontend.sh
```

**Features:**
- Checks if service is already running
- Uses systemd service if available
- Falls back to manual start if systemd not configured
- Builds frontend if not already built
- Shows service status after start

#### `start-all.sh`
Starts both backend and frontend services.

```bash
./deploy/scripts/start-all.sh
```

**Features:**
- Starts backend first
- Waits for backend to be ready
- Starts frontend
- Shows summary of all services

### Stop Scripts

#### `stop-backend.sh`
Stops the backend service.

```bash
./deploy/scripts/stop-backend.sh
```

**Features:**
- Stops systemd service if configured
- Falls back to manual process termination
- Cleans up PID files
- Handles processes gracefully

#### `stop-frontend.sh`
Stops the frontend service.

```bash
./deploy/scripts/stop-frontend.sh
```

**Features:**
- Stops systemd service if configured
- Falls back to manual process termination
- Cleans up PID files
- Handles processes gracefully

#### `stop-all.sh`
Stops both backend and frontend services.

```bash
./deploy/scripts/stop-all.sh
```

### Restart Scripts

#### `restart-backend.sh`
Restarts the backend service.

```bash
./deploy/scripts/restart-backend.sh
```

**Process:**
1. Stops backend
2. Waits 2 seconds
3. Starts backend

#### `restart-frontend.sh`
Restarts the frontend service.

```bash
./deploy/scripts/restart-frontend.sh
```

#### `restart-all.sh`
Restarts both services.

```bash
./deploy/scripts/restart-all.sh
```

**Process:**
1. Stops all services
2. Waits 3 seconds
3. Starts all services

### Status Script

#### `status.sh`
Shows comprehensive status of all services.

```bash
./deploy/scripts/status.sh
```

**Shows:**
- Service running status
- Auto-start configuration
- Systemd service details
- Quick command reference

## Using Systemd Directly

### Start Services
```bash
# Start backend
sudo systemctl start trading-api-backend

# Start frontend
sudo systemctl start trading-api-frontend

# Start both
sudo systemctl start trading-api-backend trading-api-frontend
```

### Stop Services
```bash
# Stop backend
sudo systemctl stop trading-api-backend

# Stop frontend
sudo systemctl stop trading-api-frontend

# Stop both
sudo systemctl stop trading-api-backend trading-api-frontend
```

### Restart Services
```bash
# Restart backend
sudo systemctl restart trading-api-backend

# Restart frontend
sudo systemctl restart trading-api-frontend

# Restart both
sudo systemctl restart trading-api-backend trading-api-frontend
```

### Check Status
```bash
# Backend status
sudo systemctl status trading-api-backend

# Frontend status
sudo systemctl status trading-api-frontend

# Both services
sudo systemctl status trading-api-backend trading-api-frontend
```

### Enable Auto-Start
```bash
# Enable backend to start on boot
sudo systemctl enable trading-api-backend

# Enable frontend to start on boot
sudo systemctl enable trading-api-frontend

# Enable both
sudo systemctl enable trading-api-backend trading-api-frontend
```

### Disable Auto-Start
```bash
# Disable backend auto-start
sudo systemctl disable trading-api-backend

# Disable frontend auto-start
sudo systemctl disable trading-api-frontend
```

## Common Workflows

### Initial Deployment
```bash
# 1. Start all services
./deploy/scripts/start-all.sh

# 2. Check status
./deploy/scripts/status.sh

# 3. View logs
./deploy/scripts/view-logs.sh
```

### After Code Update
```bash
# 1. Restart all services
./deploy/scripts/restart-all.sh

# 2. Check logs for errors
./deploy/scripts/view-logs.sh all --last 50

# 3. Verify services are running
./deploy/scripts/status.sh
```

### Troubleshooting
```bash
# 1. Check service status
./deploy/scripts/status.sh

# 2. View logs
./deploy/scripts/view-backend-logs.sh --last 100
./deploy/scripts/view-frontend-logs.sh --last 100

# 3. Restart problematic service
./deploy/scripts/restart-backend.sh
# or
./deploy/scripts/restart-frontend.sh
```

### Maintenance Window
```bash
# 1. Stop all services
./deploy/scripts/stop-all.sh

# 2. Perform maintenance (updates, backups, etc.)

# 3. Start all services
./deploy/scripts/start-all.sh

# 4. Verify everything is working
./deploy/scripts/status.sh
./deploy/scripts/view-logs.sh all --last 20
```

## Service Management Best Practices

### 1. Always Check Status First
```bash
./deploy/scripts/status.sh
```

### 2. Restart After Configuration Changes
```bash
# After changing .env files
./deploy/scripts/restart-all.sh
```

### 3. Monitor Logs After Restart
```bash
# Restart and immediately check logs
./deploy/scripts/restart-all.sh
./deploy/scripts/view-logs.sh all --last 50
```

### 4. Use Systemd for Production
```bash
# Ensure services are enabled for auto-start
sudo systemctl enable trading-api-backend trading-api-frontend

# Check they start on boot
sudo systemctl is-enabled trading-api-backend
sudo systemctl is-enabled trading-api-frontend
```

### 5. Graceful Shutdowns
Always use the stop scripts instead of killing processes:
```bash
# Good
./deploy/scripts/stop-backend.sh

# Bad
kill -9 <pid>
```

## Troubleshooting

### Service Won't Start

1. **Check logs:**
   ```bash
   ./deploy/scripts/view-backend-logs.sh --last 50
   ```

2. **Check systemd status:**
   ```bash
   sudo systemctl status trading-api-backend
   ```

3. **Check if port is in use:**
   ```bash
   sudo lsof -i :8501  # Backend
   sudo lsof -i :3000  # Frontend
   ```

4. **Check permissions:**
   ```bash
   ls -la /opt/trading-api/
   sudo chown -R ec2-user:ec2-user /opt/trading-api
   ```

### Service Keeps Stopping

1. **Check systemd logs:**
   ```bash
   sudo journalctl -u trading-api-backend -n 100
   ```

2. **Check for errors:**
   ```bash
   ./deploy/scripts/view-backend-logs.sh | grep -i error
   ```

3. **Check system resources:**
   ```bash
   free -h
   df -h
   top
   ```

### Service Not Responding

1. **Restart service:**
   ```bash
   ./deploy/scripts/restart-backend.sh
   ```

2. **Check if process is running:**
   ```bash
   ps aux | grep uvicorn
   ps aux | grep next
   ```

3. **Check network connectivity:**
   ```bash
   curl http://localhost:8501/
   curl http://localhost:3000/
   ```

## Script Locations

All scripts are located in `/opt/trading-api/deploy/scripts/`:

- `start-backend.sh`
- `start-frontend.sh`
- `start-all.sh`
- `stop-backend.sh`
- `stop-frontend.sh`
- `stop-all.sh`
- `restart-backend.sh`
- `restart-frontend.sh`
- `restart-all.sh`
- `status.sh`

## Quick Command Cheat Sheet

```bash
# Start
./deploy/scripts/start-backend.sh
./deploy/scripts/start-frontend.sh
./deploy/scripts/start-all.sh

# Stop
./deploy/scripts/stop-backend.sh
./deploy/scripts/stop-frontend.sh
./deploy/scripts/stop-all.sh

# Restart
./deploy/scripts/restart-backend.sh
./deploy/scripts/restart-frontend.sh
./deploy/scripts/restart-all.sh

# Status
./deploy/scripts/status.sh

# Logs
./deploy/scripts/view-backend-logs.sh
./deploy/scripts/view-frontend-logs.sh
./deploy/scripts/view-logs.sh
```

## Notes

- All scripts work with both systemd services and manual processes
- Scripts automatically detect the deployment method
- Scripts provide helpful error messages and status updates
- All scripts are executable and ready to use
- Scripts handle edge cases (already running, not found, etc.)


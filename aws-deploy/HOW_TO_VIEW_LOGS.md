# How to View Logs - Complete Guide

## 📝 Quick Reference

### Backend Logs

```bash
# Real-time logs
tail -f logs/backend.log

# Last 50 lines
tail -n 50 logs/backend.log

# Using view-logs script
./view-logs.sh backend tail
```

### Frontend Logs

```bash
# Real-time logs
tail -f logs/frontend.log

# Last 50 lines
tail -n 50 logs/frontend.log

# Using view-logs script
./view-logs.sh frontend tail
```

### Systemd Logs (if using systemd services)

```bash
# Backend logs (real-time)
sudo journalctl -u trading-backend -f

# Frontend logs (real-time)
sudo journalctl -u trading-frontend -f
```

## 📍 Log File Locations

### Script-based Deployment

- **Backend**: 
  - `logs/backend.log` (main log)
  - `backend/logs/bot.log` (detailed backend log)
- **Frontend**: 
  - `logs/frontend.log`
- **PID files**: 
  - `logs/backend.pid`
  - `logs/frontend.pid`

### Systemd Services

- **Backend**: 
  - `logs/backend.log` (configured in service file)
  - System logs: `journalctl -u trading-backend`
- **Frontend**: 
  - `logs/frontend.log` (configured in service file)
  - System logs: `journalctl -u trading-frontend`

## 🔍 Detailed Log Viewing Commands

### Method 1: Direct File Access

#### Backend Logs

```bash
# View last 20 lines
tail -n 20 logs/backend.log

# View last 100 lines
tail -n 100 logs/backend.log

# Follow logs in real-time
tail -f logs/backend.log

# Search for errors
grep -i "error" logs/backend.log | tail -20

# Search for specific text
grep -i "fear\|greed" logs/backend.log

# View backend-specific log
tail -f backend/logs/bot.log
```

#### Frontend Logs

```bash
# View last 20 lines
tail -n 20 logs/frontend.log

# View last 100 lines
tail -n 100 logs/frontend.log

# Follow logs in real-time
tail -f logs/frontend.log

# Search for errors
grep -i "error" logs/frontend.log | tail -20
```

### Method 2: Using view-logs.sh Script

```bash
# View all logs (last 20 lines)
./view-logs.sh

# Backend logs (real-time)
./view-logs.sh backend tail

# Backend logs (last 50 lines)
./view-logs.sh backend lines 50

# Backend logs (last 100 lines)
./view-logs.sh backend lines 100

# Backend logs (all)
./view-logs.sh backend all

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

# Logs since 1 hour ago
sudo journalctl -u trading-backend --since "1 hour ago"

# Logs with specific time range
sudo journalctl -u trading-backend --since "2024-11-06 10:00:00" --until "2024-11-06 12:00:00"

# Search for errors
sudo journalctl -u trading-backend | grep -i error | tail -20
```

## 🔎 Searching Logs

### Search for Errors

```bash
# Backend errors
grep -i "error" logs/backend.log | tail -20

# Frontend errors
grep -i "error" logs/frontend.log | tail -20

# All errors
grep -i "error" logs/*.log
```

### Search for Specific Events

```bash
# Fear & Greed Index
grep -i "fear\|greed" logs/backend.log

# Connection issues
grep -i "connection\|timeout" logs/backend.log

# API requests
grep -i "request\|response" logs/backend.log

# Order placement
grep -i "order\|position" logs/backend.log
```

### Search with Context

```bash
# Show 5 lines before and after match
grep -i -C 5 "error" logs/backend.log

# Show 10 lines after match
grep -i -A 10 "error" logs/backend.log

# Show 10 lines before match
grep -i -B 10 "error" logs/backend.log
```

## 📊 Monitoring Logs in Real-Time

### Watch Multiple Logs

```bash
# Terminal 1: Backend logs
tail -f logs/backend.log

# Terminal 2: Frontend logs
tail -f logs/frontend.log

# Terminal 3: Both logs (using multitail if installed)
multitail logs/backend.log logs/frontend.log
```

### Filter Logs While Watching

```bash
# Watch backend logs and filter for errors
tail -f logs/backend.log | grep -i error

# Watch backend logs and filter for specific events
tail -f logs/backend.log | grep -i "fear\|greed\|connection"
```

## 🛠️ Log Management

### Check Log File Sizes

```bash
# Check log file sizes
ls -lh logs/
ls -lh backend/logs/

# Check disk space
df -h
```

### Clear Logs (Use with Caution)

```bash
# Clear backend log
> logs/backend.log

# Clear frontend log
> logs/frontend.log

# Clear backend bot log
> backend/logs/bot.log
```

### Rotate Logs

```bash
# Rotate backend log (keep last 1000 lines)
tail -n 1000 logs/backend.log > logs/backend.log.tmp
mv logs/backend.log.tmp logs/backend.log

# Rotate frontend log
tail -n 1000 logs/frontend.log > logs/frontend.log.tmp
mv logs/frontend.log.tmp logs/frontend.log
```

## 📋 Common Log Patterns

### Successful Startup

```
INFO - Starting Trading API Server
INFO - Log file: /path/to/logs/bot.log
INFO - Application startup complete
```

### Error Patterns

```
ERROR - Failed to start server
ERROR - ModuleNotFoundError
ERROR - Connection refused
ERROR - Port already in use
```

### API Request Patterns

```
INFO - Request: GET /api/v1/fear-greed-index
INFO - Response: GET /api/v1/fear-greed-index - Status: 200
```

## 💡 Tips

1. **Use `tail -f`** for real-time monitoring
2. **Use `grep`** to filter logs for specific events
3. **Check both log files** if issues occur (backend.log and bot.log)
4. **Use systemd logs** if using systemd services
5. **Rotate logs regularly** to prevent disk space issues
6. **Monitor log file sizes** to prevent disk full errors

## 🔗 Related Documentation

- [AWS_EC2_DEPLOYMENT.md](./AWS_EC2_DEPLOYMENT.md) - Complete deployment guide
- [README_DEPLOYMENT.md](./README_DEPLOYMENT.md) - Service management
- [HOW_TO_CHECK_BACKEND_LOGS.md](./HOW_TO_CHECK_BACKEND_LOGS.md) - Detailed backend log guide


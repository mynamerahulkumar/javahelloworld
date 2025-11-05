# Log Viewing Guide for Amazon Linux

This guide explains how to view and manage logs for the Trading API on Amazon Linux.

## Quick Reference

### View Backend Logs
```bash
# Real-time logs (follow)
./deploy/scripts/view-backend-logs.sh

# Last 100 lines
./deploy/scripts/view-backend-logs.sh --last 100

# Last 50 lines
./deploy/scripts/view-backend-logs.sh --last 50
```

### View Frontend Logs
```bash
# Real-time logs (follow)
./deploy/scripts/view-frontend-logs.sh

# Last 100 lines
./deploy/scripts/view-frontend-logs.sh --last 100
```

### View All Logs
```bash
# Real-time logs (both services)
./deploy/scripts/view-logs.sh

# View backend only
./deploy/scripts/view-logs.sh backend

# View frontend only
./deploy/scripts/view-logs.sh frontend

# Last 200 lines of all logs
./deploy/scripts/view-logs.sh all --last 200
```

### Check Log Status
```bash
# Check all services
./deploy/scripts/check-logs.sh

# Check backend only
./deploy/scripts/check-logs.sh backend

# Check frontend only
./deploy/scripts/check-logs.sh frontend
```

## Using Systemd Journalctl (Direct Commands)

### Backend Logs

```bash
# Follow backend logs in real-time
sudo journalctl -u trading-api-backend -f

# Show last 100 lines
sudo journalctl -u trading-api-backend -n 100

# Show last 50 lines with timestamps
sudo journalctl -u trading-api-backend -n 50 --no-pager

# Show logs since today
sudo journalctl -u trading-api-backend --since today

# Show logs for a specific date
sudo journalctl -u trading-api-backend --since "2024-01-01 00:00:00" --until "2024-01-01 23:59:59"

# Show logs with error level and above
sudo journalctl -u trading-api-backend -p err

# Show logs between two times
sudo journalctl -u trading-api-backend --since "1 hour ago"
```

### Frontend Logs

```bash
# Follow frontend logs in real-time
sudo journalctl -u trading-api-frontend -f

# Show last 100 lines
sudo journalctl -u trading-api-frontend -n 100

# Show logs since today
sudo journalctl -u trading-api-frontend --since today
```

### Both Services

```bash
# Follow both services
sudo journalctl -u trading-api-backend -u trading-api-frontend -f

# Show last 100 lines from both
sudo journalctl -u trading-api-backend -u trading-api-frontend -n 100
```

## File-Based Logs

If systemd services are not configured, logs are written to files:

### Backend Logs
- Standard output: `/var/log/trading-api/backend.log`
- Error output: `/var/log/trading-api/backend.error.log`

### Frontend Logs
- Standard output: `/var/log/trading-api/frontend.log`
- Error output: `/var/log/trading-api/frontend.error.log`

### View File Logs

```bash
# Follow backend log file
tail -f /var/log/trading-api/backend.log

# Show last 100 lines
tail -n 100 /var/log/trading-api/backend.log

# Follow both standard and error logs
tail -f /var/log/trading-api/backend.log /var/log/trading-api/backend.error.log

# View frontend logs
tail -f /var/log/trading-api/frontend.log
tail -n 100 /var/log/trading-api/frontend.log
```

## Log Locations Summary

### Systemd Journal (Recommended)
- **Backend**: `sudo journalctl -u trading-api-backend`
- **Frontend**: `sudo journalctl -u trading-api-frontend`
- **Location**: Managed by systemd, stored in `/var/log/journal/`

### File-Based Logs (Fallback)
- **Backend**: `/var/log/trading-api/backend.log`
- **Backend Errors**: `/var/log/trading-api/backend.error.log`
- **Frontend**: `/var/log/trading-api/frontend.log`
- **Frontend Errors**: `/var/log/trading-api/frontend.error.log`

## Useful Log Commands

### Search Logs

```bash
# Search for errors in backend logs
sudo journalctl -u trading-api-backend | grep -i error

# Search for specific text
sudo journalctl -u trading-api-backend | grep "order"

# Search case-insensitive
sudo journalctl -u trading-api-backend | grep -i "api"

# Search with context (3 lines before and after)
sudo journalctl -u trading-api-backend | grep -i "error" -A 3 -B 3
```

### Filter by Time

```bash
# Logs from last hour
sudo journalctl -u trading-api-backend --since "1 hour ago"

# Logs from last 30 minutes
sudo journalctl -u trading-api-backend --since "30 minutes ago"

# Logs from today
sudo journalctl -u trading-api-backend --since today

# Logs from yesterday
sudo journalctl -u trading-api-backend --since yesterday --until today

# Logs between specific times
sudo journalctl -u trading-api-backend --since "2024-01-15 10:00:00" --until "2024-01-15 11:00:00"
```

### Filter by Log Level

```bash
# Show only errors
sudo journalctl -u trading-api-backend -p err

# Show errors and warnings
sudo journalctl -u trading-api-backend -p warning

# Show all levels
sudo journalctl -u trading-api-backend -p debug
```

### Export Logs

```bash
# Export to file
sudo journalctl -u trading-api-backend > backend-logs.txt

# Export last 1000 lines
sudo journalctl -u trading-api-backend -n 1000 > backend-logs.txt

# Export with timestamps
sudo journalctl -u trading-api-backend --since today > backend-logs-$(date +%Y%m%d).txt
```

## Troubleshooting

### No Logs Found

```bash
# Check if service is running
sudo systemctl status trading-api-backend
sudo systemctl status trading-api-frontend

# Check if log directory exists
ls -la /var/log/trading-api/

# Check systemd service status
sudo systemctl list-units | grep trading-api
```

### Logs Not Updating

```bash
# Check if service is active
sudo systemctl is-active trading-api-backend

# Restart service to generate new logs
sudo systemctl restart trading-api-backend

# Check disk space (logs might be full)
df -h /var/log
```

### Permission Issues

```bash
# Fix log directory permissions
sudo chown -R ec2-user:ec2-user /var/log/trading-api
sudo chmod -R 755 /var/log/trading-api

# Check current permissions
ls -la /var/log/trading-api/
```

### Clear Old Logs

```bash
# Clear systemd journal (keep last 3 days)
sudo journalctl --vacuum-time=3d

# Clear systemd journal (keep last 100MB)
sudo journalctl --vacuum-size=100M

# Clear specific service logs
sudo journalctl --vacuum-time=1d -u trading-api-backend
```

## Log Rotation

Systemd automatically manages log rotation. To configure:

```bash
# Edit journald configuration
sudo nano /etc/systemd/journald.conf

# Key settings:
# SystemMaxUse=500M    # Maximum disk space
# MaxRetentionSec=7d   # Keep logs for 7 days

# Apply changes
sudo systemctl restart systemd-journald
```

## Monitoring Logs

### Watch Logs in Real-Time

```bash
# Terminal 1: Backend logs
./deploy/scripts/view-backend-logs.sh

# Terminal 2: Frontend logs
./deploy/scripts/view-frontend-logs.sh

# Or use tmux/screen for multiple panes
tmux new -s logs
# Split window: Ctrl+B then "
# Switch panes: Ctrl+B then arrow keys
```

### Set Up Log Alerts

```bash
# Monitor for errors and send alert
sudo journalctl -u trading-api-backend -f | grep -i "error" | while read line; do
    echo "ALERT: $line" | mail -s "Trading API Error" your-email@example.com
done
```

## Best Practices

1. **Use systemd journalctl** for centralized log management
2. **Monitor logs regularly** to catch issues early
3. **Set up log rotation** to prevent disk space issues
4. **Export important logs** before clearing
5. **Use grep** to filter relevant information
6. **Check logs after deployments** to ensure services started correctly

## Quick Commands Cheat Sheet

```bash
# Backend - follow logs
sudo journalctl -u trading-api-backend -f

# Frontend - follow logs
sudo journalctl -u trading-api-frontend -f

# Backend - last 100 lines
sudo journalctl -u trading-api-backend -n 100

# Search for errors
sudo journalctl -u trading-api-backend | grep -i error

# Logs since today
sudo journalctl -u trading-api-backend --since today

# Check service status
sudo systemctl status trading-api-backend

# View log files directly
tail -f /var/log/trading-api/backend.log
```

## Scripts Available

1. **`view-logs.sh`** - Main log viewer (supports backend/frontend/all)
2. **`view-backend-logs.sh`** - Quick backend log viewer
3. **`view-frontend-logs.sh`** - Quick frontend log viewer
4. **`check-logs.sh`** - Comprehensive log status checker

All scripts are located in `deploy/scripts/` and are executable.


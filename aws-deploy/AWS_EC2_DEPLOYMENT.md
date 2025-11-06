# AWS EC2 Linux Deployment Guide

This guide explains how to deploy and manage the Trading Application on AWS EC2 Linux.

## Prerequisites

- AWS EC2 instance running Amazon Linux 2 or Ubuntu
- Python 3.12+ installed
- Node.js 18+ installed
- `uv` Python package manager (will be installed automatically)
- Ports 8501 (backend) and 3000 (frontend) open in security group

## Initial Setup

### 1. Clone and Navigate to Project

```bash
cd /path/to/your/project
```

### 2. Run Deployment Script

```bash
chmod +x deploy.sh
./deploy.sh
```

This will:
- Install system dependencies
- Install backend Python dependencies
- Install frontend Node.js dependencies
- Build frontend for production
- Set up necessary directories and permissions

### 3. Configure Environment Variables

#### Backend Environment Variables

Edit `backend/.env`:

```bash
cd backend
nano .env
```

Required variables:
```env
CRYPTO_MARKET_API_KEY=your_coinmarketcap_api_key
SUPABASE_URL=your_supabase_url (optional)
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key (optional)
SUPABASE_ANON_KEY=your_supabase_anon_key (optional)
```

#### Frontend Environment Variables

Edit `frontend/.env.local`:

```bash
cd frontend
nano .env.local
```

Required variables:
```env
NEXT_PUBLIC_API_BASE_URL=http://your-ec2-ip:8501/api/v1
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

## Starting Services

### Option 1: Using Scripts (Recommended for Development/Testing)

#### Start All Services

```bash
./start-all.sh
```

#### Stop All Services

```bash
./stop-all.sh
```

#### Restart All Services

```bash
./restart-all.sh
```

### Option 2: Using Systemd Services (Recommended for Production)

#### Setup Systemd Services

```bash
sudo chmod +x setup-systemd.sh
sudo ./setup-systemd.sh
```

#### Start Services

```bash
sudo systemctl start trading-backend
sudo systemctl start trading-frontend
```

#### Stop Services

```bash
sudo systemctl stop trading-backend
sudo systemctl stop trading-frontend
```

#### Enable Services on Boot

```bash
sudo systemctl enable trading-backend
sudo systemctl enable trading-frontend
```

#### Check Service Status

```bash
sudo systemctl status trading-backend
sudo systemctl status trading-frontend
```

## Viewing Logs

### Method 1: Using Log Files (Script-based deployment)

#### Backend Logs

```bash
# View last 50 lines
tail -n 50 logs/backend.log

# Follow logs in real-time
tail -f logs/backend.log

# View last 100 lines
tail -n 100 logs/backend.log

# Search for errors
grep -i "error" logs/backend.log | tail -20

# View backend-specific logs
tail -f backend/logs/bot.log
```

#### Frontend Logs

```bash
# View last 50 lines
tail -n 50 logs/frontend.log

# Follow logs in real-time
tail -f logs/frontend.log

# Search for errors
grep -i "error" logs/frontend.log | tail -20
```

#### All Logs

```bash
# View last 20 lines of all logs
./view-logs.sh all

# Follow backend logs
./view-logs.sh backend tail

# Follow frontend logs
./view-logs.sh frontend tail
```

### Method 2: Using Journalctl (Systemd services)

#### Backend Logs

```bash
# View recent logs
sudo journalctl -u trading-backend -n 50

# Follow logs in real-time
sudo journalctl -u trading-backend -f

# View logs since today
sudo journalctl -u trading-backend --since today

# View logs with timestamps
sudo journalctl -u trading-backend --since "1 hour ago"
```

#### Frontend Logs

```bash
# View recent logs
sudo journalctl -u trading-frontend -n 50

# Follow logs in real-time
sudo journalctl -u trading-frontend -f

# View logs since today
sudo journalctl -u trading-frontend --since today
```

### Method 3: Using view-logs.sh Script

```bash
# View all logs (last 20 lines)
./view-logs.sh

# View backend logs in real-time
./view-logs.sh backend tail

# View last 100 lines of backend logs
./view-logs.sh backend lines 100

# View frontend logs in real-time
./view-logs.sh frontend tail
```

## Log File Locations

### Script-based Deployment

- **Backend logs**: `logs/backend.log` and `backend/logs/bot.log`
- **Frontend logs**: `logs/frontend.log`
- **PID files**: `logs/backend.pid` and `logs/frontend.pid`

### Systemd Services

- **Backend logs**: `logs/backend.log` (configured in service file)
- **Frontend logs**: `logs/frontend.log` (configured in service file)
- **System logs**: `journalctl -u trading-backend` and `journalctl -u trading-frontend`

## Troubleshooting

### Check if Services are Running

```bash
# Check backend
ps aux | grep uvicorn
netstat -tuln | grep 8501
# or
ss -tuln | grep 8501

# Check frontend
ps aux | grep "next"
netstat -tuln | grep 3000
# or
ss -tuln | grep 3000
```

### Check Port Availability

```bash
# Check port 8501 (backend)
sudo netstat -tuln | grep 8501
# or
sudo ss -tuln | grep 8501

# Check port 3000 (frontend)
sudo netstat -tuln | grep 3000
# or
sudo ss -tuln | grep 3000
```

### Common Issues

#### Port Already in Use

```bash
# Find process using port 8501
sudo lsof -i :8501
# or
sudo ss -tlnp | grep 8501

# Kill the process
sudo kill -9 <PID>
```

#### Services Not Starting

1. Check logs for errors:
   ```bash
   tail -50 logs/backend.log
   tail -50 logs/frontend.log
   ```

2. Verify environment variables are set:
   ```bash
   cat backend/.env
   cat frontend/.env.local
   ```

3. Check Python/Node.js versions:
   ```bash
   python3 --version  # Should be 3.12+
   node --version     # Should be 18+
   ```

#### Permission Issues

```bash
# Make scripts executable
chmod +x *.sh
chmod +x backend/*.sh
chmod +x scripts/*.sh

# Check file ownership
ls -la
```

## Security Considerations

### Firewall Configuration

Ensure your EC2 security group allows:
- Port 8501 (Backend API) - from your IP or load balancer
- Port 3000 (Frontend) - from your IP or load balancer
- Port 22 (SSH) - from your IP only

### Environment Variables

- Never commit `.env` files to git
- Use AWS Secrets Manager or Parameter Store for sensitive data
- Restrict file permissions: `chmod 600 backend/.env frontend/.env.local`

### Process Management

- Use systemd services for production (better process management)
- Set up log rotation to prevent disk space issues
- Monitor disk space regularly

## Production Recommendations

1. **Use Nginx as Reverse Proxy**: Configure Nginx to proxy requests to backend and frontend
2. **Use PM2 or Systemd**: For better process management
3. **Set up Log Rotation**: Prevent log files from filling disk
4. **Monitor Resources**: Use CloudWatch or similar monitoring
5. **Use HTTPS**: Set up SSL certificates (Let's Encrypt)
6. **Backup**: Regular backups of database and configuration files

## Quick Reference

### Start Services
```bash
./start-all.sh                    # Script-based
sudo systemctl start trading-backend trading-frontend  # Systemd
```

### Stop Services
```bash
./stop-all.sh                     # Script-based
sudo systemctl stop trading-backend trading-frontend   # Systemd
```

### Restart Services
```bash
./restart-all.sh                  # Script-based
sudo systemctl restart trading-backend trading-frontend  # Systemd
```

### View Logs
```bash
tail -f logs/backend.log          # Backend
tail -f logs/frontend.log         # Frontend
sudo journalctl -u trading-backend -f  # Systemd backend
sudo journalctl -u trading-frontend -f # Systemd frontend
```

### Check Status
```bash
ps aux | grep uvicorn             # Backend process
ps aux | grep next                # Frontend process
sudo systemctl status trading-backend   # Systemd backend
sudo systemctl status trading-frontend  # Systemd frontend
```


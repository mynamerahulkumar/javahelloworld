# AWS EC2 Deployment Guide

This guide explains how to deploy the Trading API application to AWS EC2 for production use.

## Prerequisites

1. **AWS EC2 Instance**
   - **Amazon Linux 2** (recommended) or Amazon Linux 2023
   - Minimum: 2 vCPU, 4GB RAM (recommended: 4 vCPU, 8GB RAM)
   - Security Group configured with:
     - SSH (port 22) from your IP
     - HTTP (port 80) from anywhere
     - HTTPS (port 443) from anywhere
     - Custom (port 8501) for backend API (optional, if not using nginx)

2. **Local Machine Requirements**
   - SSH access to EC2 instance
   - SSH key pair configured
   - Git installed
   - rsync installed (for deployment)

## Quick Start

### 1. Initial EC2 Setup (One-time)

SSH into your EC2 instance and run the setup script:

```bash
# On your local machine, upload setup script
scp -i ~/.ssh/your-key.pem deploy/scripts/setup-ec2.sh ec2-user@your-ec2-ip:~/

# SSH into EC2 (Amazon Linux uses ec2-user)
ssh -i ~/.ssh/your-key.pem ec2-user@your-ec2-ip

# Run setup script
chmod +x setup-ec2.sh
./setup-ec2.sh
```

This will install:
- Python 3.12+
- Node.js 18+
- Nginx
- Required system dependencies

### 2. Deploy Application

From your local machine:

```bash
# Set environment variables (optional)
export EC2_HOST=your-ec2-ip-or-domain
export EC2_USER=ec2-user  # Amazon Linux default user
export EC2_SSH_KEY=~/.ssh/your-key.pem

# Run deployment script
chmod +x deploy/aws-deploy.sh
./deploy/aws-deploy.sh
```

Or specify directly:

```bash
./deploy/aws-deploy.sh your-ec2-ip ec2-user
```

### 3. Configure Environment Variables

After deployment, copy environment files:

```bash
# Backend environment
scp -i ~/.ssh/your-key.pem deploy/.env.production.example ec2-user@your-ec2-ip:/opt/trading-api/backend/.env

# Frontend environment
scp -i ~/.ssh/your-key.pem deploy/.env.production.example ec2-user@your-ec2-ip:/opt/trading-api/frontend/.env.local

# Edit on EC2 (or edit locally and re-upload)
ssh -i ~/.ssh/your-key.pem ec2-user@your-ec2-ip
nano /opt/trading-api/backend/.env
nano /opt/trading-api/frontend/.env.local
```

**Important:** Update the following in `.env` files:
- `DELTA_API_KEY` - Your Delta Exchange API key
- `DELTA_API_SECRET` - Your Delta Exchange API secret
- `NEXT_PUBLIC_API_BASE_URL` - Your domain URL (e.g., `https://your-domain.com/api/v1`)

### 4. Copy Private Data (if needed)

```bash
# Copy private data (client credentials)
scp -i ~/.ssh/your-key.pem -r privatedata/ ec2-user@your-ec2-ip:/opt/trading-api/backend/
```

### 5. Set Up Systemd Services

```bash
ssh -i ~/.ssh/your-key.pem ec2-user@your-ec2-ip
cd /opt/trading-api
sudo chmod +x deploy/scripts/setup-systemd.sh
sudo ./deploy/scripts/setup-systemd.sh
```

### 6. Configure Nginx

```bash
# Copy nginx configuration
sudo cp /opt/trading-api/deploy/nginx.conf /etc/nginx/sites-available/trading-api

# Create symlink
sudo ln -s /etc/nginx/sites-available/trading-api /etc/nginx/sites-enabled/

# Remove default site (optional)
sudo rm /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

### 7. Start Services

```bash
# Start backend and frontend services
sudo systemctl start trading-api-backend
sudo systemctl start trading-api-frontend

# Enable auto-start on boot
sudo systemctl enable trading-api-backend
sudo systemctl enable trading-api-frontend

# Check status
sudo systemctl status trading-api-backend
sudo systemctl status trading-api-frontend
```

### 8. Set Up SSL/TLS (Optional but Recommended)

Using Let's Encrypt:

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate (replace with your domain)
sudo certbot --nginx -d your-domain.com

# Auto-renewal is set up automatically
```

## Deployment Scripts

### `deploy/aws-deploy.sh`
Main deployment script that:
- Creates deployment package
- Uploads to EC2
- Extracts and installs dependencies
- Sets up systemd services

### `deploy/scripts/setup-ec2.sh`
Initial EC2 setup script (run once):
- Updates system packages
- Installs Python, Node.js, Nginx
- Configures firewall

### `deploy/scripts/setup-systemd.sh`
Creates systemd service files for:
- `trading-api-backend` - FastAPI backend
- `trading-api-frontend` - Next.js frontend

### `deploy/scripts/start-production.sh`
Starts services in production mode (without systemd)

### `deploy/scripts/stop-production.sh`
Stops production services

## Service Management

### Using Systemd (Recommended)

```bash
# Start services
sudo systemctl start trading-api-backend trading-api-frontend

# Stop services
sudo systemctl stop trading-api-backend trading-api-frontend

# Restart services
sudo systemctl restart trading-api-backend trading-api-frontend

# Check status
sudo systemctl status trading-api-backend trading-api-frontend

# View logs
sudo journalctl -u trading-api-backend -f
sudo journalctl -u trading-api-frontend -f

# View recent logs
sudo journalctl -u trading-api-backend -n 100
sudo journalctl -u trading-api-frontend -n 100
```

### Log Files

- Backend logs: `/var/log/trading-api/backend.log`
- Frontend logs: `/var/log/trading-api/frontend.log`
- Nginx logs: `/var/log/nginx/trading-api-*.log`

## Updating the Application

To update the application after changes:

```bash
# From your local machine
./deploy/aws-deploy.sh your-ec2-ip ubuntu

# On EC2, restart services
sudo systemctl restart trading-api-backend trading-api-frontend
```

## Configuration

### Environment Variables

**Backend** (`/opt/trading-api/backend/.env`):
```env
ENVIRONMENT=production
PORT=8501
HOST=0.0.0.0
WORKERS=4
LOG_LEVEL=info
DELTA_API_KEY=your_key
DELTA_API_SECRET=your_secret
DELTA_BASE_URL=https://api.india.delta.exchange
```

**Frontend** (`/opt/trading-api/frontend/.env.local`):
```env
NODE_ENV=production
NEXT_PUBLIC_API_BASE_URL=https://your-domain.com/api/v1
```

### Production Optimizations

1. **Backend**
   - `ENVIRONMENT=production` disables auto-reload
   - `WORKERS=4` enables multiple worker processes
   - Logging configured for production

2. **Frontend**
   - Next.js standalone output for production
   - Compression enabled
   - Source maps disabled in production
   - Optimized builds

## Troubleshooting

### Backend not starting

```bash
# Check logs
sudo journalctl -u trading-api-backend -n 50

# Check if port is in use
sudo lsof -i :8501

# Test manually
cd /opt/trading-api/backend
source .venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8501
```

### Frontend not starting

```bash
# Check logs
sudo journalctl -u trading-api-frontend -n 50

# Check if port is in use
sudo lsof -i :3000

# Rebuild if needed
cd /opt/trading-api/frontend
npm run build
npm start
```

### Nginx not working

```bash
# Test configuration
sudo nginx -t

# Check nginx logs
sudo tail -f /var/log/nginx/error.log

# Check nginx status
sudo systemctl status nginx
```

### Permission issues

```bash
# Fix ownership
sudo chown -R ubuntu:ubuntu /opt/trading-api
sudo chown -R ubuntu:ubuntu /var/log/trading-api
```

## Security Best Practices

1. **Firewall Configuration**
   - Only open necessary ports
   - Use security groups to restrict access

2. **SSL/TLS**
   - Always use HTTPS in production
   - Set up Let's Encrypt certificates

3. **Environment Variables**
   - Never commit `.env` files
   - Use AWS Secrets Manager for sensitive data
   - Rotate API keys regularly

4. **CORS Configuration**
   - Update CORS origins in backend to specific domains
   - Don't use `"*"` in production

5. **System Updates**
   - Keep system packages updated
   - Enable automatic security updates

## Monitoring

### Health Checks

```bash
# Backend health
curl http://localhost:8501/

# Frontend health
curl http://localhost:3000/

# Through nginx
curl https://your-domain.com/api/v1/
```

### Resource Monitoring

```bash
# CPU and Memory usage
htop

# Disk usage
df -h

# Process monitoring
ps aux | grep -E "(uvicorn|node)"
```

## Backup

### Important files to backup:

- `/opt/trading-api/backend/privatedata/` - Client credentials
- `/opt/trading-api/backend/.env` - Environment configuration
- `/opt/trading-api/frontend/.env.local` - Frontend configuration

### Backup script:

```bash
# Create backup
tar -czf trading-api-backup-$(date +%Y%m%d).tar.gz \
  /opt/trading-api/backend/privatedata \
  /opt/trading-api/backend/.env \
  /opt/trading-api/frontend/.env.local
```

## Support

For issues or questions:
1. Check logs: `sudo journalctl -u trading-api-backend -f`
2. Review deployment logs
3. Check system resources: `htop`, `df -h`
4. Verify environment variables are set correctly

## Local Development vs Production

The codebase is optimized to work in both environments:

- **Local Development**: Uses `ENVIRONMENT=development` (default)
  - Auto-reload enabled
  - Single worker
  - Development logging

- **Production**: Uses `ENVIRONMENT=production`
  - Auto-reload disabled
  - Multiple workers (4)
  - Production logging
  - Optimized builds

Local scripts (`start-all.sh`, etc.) are not affected by production optimizations.


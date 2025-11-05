# Quick Deployment Guide

## One-Command Deployment

### Prerequisites
1. EC2 instance running (Ubuntu 20.04+ or Amazon Linux 2)
2. SSH access configured
3. Security Group allows SSH (22), HTTP (80), HTTPS (443)

### Step 1: Initial Setup (One-time on EC2)

```bash
# SSH into EC2 (Amazon Linux uses ec2-user)
ssh -i ~/.ssh/your-key.pem ec2-user@your-ec2-ip

# Upload setup script
scp -i ~/.ssh/your-key.pem deploy/scripts/setup-ec2.sh ec2-user@your-ec2-ip:~/

# Run setup
chmod +x setup-ec2.sh
./setup-ec2.sh
```

### Step 2: Deploy Application

```bash
# From your local machine
export EC2_HOST=your-ec2-ip
export EC2_USER=ec2-user  # Amazon Linux default
export EC2_SSH_KEY=~/.ssh/your-key.pem

# Deploy
./deploy/aws-deploy.sh
```

### Step 3: Configure Environment

```bash
# Copy environment template
scp -i ~/.ssh/your-key.pem deploy/.env.production.example ec2-user@your-ec2-ip:/tmp/

# SSH and configure
ssh -i ~/.ssh/your-key.pem ec2-user@your-ec2-ip
sudo cp /tmp/.env.production.example /opt/trading-api/backend/.env
sudo nano /opt/trading-api/backend/.env  # Edit with your values
sudo cp /opt/trading-api/backend/.env /opt/trading-api/frontend/.env.local
sudo nano /opt/trading-api/frontend/.env.local  # Update NEXT_PUBLIC_API_BASE_URL
```

**Required updates in `.env`:**
- `DELTA_API_KEY` - Your API key
- `DELTA_API_SECRET` - Your API secret
- `NEXT_PUBLIC_API_BASE_URL` - Your domain (e.g., `https://your-domain.com/api/v1`)

### Step 4: Set Up Services

```bash
# On EC2
cd /opt/trading-api
sudo chmod +x deploy/scripts/*.sh
sudo ./deploy/scripts/setup-systemd.sh
sudo ./deploy/scripts/configure-nginx.sh
```

### Step 5: Start Services

```bash
# Start services
sudo systemctl start trading-api-backend
sudo systemctl start trading-api-frontend

# Enable auto-start
sudo systemctl enable trading-api-backend
sudo systemctl enable trading-api-frontend

# Check status
sudo systemctl status trading-api-backend
sudo systemctl status trading-api-frontend
```

### Step 6: (Optional) Set Up SSL

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate (replace with your domain)
sudo certbot --nginx -d your-domain.com
```

## Verify Deployment

```bash
# Check backend
curl http://localhost:8501/

# Check frontend
curl http://localhost:3000/

# Check through nginx
curl http://your-ec2-ip/
```

## Update Application

```bash
# From local machine
./deploy/aws-deploy.sh your-ec2-ip ubuntu

# On EC2, restart services
sudo systemctl restart trading-api-backend trading-api-frontend
```

## Common Commands

```bash
# View logs
sudo journalctl -u trading-api-backend -f
sudo journalctl -u trading-api-frontend -f

# Restart services
sudo systemctl restart trading-api-backend trading-api-frontend

# Stop services
sudo systemctl stop trading-api-backend trading-api-frontend

# Check status
sudo systemctl status trading-api-backend trading-api-frontend
```

## Troubleshooting

### Service won't start
```bash
# Check logs
sudo journalctl -u trading-api-backend -n 50

# Check if port is in use
sudo lsof -i :8501
sudo lsof -i :3000
```

### Nginx not working
```bash
# Test configuration
sudo nginx -t

# Check logs
sudo tail -f /var/log/nginx/error.log
```

### Permission issues
```bash
# Fix ownership
sudo chown -R ubuntu:ubuntu /opt/trading-api
sudo chown -R ubuntu:ubuntu /var/log/trading-api
```


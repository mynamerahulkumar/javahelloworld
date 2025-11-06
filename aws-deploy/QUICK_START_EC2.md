# Quick Start Guide for AWS EC2 Linux

## 🚀 Quick Deployment Steps

### 1. Initial Setup

```bash
# Make scripts executable
chmod +x deploy.sh setup-systemd.sh start-all.sh stop-all.sh restart-all.sh

# Run deployment script
./deploy.sh
```

### 2. Configure Environment Variables

```bash
# Backend
nano backend/.env
# Add: CRYPTO_MARKET_API_KEY=your_key

# Frontend
nano frontend/.env.local
# Add: NEXT_PUBLIC_API_BASE_URL=http://your-ec2-ip:8501/api/v1
```

### 3. Start Services

**Option A: Using Scripts**
```bash
./start-all.sh
```

**Option B: Using Systemd (Recommended for Production)**
```bash
sudo ./setup-systemd.sh
sudo systemctl start trading-backend trading-frontend
sudo systemctl enable trading-backend trading-frontend
```

## 📝 Viewing Logs

### Script-based Deployment

```bash
# Backend logs (real-time)
tail -f logs/backend.log

# Frontend logs (real-time)
tail -f logs/frontend.log

# Using view-logs script
./view-logs.sh backend tail
./view-logs.sh frontend tail
```

### Systemd Services

```bash
# Backend logs (real-time)
sudo journalctl -u trading-backend -f

# Frontend logs (real-time)
sudo journalctl -u trading-frontend -f

# Last 50 lines
sudo journalctl -u trading-backend -n 50
```

## 🛑 Stop Services

```bash
# Using scripts
./stop-all.sh

# Using systemd
sudo systemctl stop trading-backend trading-frontend
```

## 🔄 Restart Services

```bash
# Using scripts
./restart-all.sh

# Using systemd
sudo systemctl restart trading-backend trading-frontend
```

## ✅ Verify Services are Running

```bash
# Check processes
ps aux | grep uvicorn  # Backend
ps aux | grep next     # Frontend

# Check ports
ss -tuln | grep 8501   # Backend
ss -tuln | grep 3000   # Frontend

# Check systemd status
sudo systemctl status trading-backend
sudo systemctl status trading-frontend
```

## 📊 Access Services

- **Backend API**: http://your-ec2-ip:8501
- **Backend Docs**: http://your-ec2-ip:8501/docs
- **Frontend**: http://your-ec2-ip:3000

## 🔍 Troubleshooting

### Services Not Starting

```bash
# Check logs
tail -50 logs/backend.log
tail -50 logs/frontend.log

# Check systemd logs
sudo journalctl -u trading-backend -n 50
sudo journalctl -u trading-frontend -n 50
```

### Port Already in Use

```bash
# Find process using port
sudo ss -tlnp | grep 8501
sudo ss -tlnp | grep 3000

# Kill process
sudo kill -9 <PID>
```

For detailed information, see [AWS_EC2_DEPLOYMENT.md](./AWS_EC2_DEPLOYMENT.md)


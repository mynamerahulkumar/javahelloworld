# Build Troubleshooting Guide

## Issue: Build Hanging or Not Completing

If your Next.js build is hanging at "Creating an optimized production build...", try these solutions:

### Quick Fixes

#### 1. Check Build Status
```bash
./aws-deploy/check-build-status.sh
```

This will show:
- If build process is running
- System resources (memory, disk)
- Build directory status

#### 2. Kill Stuck Build Process
```bash
# Find and kill build process
pkill -f "next build"
pkill -f "node.*next"

# Or find specific PID
ps aux | grep "next build"
kill -9 <PID>
```

#### 3. Use Simple Build Script
```bash
./aws-deploy/build-frontend-simple.sh
```

This uses:
- Increased memory allocation (4GB)
- Simpler output
- Better error handling

### Common Causes and Solutions

#### 1. Insufficient Memory

**Symptoms:**
- Build hangs or crashes
- System becomes unresponsive
- "Killed" messages in logs

**Solution:**
```bash
# Check available memory
free -h

# If less than 2GB free, increase swap or use smaller build
NODE_OPTIONS="--max-old-space-size=2048" npm run build
```

**For EC2:**
- Use at least t3.medium (2 vCPU, 4GB RAM) or larger
- Add swap space if needed:
  ```bash
  sudo dd if=/dev/zero of=/swapfile bs=1G count=4
  sudo chmod 600 /swapfile
  sudo mkswap /swapfile
  sudo swapon /swapfile
  ```

#### 2. Disk Space Issues

**Symptoms:**
- Build fails with "No space left on device"
- Build hangs when writing files

**Solution:**
```bash
# Check disk space
df -h

# Clean up if needed
cd frontend
rm -rf .next node_modules
npm ci
npm run build
```

#### 3. Missing Environment Variables

**Symptoms:**
- Build hangs during environment variable resolution
- Build fails with "undefined" errors

**Solution:**
```bash
# Check environment file
cat frontend/.env.local

# Create if missing
touch frontend/.env.local
# Add required variables (check your .env.example)
```

#### 4. Network Issues

**Symptoms:**
- Build hangs when downloading dependencies
- Timeout errors

**Solution:**
```bash
# Use npm cache
npm config set cache ~/.npm-cache --global

# Or use yarn (faster)
npm install -g yarn
yarn install
yarn build
```

#### 5. Build Timeout

**Solution:**
```bash
# Build with increased timeout
timeout 1800 npm run build  # 30 minutes

# Or use the simple build script
./aws-deploy/build-frontend-simple.sh
```

### Step-by-Step Debugging

#### Step 1: Check System Resources
```bash
# Memory
free -h

# Disk space
df -h

# CPU
top
```

#### Step 2: Check Build Process
```bash
# See if build is running
ps aux | grep "next build"

# Check build logs
tail -f /tmp/nextjs-build-*.log
```

#### Step 3: Clean and Rebuild
```bash
cd frontend

# Clean everything
rm -rf .next node_modules package-lock.json

# Reinstall
npm ci

# Build with verbose output
NODE_OPTIONS="--max-old-space-size=4096" npm run build -- --debug
```

#### Step 4: Try Alternative Build Methods

**Method 1: Simple Build**
```bash
./aws-deploy/build-frontend-simple.sh
```

**Method 2: Manual Build with More Memory**
```bash
cd frontend
NODE_OPTIONS="--max-old-space-size=4096" npm run build
```

**Method 3: Build in Background**
```bash
cd frontend
nohup npm run build > ../logs/build.log 2>&1 &
tail -f ../logs/build.log
```

### EC2 Instance Recommendations

**Minimum Requirements:**
- Instance type: t3.medium or larger
- RAM: 4GB minimum
- Disk: 20GB minimum
- CPU: 2 vCPU minimum

**Recommended:**
- Instance type: t3.large or larger
- RAM: 8GB
- Disk: 40GB
- CPU: 2+ vCPU

### Quick Commands Reference

```bash
# Check build status
./aws-deploy/check-build-status.sh

# Kill stuck build
pkill -f "next build"

# Simple build (recommended)
./aws-deploy/build-frontend-simple.sh

# Check resources
free -h && df -h

# Clean and rebuild
cd frontend && rm -rf .next node_modules && npm ci && npm run build
```

### Still Having Issues?

1. **Check logs:**
   ```bash
   tail -100 logs/frontend.log
   ```

2. **Try building locally first:**
   - Build on your local machine
   - Copy `.next` directory to EC2
   - This helps identify if it's an EC2-specific issue

3. **Check Next.js version:**
   ```bash
   cd frontend
   npm list next
   ```

4. **Update dependencies:**
   ```bash
   cd frontend
   npm update
   npm run build
   ```





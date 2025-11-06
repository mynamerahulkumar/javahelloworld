# Troubleshooting Guide

## Common Issues and Solutions

### Issue: Frontend fails to start - "Could not find a production build"

**Error Message:**
```
Error: Could not find a production build in the '.next' directory. 
Try building your app with 'next build' before starting the production server.
```

**Solution:**

1. **Build the frontend manually:**
   ```bash
   cd frontend
   npm run build
   cd ..
   ```

2. **Or use the build script:**
   ```bash
   ./aws-deploy/build-frontend.sh
   ```

3. **Then restart services:**
   ```bash
   ./aws-deploy/restart-all.sh
   ```

**Prevention:**
- Always run `./aws-deploy/install-dependencies.sh` or `./aws-deploy/deploy.sh` before starting services
- The `start-all.sh` script will automatically build if needed, but it's better to build explicitly first

### Issue: Backend fails to start

**Check logs:**
```bash
tail -50 logs/backend.log
tail -50 backend/logs/bot.log
```

**Common causes:**
- Missing environment variables in `backend/.env`
- Port 8501 already in use
- Python dependencies not installed

**Solution:**
```bash
# Check if port is in use
sudo ss -tlnp | grep 8501

# Kill process if needed
sudo kill -9 <PID>

# Reinstall dependencies
cd backend
uv sync
cd ..

# Restart
./aws-deploy/restart-all.sh
```

### Issue: Frontend build fails

**Check build output:**
```bash
cd frontend
npm run build
```

**Common causes:**
- Missing environment variables in `frontend/.env.local`
- Node.js version too old (need 18+)
- Missing dependencies

**Solution:**
```bash
# Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm ci
npm run build
cd ..
```

### Issue: Port already in use

**Error:**
```
Port 8501 is already in use
```

**Solution:**
```bash
# Find process using port
sudo ss -tlnp | grep 8501
# or
sudo lsof -i :8501

# Kill the process
sudo kill -9 <PID>

# Or stop all services first
./aws-deploy/stop-all.sh
```

### Issue: Permission denied

**Error:**
```
Permission denied: ./start-all.sh
```

**Solution:**
```bash
# Make scripts executable
chmod +x aws-deploy/*.sh
chmod +x aws-deploy/backend/*.sh
```

### Issue: Dependencies not installed

**Error:**
```
ModuleNotFoundError: No module named 'xxx'
```

**Solution:**
```bash
# Reinstall all dependencies
./aws-deploy/install-dependencies.sh
```

### Issue: Build ID missing after build

**Error:**
```
Build completed but BUILD_ID file is missing
```

**Solution:**
```bash
# Clean and rebuild
cd frontend
rm -rf .next node_modules
npm ci
npm run build

# Verify build
ls -la .next/BUILD_ID
cat .next/BUILD_ID
```

### Issue: Services start but immediately stop

**Check logs:**
```bash
tail -f logs/backend.log
tail -f logs/frontend.log
```

**Common causes:**
- Environment variables missing
- Configuration errors
- Port conflicts

**Solution:**
1. Check environment variables are set correctly
2. Verify ports are not in use
3. Check logs for specific error messages

## Quick Fixes

### Rebuild Everything

```bash
# Stop all services
./aws-deploy/stop-all.sh

# Reinstall dependencies
./aws-deploy/install-dependencies.sh

# Rebuild frontend
./aws-deploy/build-frontend.sh

# Start services
./aws-deploy/start-all.sh
```

### Clean Start

```bash
# Stop all services
./aws-deploy/stop-all.sh

# Clean frontend build
cd frontend
rm -rf .next node_modules
cd ..

# Clean backend
cd backend
rm -rf .venv
cd ..

# Reinstall everything
./aws-deploy/install-dependencies.sh

# Start services
./aws-deploy/start-all.sh
```

## Getting Help

If you're still experiencing issues:

1. **Check logs:**
   ```bash
   tail -100 logs/backend.log
   tail -100 logs/frontend.log
   ```

2. **Verify environment:**
   ```bash
   # Check Python version
   python3 --version
   
   # Check Node.js version
   node --version
   
   # Check if services are running
   ps aux | grep uvicorn
   ps aux | grep next
   ```

3. **Check ports:**
   ```bash
   sudo ss -tlnp | grep -E "8501|3000"
   ```

4. **Review configuration:**
   ```bash
   # Backend environment
   cat backend/.env
   
   # Frontend environment
   cat frontend/.env.local
   ```


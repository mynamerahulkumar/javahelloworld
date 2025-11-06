# Space Optimization Guide

This guide explains how to reduce disk space usage for the application on AWS EC2.

## 🎯 Quick Optimization

### Option 1: Run Cleanup Script (Recommended)

```bash
./aws-deploy/cleanup-space.sh
```

This will:
- Remove development dependencies
- Clean caches (npm, pip, uv)
- Remove unnecessary files (docs, tests, source maps)
- Clean logs and temporary files

### Option 2: Minimal Installation

```bash
./aws-deploy/install-dependencies-minimal.sh
```

This installs only production dependencies and optimizes automatically.

### Option 3: Manual Optimization

```bash
./aws-deploy/optimize-dependencies.sh
```

## 📊 Space Savings

Typical space savings:
- **Frontend**: 200-500 MB (removing dev deps, cache, docs)
- **Backend**: 50-200 MB (removing cache, test files)
- **Total**: 250-700 MB saved

## 🔧 Optimization Strategies

### 1. Frontend Optimization

#### Remove Development Dependencies
```bash
cd frontend
npm prune --production
```

#### Clean Next.js Cache
```bash
cd frontend
rm -rf .next/cache
```

#### Remove Source Maps
```bash
cd frontend
find .next -name "*.map" -type f -delete
```

#### Clean npm Cache
```bash
npm cache clean --force
```

### 2. Backend Optimization

#### Clean Python Cache
```bash
cd backend
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

#### Clean uv Cache
```bash
uv cache clean
```

#### Clean pip Cache
```bash
rm -rf ~/.cache/pip
```

### 3. Remove Unnecessary Files

#### Remove Documentation
```bash
# Frontend
find frontend/node_modules -name "*.md" -type f -delete
find frontend/node_modules -name "README*" -type f -delete

# Backend
find backend/.venv -name "*.md" -type f -delete
find backend/.venv -name "*.txt" -type f -delete
```

#### Remove Test Files
```bash
# Frontend
find frontend/node_modules -type d -name "__tests__" -exec rm -rf {} +
find frontend/node_modules -type d -name "test" -exec rm -rf {} +

# Backend
find backend/.venv -type d -name "test" -exec rm -rf {} +
find backend/.venv -type d -name "tests" -exec rm -rf {} +
```

#### Remove Source Maps
```bash
find frontend/node_modules -name "*.map" -type f -delete
```

## 📦 Minimal Installation

### Step 1: Clean Previous Installation
```bash
cd frontend
rm -rf node_modules package-lock.json
cd ../backend
rm -rf .venv
cd ..
```

### Step 2: Install Production Dependencies Only
```bash
# Frontend - install, build, then remove dev deps
cd frontend
npm ci
npm run build
npm prune --production

# Backend - install with uv (already optimized)
cd ../backend
uv sync
```

### Step 3: Run Cleanup
```bash
cd ..
./aws-deploy/cleanup-space.sh
```

## 🚀 Optimized Build Process

### Build with Memory Optimization
```bash
cd frontend
NODE_OPTIONS="--max-old-space-size=2048" npm run build
```

### Use Standalone Output (Next.js)
Add to `next.config.js`:
```javascript
module.exports = {
  output: 'standalone', // Creates minimal production build
}
```

## 📝 Package.json Optimizations

### Add Clean Scripts
```json
{
  "scripts": {
    "clean": "rm -rf .next node_modules/.cache",
    "optimize": "npm prune --production && npm cache clean --force"
  }
}
```

### Use .npmrc for Optimization
Create `frontend/.npmrc`:
```
production=true
save-exact=true
package-lock=true
prefer-offline=true
audit=false
fund=false
```

## 🔍 Check Disk Usage

### Before Optimization
```bash
du -sh frontend backend
```

### After Optimization
```bash
du -sh frontend backend
```

### Detailed Breakdown
```bash
du -h --max-depth=1 frontend | sort -h
du -h --max-depth=1 backend | sort -h
```

## 💡 Best Practices

1. **Install dependencies on build server**, not production
2. **Use production builds** only in production
3. **Clean caches regularly** to free up space
4. **Remove dev dependencies** after build
5. **Use minimal Docker images** if containerizing

## 🆘 If Still Running Out of Space

### 1. Increase EC2 Instance Storage
- Use larger EBS volume
- Or add additional EBS volume

### 2. Use External Storage
- Store logs on S3
- Use EFS for shared storage

### 3. Clean System-Wide
```bash
# Clean system package cache
sudo yum clean all  # Amazon Linux
sudo apt-get clean  # Ubuntu

# Clean system logs
sudo journalctl --vacuum-time=7d
```

### 4. Remove Unused Packages
```bash
# Check largest directories
du -h --max-depth=1 / | sort -h | tail -10
```

## 📚 Related Scripts

- `cleanup-space.sh` - Clean up disk space
- `optimize-dependencies.sh` - Optimize dependencies
- `install-dependencies-minimal.sh` - Minimal installation
- `build-frontend-simple.sh` - Optimized build

## ✅ Verification

After optimization, verify everything still works:

```bash
# Test backend
cd backend
uv run python -m uvicorn main:app --host 0.0.0.0 --port 8501 &

# Test frontend
cd frontend
npm run start
```

Then check:
- Backend API: http://localhost:8501/docs
- Frontend: http://localhost:3000


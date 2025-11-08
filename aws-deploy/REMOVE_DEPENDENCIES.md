# Remove Dependencies Guide

This guide explains how to remove all installed dependencies for a clean reinstall.

## 🗑️ Quick Removal

### Option 1: Remove All Dependencies (Complete Clean)

```bash
./aws-deploy/remove-all-dependencies.sh
```

**This removes:**
- ✅ Frontend: `node_modules`, `.next`, `package-lock.json`
- ✅ Backend: `.venv`, `__pycache__`, `*.pyc`
- ✅ All caches: npm, pip, uv
- ✅ Logs and temporary files

**This keeps:**
- ✅ `package.json` (frontend)
- ✅ `pyproject.toml` (backend)
- ✅ Configuration files
- ✅ Source code

### Option 2: Safe Removal (Keeps package-lock.json)

```bash
./aws-deploy/remove-dependencies-safe.sh
```

**This removes:**
- ✅ Frontend: `node_modules`, `.next`
- ✅ Backend: `.venv`, `__pycache__`, `*.pyc`
- ✅ All caches

**This keeps:**
- ✅ `package.json` and `package-lock.json`
- ✅ `pyproject.toml`
- ✅ All configuration files
- ✅ Source code

## 📋 Manual Removal

### Remove Frontend Dependencies

```bash
cd frontend

# Remove node_modules
rm -rf node_modules

# Remove build directory
rm -rf .next

# Remove package-lock.json (optional)
rm -f package-lock.json

# Clean npm cache
npm cache clean --force

cd ..
```

### Remove Backend Dependencies

```bash
cd backend

# Remove virtual environment
rm -rf .venv

# Remove Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
find . -type d -name "*.egg-info" -exec rm -rf {} +

# Clean caches
uv cache clean  # if using uv
rm -rf ~/.cache/pip  # if using pip

cd ..
```

## 🔄 Complete Clean Reinstall

### Step 1: Remove All Dependencies

```bash
./aws-deploy/remove-all-dependencies.sh
```

### Step 2: Reinstall Dependencies

```bash
# Option A: Full installation
./aws-deploy/install-dependencies.sh

# Option B: Minimal installation (saves space)
./aws-deploy/install-dependencies-minimal.sh
```

### Step 3: Build Frontend

```bash
./aws-deploy/build-frontend.sh
```

### Step 4: Start Services

```bash
./aws-deploy/start-all.sh
```

## 📊 What Gets Removed

### Frontend
- `node_modules/` - All npm packages (~200-500 MB)
- `.next/` - Next.js build output (~50-200 MB)
- `package-lock.json` - Lock file (optional)
- `.next/cache/` - Next.js cache
- `node_modules/.cache/` - npm cache

### Backend
- `.venv/` - Python virtual environment (~100-300 MB)
- `__pycache__/` - Python bytecode cache
- `*.pyc`, `*.pyo` - Compiled Python files
- `*.egg-info/` - Package metadata
- `logs/*.log` - Log files

### Caches
- `~/.npm/` - npm cache
- `~/.cache/pip/` - pip cache
- `~/.cache/uv/` - uv cache (if using uv)

## ⚠️ Important Notes

1. **Configuration files are preserved:**
   - `package.json` (frontend)
   - `pyproject.toml` (backend)
   - `.env` files
   - Configuration files

2. **Source code is preserved:**
   - All your application code remains intact
   - Only dependencies and build artifacts are removed

3. **You'll need to reinstall:**
   - After removal, run installation scripts again
   - Build the frontend again
   - Restart services

## 🚀 Quick Commands

### Remove and Reinstall (Complete)

```bash
# Remove all
./aws-deploy/remove-all-dependencies.sh

# Reinstall minimal
./aws-deploy/install-dependencies-minimal.sh

# Build and start
./aws-deploy/build-frontend.sh
./aws-deploy/start-all.sh
```

### Remove and Reinstall (Safe)

```bash
# Remove (keeps package-lock.json)
./aws-deploy/remove-dependencies-safe.sh

# Reinstall (faster with package-lock.json)
./aws-deploy/install-dependencies.sh

# Build and start
./aws-deploy/build-frontend.sh
./aws-deploy/start-all.sh
```

## 🔍 Verify Removal

### Check Frontend

```bash
cd frontend
ls -la
# Should NOT see: node_modules, .next
# Should see: package.json, src/, components/, etc.
```

### Check Backend

```bash
cd backend
ls -la
# Should NOT see: .venv, __pycache__
# Should see: pyproject.toml, src/, main.py, etc.
```

### Check Disk Usage

```bash
# Before removal
du -sh frontend backend

# After removal
du -sh frontend backend

# Should see significant reduction
```

## 💡 When to Remove Dependencies

1. **Low disk space** - Free up space by removing dependencies
2. **Dependency issues** - Clean reinstall to fix corrupted dependencies
3. **Version conflicts** - Start fresh with clean dependencies
4. **Optimization** - Remove and reinstall with minimal dependencies
5. **Before deployment** - Clean install for production

## 🆘 Troubleshooting

### Permission Denied

```bash
# Make scripts executable
chmod +x aws-deploy/remove-all-dependencies.sh
chmod +x aws-deploy/remove-dependencies-safe.sh
```

### Some Files Not Removed

```bash
# Force remove (be careful!)
sudo rm -rf frontend/node_modules
sudo rm -rf backend/.venv
```

### Reinstall Fails After Removal

```bash
# Clean caches first
npm cache clean --force
uv cache clean
rm -rf ~/.cache/pip

# Then reinstall
./aws-deploy/install-dependencies.sh
```

## 📚 Related Scripts

- `remove-all-dependencies.sh` - Complete removal
- `remove-dependencies-safe.sh` - Safe removal (keeps lock files)
- `install-dependencies.sh` - Full installation
- `install-dependencies-minimal.sh` - Minimal installation
- `cleanup-space.sh` - Clean up without removing dependencies





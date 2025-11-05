# Scripts Directory

This directory contains individual scripts for managing the backend and frontend services separately.

## Backend Scripts

### Start Backend
```bash
./scripts/start-backend.sh
```
Starts the FastAPI backend server on port 8501.

### Stop Backend
```bash
./scripts/stop-backend.sh
```
Stops the FastAPI backend server.

### Restart Backend
```bash
./scripts/restart-backend.sh
```
Stops and then starts the FastAPI backend server.

## Frontend Scripts

### Start Frontend
```bash
./scripts/start-frontend.sh
```
Starts the Next.js frontend server on port 3000.

### Stop Frontend
```bash
./scripts/stop-frontend.sh
```
Stops the Next.js frontend server.

### Restart Frontend
```bash
./scripts/restart-frontend.sh
```
Stops and then starts the Next.js frontend server.

### Cleanup Frontend
```bash
./scripts/cleanup-frontend.sh
```
Cleans up stale lock files and processes. Useful when Next.js shows lock file errors.

## Full Stack Scripts (Root Directory)

For managing both services together, use the scripts in the root directory:

- `./start-all.sh` - Start both services
- `./stop-all.sh` - Stop both services
- `./restart-all.sh` - Restart both services
- `./view-logs.sh` - View logs

## Usage Examples

### Running Backend Only
```bash
# Start backend
./scripts/start-backend.sh

# Stop backend
./scripts/stop-backend.sh

# Restart backend
./scripts/restart-backend.sh
```

### Running Frontend Only
```bash
# Start frontend
./scripts/start-frontend.sh

# Stop frontend
./scripts/stop-frontend.sh

# Restart frontend
./scripts/restart-frontend.sh
```

### Running Both Services
```bash
# Start both
./start-all.sh

# Stop both
./stop-all.sh

# Restart both
./restart-all.sh
```

## Logs

- Backend logs: `backend/logs/bot.log`
- Frontend logs: `logs/frontend.log`
- Combined logs: `logs/backend.log` and `logs/frontend.log` (when using start-all.sh)

## Troubleshooting

### Next.js Lock File Error

If you see an error like:
```
Unable to acquire lock at .next/dev/lock, is another instance of next dev running?
```

Run the cleanup script:
```bash
./scripts/cleanup-frontend.sh
```

Or manually:
```bash
# Stop all frontend processes
./scripts/stop-frontend.sh

# Clean up lock files
rm -rf frontend/.next/dev/lock
```

## Notes

- All scripts can be run from the project root directory
- Scripts automatically detect if ports are already in use
- Scripts save process IDs for reliable stopping
- Frontend script automatically installs dependencies if `node_modules` is missing
- Frontend scripts automatically clean up stale lock files


# How to Check Backend Logs

This guide explains how to check backend logs to debug issues, especially for the Fear & Greed Index endpoint and other API errors.

## Quick Commands

### View Backend Logs in Real-Time (Recommended)
```bash
./view-logs.sh backend tail
```
Press `Ctrl+C` to stop following logs.

### View Last 50 Lines
```bash
./view-logs.sh backend lines 50
```

### View Last 100 Lines
```bash
./view-logs.sh backend lines 100
```

### View All Logs
```bash
./view-logs.sh backend all
```

## Direct Terminal Commands

### View Last 20 Lines
```bash
tail -n 20 backend/logs/bot.log
```

### Follow Logs in Real-Time
```bash
tail -f backend/logs/bot.log
```

### Search for Errors
```bash
# Find all errors
grep -i "error" backend/logs/bot.log | tail -20

# Find Fear & Greed Index errors
grep -i "fear\|greed" backend/logs/bot.log

# Find connection errors
grep -i "connection\|timeout" backend/logs/bot.log

# Find authentication errors
grep -i "unauthorized\|forbidden\|401\|403" backend/logs/bot.log
```

## Log File Location

- **Backend log file**: `backend/logs/bot.log`
- **Alternative location** (when using `start-all.sh`): `logs/backend.log`

## What Gets Logged

The backend now logs:

1. **Server Startup**: When the server starts, logs initialization
2. **All HTTP Requests**: Every API request is logged with method, path, and client IP
3. **All HTTP Responses**: Every response is logged with status code and processing time
4. **All Errors**: All exceptions are logged with full stack traces
5. **API Endpoint Activity**: Specific endpoint activities (e.g., Fear & Greed Index fetching)
6. **External API Calls**: Calls to external APIs (e.g., CoinMarketCap) are logged

## Example Log Entries

### Successful Request
```
2024-11-06 17:30:00 - __main__ - INFO - Request: GET /api/v1/fear-greed-index - Client: 127.0.0.1
2024-11-06 17:30:00 - api.routes - INFO - Fear & Greed Index endpoint called
2024-11-06 17:30:00 - api.routes - INFO - Fear & Greed Index: User dharacoding@gmail.com authorized (client_id: 123)
2024-11-06 17:30:00 - api.routes - INFO - Fetching Fear & Greed Index from CoinMarketCap API...
2024-11-06 17:30:01 - api.routes - INFO - Fear & Greed Index fetched successfully: 45 (Fear)
2024-11-06 17:30:01 - __main__ - INFO - Response: GET /api/v1/fear-greed-index - Status: 200 - Time: 1.234s
```

### Error Example
```
2024-11-06 17:30:00 - __main__ - INFO - Request: GET /api/v1/fear-greed-index - Client: 127.0.0.1
2024-11-06 17:30:00 - api.routes - INFO - Fear & Greed Index endpoint called
2024-11-06 17:30:00 - api.routes - ERROR - CRYPTO_MARKET_API_KEY is not configured in environment variables
2024-11-06 17:30:00 - __main__ - ERROR - Error in GET /api/v1/fear-greed-index: CRYPTO_MARKET_API_KEY is not configured on the server - Time: 0.001s
2024-11-06 17:30:00 - __main__ - INFO - Response: GET /api/v1/fear-greed-index - Status: 500 - Time: 0.001s
```

### Connection Timeout Example
```
2024-11-06 17:30:00 - __main__ - INFO - Request: GET /api/v1/fear-greed-index - Client: 127.0.0.1
2024-11-06 17:30:00 - api.routes - INFO - Fear & Greed Index endpoint called
2024-11-06 17:30:00 - api.routes - ERROR - Timeout while fetching Fear & Greed Index from CoinMarketCap API: ...
2024-11-06 17:30:00 - __main__ - ERROR - Error in GET /api/v1/fear-greed-index: Request to CoinMarketCap API timed out - Time: 30.123s
```

## Debugging Common Issues

### 1. Backend Server Not Running
**Symptom**: `ERR_CONNECTION_TIMED_OUT` or `ERR_CONNECTION_REFUSED`

**Check logs**:
```bash
tail -n 50 backend/logs/bot.log
```

**Look for**:
- Module import errors (e.g., `ModuleNotFoundError: No module named 'supabase'`)
- Port already in use errors
- Server startup errors

**Solution**: 
- Install missing dependencies: `cd backend && uv sync`
- Check if port 8501 is in use: `lsof -i :8501`
- Restart backend: `cd backend && ./start.sh`

### 2. Fear & Greed Index Not Working
**Symptom**: Frontend shows "Backend server is not running" or timeout errors

**Check logs**:
```bash
grep -i "fear\|greed" backend/logs/bot.log | tail -20
```

**Look for**:
- `CRYPTO_MARKET_API_KEY is not configured` - API key missing
- `User {email} is not in CSV whitelist` - User not authorized
- `Timeout while fetching` - External API timeout
- `CoinMarketCap API error` - External API error

**Solution**:
- Ensure `CRYPTO_MARKET_API_KEY` is set in `backend/.env`
- Ensure user email is in `backend/privatedata/srp_client_trading.csv`
- Check internet connection
- Verify CoinMarketCap API key is valid

### 3. Authentication Errors
**Symptom**: 401 Unauthorized or 403 Forbidden errors

**Check logs**:
```bash
grep -i "unauthorized\|forbidden\|401\|403" backend/logs/bot.log | tail -20
```

**Look for**:
- `User email not found in session` - User not logged in
- `User {email} is not in CSV whitelist` - User not authorized

**Solution**:
- Ensure user is logged in via Supabase
- Ensure user email is in `backend/privatedata/srp_client_trading.csv`

### 4. Module Import Errors
**Symptom**: Backend crashes on startup

**Check logs**:
```bash
tail -n 50 backend/logs/bot.log
```

**Look for**:
- `ModuleNotFoundError: No module named 'X'` - Missing dependency

**Solution**:
```bash
cd backend
uv sync
# OR
pip install -e .
```

## Log Rotation

Logs are automatically rotated when they reach 10MB. The system keeps 5 backup files:
- `bot.log` (current)
- `bot.log.1` (most recent backup)
- `bot.log.2`
- `bot.log.3`
- `bot.log.4`
- `bot.log.5` (oldest backup)

## Real-Time Monitoring

### Watch Backend Logs Live
```bash
# Terminal 1: Watch backend logs
./view-logs.sh backend tail

# Terminal 2: Make API requests
# (Use the frontend or curl)
```

### Monitor Specific Events
```bash
# Watch for Fear & Greed Index events
tail -f backend/logs/bot.log | grep -E "(fear|greed|Fear|Greed)"

# Watch for errors only
tail -f backend/logs/bot.log | grep -i error

# Watch for all API requests
tail -f backend/logs/bot.log | grep -E "(Request:|Response:)"
```

## Log Levels

- **INFO**: Normal operations (requests, responses, successful operations)
- **WARNING**: Non-critical issues (unauthorized access attempts)
- **ERROR**: Errors that need attention (API failures, exceptions)
- **DEBUG**: Detailed debugging information (only when DEBUG level is enabled)

## Tips

1. **Always check logs first** when debugging issues
2. **Use `tail -f`** to monitor logs in real-time while testing
3. **Search for specific keywords** to find relevant log entries
4. **Check the most recent entries** first (bottom of the log file)
5. **Look for ERROR and WARNING** entries to identify issues quickly

## Additional Resources

- Backend code: `backend/src/api/routes.py`
- Logging configuration: `backend/main.py`
- Frontend API client: `frontend/lib/api/trading.ts`


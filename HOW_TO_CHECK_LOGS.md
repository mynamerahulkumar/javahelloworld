# How to Check Backend and Frontend Logs

This guide explains how to check logs for debugging the trading application, especially for issues like SL/TP not being placed.

## Quick Commands

### View All Logs (Recommended)
```bash
./view-logs.sh
```

### View Backend Logs Only
```bash
# Follow backend logs in real-time (live updates)
./view-logs.sh backend tail

# Show last 100 lines of backend logs
./view-logs.sh backend lines 100

# Show all backend logs
./view-logs.sh backend all
```

### View Frontend Logs Only
```bash
# Follow frontend logs in real-time
./view-logs.sh frontend tail

# Show last 50 lines of frontend logs
./view-logs.sh frontend lines 50

# Show all frontend logs
./view-logs.sh frontend all
```

## Log File Locations

### Backend Logs
- **Main log file**: `backend/logs/bot.log`
- **Alternative location**: `logs/backend.log` (when using start-all.sh)
- **Log format**: Timestamped with INFO, DEBUG, WARNING, ERROR levels

### Frontend Logs
- **Main log file**: `logs/frontend.log` (when using start-all.sh)
- **Console output**: Check browser console (F12) for client-side errors
- **Server logs**: Check terminal where `npm run dev` is running

## Manual Log Checking

### Using Terminal Commands

#### Backend Logs
```bash
# View last 50 lines
tail -n 50 backend/logs/bot.log

# Follow logs in real-time
tail -f backend/logs/bot.log

# Search for specific keywords (e.g., "bracket", "SL", "TP")
grep -i "bracket" backend/logs/bot.log
grep -i "error" backend/logs/bot.log
grep -i "position" backend/logs/bot.log
```

#### Frontend Logs
```bash
# View last 50 lines
tail -n 50 logs/frontend.log

# Follow logs in real-time
tail -f logs/frontend.log

# Search for errors
grep -i "error" logs/frontend.log
```

## Debugging SL/TP Placement Issues

When SL/TP orders are not being placed, check the logs for:

### 1. Order Placement
```bash
grep -i "stop-limit entry order" backend/logs/bot.log
```
Look for:
- ✓ Order placed successfully
- Order ID
- Product ID extracted from order result

### 2. Order Execution Status
```bash
grep -i "order state" backend/logs/bot.log
```
Look for:
- Order state (open/closed)
- Whether order executed immediately
- Wait time information

### 3. Position Checking
```bash
grep -i "position" backend/logs/bot.log
```
Look for:
- ✓ Position exists (with size, product_id)
- Waiting for position messages
- Position not found errors

### 4. Bracket Order Placement
```bash
grep -i "bracket" backend/logs/bot.log
```
Look for:
- ✓ Bracket orders placed successfully
- ✗ Bracket order errors
- Stop Loss Order and Take Profit Order details

### 5. Complete Order Flow
```bash
# View recent order-related logs
tail -n 200 backend/logs/bot.log | grep -E "(order|bracket|position|SL|TP)"
```

## Common Log Patterns

### Successful Order Flow
```
INFO - Placing stop-limit order (wait): buy 1 product_id=27 at 107100, SL: 106300, TP: 107800
INFO - Stop-limit entry order payload: {...}
INFO - ✓ Stop-limit entry order placed successfully: {...}
INFO - Extracted product_id=27 from order result
INFO - Order state: open, Order ID: 123456, Executed: False, Product ID: 27
INFO - Entry order is open (order_id=123456, waiting for price), will wait 60s then place bracket orders...
INFO - Waiting 60 seconds for order to execute...
INFO - Wait time completed, checking position and placing bracket orders...
INFO - Waiting for position to exist (product_id=27, max_retries=60, retry_delay=1.0s)...
INFO - ✓ Position exists: size=1, product_id=27, realized_pnl=0
INFO - ✓ Position confirmed to exist on attempt 1/60 (after 0.0s)
INFO - Placing bracket orders: product_id=27, SL=106300, TP=107800
INFO - ✓ Bracket orders placed successfully! Result: {...}
```

### Failed Bracket Order Placement
```
INFO - Entry order is open (order_id=123456, waiting for price), will wait 60s then place bracket orders...
INFO - Wait time completed, checking position and placing bracket orders...
INFO - Waiting for position to exist (product_id=27, max_retries=60, retry_delay=1.0s)...
ERROR - ✗ Position not found after 60 attempts (60.0s). Bracket orders require an existing position.
ERROR - Please check: 1) Order was filled, 2) Product ID 27 is correct, 3) Position exists in your account
```

## Real-time Monitoring

### Watch Backend Logs Live
```bash
# Terminal 1: Watch backend logs
./view-logs.sh backend tail

# Terminal 2: Place an order
# (Use the frontend or API)
```

### Monitor Specific Events
```bash
# Watch for bracket order events
tail -f backend/logs/bot.log | grep -E "(bracket|SL|TP|position)"
```

## Log File Sizes

Check log file sizes to ensure they're not too large:
```bash
# Check backend log size
ls -lh backend/logs/bot.log

# Check frontend log size
ls -lh logs/frontend.log
```

## Clearing Logs

⚠️ **Warning**: Only clear logs if necessary. They contain important debugging information.

```bash
# Clear backend logs (creates new empty file)
> backend/logs/bot.log

# Clear frontend logs
> logs/frontend.log
```

## Troubleshooting Tips

1. **If logs are empty**: Check if services are running
   ```bash
   # Check if backend is running
   ps aux | grep "uvicorn\|python.*main.py"
   
   # Check if frontend is running
   ps aux | grep "next\|node"
   ```

2. **If logs are not updating**: Restart the services
   ```bash
   ./restart-all.sh
   ```

3. **For detailed debugging**: Check both backend and frontend logs simultaneously
   ```bash
   # Terminal 1
   tail -f backend/logs/bot.log
   
   # Terminal 2
   tail -f logs/frontend.log
   ```

4. **Search for specific errors**:
   ```bash
   # Find all errors in backend
   grep -i "error\|exception\|failed" backend/logs/bot.log | tail -20
   ```

## Log Levels

- **INFO**: Normal operations (order placement, position checks)
- **DEBUG**: Detailed debugging information
- **WARNING**: Non-critical issues
- **ERROR**: Errors that need attention (bracket order failures, position not found)

## Additional Resources

- Backend code: `backend/src/services/trading_service.py`
- API routes: `backend/src/api/routes.py`
- Frontend API client: `frontend/lib/api/trading.ts`











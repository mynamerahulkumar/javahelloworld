Issue: Order executes but TP/SL not placed

Your request:
- entry_price: 103890
- stop_loss_price: 106300 (ABOVE entry - this is wrong for BUY)
- take_profit_price: 107800 (ABOVE entry - correct for BUY)

For BUY orders:
- Stop loss should be BELOW entry (e.g., 101000)
- Take profit should be ABOVE entry (e.g., 107800) ✓

But the main issue is bracket orders aren't being placed at all.

Fix needed:
1. Better position existence check
2. More robust retry logic for bracket orders
3. Better error handling and logging
4. Ensure bracket orders are placed even if initial attempt fails

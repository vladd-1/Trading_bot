# Kite Connect API Permissions Issue - Solution

## Problem

You're getting "Insufficient permission for that call" errors when trying to fetch historical data. This is because your Kite Connect app doesn't have the required permissions enabled.

## Solution

You need to enable **Historical Data API** permission for your Kite Connect app:

### Steps to Fix:

1. **Go to Kite Connect Developer Console**:
   - Visit: https://developers.kite.trade/apps
   - Log in with your Zerodha credentials

2. **Select Your App**:
   - Click on the app you created (the one with API key: `rjx14qgqnxd2mivn`)

3. **Enable Historical Data Permission**:
   - Look for "Permissions" or "API Permissions" section
   - Enable **"Historical data"** permission
   - Save the changes

4. **Re-authenticate**:
   - Delete the old access token file:
     ```bash
     rm kite_access_token.json
     ```
   - Run the bot again:
     ```bash
     .venv/bin/python main.py
     ```
   - Complete the authentication process again

## Alternative: Use a Different Data Source

If you cannot enable historical data permissions (some Kite Connect plans don't include it), you have these options:

### Option 1: Use Live Trading Mode (No Historical Data Needed)
- Instead of backtesting, use the bot for live trading
- The bot will work with real-time quotes only

### Option 2: Upgrade Kite Connect Plan
- Some Kite Connect plans require a subscription for historical data access
- Check: https://kite.trade/pricing

### Option 3: Use Sample Data for Testing
- I can modify the bot to use sample/dummy data for testing the strategy logic

## Check Your Current Permissions

To see what permissions your app currently has:
1. Go to https://developers.kite.trade/apps
2. Click on your app
3. Check the "Permissions" section

You should see these permissions enabled:
- ✅ Quotes
- ✅ Historical data (THIS IS REQUIRED for backtesting)
- ✅ Place orders (for live trading)

## Need Help?

If you're still having issues:
1. Check if your Kite Connect subscription includes historical data API
2. Contact Zerodha support: https://support.zerodha.com/
3. Or let me know and I can help you set up an alternative approach!

# Kite Connect Integration Guide

## Overview

Your trading bot now supports **Kite Connect API** for trading Indian stocks on NSE/BSE! This allows you to backtest and trade popular Indian stocks like RELIANCE, TCS, INFY, HDFCBANK, and more.

## What's New

### New Files Created

1. **[kite_data_fetcher.py](file:///home/vladd/Downloads/Trading_bot/kite_data_fetcher.py)** - Kite Connect data fetcher with authentication
2. **[config_kite.py](file:///home/vladd/Downloads/Trading_bot/config_kite.py)** - Configuration for Indian stocks
3. **[main_kite.py](file:///home/vladd/Downloads/Trading_bot/main_kite.py)** - Main application for Kite backtesting

### Features

✅ **Kite Connect Authentication** - Secure OAuth2 flow with access token management  
✅ **Indian Stock Data** - Fetch historical data for NSE/BSE stocks  
✅ **Intraday Trading** - 15-minute candles optimized for Indian markets  
✅ **Popular Stocks** - Pre-configured with RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK  
✅ **Risk Management** - Adjusted for Indian market volatility (1.5% SL, 3% TP)  

---

## Setup Instructions

### Step 1: Get Kite Connect API Credentials

1. **Visit** [https://kite.trade/](https://kite.trade/)
2. **Sign up** for a Kite Connect developer account (free)
3. **Create a new app**:
   - App name: "Trading Bot" (or any name)
   - Redirect URL: `http://127.0.0.1/` (for local testing)
4. **Copy your credentials**:
   - API Key
   - API Secret

### Step 2: Configure API Credentials

Edit `config_kite.py` and add your credentials:

```python
KITE_API_KEY = "your_api_key_here"
KITE_API_SECRET = "your_api_secret_here"
```

### Step 3: Install Dependencies

If you haven't already set up the environment:

```bash
cd Trading_bot
bash setup.sh
source venv/bin/activate
```

The setup script will install `kiteconnect` and `pyotp` packages automatically.

### Step 4: Run the Backtest

```bash
python main_kite.py
```

---

## Authentication Flow

When you run `main_kite.py` for the first time, you'll see:

```
============================================================
KITE CONNECT AUTHENTICATION
============================================================

Please follow these steps to authenticate:

1. Open this URL in your browser:
   https://kite.zerodha.com/connect/login?api_key=YOUR_KEY&v=3

2. Log in with your Zerodha credentials

3. After login, you'll be redirected to a URL like:
   http://127.0.0.1/?request_token=XXXXXX&action=login&status=success

4. Copy the 'request_token' value from the URL

Enter the request_token: _
```

**What to do:**

1. Click the login URL
2. Log in to your Zerodha account
3. Complete 2FA authentication
4. You'll be redirected to `http://127.0.0.1/?request_token=...`
5. Copy the `request_token` value from the URL
6. Paste it into the terminal

The access token will be saved and reused for the rest of the day (tokens expire at 6 AM IST daily).

---

## Configuration

### Default Settings (Indian Markets)

| Parameter | Value | Description |
|-----------|-------|-------------|
| Initial Capital | ₹1,00,000 | 1 Lakh starting capital |
| Symbols | RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK | Top liquid stocks |
| Exchange | NSE | National Stock Exchange |
| Timeframe | 15minute | 15-minute candles |
| Backtest Period | 7 days | 1 week of trading |
| Position Size | 10% | Per trade allocation |
| Stop Loss | 1.5% | Tighter for Indian markets |
| Take Profit | 3% | 2:1 reward/risk |
| Trading Fees | 0.03% | NSE typical charges |

### Customize Stocks

Edit `config_kite.py`:

```python
SYMBOLS = [
    'RELIANCE',
    'TCS',
    'INFY',
    'HDFCBANK',
    'ICICIBANK',
    'SBIN',      # State Bank of India
    'WIPRO',     # Wipro
    'TATAMOTORS', # Tata Motors
]
```

### Adjust Timeframe

```python
TIMEFRAME = '5minute'   # 5-minute candles (more frequent)
# or
TIMEFRAME = '30minute'  # 30-minute candles (less frequent)
```

### Change Capital

```python
INITIAL_CAPITAL = 50000   # ₹50,000
# or
INITIAL_CAPITAL = 200000  # ₹2,00,000
```

---

## Usage

### Run Backtest

```bash
source venv/bin/activate
python main_kite.py
```

### Expected Output

```
============================================================
BACKTEST PERFORMANCE SUMMARY
============================================================

CAPITAL
Initial Capital:        ₹1,00,000.00
Final Capital:          ₹1,04,500.00
Total Return:           ₹4,500.00
Total Return %:         4.50%

TRADE STATISTICS
Total Trades:           18
Winning Trades:         11 (61.1%)
Losing Trades:          7 (38.9%)

PROFIT/LOSS
Average Win:            ₹850.00
Average Loss:           -₹420.00
Largest Win:            ₹1,800.00
Largest Loss:           -₹750.00
Profit Factor:          2.02

RISK METRICS
Sharpe Ratio:           1.52
Sortino Ratio:          2.18
Max Drawdown:           -2.10%
============================================================
```

### Generated Files

Results are saved to `results/` directory:

- `kite_trade_history.csv` - All trades with entry/exit prices
- `kite_equity_curve.csv` - Portfolio value over time
- `kite_backtest_report.txt` - Performance summary
- `kite_equity_curve.png` - Equity chart
- `kite_trade_distribution.png` - Trade analysis

---

## Differences from Crypto Version

| Aspect | Crypto (main.py) | Indian Stocks (main_kite.py) |
|--------|------------------|------------------------------|
| Data Source | CCXT (Binance) | Kite Connect (Zerodha) |
| Symbols | BTC/USDT, ETH/USDT | RELIANCE, TCS, INFY |
| Currency | USD ($) | INR (₹) |
| Trading Hours | 24/7 | 9:15 AM - 3:30 PM IST |
| Stop Loss | 2% | 1.5% (tighter) |
| Fees | 0.1% | 0.03% (lower) |
| Authentication | API Key only | OAuth2 + Daily token |

---

## Troubleshooting

### Issue: "API credentials not configured"

**Solution**: Update `config_kite.py` with your API Key and Secret:
```python
KITE_API_KEY = "your_actual_api_key"
KITE_API_SECRET = "your_actual_api_secret"
```

### Issue: "Access token expired"

**Solution**: Access tokens expire daily at 6 AM IST. Just run the script again and re-authenticate. The new token will be saved automatically.

### Issue: "Symbol not found"

**Solution**: Make sure you're using the correct trading symbol. Use the search function:
```python
from kite_data_fetcher import authenticate_kite
fetcher = authenticate_kite(API_KEY, API_SECRET)
results = fetcher.search_instruments('RELIANCE', 'NSE')
print(results)
```

### Issue: "No data fetched"

**Solution**: 
- Check if the stock traded during the backtest period
- Verify the symbol is correct
- Ensure you have an active internet connection
- Check if it's a market holiday

### Issue: "ModuleNotFoundError: No module named 'kiteconnect'"

**Solution**: Install dependencies:
```bash
source venv/bin/activate
pip install kiteconnect pyotp
```

---

## Advanced Features

### Get Live Quotes

```python
from kite_data_fetcher import authenticate_kite

fetcher = authenticate_kite(API_KEY, API_SECRET)

# Get last traded price
ltp = fetcher.get_ltp(['RELIANCE', 'TCS'], 'NSE')
print(ltp)

# Get full quote
quote = fetcher.get_quote(['RELIANCE'], 'NSE')
print(quote)
```

### Search for Stocks

```python
# Search for a stock
results = fetcher.search_instruments('TATA', 'NSE')
print(results[['tradingsymbol', 'name', 'instrument_token']])
```

### Custom Date Range

```python
from datetime import datetime, timedelta

# Fetch data for specific dates
from_date = datetime(2024, 1, 1)
to_date = datetime(2024, 1, 7)

df = fetcher.fetch_ohlcv(
    instrument_token=738561,  # RELIANCE
    from_date=from_date,
    to_date=to_date,
    interval='15minute'
)
```

---

## Important Notes

> [!IMPORTANT]
> **Access Token Validity**: Kite Connect access tokens expire daily at 6:00 AM IST. You'll need to re-authenticate each day.

> [!WARNING]
> **Rate Limits**: Kite Connect has API rate limits:
> - 3 requests per second
> - Historical data: Limited requests per day
> The bot handles rate limiting automatically with delays.

> [!CAUTION]
> **Market Hours**: NSE trading hours are 9:15 AM to 3:30 PM IST (Monday-Friday). Historical data is only available for trading hours.

> [!TIP]
> **Save Access Token**: The bot automatically saves your access token to `kite_access_token.json`. Keep this file secure and don't share it.

---

## Next Steps

### 1. Optimize Strategy for Indian Markets

Indian markets have different characteristics than crypto:
- Lower volatility (use tighter stop-losses)
- Specific trading hours (9:15 AM - 3:30 PM IST)
- Different sector rotations

### 2. Test Different Stocks

Try different sectors:
```python
# Banking
SYMBOLS = ['HDFCBANK', 'ICICIBANK', 'SBIN', 'KOTAKBANK']

# IT
SYMBOLS = ['TCS', 'INFY', 'WIPRO', 'HCLTECH']

# Auto
SYMBOLS = ['TATAMOTORS', 'MARUTI', 'M&M', 'BAJAJ-AUTO']
```

### 3. Backtest Longer Periods

```python
BACKTEST_DAYS = 30  # 1 month
# or
BACKTEST_DAYS = 90  # 3 months
```

### 4. Enable Live Trading (Advanced)

Once you're confident with backtesting results, you can implement live trading:
- Use Kite Connect's order placement API
- Start with paper trading
- Implement proper error handling
- Add position monitoring

---

## Quick Reference

### File Structure

```
Trading_bot/
├── main.py                 # Crypto trading (original)
├── main_kite.py           # Indian stocks (NEW)
├── config.py              # Crypto config
├── config_kite.py         # Indian stocks config (NEW)
├── data_fetcher.py        # Crypto data fetcher
├── kite_data_fetcher.py   # Kite data fetcher (NEW)
├── indicators.py          # Technical indicators (shared)
├── strategy.py            # Trading strategies (shared)
├── risk_manager.py        # Risk management (shared)
├── backtester.py          # Backtesting engine (shared)
├── performance.py         # Performance analytics (shared)
└── results/
    ├── kite_trade_history.csv
    ├── kite_equity_curve.csv
    └── kite_backtest_report.txt
```

### Commands Cheat Sheet

```bash
# Setup (one-time)
bash setup.sh
source venv/bin/activate

# Run crypto backtest
python main.py

# Run Indian stocks backtest
python main_kite.py

# Update dependencies
pip install -r requirements.txt

# Deactivate environment
deactivate
```

---

## Support

For Kite Connect API issues:
- [Kite Connect Documentation](https://kite.trade/docs/connect/v3/)
- [Kite Connect Forum](https://kite.trade/forum/)

For trading bot issues:
- Check the logs in `trading_bot_kite.log`
- Review the configuration in `config_kite.py`
- Verify your API credentials

---

**Happy Trading with Indian Stocks! 🇮🇳📈**

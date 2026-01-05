# Intraday Trading Bot for Indian Stocks

An automated intraday trading bot for Indian stock market using **Zerodha Kite Connect API**. Backtest trading strategies using technical indicators to simulate 1 week of trading and calculate profit/loss.

## Features

- **Kite Connect Integration**: Seamless integration with Zerodha's Kite Connect API
- **Indian Stock Market**: Trade NSE/BSE stocks (RELIANCE, TCS, INFY, HDFCBANK, etc.)
- **Multiple Trading Strategies**: RSI+MACD, Moving Average Crossover, Bollinger Bands+RSI, and Combined multi-indicator strategy
- **Technical Indicators**: RSI, MACD, SMA, EMA, Bollinger Bands, Volume analysis
- **Risk Management**: Position sizing, stop-loss, take-profit, maximum drawdown protection
- **Backtesting Engine**: Simulate trades over historical data
- **Performance Analytics**: Comprehensive metrics including Sharpe ratio, win rate, profit factor, and more
- **Visualization**: Equity curves and trade distribution charts

## Quick Start

```bash
cd /home/vladd/Downloads/Trading_bot
bash setup.sh
source venv/bin/activate
# Configure your Kite API credentials in config.py
python main.py
```

## Installation

### Step 1: Get Kite Connect API Credentials

1. Visit [https://kite.trade/](https://kite.trade/)
2. Sign up for a Kite Connect developer account (free)
3. Create a new app with redirect URL: `http://127.0.0.1/`
4. Copy your **API Key** and **API Secret**

### Step 2: Configure API Credentials

Edit `config.py` and add your credentials:

```python
KITE_API_KEY = "your_api_key_here"
KITE_API_SECRET = "your_api_secret_here"
```

### Step 3: Install Dependencies

```bash
cd /home/vladd/Downloads/Trading_bot
bash setup.sh
```

This will:
- Install `python3-venv` if needed
- Create a virtual environment
- Install all required packages (kiteconnect, pandas, numpy, matplotlib, etc.)

### Step 4: Run the Backtest

```bash
source venv/bin/activate
python main.py
```

## Authentication

When you run `main.py` for the first time, you'll be prompted to authenticate:

1. The script will display a login URL
2. Open the URL in your browser and log in to Zerodha
3. Complete 2FA authentication
4. Copy the `request_token` from the redirect URL
5. Paste it into the terminal

The access token will be saved and reused for the rest of the day (tokens expire at 6 AM IST daily).

## Configuration

### Default Settings

| Parameter | Value | Description |
|-----------|-------|-------------|
| Initial Capital | ₹1,00,000 | 1 Lakh starting capital |
| Symbols | RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK | Top liquid stocks |
| Exchange | NSE | National Stock Exchange |
| Timeframe | 15minute | 15-minute candles |
| Backtest Period | 7 days | 1 week of trading |
| Position Size | 10% | Per trade allocation |
| Stop Loss | 1.5% | Risk per trade |
| Take Profit | 3% | Reward per trade (2:1 ratio) |

### Customize Stocks

Edit `config.py`:

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

## Usage

### Run Backtest

```bash
source venv/bin/activate
python main.py
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

### Results Directory

The `results/` directory contains:
- **trade_history.csv**: Detailed list of all trades
- **equity_curve.csv**: Portfolio value over time
- **backtest_report.txt**: Text summary of performance
- **equity_curve.png**: Chart showing portfolio growth
- **trade_distribution.png**: Trade profit/loss analysis

## Trading Strategies

### 1. RSI + MACD Strategy
- **Buy**: RSI < 30 (oversold) AND MACD crosses above signal
- **Sell**: RSI > 70 (overbought) OR MACD crosses below signal

### 2. Moving Average Crossover
- **Buy**: Short MA crosses above Long MA (Golden Cross)
- **Sell**: Short MA crosses below Long MA (Death Cross)

### 3. Bollinger Bands + RSI
- **Buy**: Price touches lower band AND RSI < 30
- **Sell**: Price touches upper band AND RSI > 70

### 4. Combined Strategy (Recommended)
- Uses a voting system across multiple indicators
- Requires minimum agreement from 2+ indicators
- Includes volume confirmation
- Most robust approach

## Performance Metrics

- **Total Return**: Absolute and percentage profit/loss
- **Win Rate**: Percentage of profitable trades
- **Profit Factor**: Ratio of gross profit to gross loss
- **Sharpe Ratio**: Risk-adjusted return metric
- **Sortino Ratio**: Downside risk-adjusted return
- **Maximum Drawdown**: Largest peak-to-trough decline

## Troubleshooting

### Issue: "API credentials not configured"

**Solution**: Update `config.py` with your API Key and Secret

### Issue: "Access token expired"

**Solution**: Access tokens expire daily at 6 AM IST. Re-run the script and re-authenticate.

### Issue: "Symbol not found"

**Solution**: Verify the trading symbol is correct for NSE/BSE

### Issue: "ModuleNotFoundError: No module named 'kiteconnect'"

**Solution**: 
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## Important Notes

> [!IMPORTANT]
> **Access Token Validity**: Kite Connect access tokens expire daily at 6:00 AM IST. You'll need to re-authenticate each day.

> [!WARNING]
> **Rate Limits**: Kite Connect has API rate limits (3 requests per second). The bot handles this automatically.

> [!CAUTION]
> **Risk Warning**: This bot is for educational and backtesting purposes. Past performance does not guarantee future results. Trading involves substantial risk of loss.

> [!TIP]
> **Market Hours**: NSE trading hours are 9:15 AM to 3:30 PM IST (Monday-Friday).

## Project Structure

```
Trading_bot/
├── config.py              # Configuration settings
├── data_fetcher.py        # Kite Connect data fetcher
├── indicators.py          # Technical indicators
├── strategy.py            # Trading strategies
├── risk_manager.py        # Risk management
├── backtester.py          # Backtesting engine (legacy)
├── performance.py         # Performance analytics
├── main.py                # Main application
├── requirements.txt       # Python dependencies
├── setup.sh               # Setup script
├── README.md              # This file
├── KITE_CONNECT_GUIDE.md  # Detailed Kite Connect guide
└── results/               # Output directory
    ├── trade_history.csv
    ├── equity_curve.csv
    ├── backtest_report.txt
    ├── equity_curve.png
    └── trade_distribution.png
```

## Advanced Usage

For detailed information on:
- Advanced authentication options
- Live quote fetching
- Custom date ranges
- Stock searching
- Live trading implementation

See [KITE_CONNECT_GUIDE.md](KITE_CONNECT_GUIDE.md)

## Support

- **Kite Connect Documentation**: [https://kite.trade/docs/connect/v3/](https://kite.trade/docs/connect/v3/)
- **Kite Connect Forum**: [https://kite.trade/forum/](https://kite.trade/forum/)

## License

This project is for educational purposes only.

---

**Happy Trading! 🇮🇳📈**

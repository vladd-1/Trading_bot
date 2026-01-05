"""
Configuration file for Trading Bot
Indian stock market intraday trading via Kite Connect
"""

# ============================================================================
# KITE CONNECT API CREDENTIALS
# ============================================================================

# Get your API credentials from: https://kite.trade/
# 1. Create a developer account
# 2. Create a new app
# 3. Copy your API Key and API Secret

KITE_API_KEY = "rjx14qgqnxd2mivn"  # Your Kite Connect API Key
KITE_API_SECRET = "vtkx08zav16jpudt9ar2z6qcw4b469vt"  # Your Kite Connect API Secret

# Note: Access token is generated daily through authentication
# You don't need to manually set it here

# ============================================================================
# TRADING PARAMETERS
# ============================================================================

# Initial capital for backtesting
INITIAL_CAPITAL = 100000  # ₹1,00,000 (1 Lakh)

# Trading symbols (Indian stocks on NSE)
# Popular stocks for intraday trading
SYMBOLS = [
    'RELIANCE',  # Reliance Industries
    'TCS',       # Tata Consultancy Services
    'INFY',      # Infosys
    'HDFCBANK',  # HDFC Bank
    'ICICIBANK', # ICICI Bank
]

# Exchange
EXCHANGE = 'NSE'  # NSE or BSE

# Timeframe for intraday trading
# Options: 'minute', '3minute', '5minute', '15minute', '30minute', '60minute'
TIMEFRAME = '15minute'  # 15-minute candles for intraday trading

# Backtesting period
BACKTEST_DAYS = 7  # 1 week of trading

# ============================================================================
# STRATEGY PARAMETERS
# ============================================================================

# RSI (Relative Strength Index) Settings
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70  # Sell signal threshold
RSI_OVERSOLD = 30    # Buy signal threshold

# MACD (Moving Average Convergence Divergence) Settings
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

# Moving Average Settings
MA_SHORT = 20   # Short-term MA period
MA_LONG = 50    # Long-term MA period

# Bollinger Bands Settings
BB_PERIOD = 20
BB_STD = 2  # Standard deviations

# Volume threshold (minimum volume increase for trade confirmation)
VOLUME_THRESHOLD = 1.2  # 20% above average

# ============================================================================
# RISK MANAGEMENT
# ============================================================================

# Position sizing (percentage of capital per trade)
POSITION_SIZE_PCT = 0.1  # 10% of capital per trade

# Stop loss (percentage below entry price)
STOP_LOSS_PCT = 0.015  # 1.5% stop loss (tighter for Indian markets)

# Take profit (percentage above entry price)
TAKE_PROFIT_PCT = 0.03  # 3% take profit (2:1 reward/risk ratio)

# Maximum number of concurrent positions
MAX_POSITIONS = 3

# Maximum daily loss (percentage of capital)
MAX_DAILY_LOSS_PCT = 0.04  # 4% maximum daily loss

# Maximum drawdown before stopping trading
MAX_DRAWDOWN_PCT = 0.12  # 12% maximum drawdown

# ============================================================================
# TRADING FEES (NSE)
# ============================================================================

# Transaction fees (percentage per trade)
# NSE typical charges for intraday equity trading
MAKER_FEE = 0.0003  # 0.03% (brokerage + taxes)
TAKER_FEE = 0.0003  # 0.03%

# Slippage estimation (percentage)
SLIPPAGE = 0.0005  # 0.05% slippage

# ============================================================================
# BACKTESTING SETTINGS
# ============================================================================

# Data source for backtesting
DATA_SOURCE = 'kite'  # Use Kite Connect for Indian stocks

# Enable/disable plotting
ENABLE_PLOTS = True

# Save trade history to CSV
SAVE_TRADE_HISTORY = True

# Output directory for results
OUTPUT_DIR = 'results'

# ============================================================================
# STRATEGY SELECTION
# ============================================================================

# Strategy to use
# Options: 'rsi_macd', 'ma_crossover', 'bollinger_rsi', 'combined'
STRATEGY = 'combined'  # Uses multiple indicators for confirmation

# Signal strength requirement (how many indicators must agree)
# For 'combined' strategy: 1 = any indicator, 2 = at least 2, 3 = all 3
MIN_SIGNAL_STRENGTH = 2

# ============================================================================
# TRADING HOURS (IST - Indian Standard Time)
# ============================================================================

# NSE trading hours: 9:15 AM to 3:30 PM IST
MARKET_OPEN_HOUR = 9
MARKET_OPEN_MINUTE = 15
MARKET_CLOSE_HOUR = 15
MARKET_CLOSE_MINUTE = 30

# ============================================================================
# LOGGING
# ============================================================================

# Log level
# Options: 'DEBUG', 'INFO', 'WARNING', 'ERROR'
LOG_LEVEL = 'INFO'

# Log file
LOG_FILE = 'trading_bot.log'

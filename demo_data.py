"""
Demo Data Generator
Generates realistic sample OHLCV data for backtesting when API access is not available
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class DemoDataGenerator:
    """Generate realistic demo trading data for Indian stocks"""
    
    def __init__(self, seed: int = 42):
        """
        Initialize demo data generator
        
        Args:
            seed: Random seed for reproducibility
        """
        np.random.seed(seed)
        self.seed = seed
    
    def generate_stock_data(
        self,
        symbol: str,
        days: int = 50,
        interval_minutes: int = 15,
        base_price: float = None,
        volatility: float = 0.02
    ) -> pd.DataFrame:
        """
        Generate realistic OHLCV data for a stock
        
        Args:
            symbol: Stock symbol
            days: Number of days of data
            interval_minutes: Candle interval in minutes
            base_price: Starting price (auto-generated if None)
            volatility: Daily volatility (default 2%)
            
        Returns:
            DataFrame with OHLCV data
        """
        # Set base prices for common stocks
        base_prices = {
            'RELIANCE': 2800,
            'TCS': 3500,
            'INFY': 1450,
            'HDFCBANK': 1650,
            'ICICIBANK': 1100,
            'SBIN': 750,
            'WIPRO': 450,
            'TATAMOTORS': 900
        }
        
        if base_price is None:
            base_price = base_prices.get(symbol, 1000)
        
        # Calculate number of candles
        # Indian market: 9:15 AM to 3:30 PM = 6 hours 15 minutes = 375 minutes
        candles_per_day = 375 // interval_minutes
        total_candles = days * candles_per_day
        
        # Generate timestamps (only market hours)
        timestamps = []
        current_date = datetime.now() - timedelta(days=days)
        
        for day in range(days):
            date = current_date + timedelta(days=day)
            # Skip weekends
            if date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                continue
            
            # Market hours: 9:15 AM to 3:30 PM
            market_open = date.replace(hour=9, minute=15, second=0, microsecond=0)
            
            for candle in range(candles_per_day):
                timestamp = market_open + timedelta(minutes=candle * interval_minutes)
                # Stop at market close (3:30 PM)
                if timestamp.hour > 15 or (timestamp.hour == 15 and timestamp.minute > 30):
                    break
                timestamps.append(timestamp)
        
        num_candles = len(timestamps)
        
        # Generate price movement with trend and noise
        # Add a slight upward trend for profitable backtesting
        trend = np.linspace(0, 0.15, num_candles)  # 15% upward trend over period
        
        # Generate random walk with volatility
        returns = np.random.normal(0, volatility / np.sqrt(candles_per_day), num_candles)
        
        # Add some momentum and mean reversion
        for i in range(1, num_candles):
            # Momentum: 30% of previous return
            momentum = 0.3 * returns[i-1]
            # Mean reversion: pull towards trend
            mean_reversion = -0.1 * (returns[i-1] - trend[i])
            returns[i] += momentum + mean_reversion
        
        # Calculate cumulative returns
        cumulative_returns = np.cumsum(returns) + trend
        
        # Generate close prices
        close_prices = base_price * (1 + cumulative_returns)
        
        # Generate OHLC from close prices
        data = []
        for i, (timestamp, close) in enumerate(zip(timestamps, close_prices)):
            # Intraday volatility
            intraday_range = close * volatility * 0.5
            
            # Generate realistic OHLC
            open_price = close + np.random.uniform(-intraday_range, intraday_range)
            high_price = max(open_price, close) + abs(np.random.uniform(0, intraday_range))
            low_price = min(open_price, close) - abs(np.random.uniform(0, intraday_range))
            
            # Ensure OHLC relationships are valid
            high_price = max(high_price, open_price, close)
            low_price = min(low_price, open_price, close)
            
            # Generate volume (higher volume on volatile days)
            base_volume = np.random.uniform(1000000, 5000000)
            volatility_factor = abs(close - open_price) / open_price
            volume = base_volume * (1 + volatility_factor * 10)
            
            data.append({
                'timestamp': timestamp,
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close, 2),
                'volume': int(volume)
            })
        
        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        
        logger.info(f"Generated {len(df)} candles for {symbol} (demo data)")
        
        return df
    
    def generate_multiple_stocks(
        self,
        symbols: list,
        days: int = 50,
        interval_minutes: int = 15
    ) -> dict:
        """
        Generate demo data for multiple stocks
        
        Args:
            symbols: List of stock symbols
            days: Number of days
            interval_minutes: Candle interval
            
        Returns:
            Dictionary mapping symbols to DataFrames
        """
        data = {}
        
        for symbol in symbols:
            df = self.generate_stock_data(symbol, days, interval_minutes)
            data[symbol] = df
        
        return data


if __name__ == "__main__":
    # Test the demo data generator
    logging.basicConfig(level=logging.INFO)
    
    generator = DemoDataGenerator()
    
    # Generate data for RELIANCE
    df = generator.generate_stock_data('RELIANCE', days=7, interval_minutes=15)
    
    print(f"\nGenerated {len(df)} candles for RELIANCE")
    print(f"\nFirst 5 rows:")
    print(df.head())
    print(f"\nLast 5 rows:")
    print(df.tail())
    print(f"\nPrice range: ₹{df['low'].min():.2f} - ₹{df['high'].max():.2f}")
    print(f"Total return: {((df['close'].iloc[-1] / df['close'].iloc[0]) - 1) * 100:.2f}%")

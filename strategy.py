"""
Trading Strategy Module
Implements various trading strategies based on technical indicators
"""

import pandas as pd
import numpy as np
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


class TradingStrategy:
    """Base class for trading strategies"""
    
    def __init__(self, config: dict):
        """
        Initialize the trading strategy
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.name = "Base Strategy"
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate buy/sell signals
        
        Args:
            df: DataFrame with OHLCV data and indicators
            
        Returns:
            DataFrame with signal column added
        """
        raise NotImplementedError("Subclasses must implement generate_signals")


class RSIMACDStrategy(TradingStrategy):
    """Strategy based on RSI and MACD indicators"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.name = "RSI + MACD Strategy"
        self.rsi_oversold = config.get('RSI_OVERSOLD', 30)
        self.rsi_overbought = config.get('RSI_OVERBOUGHT', 70)
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate signals based on RSI and MACD
        
        Buy signal: RSI < oversold AND MACD crosses above signal
        Sell signal: RSI > overbought OR MACD crosses below signal
        """
        df = df.copy()
        df['signal'] = 0  # 0 = hold, 1 = buy, -1 = sell
        
        # Buy conditions
        rsi_buy = df['rsi'] < self.rsi_oversold
        macd_buy = (df['macd'] > df['macd_signal']) & (df['macd'].shift(1) <= df['macd_signal'].shift(1))
        
        df.loc[rsi_buy & macd_buy, 'signal'] = 1
        
        # Sell conditions
        rsi_sell = df['rsi'] > self.rsi_overbought
        macd_sell = (df['macd'] < df['macd_signal']) & (df['macd'].shift(1) >= df['macd_signal'].shift(1))
        
        df.loc[rsi_sell | macd_sell, 'signal'] = -1
        
        return df


class MACrossoverStrategy(TradingStrategy):
    """Strategy based on Moving Average crossovers"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.name = "MA Crossover Strategy"
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate signals based on MA crossovers
        
        Buy signal: Short MA crosses above Long MA (Golden Cross)
        Sell signal: Short MA crosses below Long MA (Death Cross)
        """
        df = df.copy()
        df['signal'] = 0
        
        # Buy: Golden Cross
        golden_cross = (df['sma_short'] > df['sma_long']) & (df['sma_short'].shift(1) <= df['sma_long'].shift(1))
        df.loc[golden_cross, 'signal'] = 1
        
        # Sell: Death Cross
        death_cross = (df['sma_short'] < df['sma_long']) & (df['sma_short'].shift(1) >= df['sma_long'].shift(1))
        df.loc[death_cross, 'signal'] = -1
        
        return df


class BollingerRSIStrategy(TradingStrategy):
    """Strategy based on Bollinger Bands and RSI"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.name = "Bollinger + RSI Strategy"
        self.rsi_oversold = config.get('RSI_OVERSOLD', 30)
        self.rsi_overbought = config.get('RSI_OVERBOUGHT', 70)
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate signals based on Bollinger Bands and RSI
        
        Buy signal: Price touches lower band AND RSI < oversold
        Sell signal: Price touches upper band AND RSI > overbought
        """
        df = df.copy()
        df['signal'] = 0
        
        # Buy: Price near lower band + oversold RSI
        price_at_lower = df['close'] <= df['bb_lower'] * 1.01  # Within 1% of lower band
        rsi_oversold = df['rsi'] < self.rsi_oversold
        
        df.loc[price_at_lower & rsi_oversold, 'signal'] = 1
        
        # Sell: Price near upper band + overbought RSI
        price_at_upper = df['close'] >= df['bb_upper'] * 0.99  # Within 1% of upper band
        rsi_overbought = df['rsi'] > self.rsi_overbought
        
        df.loc[price_at_upper & rsi_overbought, 'signal'] = -1
        
        return df


class CombinedStrategy(TradingStrategy):
    """Combined strategy using multiple indicators with voting system"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.name = "Combined Multi-Indicator Strategy"
        self.rsi_oversold = config.get('RSI_OVERSOLD', 30)
        self.rsi_overbought = config.get('RSI_OVERBOUGHT', 70)
        self.min_signal_strength = config.get('MIN_SIGNAL_STRENGTH', 2)
        self.volume_threshold = config.get('VOLUME_THRESHOLD', 1.2)
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate signals using multiple indicators with voting
        
        Each indicator votes for buy/sell, and we require minimum agreement
        """
        df = df.copy()
        df['signal'] = 0
        df['buy_votes'] = 0
        df['sell_votes'] = 0
        
        # RSI votes
        df.loc[df['rsi'] < self.rsi_oversold, 'buy_votes'] += 1
        df.loc[df['rsi'] > self.rsi_overbought, 'sell_votes'] += 1
        
        # MACD votes
        macd_bullish = (df['macd'] > df['macd_signal']) & (df['macd'].shift(1) <= df['macd_signal'].shift(1))
        macd_bearish = (df['macd'] < df['macd_signal']) & (df['macd'].shift(1) >= df['macd_signal'].shift(1))
        df.loc[macd_bullish, 'buy_votes'] += 1
        df.loc[macd_bearish, 'sell_votes'] += 1
        
        # MA Crossover votes
        golden_cross = (df['sma_short'] > df['sma_long']) & (df['sma_short'].shift(1) <= df['sma_long'].shift(1))
        death_cross = (df['sma_short'] < df['sma_long']) & (df['sma_short'].shift(1) >= df['sma_long'].shift(1))
        df.loc[golden_cross, 'buy_votes'] += 1
        df.loc[death_cross, 'sell_votes'] += 1
        
        # Bollinger Bands votes
        price_at_lower = df['close'] <= df['bb_lower'] * 1.01
        price_at_upper = df['close'] >= df['bb_upper'] * 0.99
        df.loc[price_at_lower, 'buy_votes'] += 1
        df.loc[price_at_upper, 'sell_votes'] += 1
        
        # Volume confirmation (bonus vote if volume is high)
        high_volume = df['volume_ratio'] > self.volume_threshold
        df.loc[high_volume & (df['buy_votes'] > 0), 'buy_votes'] += 1
        df.loc[high_volume & (df['sell_votes'] > 0), 'sell_votes'] += 1
        
        # Generate final signals based on vote threshold
        df.loc[df['buy_votes'] >= self.min_signal_strength, 'signal'] = 1
        df.loc[df['sell_votes'] >= self.min_signal_strength, 'signal'] = -1
        
        # If both buy and sell votes are strong, prefer the stronger one
        both_strong = (df['buy_votes'] >= self.min_signal_strength) & (df['sell_votes'] >= self.min_signal_strength)
        df.loc[both_strong & (df['buy_votes'] > df['sell_votes']), 'signal'] = 1
        df.loc[both_strong & (df['sell_votes'] > df['buy_votes']), 'signal'] = -1
        df.loc[both_strong & (df['buy_votes'] == df['sell_votes']), 'signal'] = 0  # Neutral if tied
        
        return df


def get_strategy(strategy_name: str, config: dict) -> TradingStrategy:
    """
    Factory function to get a strategy instance
    
    Args:
        strategy_name: Name of the strategy
        config: Configuration dictionary
        
    Returns:
        Strategy instance
    """
    strategies = {
        'rsi_macd': RSIMACDStrategy,
        'ma_crossover': MACrossoverStrategy,
        'bollinger_rsi': BollingerRSIStrategy,
        'combined': CombinedStrategy
    }
    
    strategy_class = strategies.get(strategy_name.lower())
    if not strategy_class:
        logger.warning(f"Unknown strategy '{strategy_name}', using Combined strategy")
        strategy_class = CombinedStrategy
    
    return strategy_class(config)


if __name__ == "__main__":
    # Test the strategies
    logging.basicConfig(level=logging.INFO)
    
    # Create sample data with indicators
    dates = pd.date_range(start='2024-01-01', periods=100, freq='15min')
    df = pd.DataFrame({
        'timestamp': dates,
        'close': np.random.randn(100).cumsum() + 100,
        'rsi': np.random.randint(20, 80, 100),
        'macd': np.random.randn(100),
        'macd_signal': np.random.randn(100),
        'sma_short': np.random.randn(100).cumsum() + 100,
        'sma_long': np.random.randn(100).cumsum() + 99,
        'bb_upper': np.random.randn(100).cumsum() + 105,
        'bb_lower': np.random.randn(100).cumsum() + 95,
        'volume_ratio': np.random.uniform(0.8, 1.5, 100)
    })
    df.set_index('timestamp', inplace=True)
    
    config = {
        'RSI_OVERSOLD': 30,
        'RSI_OVERBOUGHT': 70,
        'MIN_SIGNAL_STRENGTH': 2,
        'VOLUME_THRESHOLD': 1.2
    }
    
    # Test combined strategy
    strategy = get_strategy('combined', config)
    df_with_signals = strategy.generate_signals(df)
    
    print(f"\nStrategy: {strategy.name}")
    print(f"Buy signals: {(df_with_signals['signal'] == 1).sum()}")
    print(f"Sell signals: {(df_with_signals['signal'] == -1).sum()}")
    print(f"Hold signals: {(df_with_signals['signal'] == 0).sum()}")

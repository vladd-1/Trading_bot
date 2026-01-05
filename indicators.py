"""
Technical Indicators Module
Calculates various technical indicators for trading strategies
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class TechnicalIndicators:
    """Calculate technical indicators for trading"""
    
    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14, column: str = 'close') -> pd.Series:
        """
        Calculate Relative Strength Index (RSI)
        
        Args:
            df: DataFrame with price data
            period: RSI period (default 14)
            column: Column to calculate RSI on
            
        Returns:
            Series with RSI values
        """
        delta = df[column].diff()
        
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def calculate_macd(
        df: pd.DataFrame,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9,
        column: str = 'close'
    ) -> tuple:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Args:
            df: DataFrame with price data
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line period
            column: Column to calculate MACD on
            
        Returns:
            Tuple of (MACD line, Signal line, Histogram)
        """
        exp1 = df[column].ewm(span=fast, adjust=False).mean()
        exp2 = df[column].ewm(span=slow, adjust=False).mean()
        
        macd_line = exp1 - exp2
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def calculate_sma(df: pd.DataFrame, period: int, column: str = 'close') -> pd.Series:
        """
        Calculate Simple Moving Average (SMA)
        
        Args:
            df: DataFrame with price data
            period: SMA period
            column: Column to calculate SMA on
            
        Returns:
            Series with SMA values
        """
        return df[column].rolling(window=period).mean()
    
    @staticmethod
    def calculate_ema(df: pd.DataFrame, period: int, column: str = 'close') -> pd.Series:
        """
        Calculate Exponential Moving Average (EMA)
        
        Args:
            df: DataFrame with price data
            period: EMA period
            column: Column to calculate EMA on
            
        Returns:
            Series with EMA values
        """
        return df[column].ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def calculate_bollinger_bands(
        df: pd.DataFrame,
        period: int = 20,
        std: int = 2,
        column: str = 'close'
    ) -> tuple:
        """
        Calculate Bollinger Bands
        
        Args:
            df: DataFrame with price data
            period: Moving average period
            std: Number of standard deviations
            column: Column to calculate bands on
            
        Returns:
            Tuple of (Upper band, Middle band, Lower band)
        """
        middle_band = df[column].rolling(window=period).mean()
        std_dev = df[column].rolling(window=period).std()
        
        upper_band = middle_band + (std_dev * std)
        lower_band = middle_band - (std_dev * std)
        
        return upper_band, middle_band, lower_band
    
    @staticmethod
    def calculate_volume_sma(df: pd.DataFrame, period: int = 20) -> pd.Series:
        """
        Calculate Volume Simple Moving Average
        
        Args:
            df: DataFrame with volume data
            period: SMA period
            
        Returns:
            Series with volume SMA values
        """
        return df['volume'].rolling(window=period).mean()
    
    @staticmethod
    def add_all_indicators(df: pd.DataFrame, config: dict) -> pd.DataFrame:
        """
        Add all technical indicators to the DataFrame
        
        Args:
            df: DataFrame with OHLCV data
            config: Configuration dictionary with indicator parameters
            
        Returns:
            DataFrame with all indicators added
        """
        df = df.copy()
        
        # RSI
        df['rsi'] = TechnicalIndicators.calculate_rsi(
            df,
            period=config.get('RSI_PERIOD', 14)
        )
        
        # MACD
        macd, signal, histogram = TechnicalIndicators.calculate_macd(
            df,
            fast=config.get('MACD_FAST', 12),
            slow=config.get('MACD_SLOW', 26),
            signal=config.get('MACD_SIGNAL', 9)
        )
        df['macd'] = macd
        df['macd_signal'] = signal
        df['macd_histogram'] = histogram
        
        # Moving Averages
        df['sma_short'] = TechnicalIndicators.calculate_sma(
            df,
            period=config.get('MA_SHORT', 20)
        )
        df['sma_long'] = TechnicalIndicators.calculate_sma(
            df,
            period=config.get('MA_LONG', 50)
        )
        df['ema_short'] = TechnicalIndicators.calculate_ema(
            df,
            period=config.get('MA_SHORT', 20)
        )
        df['ema_long'] = TechnicalIndicators.calculate_ema(
            df,
            period=config.get('MA_LONG', 50)
        )
        
        # Bollinger Bands
        upper, middle, lower = TechnicalIndicators.calculate_bollinger_bands(
            df,
            period=config.get('BB_PERIOD', 20),
            std=config.get('BB_STD', 2)
        )
        df['bb_upper'] = upper
        df['bb_middle'] = middle
        df['bb_lower'] = lower
        
        # Volume indicators
        df['volume_sma'] = TechnicalIndicators.calculate_volume_sma(df, period=20)
        df['volume_ratio'] = df['volume'] / df['volume_sma']
        
        # Drop NaN values
        df.dropna(inplace=True)
        
        logger.info(f"Added all indicators. DataFrame shape: {df.shape}")
        
        return df


if __name__ == "__main__":
    # Test the indicators
    logging.basicConfig(level=logging.INFO)
    
    # Create sample data
    dates = pd.date_range(start='2024-01-01', periods=100, freq='15min')
    df = pd.DataFrame({
        'timestamp': dates,
        'open': np.random.randn(100).cumsum() + 100,
        'high': np.random.randn(100).cumsum() + 102,
        'low': np.random.randn(100).cumsum() + 98,
        'close': np.random.randn(100).cumsum() + 100,
        'volume': np.random.randint(1000, 10000, 100)
    })
    df.set_index('timestamp', inplace=True)
    
    # Add indicators
    config = {
        'RSI_PERIOD': 14,
        'MACD_FAST': 12,
        'MACD_SLOW': 26,
        'MACD_SIGNAL': 9,
        'MA_SHORT': 20,
        'MA_LONG': 50,
        'BB_PERIOD': 20,
        'BB_STD': 2
    }
    
    df_with_indicators = TechnicalIndicators.add_all_indicators(df, config)
    
    print("\nDataFrame with indicators:")
    print(df_with_indicators.tail())
    print("\nColumns:")
    print(df_with_indicators.columns.tolist())

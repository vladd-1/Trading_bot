"""
Backtester Module
Simulates trading over historical data to evaluate strategy performance
"""

import pandas as pd
import numpy as np
import logging
from typing import List, Dict
from datetime import datetime

from data_fetcher import DataFetcher
from indicators import TechnicalIndicators
from strategy import get_strategy
from risk_manager import RiskManager

logger = logging.getLogger(__name__)


class Backtester:
    """Backtesting engine for trading strategies"""
    
    def __init__(self, config: dict):
        """
        Initialize the backtester
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.data_fetcher = DataFetcher(config.get('EXCHANGE', 'binance'))
        self.strategy = get_strategy(config.get('STRATEGY', 'combined'), config)
        self.risk_manager = RiskManager(config)
        
        self.trades = []
        self.equity_curve = []
        
        logger.info(f"Backtester initialized with {self.strategy.name}")
    
    def prepare_data(self, symbol: str) -> pd.DataFrame:
        """
        Fetch and prepare data for backtesting
        
        Args:
            symbol: Trading symbol
            
        Returns:
            DataFrame with OHLCV data and indicators
        """
        logger.info(f"Preparing data for {symbol}")
        
        # Fetch historical data
        df = self.data_fetcher.fetch_ohlcv(
            symbol,
            timeframe=self.config.get('TIMEFRAME', '15m'),
            days=self.config.get('BACKTEST_DAYS', 7)
        )
        
        # Add technical indicators
        df = TechnicalIndicators.add_all_indicators(df, self.config)
        
        # Generate trading signals
        df = self.strategy.generate_signals(df)
        
        logger.info(f"Data prepared: {len(df)} candles with signals")
        
        return df
    
    def run_backtest(self, symbol: str) -> Dict:
        """
        Run backtest for a single symbol
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Dictionary with backtest results
        """
        logger.info(f"Starting backtest for {symbol}")
        
        # Prepare data
        df = self.prepare_data(symbol)
        
        # Track equity over time
        equity_history = []
        
        # Iterate through each candle
        for idx, row in df.iterrows():
            current_price = row['close']
            signal = row['signal']
            
            # Check stop-loss and take-profit for open positions
            trade = self.risk_manager.check_stop_loss_take_profit(
                symbol,
                current_price,
                idx
            )
            if trade:
                self.trades.append(trade)
            
            # Process buy signal
            if signal == 1 and self.risk_manager.can_open_position(symbol):
                position_size = self.risk_manager.calculate_position_size(current_price, symbol)
                position = self.risk_manager.open_position(
                    symbol,
                    current_price,
                    position_size,
                    idx
                )
            
            # Process sell signal
            elif signal == -1 and symbol in self.risk_manager.open_positions:
                trade = self.risk_manager.close_position(
                    symbol,
                    current_price,
                    idx,
                    'signal'
                )
                if trade:
                    self.trades.append(trade)
            
            # Record equity
            portfolio_value = self.risk_manager.get_portfolio_value({symbol: current_price})
            equity_history.append({
                'timestamp': idx,
                'equity': portfolio_value,
                'symbol': symbol
            })
        
        # Close any remaining open positions at the end
        if symbol in self.risk_manager.open_positions:
            final_price = df.iloc[-1]['close']
            final_timestamp = df.index[-1]
            trade = self.risk_manager.close_position(
                symbol,
                final_price,
                final_timestamp,
                'end_of_backtest'
            )
            if trade:
                self.trades.append(trade)
        
        # Store equity curve
        self.equity_curve.extend(equity_history)
        
        logger.info(f"Backtest completed for {symbol}: {len(self.trades)} trades")
        
        return {
            'symbol': symbol,
            'trades': len(self.trades),
            'final_capital': self.risk_manager.current_capital
        }
    
    def run_multi_symbol_backtest(self, symbols: List[str]) -> Dict:
        """
        Run backtest for multiple symbols
        
        Args:
            symbols: List of trading symbols
            
        Returns:
            Dictionary with combined backtest results
        """
        logger.info(f"Starting multi-symbol backtest for {len(symbols)} symbols")
        
        results = {}
        
        for symbol in symbols:
            try:
                result = self.run_backtest(symbol)
                results[symbol] = result
            except Exception as e:
                logger.error(f"Error backtesting {symbol}: {e}")
                continue
        
        return results
    
    def get_trades_dataframe(self) -> pd.DataFrame:
        """
        Get all trades as a DataFrame
        
        Returns:
            DataFrame with trade history
        """
        if not self.trades:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.trades)
        return df
    
    def get_equity_curve_dataframe(self) -> pd.DataFrame:
        """
        Get equity curve as a DataFrame
        
        Returns:
            DataFrame with equity over time
        """
        if not self.equity_curve:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.equity_curve)
        df.set_index('timestamp', inplace=True)
        return df
    
    def save_results(self, output_dir: str = 'results'):
        """
        Save backtest results to files
        
        Args:
            output_dir: Directory to save results
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Save trades
        if self.trades:
            trades_df = self.get_trades_dataframe()
            trades_path = os.path.join(output_dir, 'trade_history.csv')
            trades_df.to_csv(trades_path, index=False)
            logger.info(f"Saved trade history to {trades_path}")
        
        # Save equity curve
        if self.equity_curve:
            equity_df = self.get_equity_curve_dataframe()
            equity_path = os.path.join(output_dir, 'equity_curve.csv')
            equity_df.to_csv(equity_path)
            logger.info(f"Saved equity curve to {equity_path}")


if __name__ == "__main__":
    # Test the backtester
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    import config
    
    # Convert config module to dictionary
    config_dict = {k: v for k, v in vars(config).items() if not k.startswith('_')}
    
    backtester = Backtester(config_dict)
    
    # Run backtest for a single symbol
    result = backtester.run_backtest('BTC/USDT')
    
    print(f"\nBacktest Result:")
    print(f"Symbol: {result['symbol']}")
    print(f"Trades: {result['trades']}")
    print(f"Final Capital: ${result['final_capital']:.2f}")
    
    # Get trades
    trades_df = backtester.get_trades_dataframe()
    if not trades_df.empty:
        print(f"\nTrade History:")
        print(trades_df)

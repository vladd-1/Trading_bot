"""
Main Trading Bot Application
Intraday trading for Indian stocks using Zerodha Kite Connect API
"""

import logging
import os
import sys
from datetime import datetime
import pandas as pd

# Import modules
import config
from data_fetcher import KiteDataFetcher, authenticate_kite
from indicators import TechnicalIndicators
from strategy import get_strategy
from risk_manager import RiskManager
from performance import PerformanceAnalyzer

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class KiteBacktester:
    """Backtester for Kite Connect (Indian stocks)"""
    
    def __init__(self, kite_fetcher: KiteDataFetcher, config_dict: dict):
        """
        Initialize the Kite backtester
        
        Args:
            kite_fetcher: Authenticated KiteDataFetcher instance
            config_dict: Configuration dictionary
        """
        self.kite_fetcher = kite_fetcher
        self.config = config_dict
        self.strategy = get_strategy(config_dict.get('STRATEGY', 'combined'), config_dict)
        self.risk_manager = RiskManager(config_dict)
        
        self.trades = []
        self.equity_curve = []
        
        logger.info(f"Kite Backtester initialized with {self.strategy.name}")
    
    def prepare_data(self, symbol: str) -> pd.DataFrame:
        """
        Fetch and prepare data for backtesting
        
        Args:
            symbol: Stock symbol
            
        Returns:
            DataFrame with OHLCV data and indicators
        """
        logger.info(f"Preparing data for {symbol}")
        
        # Fetch historical data from Kite
        df = self.kite_fetcher.fetch_ohlcv_by_symbol(
            symbol,
            exchange=self.config.get('EXCHANGE', 'NSE'),
            days=self.config.get('BACKTEST_DAYS', 7),
            interval=self.config.get('TIMEFRAME', '15minute')
        )
        
        # Add technical indicators
        df = TechnicalIndicators.add_all_indicators(df, self.config)
        
        # Generate trading signals
        df = self.strategy.generate_signals(df)
        
        logger.info(f"Data prepared: {len(df)} candles with signals")
        
        return df
    
    def run_backtest(self, symbol: str) -> dict:
        """
        Run backtest for a single symbol
        
        Args:
            symbol: Stock symbol
            
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
    
    def run_multi_symbol_backtest(self, symbols: list) -> dict:
        """
        Run backtest for multiple symbols
        
        Args:
            symbols: List of stock symbols
            
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


def run_kite_backtest():
    """Run the backtesting simulation with Kite Connect"""
    
    import pandas as pd
    
    logger.info("="*60)
    logger.info("KITE CONNECT INTRADAY TRADING BOT - BACKTEST MODE")
    logger.info("="*60)
    
    # Check if API credentials are set
    if not config.KITE_API_KEY or not config.KITE_API_SECRET:
        logger.error("\n❌ Kite Connect API credentials not configured!")
        logger.error("\nPlease update config_kite.py with your API credentials:")
        logger.error("  1. Visit https://kite.trade/")
        logger.error("  2. Create a developer account and app")
        logger.error("  3. Copy your API Key and API Secret")
        logger.error("  4. Update KITE_API_KEY and KITE_API_SECRET in config_kite.py")
        return None
    
    # Convert config module to dictionary
    config_dict = {k: v for k, v in vars(config).items() if not k.startswith('_')}
    
    # Display configuration
    logger.info(f"\nConfiguration:")
    logger.info(f"  Strategy: {config.STRATEGY}")
    logger.info(f"  Symbols: {', '.join(config.SYMBOLS)}")
    logger.info(f"  Exchange: {config.EXCHANGE}")
    logger.info(f"  Timeframe: {config.TIMEFRAME}")
    logger.info(f"  Backtest Period: {config.BACKTEST_DAYS} days")
    logger.info(f"  Initial Capital: ₹{config.INITIAL_CAPITAL:,.2f}")
    logger.info(f"  Position Size: {config.POSITION_SIZE_PCT:.1%}")
    logger.info(f"  Stop Loss: {config.STOP_LOSS_PCT:.1%}")
    logger.info(f"  Take Profit: {config.TAKE_PROFIT_PCT:.1%}")
    
    # Authenticate with Kite Connect
    logger.info("\nAuthenticating with Kite Connect...")
    try:
        kite_fetcher = authenticate_kite(config.KITE_API_KEY, config.KITE_API_SECRET)
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        return None
    
    # Initialize backtester
    logger.info("\nInitializing backtester...")
    backtester = KiteBacktester(kite_fetcher, config_dict)
    
    # Run backtest for all symbols
    logger.info(f"\nRunning backtest for {len(config.SYMBOLS)} symbol(s)...")
    
    try:
        if len(config.SYMBOLS) == 1:
            # Single symbol backtest
            result = backtester.run_backtest(config.SYMBOLS[0])
        else:
            # Multi-symbol backtest
            result = backtester.run_multi_symbol_backtest(config.SYMBOLS)
        
        logger.info("\nBacktest completed successfully!")
        
        # Get results
        trades_df = pd.DataFrame(backtester.trades) if backtester.trades else pd.DataFrame()
        equity_df = pd.DataFrame(backtester.equity_curve)
        if not equity_df.empty:
            equity_df.set_index('timestamp', inplace=True)
        
        final_capital = backtester.risk_manager.current_capital
        
        # Analyze performance
        logger.info("\nAnalyzing performance...")
        analyzer = PerformanceAnalyzer(config.INITIAL_CAPITAL)
        metrics = analyzer.calculate_metrics(trades_df, equity_df, final_capital)
        
        # Print summary
        analyzer.print_summary(metrics)
        
        # Save results
        if config.SAVE_TRADE_HISTORY:
            logger.info(f"\nSaving results to {config.OUTPUT_DIR}/...")
            os.makedirs(config.OUTPUT_DIR, exist_ok=True)
            
            # Save trade history
            if not trades_df.empty:
                trades_path = os.path.join(config.OUTPUT_DIR, 'trade_history.csv')
                trades_df.to_csv(trades_path, index=False)
                logger.info(f"Saved trade history to {trades_path}")
            
            # Save equity curve
            if not equity_df.empty:
                equity_path = os.path.join(config.OUTPUT_DIR, 'equity_curve.csv')
                equity_df.to_csv(equity_path)
                logger.info(f"Saved equity curve to {equity_path}")
            
            # Save performance report
            report_path = os.path.join(config.OUTPUT_DIR, 'backtest_report.txt')
            analyzer.save_report(metrics, report_path)
            
            # Generate plots
            if config.ENABLE_PLOTS and not equity_df.empty:
                logger.info("Generating performance charts...")
                
                equity_plot_path = os.path.join(config.OUTPUT_DIR, 'equity_curve.png')
                analyzer.plot_equity_curve(equity_df, equity_plot_path)
                
                if not trades_df.empty:
                    trade_plot_path = os.path.join(config.OUTPUT_DIR, 'trade_distribution.png')
                    analyzer.plot_trade_distribution(trades_df, trade_plot_path)
                
                logger.info(f"Charts saved to {config.OUTPUT_DIR}/")
        
        # Display key results
        if metrics:
            print("\n" + "="*60)
            print("KEY RESULTS")
            print("="*60)
            print(f"Total Profit: ₹{metrics['total_return']:,.2f} ({metrics['total_return_pct']:.2%})")
            print(f"Win Rate: {metrics['win_rate']:.1%}")
            print(f"Profit Factor: {metrics['profit_factor']:.2f}")
            print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
            print(f"Max Drawdown: {metrics['max_drawdown_pct']:.2%}")
            print("="*60)
            
            if config.SAVE_TRADE_HISTORY:
                print(f"\nDetailed results saved to: {config.OUTPUT_DIR}/")
                print(f"  - Trade history: trade_history.csv")
                print(f"  - Equity curve: equity_curve.csv")
                print(f"  - Performance report: backtest_report.txt")
                if config.ENABLE_PLOTS:
                    print(f"  - Equity chart: equity_curve.png")
                    print(f"  - Trade distribution: trade_distribution.png")
        else:
            print("\n" + "="*60)
            print("NO TRADES EXECUTED")
            print("="*60)
            print("\n⚠️  The backtest did not execute any trades.")
            print("\nPossible reasons:")
            print("  1. Insufficient API permissions (see error above)")
            print("  2. No trading signals generated during the period")
            print("  3. Risk management prevented trades")
            print("="*60)
        
        return metrics
        
    except Exception as e:
        logger.error(f"Backtest failed: {e}", exc_info=True)
        raise


def main():
    """Main entry point"""
    
    try:
        # Run backtest
        metrics = run_kite_backtest()
        
        if metrics:
            logger.info("\n" + "="*60)
            logger.info("BACKTEST COMPLETED SUCCESSFULLY")
            logger.info("="*60)
            return 0
        else:
            return 1
        
    except KeyboardInterrupt:
        logger.info("\nBacktest interrupted by user")
        return 1
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

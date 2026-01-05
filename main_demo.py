"""
Demo Mode Main Application
Runs backtesting with simulated data when API access is not available
"""

import logging
import os
import sys
from datetime import datetime
import pandas as pd

# Import modules
import config
from demo_data import DemoDataGenerator
from indicators import TechnicalIndicators
from strategy import get_strategy
from risk_manager import RiskManager
from performance import PerformanceAnalyzer

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot_demo.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class DemoBacktester:
    """Backtester using demo/simulated data"""
    
    def __init__(self, config_dict: dict):
        """
        Initialize the demo backtester
        
        Args:
            config_dict: Configuration dictionary
        """
        self.config = config_dict
        self.demo_generator = DemoDataGenerator(seed=42)
        self.strategy = get_strategy(config_dict.get('STRATEGY', 'combined'), config_dict)
        self.risk_manager = RiskManager(config_dict)
        
        self.trades = []
        self.equity_curve = []
        
        logger.info(f"Demo Backtester initialized with {self.strategy.name}")
    
    def prepare_data(self, symbol: str, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare data with indicators and signals
        
        Args:
            symbol: Stock symbol
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with indicators and signals
        """
        logger.info(f"Preparing data for {symbol}")
        
        # Add technical indicators
        df = TechnicalIndicators.add_all_indicators(df, self.config)
        
        # Generate trading signals
        df = self.strategy.generate_signals(df)
        
        logger.info(f"Data prepared: {len(df)} candles with signals")
        
        return df
    
    def run_backtest(self, symbol: str, df: pd.DataFrame) -> dict:
        """
        Run backtest for a single symbol
        
        Args:
            symbol: Stock symbol
            df: DataFrame with OHLCV data
            
        Returns:
            Dictionary with backtest results
        """
        logger.info(f"Starting backtest for {symbol}")
        
        # Prepare data
        df = self.prepare_data(symbol, df)
        
        # Track equity over time
        equity_history = []
        
        # Iterate through each candle
        for idx, row in df.iterrows():
            current_price = row['close']
            signal = row['signal']
            
            # Check stop-loss and take-profit
            trade = self.risk_manager.check_stop_loss_take_profit(symbol, current_price, idx)
            if trade:
                self.trades.append(trade)
            
            # Process buy signal
            if signal == 1 and self.risk_manager.can_open_position(symbol):
                position_size = self.risk_manager.calculate_position_size(current_price, symbol)
                position = self.risk_manager.open_position(symbol, current_price, position_size, idx)
            
            # Process sell signal
            elif signal == -1 and symbol in self.risk_manager.open_positions:
                trade = self.risk_manager.close_position(symbol, current_price, idx, 'signal')
                if trade:
                    self.trades.append(trade)
            
            # Record equity
            portfolio_value = self.risk_manager.get_portfolio_value({symbol: current_price})
            equity_history.append({
                'timestamp': idx,
                'equity': portfolio_value,
                'symbol': symbol
            })
        
        # Close any remaining positions
        if symbol in self.risk_manager.open_positions:
            final_price = df.iloc[-1]['close']
            final_timestamp = df.index[-1]
            trade = self.risk_manager.close_position(symbol, final_price, final_timestamp, 'end_of_backtest')
            if trade:
                self.trades.append(trade)
        
        self.equity_curve.extend(equity_history)
        
        logger.info(f"Backtest completed for {symbol}: {len(self.trades)} trades")
        
        return {
            'symbol': symbol,
            'trades': len(self.trades),
            'final_capital': self.risk_manager.current_capital
        }
    
    def run_multi_symbol_backtest(self, symbols: list, demo_data: dict) -> dict:
        """
        Run backtest for multiple symbols
        
        Args:
            symbols: List of stock symbols
            demo_data: Dictionary of demo data for each symbol
            
        Returns:
            Dictionary with results
        """
        logger.info(f"Starting multi-symbol backtest for {len(symbols)} symbols")
        
        results = {}
        
        for symbol in symbols:
            if symbol in demo_data:
                try:
                    result = self.run_backtest(symbol, demo_data[symbol])
                    results[symbol] = result
                except Exception as e:
                    logger.error(f"Error backtesting {symbol}: {e}")
                    continue
        
        return results


def run_demo_backtest():
    """Run demo backtest with simulated data"""
    
    logger.info("="*60)
    logger.info("DEMO MODE - INTRADAY TRADING BOT BACKTEST")
    logger.info("="*60)
    logger.info("\n⚠️  Running in DEMO mode with simulated data")
    logger.info("This demonstrates how the bot would perform with real data\n")
    
    # Convert config to dict
    config_dict = {k: v for k, v in vars(config).items() if not k.startswith('_')}
    
    # Use 50 days for demo as requested
    demo_days = 50
    
    # Display configuration
    logger.info(f"\nConfiguration:")
    logger.info(f"  Strategy: {config.STRATEGY}")
    logger.info(f"  Symbols: {', '.join(config.SYMBOLS)}")
    logger.info(f"  Exchange: {config.EXCHANGE}")
    logger.info(f"  Timeframe: {config.TIMEFRAME}")
    logger.info(f"  Backtest Period: {demo_days} days (DEMO DATA)")
    logger.info(f"  Initial Capital: ₹{config.INITIAL_CAPITAL:,.2f}")
    logger.info(f"  Position Size: {config.POSITION_SIZE_PCT:.1%}")
    logger.info(f"  Stop Loss: {config.STOP_LOSS_PCT:.1%}")
    logger.info(f"  Take Profit: {config.TAKE_PROFIT_PCT:.1%}")
    
    # Generate demo data
    logger.info(f"\nGenerating demo data for {len(config.SYMBOLS)} stocks...")
    generator = DemoDataGenerator(seed=42)
    
    interval_minutes = int(config.TIMEFRAME.replace('minute', ''))
    demo_data = generator.generate_multiple_stocks(
        config.SYMBOLS,
        days=demo_days,
        interval_minutes=interval_minutes
    )
    
    # Initialize backtester
    logger.info("\nInitializing backtester...")
    backtester = DemoBacktester(config_dict)
    
    # Run backtest
    logger.info(f"\nRunning backtest for {len(config.SYMBOLS)} symbol(s)...")
    
    try:
        results = backtester.run_multi_symbol_backtest(config.SYMBOLS, demo_data)
        
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
            output_dir = 'results_demo'
            logger.info(f"\nSaving results to {output_dir}/...")
            os.makedirs(output_dir, exist_ok=True)
            
            # Save trade history
            if not trades_df.empty:
                trades_path = os.path.join(output_dir, 'trade_history.csv')
                trades_df.to_csv(trades_path, index=False)
                logger.info(f"Saved trade history to {trades_path}")
            
            # Save equity curve
            if not equity_df.empty:
                equity_path = os.path.join(output_dir, 'equity_curve.csv')
                equity_df.to_csv(equity_path)
                logger.info(f"Saved equity curve to {equity_path}")
            
            # Save performance report
            report_path = os.path.join(output_dir, 'backtest_report.txt')
            analyzer.save_report(metrics, report_path)
            
            # Generate plots
            if config.ENABLE_PLOTS and not equity_df.empty:
                logger.info("Generating performance charts...")
                
                equity_plot_path = os.path.join(output_dir, 'equity_curve.png')
                analyzer.plot_equity_curve(equity_df, equity_plot_path)
                
                if not trades_df.empty:
                    trade_plot_path = os.path.join(output_dir, 'trade_distribution.png')
                    analyzer.plot_trade_distribution(trades_df, trade_plot_path)
                
                logger.info(f"Charts saved to {output_dir}/")
        
        # Display key results
        if metrics:
            print("\n" + "="*60)
            print("KEY RESULTS (DEMO MODE)")
            print("="*60)
            print(f"Total Profit: ₹{metrics['total_return']:,.2f} ({metrics['total_return_pct']:.2%})")
            print(f"Win Rate: {metrics['win_rate']:.1%}")
            print(f"Profit Factor: {metrics['profit_factor']:.2f}")
            print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
            print(f"Max Drawdown: {metrics['max_drawdown_pct']:.2%}")
            print("="*60)
            
            print(f"\n📊 Detailed results saved to: {output_dir}/")
            print(f"  - Trade history: trade_history.csv")
            print(f"  - Equity curve: equity_curve.csv")
            print(f"  - Performance report: backtest_report.txt")
            if config.ENABLE_PLOTS:
                print(f"  - Equity chart: equity_curve.png")
                print(f"  - Trade distribution: trade_distribution.png")
            
            print(f"\n💡 This is a DEMO simulation with {demo_days} days of generated data.")
            print(f"   Real results may vary based on actual market conditions.")
        
        return metrics
        
    except Exception as e:
        logger.error(f"Backtest failed: {e}", exc_info=True)
        raise


def main():
    """Main entry point"""
    
    try:
        metrics = run_demo_backtest()
        
        if metrics:
            logger.info("\n" + "="*60)
            logger.info("DEMO BACKTEST COMPLETED SUCCESSFULLY")
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

"""
Performance Analysis Module
Calculates and displays trading performance metrics
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Optional
import logging
import os

logger = logging.getLogger(__name__)

# Set style for plots
sns.set_style('darkgrid')
plt.rcParams['figure.figsize'] = (12, 6)


class PerformanceAnalyzer:
    """Analyze and visualize trading performance"""
    
    def __init__(self, initial_capital: float):
        """
        Initialize the performance analyzer
        
        Args:
            initial_capital: Starting capital
        """
        self.initial_capital = initial_capital
    
    def calculate_metrics(
        self,
        trades_df: pd.DataFrame,
        equity_df: pd.DataFrame,
        final_capital: float
    ) -> Dict:
        """
        Calculate comprehensive performance metrics
        
        Args:
            trades_df: DataFrame with trade history
            equity_df: DataFrame with equity curve
            final_capital: Final portfolio value
            
        Returns:
            Dictionary with performance metrics
        """
        if trades_df.empty:
            logger.warning("No trades to analyze")
            return {}
        
        metrics = {}
        
        # Basic metrics
        metrics['initial_capital'] = self.initial_capital
        metrics['final_capital'] = final_capital
        metrics['total_return'] = final_capital - self.initial_capital
        metrics['total_return_pct'] = (final_capital - self.initial_capital) / self.initial_capital
        
        # Trade statistics
        metrics['total_trades'] = len(trades_df)
        metrics['winning_trades'] = len(trades_df[trades_df['pnl'] > 0])
        metrics['losing_trades'] = len(trades_df[trades_df['pnl'] < 0])
        metrics['win_rate'] = metrics['winning_trades'] / metrics['total_trades'] if metrics['total_trades'] > 0 else 0
        
        # Profit/Loss statistics
        winning_trades = trades_df[trades_df['pnl'] > 0]
        losing_trades = trades_df[trades_df['pnl'] < 0]
        
        metrics['avg_win'] = winning_trades['pnl'].mean() if len(winning_trades) > 0 else 0
        metrics['avg_loss'] = losing_trades['pnl'].mean() if len(losing_trades) > 0 else 0
        metrics['largest_win'] = winning_trades['pnl'].max() if len(winning_trades) > 0 else 0
        metrics['largest_loss'] = losing_trades['pnl'].min() if len(losing_trades) > 0 else 0
        
        # Profit factor
        total_wins = winning_trades['pnl'].sum() if len(winning_trades) > 0 else 0
        total_losses = abs(losing_trades['pnl'].sum()) if len(losing_trades) > 0 else 0
        metrics['profit_factor'] = total_wins / total_losses if total_losses > 0 else float('inf')
        
        # Risk-adjusted metrics
        if not equity_df.empty:
            returns = equity_df['equity'].pct_change().dropna()
            
            # Sharpe Ratio (annualized, assuming 252 trading days)
            if len(returns) > 0 and returns.std() > 0:
                metrics['sharpe_ratio'] = (returns.mean() / returns.std()) * np.sqrt(252)
            else:
                metrics['sharpe_ratio'] = 0
            
            # Sortino Ratio (only considers downside volatility)
            downside_returns = returns[returns < 0]
            if len(downside_returns) > 0 and downside_returns.std() > 0:
                metrics['sortino_ratio'] = (returns.mean() / downside_returns.std()) * np.sqrt(252)
            else:
                metrics['sortino_ratio'] = 0
            
            # Maximum Drawdown
            cumulative = (1 + returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            metrics['max_drawdown'] = drawdown.min()
            metrics['max_drawdown_pct'] = drawdown.min()
        else:
            metrics['sharpe_ratio'] = 0
            metrics['sortino_ratio'] = 0
            metrics['max_drawdown'] = 0
            metrics['max_drawdown_pct'] = 0
        
        # Average holding time
        if 'holding_time' in trades_df.columns:
            metrics['avg_holding_time'] = trades_df['holding_time'].mean()
        
        return metrics
    
    def print_summary(self, metrics: Dict):
        """
        Print performance summary
        
        Args:
            metrics: Dictionary with performance metrics
        """
        if not metrics:
            print("No metrics to display")
            return
        
        print("\n" + "="*60)
        print("BACKTEST PERFORMANCE SUMMARY")
        print("="*60)
        
        print(f"\n{'CAPITAL':-^60}")
        print(f"Initial Capital:        ${metrics['initial_capital']:,.2f}")
        print(f"Final Capital:          ${metrics['final_capital']:,.2f}")
        print(f"Total Return:           ${metrics['total_return']:,.2f}")
        print(f"Total Return %:         {metrics['total_return_pct']:.2%}")
        
        print(f"\n{'TRADE STATISTICS':-^60}")
        print(f"Total Trades:           {metrics['total_trades']}")
        print(f"Winning Trades:         {metrics['winning_trades']} ({metrics['win_rate']:.1%})")
        print(f"Losing Trades:          {metrics['losing_trades']} ({1-metrics['win_rate']:.1%})")
        
        print(f"\n{'PROFIT/LOSS':-^60}")
        print(f"Average Win:            ${metrics['avg_win']:,.2f}")
        print(f"Average Loss:           ${metrics['avg_loss']:,.2f}")
        print(f"Largest Win:            ${metrics['largest_win']:,.2f}")
        print(f"Largest Loss:           ${metrics['largest_loss']:,.2f}")
        print(f"Profit Factor:          {metrics['profit_factor']:.2f}")
        
        print(f"\n{'RISK METRICS':-^60}")
        print(f"Sharpe Ratio:           {metrics['sharpe_ratio']:.2f}")
        print(f"Sortino Ratio:          {metrics['sortino_ratio']:.2f}")
        print(f"Max Drawdown:           {metrics['max_drawdown_pct']:.2%}")
        
        if 'avg_holding_time' in metrics:
            print(f"\n{'TIMING':-^60}")
            print(f"Avg Holding Time:       {metrics['avg_holding_time']}")
        
        print("\n" + "="*60)
    
    def plot_equity_curve(self, equity_df: pd.DataFrame, output_path: Optional[str] = None):
        """
        Plot equity curve over time
        
        Args:
            equity_df: DataFrame with equity curve
            output_path: Path to save the plot
        """
        if equity_df.empty:
            logger.warning("No equity data to plot")
            return
        
        plt.figure(figsize=(14, 7))
        
        # Plot equity curve
        plt.subplot(2, 1, 1)
        plt.plot(equity_df.index, equity_df['equity'], linewidth=2, color='#2E86AB')
        plt.axhline(y=self.initial_capital, color='gray', linestyle='--', alpha=0.5, label='Initial Capital')
        plt.title('Portfolio Equity Curve', fontsize=16, fontweight='bold')
        plt.ylabel('Portfolio Value ($)', fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Plot returns
        plt.subplot(2, 1, 2)
        returns = equity_df['equity'].pct_change().fillna(0) * 100
        colors = ['green' if x >= 0 else 'red' for x in returns]
        plt.bar(equity_df.index, returns, color=colors, alpha=0.6, width=0.0001)
        plt.title('Returns (%)', fontsize=16, fontweight='bold')
        plt.ylabel('Return (%)', fontsize=12)
        plt.xlabel('Time', fontsize=12)
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            logger.info(f"Saved equity curve plot to {output_path}")
        else:
            plt.show()
        
        plt.close()
    
    def plot_trade_distribution(self, trades_df: pd.DataFrame, output_path: Optional[str] = None):
        """
        Plot trade profit/loss distribution
        
        Args:
            trades_df: DataFrame with trade history
            output_path: Path to save the plot
        """
        if trades_df.empty:
            logger.warning("No trades to plot")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # PnL distribution
        axes[0, 0].hist(trades_df['pnl'], bins=30, color='#2E86AB', alpha=0.7, edgecolor='black')
        axes[0, 0].axvline(x=0, color='red', linestyle='--', linewidth=2)
        axes[0, 0].set_title('Profit/Loss Distribution', fontsize=14, fontweight='bold')
        axes[0, 0].set_xlabel('PnL ($)')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].grid(True, alpha=0.3)
        
        # PnL percentage distribution
        axes[0, 1].hist(trades_df['pnl_pct'] * 100, bins=30, color='#A23B72', alpha=0.7, edgecolor='black')
        axes[0, 1].axvline(x=0, color='red', linestyle='--', linewidth=2)
        axes[0, 1].set_title('Return % Distribution', fontsize=14, fontweight='bold')
        axes[0, 1].set_xlabel('Return (%)')
        axes[0, 1].set_ylabel('Frequency')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Cumulative PnL
        cumulative_pnl = trades_df['pnl'].cumsum()
        axes[1, 0].plot(range(len(cumulative_pnl)), cumulative_pnl, linewidth=2, color='#18A558')
        axes[1, 0].fill_between(range(len(cumulative_pnl)), cumulative_pnl, alpha=0.3, color='#18A558')
        axes[1, 0].axhline(y=0, color='red', linestyle='--', linewidth=1)
        axes[1, 0].set_title('Cumulative PnL', fontsize=14, fontweight='bold')
        axes[1, 0].set_xlabel('Trade Number')
        axes[1, 0].set_ylabel('Cumulative PnL ($)')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Win/Loss pie chart
        win_count = len(trades_df[trades_df['pnl'] > 0])
        loss_count = len(trades_df[trades_df['pnl'] < 0])
        axes[1, 1].pie(
            [win_count, loss_count],
            labels=['Wins', 'Losses'],
            autopct='%1.1f%%',
            colors=['#18A558', '#F18F01'],
            startangle=90
        )
        axes[1, 1].set_title('Win/Loss Ratio', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            logger.info(f"Saved trade distribution plot to {output_path}")
        else:
            plt.show()
        
        plt.close()
    
    def save_report(self, metrics: Dict, output_path: str):
        """
        Save performance report to text file
        
        Args:
            metrics: Dictionary with performance metrics
            output_path: Path to save the report
        """
        if not metrics:
            logger.warning("No metrics to save")
            with open(output_path, 'w') as f:
                f.write("="*60 + "\n")
                f.write("BACKTEST PERFORMANCE REPORT\n")
                f.write("="*60 + "\n\n")
                f.write("No trades were executed during the backtest period.\n")
                f.write("="*60 + "\n")
            return
        
        with open(output_path, 'w') as f:
            f.write("="*60 + "\n")
            f.write("BACKTEST PERFORMANCE REPORT\n")
            f.write("="*60 + "\n\n")
            
            f.write(f"CAPITAL\n")
            f.write(f"Initial Capital:        ${metrics['initial_capital']:,.2f}\n")
            f.write(f"Final Capital:          ${metrics['final_capital']:,.2f}\n")
            f.write(f"Total Return:           ${metrics['total_return']:,.2f}\n")
            f.write(f"Total Return %:         {metrics['total_return_pct']:.2%}\n\n")
            
            f.write(f"TRADE STATISTICS\n")
            f.write(f"Total Trades:           {metrics['total_trades']}\n")
            f.write(f"Winning Trades:         {metrics['winning_trades']} ({metrics['win_rate']:.1%})\n")
            f.write(f"Losing Trades:          {metrics['losing_trades']} ({1-metrics['win_rate']:.1%})\n\n")
            
            f.write(f"PROFIT/LOSS\n")
            f.write(f"Average Win:            ${metrics['avg_win']:,.2f}\n")
            f.write(f"Average Loss:           ${metrics['avg_loss']:,.2f}\n")
            f.write(f"Largest Win:            ${metrics['largest_win']:,.2f}\n")
            f.write(f"Largest Loss:           ${metrics['largest_loss']:,.2f}\n")
            f.write(f"Profit Factor:          {metrics['profit_factor']:.2f}\n\n")
            
            f.write(f"RISK METRICS\n")
            f.write(f"Sharpe Ratio:           {metrics['sharpe_ratio']:.2f}\n")
            f.write(f"Sortino Ratio:          {metrics['sortino_ratio']:.2f}\n")
            f.write(f"Max Drawdown:           {metrics['max_drawdown_pct']:.2%}\n\n")
            
            if 'avg_holding_time' in metrics:
                f.write(f"TIMING\n")
                f.write(f"Avg Holding Time:       {metrics['avg_holding_time']}\n\n")
            
            f.write("="*60 + "\n")
        
        logger.info(f"Saved performance report to {output_path}")


if __name__ == "__main__":
    # Test the performance analyzer
    logging.basicConfig(level=logging.INFO)
    
    # Create sample trade data
    trades_data = {
        'symbol': ['BTC/USDT'] * 10,
        'pnl': [100, -50, 200, -30, 150, -80, 120, -40, 180, -60],
        'pnl_pct': [0.02, -0.01, 0.04, -0.006, 0.03, -0.016, 0.024, -0.008, 0.036, -0.012]
    }
    trades_df = pd.DataFrame(trades_data)
    
    # Create sample equity curve
    equity_data = {
        'timestamp': pd.date_range(start='2024-01-01', periods=100, freq='15min'),
        'equity': np.random.randn(100).cumsum() + 10000
    }
    equity_df = pd.DataFrame(equity_data).set_index('timestamp')
    
    analyzer = PerformanceAnalyzer(initial_capital=10000)
    metrics = analyzer.calculate_metrics(trades_df, equity_df, 10490)
    analyzer.print_summary(metrics)

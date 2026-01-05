"""
Risk Manager Module
Handles position sizing, stop-loss, take-profit, and risk limits
"""

import pandas as pd
import numpy as np
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class RiskManager:
    """Manages risk for trading operations"""
    
    def __init__(self, config: dict):
        """
        Initialize the risk manager
        
        Args:
            config: Configuration dictionary
        """
        self.initial_capital = config.get('INITIAL_CAPITAL', 10000)
        self.position_size_pct = config.get('POSITION_SIZE_PCT', 0.1)
        self.stop_loss_pct = config.get('STOP_LOSS_PCT', 0.02)
        self.take_profit_pct = config.get('TAKE_PROFIT_PCT', 0.04)
        self.max_positions = config.get('MAX_POSITIONS', 3)
        self.max_daily_loss_pct = config.get('MAX_DAILY_LOSS_PCT', 0.05)
        self.max_drawdown_pct = config.get('MAX_DRAWDOWN_PCT', 0.15)
        
        self.current_capital = self.initial_capital
        self.peak_capital = self.initial_capital
        self.daily_start_capital = self.initial_capital
        self.open_positions = {}
        
        logger.info(f"Risk Manager initialized with ${self.initial_capital} capital")
    
    def calculate_position_size(self, price: float, symbol: str) -> float:
        """
        Calculate position size based on available capital
        
        Args:
            price: Current price of the asset
            symbol: Trading symbol
            
        Returns:
            Position size (number of units to buy)
        """
        # Calculate available capital for this position
        position_capital = self.current_capital * self.position_size_pct
        
        # Calculate number of units
        position_size = position_capital / price
        
        logger.debug(f"Position size for {symbol}: {position_size:.6f} units (${position_capital:.2f})")
        
        return position_size
    
    def calculate_stop_loss(self, entry_price: float, position_type: str = 'long') -> float:
        """
        Calculate stop-loss price
        
        Args:
            entry_price: Entry price of the position
            position_type: 'long' or 'short'
            
        Returns:
            Stop-loss price
        """
        if position_type == 'long':
            stop_loss = entry_price * (1 - self.stop_loss_pct)
        else:
            stop_loss = entry_price * (1 + self.stop_loss_pct)
        
        return stop_loss
    
    def calculate_take_profit(self, entry_price: float, position_type: str = 'long') -> float:
        """
        Calculate take-profit price
        
        Args:
            entry_price: Entry price of the position
            position_type: 'long' or 'short'
            
        Returns:
            Take-profit price
        """
        if position_type == 'long':
            take_profit = entry_price * (1 + self.take_profit_pct)
        else:
            take_profit = entry_price * (1 - self.take_profit_pct)
        
        return take_profit
    
    def can_open_position(self, symbol: str) -> bool:
        """
        Check if we can open a new position
        
        Args:
            symbol: Trading symbol
            
        Returns:
            True if position can be opened, False otherwise
        """
        # Check if we already have a position in this symbol
        if symbol in self.open_positions:
            logger.debug(f"Already have an open position in {symbol}")
            return False
        
        # Check if we've reached max positions
        if len(self.open_positions) >= self.max_positions:
            logger.debug(f"Max positions ({self.max_positions}) reached")
            return False
        
        # Check daily loss limit
        daily_loss = (self.current_capital - self.daily_start_capital) / self.daily_start_capital
        if daily_loss < -self.max_daily_loss_pct:
            logger.warning(f"Daily loss limit reached: {daily_loss:.2%}")
            return False
        
        # Check max drawdown
        drawdown = (self.current_capital - self.peak_capital) / self.peak_capital
        if drawdown < -self.max_drawdown_pct:
            logger.warning(f"Max drawdown reached: {drawdown:.2%}")
            return False
        
        return True
    
    def open_position(
        self,
        symbol: str,
        entry_price: float,
        position_size: float,
        timestamp: pd.Timestamp
    ) -> dict:
        """
        Open a new position
        
        Args:
            symbol: Trading symbol
            entry_price: Entry price
            position_size: Position size (units)
            timestamp: Entry timestamp
            
        Returns:
            Position dictionary
        """
        stop_loss = self.calculate_stop_loss(entry_price)
        take_profit = self.calculate_take_profit(entry_price)
        
        position = {
            'symbol': symbol,
            'entry_price': entry_price,
            'position_size': position_size,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'entry_time': timestamp,
            'position_value': entry_price * position_size
        }
        
        self.open_positions[symbol] = position
        
        logger.info(
            f"Opened position: {symbol} | "
            f"Size: {position_size:.6f} | "
            f"Entry: ${entry_price:.2f} | "
            f"SL: ${stop_loss:.2f} | "
            f"TP: ${take_profit:.2f}"
        )
        
        return position
    
    def close_position(
        self,
        symbol: str,
        exit_price: float,
        timestamp: pd.Timestamp,
        reason: str = 'signal'
    ) -> Optional[dict]:
        """
        Close an existing position
        
        Args:
            symbol: Trading symbol
            exit_price: Exit price
            timestamp: Exit timestamp
            reason: Reason for closing ('signal', 'stop_loss', 'take_profit')
            
        Returns:
            Trade result dictionary or None if position doesn't exist
        """
        if symbol not in self.open_positions:
            logger.warning(f"No open position found for {symbol}")
            return None
        
        position = self.open_positions[symbol]
        
        # Calculate profit/loss
        entry_value = position['entry_price'] * position['position_size']
        exit_value = exit_price * position['position_size']
        pnl = exit_value - entry_value
        pnl_pct = (exit_price - position['entry_price']) / position['entry_price']
        
        # Update capital
        self.current_capital += pnl
        
        # Update peak capital
        if self.current_capital > self.peak_capital:
            self.peak_capital = self.current_capital
        
        # Create trade result
        trade = {
            'symbol': symbol,
            'entry_price': position['entry_price'],
            'exit_price': exit_price,
            'position_size': position['position_size'],
            'entry_time': position['entry_time'],
            'exit_time': timestamp,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'reason': reason,
            'holding_time': timestamp - position['entry_time']
        }
        
        # Remove position
        del self.open_positions[symbol]
        
        logger.info(
            f"Closed position: {symbol} | "
            f"Entry: ${position['entry_price']:.2f} | "
            f"Exit: ${exit_price:.2f} | "
            f"PnL: ${pnl:.2f} ({pnl_pct:.2%}) | "
            f"Reason: {reason}"
        )
        
        return trade
    
    def check_stop_loss_take_profit(
        self,
        symbol: str,
        current_price: float,
        timestamp: pd.Timestamp
    ) -> Optional[dict]:
        """
        Check if stop-loss or take-profit is hit
        
        Args:
            symbol: Trading symbol
            current_price: Current price
            timestamp: Current timestamp
            
        Returns:
            Trade result if position is closed, None otherwise
        """
        if symbol not in self.open_positions:
            return None
        
        position = self.open_positions[symbol]
        
        # Check stop-loss
        if current_price <= position['stop_loss']:
            return self.close_position(symbol, position['stop_loss'], timestamp, 'stop_loss')
        
        # Check take-profit
        if current_price >= position['take_profit']:
            return self.close_position(symbol, position['take_profit'], timestamp, 'take_profit')
        
        return None
    
    def reset_daily_capital(self):
        """Reset daily starting capital (call at start of each day)"""
        self.daily_start_capital = self.current_capital
        logger.debug(f"Daily capital reset to ${self.current_capital:.2f}")
    
    def get_portfolio_value(self, current_prices: dict) -> float:
        """
        Calculate total portfolio value including open positions
        
        Args:
            current_prices: Dictionary mapping symbols to current prices
            
        Returns:
            Total portfolio value
        """
        total_value = self.current_capital
        
        for symbol, position in self.open_positions.items():
            if symbol in current_prices:
                position_value = current_prices[symbol] * position['position_size']
                total_value += position_value - position['position_value']
        
        return total_value
    
    def get_current_drawdown(self) -> float:
        """
        Calculate current drawdown from peak
        
        Returns:
            Drawdown percentage (negative value)
        """
        return (self.current_capital - self.peak_capital) / self.peak_capital


if __name__ == "__main__":
    # Test the risk manager
    logging.basicConfig(level=logging.INFO)
    
    config = {
        'INITIAL_CAPITAL': 10000,
        'POSITION_SIZE_PCT': 0.1,
        'STOP_LOSS_PCT': 0.02,
        'TAKE_PROFIT_PCT': 0.04,
        'MAX_POSITIONS': 3,
        'MAX_DAILY_LOSS_PCT': 0.05,
        'MAX_DRAWDOWN_PCT': 0.15
    }
    
    rm = RiskManager(config)
    
    # Test opening a position
    timestamp = pd.Timestamp.now()
    entry_price = 50000
    position_size = rm.calculate_position_size(entry_price, 'BTC/USDT')
    
    if rm.can_open_position('BTC/USDT'):
        position = rm.open_position('BTC/USDT', entry_price, position_size, timestamp)
        print(f"\nOpened position: {position}")
    
    # Test closing position with profit
    exit_price = 52000
    trade = rm.close_position('BTC/USDT', exit_price, timestamp, 'take_profit')
    print(f"\nClosed trade: {trade}")
    print(f"Current capital: ${rm.current_capital:.2f}")

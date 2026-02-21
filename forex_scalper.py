"""
Forex Trading Module - Scalper Strategy with Take Profit, Stop Loss, and Position Management
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from enum import Enum

class OrderType(Enum):
    """Order types for trading"""
    BUY = 1
    SELL = -1

class PositionStatus(Enum):
    """Position status"""
    OPEN = "open"
    CLOSED = "closed"
    PENDING = "pending"

class ForexScalperBot:
    """
    Forex Scalper Trading Bot with Position Management
    - Entry based on technical indicators
    - Take Profit and Stop Loss management
    - Risk management and position sizing
    """
    
    def __init__(self, initial_balance=10000, risk_percentage=2, leverage=1):
        """
        Initialize the Scalper Bot
        
        Parameters:
        - initial_balance: Starting account balance
        - risk_percentage: Risk per trade (2% recommended)
        - leverage: Trading leverage (1 = no leverage)
        """
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.risk_percentage = risk_percentage
        self.leverage = leverage
        self.positions = []  # List of open positions
        self.closed_positions = []  # History of closed positions
        self.trades_log = []  # Log of all trades
        self.max_positions = 3  # Maximum concurrent positions
        
    def calculate_position_size(self, entry_price, stop_loss_price):
        """
        Calculate position size based on risk management
        Risk Amount = Account Balance * Risk Percentage
        Position Size = Risk Amount / (Entry Price - Stop Loss)
        """
        risk_amount = self.current_balance * (self.risk_percentage / 100)
        price_difference = abs(entry_price - stop_loss_price)
        
        if price_difference == 0:
            return 0
            
        position_size = risk_amount / price_difference
        return position_size
    
    def open_position(self, symbol, order_type, entry_price, stop_loss, take_profit, timestamp):
        """
        Open a new trading position
        
        Parameters:
        - symbol: Currency pair (e.g., 'EUR/USD')
        - order_type: BUY or SELL
        - entry_price: Entry price
        - stop_loss: Stop loss price
        - take_profit: Take profit price
        - timestamp: Entry time
        """
        
        # Check if we can open more positions
        if len([p for p in self.positions if p['status'] == PositionStatus.OPEN.value]) >= self.max_positions:
            print(f"⚠️  Maximum positions ({self.max_positions}) reached. Cannot open new position.")
            return None
        
        # Calculate position size
        position_size = self.calculate_position_size(entry_price, stop_loss)
        
        if position_size <= 0:
            print("❌ Invalid position size calculated")
            return None
        
        # Calculate potential profit/loss
        if order_type == OrderType.BUY:
            potential_profit = (take_profit - entry_price) * position_size
            potential_loss = (entry_price - stop_loss) * position_size
        else:  # SELL
            potential_profit = (entry_price - take_profit) * position_size
            potential_loss = (stop_loss - entry_price) * position_size
        
        # Create position object
        position = {
            'id': len(self.positions) + 1,
            'symbol': symbol,
            'order_type': order_type.name,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'position_size': position_size,
            'entry_time': timestamp,
            'status': PositionStatus.OPEN.value,
            'current_price': entry_price,
            'potential_profit': potential_profit,
            'potential_loss': potential_loss,
            'risk_reward_ratio': potential_profit / abs(potential_loss) if potential_loss != 0 else 0,
        }
        
        self.positions.append(position)
        
        print(f"\n✅ POSITION OPENED:")
        print(f"   Symbol: {symbol}")
        print(f"   Type: {order_type.name}")
        print(f"   Entry Price: ${entry_price:.5f}")
        print(f"   Stop Loss: ${stop_loss:.5f}")
        print(f"   Take Profit: ${take_profit:.5f}")
        print(f"   Position Size: {position_size:.2f} lots")
        print(f"   Risk/Reward Ratio: {position['risk_reward_ratio']:.2f}")
        print(f"   Potential Profit: ${potential_profit:.2f}")
        print(f"   Potential Loss: ${potential_loss:.2f}")
        
        return position
    
    def update_position(self, position_id, current_price):
        """
        Update position with current market price
        Check if Stop Loss or Take Profit is hit
        """
        position = None
        for p in self.positions:
            if p['id'] == position_id and p['status'] == PositionStatus.OPEN.value:
                position = p
                break
        
        if not position:
            return None
        
        position['current_price'] = current_price
        
        # Check Take Profit
        if position['order_type'] == OrderType.BUY.name:
            if current_price >= position['take_profit']:
                self.close_position(position_id, current_price, reason="TAKE_PROFIT")
                return position
            elif current_price <= position['stop_loss']:
                self.close_position(position_id, current_price, reason="STOP_LOSS")
                return position
        
        else:  # SELL
            if current_price <= position['take_profit']:
                self.close_position(position_id, current_price, reason="TAKE_PROFIT")
                return position
            elif current_price >= position['stop_loss']:
                self.close_position(position_id, current_price, reason="STOP_LOSS")
                return position
        
        # Update potential profit/loss
        if position['order_type'] == OrderType.BUY.name:
            position['potential_profit'] = (current_price - position['entry_price']) * position['position_size']
        else:
            position['potential_profit'] = (position['entry_price'] - current_price) * position['position_size']
        
        return position
    
    def close_position(self, position_id, exit_price, reason="MANUAL"):
        """
        Close a trading position
        
        Parameters:
        - position_id: ID of position to close
        - exit_price: Exit price
        - reason: Reason for closing (TAKE_PROFIT, STOP_LOSS, MANUAL)
        """
        position = None
        for p in self.positions:
            if p['id'] == position_id and p['status'] == PositionStatus.OPEN.value:
                position = p
                break
        
        if not position:
            return None
        
        # Calculate actual profit/loss
        if position['order_type'] == OrderType.BUY.name:
            profit_loss = (exit_price - position['entry_price']) * position['position_size']
        else:  # SELL
            profit_loss = (position['entry_price'] - exit_price) * position['position_size']
        
        # Update position
        position['exit_price'] = exit_price
        position['exit_time'] = datetime.now()
        position['status'] = PositionStatus.CLOSED.value
        position['profit_loss'] = profit_loss
        position['close_reason'] = reason
        
        # Calculate ROI
        roi = (profit_loss / self.initial_balance) * 100
        position['roi'] = roi
        
        # Update balance
        self.current_balance += profit_loss
        
        # Move to closed positions
        self.positions.remove(position)
        self.closed_positions.append(position)
        self.trades_log.append(position)
        
        # Print closure info
        status_symbol = "✅" if profit_loss > 0 else "❌"
        print(f"\n{status_symbol} POSITION CLOSED:")
        print(f"   Symbol: {position['symbol']}")
        print(f"   Reason: {reason}")
        print(f"   Entry Price: ${position['entry_price']:.5f}")
        print(f"   Exit Price: ${exit_price:.5f}")
        print(f"   Profit/Loss: ${profit_loss:.2f}")
        print(f"   ROI: {roi:.2f}%")
        print(f"   Current Balance: ${self.current_balance:.2f}")
        
        return position
    
    def get_open_positions(self):
        """Get all open positions"""
        return [p for p in self.positions if p['status'] == PositionStatus.OPEN.value]
    
    def get_position_stats(self):
        """Get statistics for all positions"""
        if not self.closed_positions:
            return None
        
        df = pd.DataFrame(self.closed_positions)
        
        stats = {
            'total_trades': len(self.closed_positions),
            'winning_trades': len(df[df['profit_loss'] > 0]),
            'losing_trades': len(df[df['profit_loss'] < 0]),
            'win_rate': (len(df[df['profit_loss'] > 0]) / len(self.closed_positions)) * 100,
            'total_profit_loss': df['profit_loss'].sum(),
            'average_profit_loss': df['profit_loss'].mean(),
            'largest_win': df['profit_loss'].max(),
            'largest_loss': df['profit_loss'].min(),
            'current_balance': self.current_balance,
            'total_return': ((self.current_balance - self.initial_balance) / self.initial_balance) * 100,
        }
        
        return stats
    
    def print_account_summary(self):
        """Print account and trading summary"""
        print("\n" + "="*80)
        print("FOREX SCALPER BOT - ACCOUNT SUMMARY")
        print("="*80)
        
        print(f"\n💰 ACCOUNT DETAILS:")
        print(f"   Initial Balance: ${self.initial_balance:.2f}")
        print(f"   Current Balance: ${self.current_balance:.2f}")
        print(f"   Total Profit/Loss: ${self.current_balance - self.initial_balance:.2f}")
        print(f"   Total Return: {((self.current_balance - self.initial_balance) / self.initial_balance) * 100:.2f}%")
        
        print(f"\n📊 OPEN POSITIONS: {len(self.get_open_positions())}")
        for pos in self.get_open_positions():
            pnl_symbol = "+" if pos['potential_profit'] > 0 else ""
            print(f"   [{pos['id']}] {pos['symbol']} {pos['order_type']} @ ${pos['entry_price']:.5f}")
            print(f"       Current: ${pos['current_price']:.5f} | P&L: {pnl_symbol}${pos['potential_profit']:.2f}")
        
        stats = self.get_position_stats()
        if stats:
            print(f"\n📈 TRADING STATISTICS:")
            print(f"   Total Trades: {stats['total_trades']}")
            print(f"   Winning Trades: {stats['winning_trades']}")
            print(f"   Losing Trades: {stats['losing_trades']}")
            print(f"   Win Rate: {stats['win_rate']:.2f}%")
            print(f"   Avg Profit/Loss per Trade: ${stats['average_profit_loss']:.2f}")
            print(f"   Largest Win: ${stats['largest_win']:.2f}")
            print(f"   Largest Loss: ${stats['largest_loss']:.2f}")
        
        print("\n" + "="*80)
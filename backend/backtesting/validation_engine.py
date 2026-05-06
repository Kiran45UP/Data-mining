"""
Unified Strategy Validation Engine
Validates trading signals against historical stock data and calculates performance metrics
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
import math


class StrategyValidator:
    """Validates trading signals and calculates performance metrics"""
    
    def __init__(self, data: pd.DataFrame, initial_capital: float = 10000.0):
        """
        Args:
            data: DataFrame with OHLCV data (Date index, columns: Open, High, Low, Close, Volume)
            initial_capital: Starting capital for validation
        """
        self.data = data.reset_index()
        self.data['Date'] = pd.to_datetime(self.data['Date'])
        self.data = self.data.sort_values('Date').reset_index(drop=True)
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.position = None  # {'entry_date': date, 'entry_price': price, 'shares': num, 'source': 'signal_source'}
        self.trades = []
        self.equity_curve = []
        self.signals_applied = []
    
    def validate(self, signals_dict: Dict[Tuple[str, str], Dict], hold_days: int = 5, ticker: str = None) -> Dict[str, Any]:
        """
        Validate signals against historical data
        
        Args:
            signals_dict: Dict with key=(date, ticker), value={'signal': 'BUY'/'SELL'/'HOLD', ...}
            hold_days: Number of days to hold position after BUY signal
            ticker: (Optional) Filter signals for specific ticker. If None, uses all tickers.
            
        Returns:
            Performance metrics and trade log
        """
        if len(self.data) == 0:
            return {"error": "No data provided for validation"}
        
        self.trades = []
        self.equity_curve = []
        self.position = None
        self.capital = self.initial_capital
        self.signals_applied = []
        
        # Build a simple date->signal map for faster lookup
        date_signals = {}
        for (sig_date, sig_ticker), sig in signals_dict.items():
            try:
                date_str = pd.Timestamp(sig_date).strftime('%Y-%m-%d')
                date_signals[date_str] = sig
            except:
                pass
        
        for idx, row in self.data.iterrows():
            current_date = row['Date']
            current_price = row['Close']
            date_str = current_date.strftime('%Y-%m-%d')
            
            # Check if we have a signal for today
            signal_data = date_signals.get(date_str)
            
            # Handle signal
            if signal_data and signal_data.get('signal') == 'BUY' and self.position is None:
                self._enter_position(current_date, current_price, signal_data)
            
            elif signal_data and signal_data.get('signal') == 'SELL' and self.position is not None:
                self._exit_position(current_date, current_price, 'sell_signal')
            
            # Check if hold period expired
            elif self.position is not None:
                days_held = (current_date - self.position['entry_date']).days
                if days_held >= hold_days:
                    self._exit_position(current_date, current_price, 'hold_period_expired')
            
            # Track equity
            current_equity = self._calculate_equity(current_price)
            self.equity_curve.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'equity': round(current_equity, 2)
            })
        
        # Close any open position
        if self.position is not None:
            last_price = self.data.iloc[-1]['Close']
            self._exit_position(self.data.iloc[-1]['Date'], last_price, 'end_of_data')
        
        return self._calculate_metrics()
    
    def _enter_position(self, date: pd.Timestamp, price: float, signal_data: Dict):
        """Enter a long position"""
        # Use 95% of capital
        investment = self.capital * 0.95
        shares = math.floor(investment / price)
        
        if shares > 0:
            self.position = {
                'entry_date': date,
                'entry_price': price,
                'shares': shares,
                'entry_capital': shares * price,
                'source': signal_data.get('sources', ['unknown'])[0]
            }
            
            self.capital -= (shares * price)
            
            self.trades.append({
                'date': date.strftime('%Y-%m-%d'),
                'action': 'BUY',
                'price': round(price, 2),
                'shares': shares,
                'amount': round(shares * price, 2),
                'signal_confidence': signal_data.get('confidence', 0),
                'source': signal_data.get('sources', ['unknown'])[0],
                'pnl': 0
            })
            
            self.signals_applied.append({
                'date': date.strftime('%Y-%m-%d'),
                'action': 'BUY',
                'signal': signal_data
            })
    
    def _exit_position(self, date: pd.Timestamp, price: float, reason: str):
        """Exit the position"""
        if self.position is None:
            return
        
        shares = self.position['shares']
        entry_price = self.position['entry_price']
        proceeds = shares * price
        pnl = proceeds - self.position['entry_capital']
        pnl_percent = (pnl / self.position['entry_capital']) * 100 if self.position['entry_capital'] > 0 else 0
        
        self.capital += proceeds
        
        self.trades.append({
            'date': date.strftime('%Y-%m-%d'),
            'action': 'SELL',
            'price': round(price, 2),
            'shares': shares,
            'amount': round(proceeds, 2),
            'entry_price': round(entry_price, 2),
            'pnl': round(pnl, 2),
            'pnl_percent': round(pnl_percent, 2),
            'days_held': (date - self.position['entry_date']).days,
            'exit_reason': reason
        })
        
        self.position = None
    
    def _calculate_equity(self, current_price: float) -> float:
        """Calculate current equity including position"""
        equity = self.capital
        if self.position is not None:
            equity += self.position['shares'] * current_price
        return equity
    
    def _calculate_metrics(self) -> Dict[str, Any]:
        """Calculate performance metrics"""
        final_equity = self._calculate_equity(self.data.iloc[-1]['Close'] if len(self.data) > 0 else 0)
        
        # Return metrics
        total_return = ((final_equity - self.initial_capital) / self.initial_capital) * 100 if self.initial_capital > 0 else 0
        
        # Count sells
        sell_trades = [t for t in self.trades if t['action'] == 'SELL']
        winning_trades = sum(1 for t in sell_trades if t.get('pnl', 0) > 0)
        win_rate = (winning_trades / len(sell_trades) * 100) if len(sell_trades) > 0 else 0
        
        # Average return per trade
        avg_return = np.mean([t.get('pnl_percent', 0) for t in sell_trades]) if len(sell_trades) > 0 else 0
        
        # Max gain/loss
        max_gain = max([t.get('pnl', 0) for t in sell_trades], default=0)
        max_loss = min([t.get('pnl', 0) for t in sell_trades], default=0)
        
        # Annualized return
        years = len(self.data) / 252 if len(self.data) > 0 else 1
        annualized_return = 0
        if years > 0 and final_equity > 0:
            annualized_return = ((final_equity / self.initial_capital) ** (1 / years) - 1) * 100
        
        # Sharpe ratio
        sharpe_ratio = 0
        if len(self.equity_curve) > 1:
            equity_df = pd.DataFrame(self.equity_curve)
            daily_returns = equity_df['equity'].pct_change().dropna()
            if len(daily_returns) > 0 and daily_returns.std() > 0:
                mean_return = daily_returns.mean()
                std_return = daily_returns.std()
                risk_free_rate = 0.02 / 252
                sharpe_ratio = ((mean_return - risk_free_rate) / std_return) * math.sqrt(252)
        
        # Max drawdown
        max_drawdown = 0
        if len(self.equity_curve) > 1:
            equity_df = pd.DataFrame(self.equity_curve)
            rolling_max = equity_df['equity'].cummax()
            drawdowns = (equity_df['equity'] - rolling_max) / rolling_max
            max_drawdown = abs(drawdowns.min() * 100)
        
        return {
            'total_return': round(total_return, 2),
            'annualized_return': round(annualized_return, 2),
            'win_rate': round(win_rate, 2),
            'total_signals': len(self.signals_applied),
            'total_trades': len(sell_trades),
            'winning_trades': winning_trades,
            'losing_trades': len(sell_trades) - winning_trades,
            'avg_return': round(avg_return, 2),
            'max_gain': round(max_gain, 2),
            'max_loss': round(max_loss, 2),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'max_drawdown': round(max_drawdown, 2),
            'final_equity': round(final_equity, 2),
            'equity_curve': self.equity_curve,
            'trades': self.trades,
            'signals_applied': self.signals_applied
        }


class MultiModuleValidator:
    """Validate combined signals from multiple modules with custom rules"""
    
    def __init__(self, data: pd.DataFrame):
        """
        Args:
            data: DataFrame with OHLCV data
        """
        self.data = data
    
    def validate_with_rules(self, 
                           signals_dict: Dict,
                           rule_config: Dict[str, Any],
                           hold_days: int = 5,
                           initial_capital: float = 10000.0) -> Dict[str, Any]:
        """
        Validate signals with custom rules
        
        rule_config example:
        {
            'condition': 'AND',  # 'AND' or 'OR'
            'requirements': [
                {'source': 'anomaly', 'signal': 'BUY', 'min_confidence': 0.5},
                {'source': 'association', 'signal': 'BUY', 'min_confidence': 0.6}
            ]
        }
        
        Returns:
            Validation result with metrics
        """
        # Filter signals based on rules
        filtered_signals = self._apply_rules(signals_dict, rule_config)
        
        # Validate filtered signals
        validator = StrategyValidator(self.data, initial_capital)
        result = validator.validate(filtered_signals, hold_days)
        
        return result
    
    def _apply_rules(self, signals_dict: Dict, rule_config: Dict) -> Dict:
        """Apply custom rules to filter signals"""
        filtered = {}
        
        condition = rule_config.get('condition', 'AND')
        requirements = rule_config.get('requirements', [])
        
        if not requirements:
            return signals_dict
        
        for key, signal_data in signals_dict.items():
            matches = []
            
            for req in requirements:
                source = req.get('source')
                signal = req.get('signal')
                min_conf = req.get('min_confidence', 0)
                
                # Check if any component signal matches the requirement
                has_match = False
                if 'signals' in signal_data:
                    for comp_signal in signal_data['signals']:
                        if (comp_signal.get('source') == source and
                            comp_signal.get('signal') == signal and
                            comp_signal.get('confidence', 0) >= min_conf):
                            has_match = True
                            break
                
                matches.append(has_match)
            
            # Apply AND/OR logic
            if condition == 'AND':
                if all(matches):
                    filtered[key] = signal_data
            elif condition == 'OR':
                if any(matches):
                    filtered[key] = signal_data
        
        return filtered

import pandas as pd
import numpy as np
import math
from typing import Dict, Any, List

class BacktestEngine:
    def __init__(self, data: pd.DataFrame, strategy, initial_capital: float = 10000.0,
                 commission: float = 1.0, slippage: float = 0.001):
        self.data = data
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        
        self.capital = initial_capital
        self.shares = 0
        self.equity_curve = []
        self.trades = []

    def run(self) -> Dict[str, Any]:
        if len(self.data) < 50:
            return {"error": "Not enough data to run backtest (minimum 50 bars needed)"}

        # Ensure index is datetime for grouping/metrics
        dates = self.data.index
        
        # Loop over each row starting from index 50
        for i in range(50, len(self.data)):
            current_bar = self.data.iloc[i]
            date_str = dates[i].strftime('%Y-%m-%d')
            
            # History up to (and including) current bar
            history_so_far = self.data.iloc[:i+1]
            
            signal = self.strategy.generate_signal(current_bar, history_so_far)
            price = float(current_bar['Close'])
            
            # Execute BUY
            if signal == "BUY" and self.capital > 0:
                # Calculate execution price with slippage
                exec_price = price * (1 + self.slippage)
                
                # Buy shares = floor((capital * 0.95) / price)
                shares_to_buy = math.floor((self.capital * 0.95) / exec_price)
                
                if shares_to_buy > 0:
                    cost = shares_to_buy * exec_price
                    self.capital -= (cost + self.commission)
                    self.shares += shares_to_buy
                    
                    self.trades.append({
                        "date": date_str,
                        "action": "BUY",
                        "price": round(exec_price, 2),
                        "shares": shares_to_buy,
                        "pnl": 0.0 # PnL is tracked on SELL
                    })
            
            # Execute SELL
            elif signal == "SELL" and self.shares > 0:
                exec_price = price * (1 - self.slippage)
                proceeds = self.shares * exec_price
                
                self.capital += (proceeds - self.commission)
                
                # Calculate PnL roughly based on last BUY (assuming we only hold one position)
                # For simplicity, we just find the last BUY trade
                buy_price = 0
                for t in reversed(self.trades):
                    if t['action'] == 'BUY':
                        buy_price = t['price']
                        break
                        
                pnl = (exec_price - buy_price) * self.shares - (self.commission * 2) if buy_price else 0
                
                self.trades.append({
                    "date": date_str,
                    "action": "SELL",
                    "price": round(exec_price, 2),
                    "shares": self.shares,
                    "pnl": round(pnl, 2)
                })
                
                self.shares = 0
                
            # Track equity curve
            current_equity = self.capital + (self.shares * price)
            self.equity_curve.append({
                "date": date_str,
                "equity": round(current_equity, 2)
            })
            
        # Force close position at the end if still open
        if self.shares > 0:
            last_price = float(self.data.iloc[-1]['Close'])
            self.capital += (self.shares * last_price)
            # Not adding to trades to keep it simple, just adding to final equity
            
        return self._calculate_metrics()

    def _calculate_metrics(self) -> Dict[str, Any]:
        final_equity = self.capital + (self.shares * float(self.data.iloc[-1]['Close']))
        
        # Return metrics
        total_return = ((final_equity - self.initial_capital) / self.initial_capital) * 100
        
        years = len(self.data) / 252
        annualized_return = 0
        if years > 0 and final_equity > 0:
            annualized_return = ((final_equity / self.initial_capital) ** (1 / years) - 1) * 100
            
        # Drawdown
        equity_df = pd.DataFrame(self.equity_curve)
        max_drawdown = 0
        if not equity_df.empty:
            rolling_max = equity_df['equity'].cummax()
            drawdowns = (equity_df['equity'] - rolling_max) / rolling_max
            max_drawdown = abs(drawdowns.min() * 100)
            
        # Trade metrics
        winning_trades = sum(1 for t in self.trades if t['action'] == 'SELL' and t.get('pnl', 0) > 0)
        sell_trades = sum(1 for t in self.trades if t['action'] == 'SELL')
        win_rate = (winning_trades / sell_trades * 100) if sell_trades > 0 else 0
        
        # Sharpe ratio (simplified)
        sharpe_ratio = 0
        if not equity_df.empty and len(equity_df) > 1:
            daily_returns = equity_df['equity'].pct_change().dropna()
            mean_return = daily_returns.mean()
            std_return = daily_returns.std()
            risk_free_rate = 0.02 / 252 # 2% annual risk-free rate
            
            if std_return > 0:
                sharpe_ratio = ((mean_return - risk_free_rate) / std_return) * math.sqrt(252)
        
        return {
            "total_return": round(total_return, 2),
            "annualized_return": round(annualized_return, 2),
            "sharpe_ratio": round(sharpe_ratio, 2),
            "max_drawdown": round(max_drawdown, 2),
            "win_rate": round(win_rate, 2),
            "trade_count": len(self.trades),
            "equity_curve": self.equity_curve,
            "trades": self.trades
        }

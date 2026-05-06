import pandas as pd
from typing import Dict, Any

class BaseStrategy:
    def generate_signal(self, current_bar: pd.Series, history: pd.DataFrame) -> str:
        """
        Takes the current bar and the history up to the current bar.
        Returns "BUY", "SELL", or "HOLD".
        """
        return "HOLD"

class SMAStrategy(BaseStrategy):
    def __init__(self, fast_period: int = 20, slow_period: int = 50):
        self.fast_period = int(fast_period)
        self.slow_period = int(slow_period)
        self.in_position = False

    def generate_signal(self, current_bar: pd.Series, history: pd.DataFrame) -> str:
        if len(history) < self.slow_period:
            return "HOLD"

        # Calculate SMAs
        fast_sma = history['Close'].tail(self.fast_period).mean()
        slow_sma = history['Close'].tail(self.slow_period).mean()

        # Simple crossover logic
        if fast_sma > slow_sma and not self.in_position:
            self.in_position = True
            return "BUY"
        elif fast_sma < slow_sma and self.in_position:
            self.in_position = False
            return "SELL"
            
        return "HOLD"

class RSIStrategy(BaseStrategy):
    def __init__(self, period: int = 14, overbought: int = 70, oversold: int = 30):
        self.period = int(period)
        self.overbought = int(overbought)
        self.oversold = int(oversold)
        self.in_position = False

    def _calculate_rsi(self, data: pd.Series) -> float:
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        
        # Handle division by zero
        if loss.iloc[-1] == 0:
            return 100
            
        rs = gain.iloc[-1] / loss.iloc[-1]
        return 100 - (100 / (1 + rs))

    def generate_signal(self, current_bar: pd.Series, history: pd.DataFrame) -> str:
        if len(history) <= self.period:
            return "HOLD"

        rsi = self._calculate_rsi(history['Close'])
        
        # Avoid generating signal if RSI is NaN
        if pd.isna(rsi):
            return "HOLD"

        if rsi < self.oversold and not self.in_position:
            self.in_position = True
            return "BUY"
        elif rsi > self.overbought and self.in_position:
            self.in_position = False
            return "SELL"
            
        return "HOLD"

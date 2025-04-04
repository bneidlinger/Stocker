# trading/strategies/rsi_oscillator.py
# Relative Strength Index (RSI) Oscillator Strategy
# MODIFIED: Use parameters passed by backtesting.py

from backtesting import Strategy
import pandas as pd


# import talib # Injected by gui/app.py into module scope

class RsiOscillator(Strategy):
    """
    RSI Oscillator Strategy (Requires TA-Lib).
    Parameters `rsi_period`, `upper_bound`, `lower_bound`, `trade_size_percent` are set via Backtest constructor.
    """
    # --- Strategy Parameters ---
    rsi_period = 14  # Default lookback period for RSI calculation
    upper_bound = 70  # Default RSI level considered overbought
    lower_bound = 30  # Default RSI level considered oversold
    trade_size_percent = 0.95  # Default trade size as fraction

    def init(self):
        """Initialize indicators using parameters accessible via self."""
        if 'talib' not in globals():
            raise ImportError("TA-Lib module not injected before initializing RsiOscillator")

        # Ensure parameters have correct types
        rsi_period_int = int(self.rsi_period)

        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=rsi_period_int)
        print(
            f"Initialized RsiOscillator Strategy (Period: {rsi_period_int}, Bounds: {self.lower_bound}/{self.upper_bound})")

    def next(self):
        """Define the trading logic for the next candle."""
        if pd.isna(self.rsi[-1]) or pd.isna(self.rsi[-2]): return

        # Use parameters via self
        if self.rsi[-1] < self.lower_bound and self.rsi[-2] >= self.lower_bound:
            if self.position.is_short: self.position.close()
            if not self.position.is_long:
                self.buy(size=self.trade_size_percent)
        elif self.rsi[-1] > self.upper_bound and self.rsi[-2] <= self.upper_bound:
            if self.position.is_long:
                self.position.close()
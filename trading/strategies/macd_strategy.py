# trading/strategies/macd_strategy.py
# Moving Average Convergence Divergence (MACD) Strategy
# MODIFIED: Use parameters passed by backtesting.py

from backtesting import Strategy
from backtesting.lib import crossover
import pandas as pd


# DEFAULT_TRADE_SIZE_PERCENT import removed, passed as param
# import talib # Injected by gui/app.py into module scope

class MacdStrategy(Strategy):
    """
    Trades based on MACD line crossing the Signal line.
    Requires TA-Lib to be installed.
    Parameters `fast_period`, `slow_period`, `signal_period`, `trade_size_percent` are set via Backtest constructor.
    """
    # --- Strategy Parameters ---
    fast_period = 12
    slow_period = 26
    signal_period = 9
    trade_size_percent = 0.95  # Default trade size as fraction

    def init(self):
        """Initialize MACD indicator."""
        if 'talib' not in globals():
            raise ImportError("TA-Lib module not injected before initializing MacdStrategy")

        # Ensure parameters have correct types
        fast_period_int = int(self.fast_period)
        slow_period_int = int(self.slow_period)
        signal_period_int = int(self.signal_period)

        self.macd, self.macdsignal, self.macdhist = self.I(
            talib.MACD,
            self.data.Close,
            fastperiod=fast_period_int,
            slowperiod=slow_period_int,
            signalperiod=signal_period_int
        )
        print(
            f"Initialized MacdStrategy (Fast: {fast_period_int}, Slow: {slow_period_int}, Signal: {signal_period_int})")

    def next(self):
        """Define trading logic based on MACD crossover."""
        if pd.isna(self.macd[-1]) or pd.isna(self.macdsignal[-1]) or \
                pd.isna(self.macd[-2]) or pd.isna(self.macdsignal[-2]): return

        if crossover(self.macd, self.macdsignal):
            if self.position.is_short: self.position.close()
            if not self.position.is_long:
                self.buy(size=self.trade_size_percent)
        elif crossover(self.macdsignal, self.macd):
            if self.position.is_long:
                self.position.close()
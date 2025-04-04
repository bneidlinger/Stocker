# trading/strategies/sma_cross.py
# Simple Moving Average Crossover Strategy
# MODIFIED: Use parameters passed by backtesting.py

from backtesting import Strategy
from backtesting.lib import crossover
import pandas as pd


# DEFAULT_TRADE_SIZE_PERCENT import removed, passed as param

class SmaCross(Strategy):
    """
    Simple Moving Average Crossover Strategy.
    Parameters `n1`, `n2`, and `trade_size_percent` are set via the Backtest constructor.
    """
    # --- Strategy Parameters ---
    # Define class variables as defaults or placeholders for parameters
    # These will be overridden by values passed to Backtest()
    n1 = 10  # Default short moving average period
    n2 = 30  # Default long moving average period
    trade_size_percent = 0.95  # Default trade size as fraction

    def init(self):
        """Initialize indicators using parameters accessible via self."""
        # Ensure parameters are integers for rolling function
        n1_int = int(self.n1)
        n2_int = int(self.n2)

        self.sma1 = self.I(lambda x: pd.Series(x).rolling(n1_int).mean(), self.data.Close)
        self.sma2 = self.I(lambda x: pd.Series(x).rolling(n2_int).mean(), self.data.Close)
        print(f"Initialized SmaCross Strategy (SMA{n1_int}, SMA{n2_int})")

    def next(self):
        """Define the trading logic for the next candle."""
        # Use the trade size parameter in buy orders
        if crossover(self.sma1, self.sma2):
            if self.position.is_short: self.position.close()
            if not self.position.is_long:
                self.buy(size=self.trade_size_percent)  # Use size from self
        elif crossover(self.sma2, self.sma1):
            if self.position.is_long:
                self.position.close()  # Close entire position
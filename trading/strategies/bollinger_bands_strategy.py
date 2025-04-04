# trading/strategies/bollinger_bands_strategy.py
# Bollinger Bands Mean Reversion Strategy
# MODIFIED: Use parameters passed by backtesting.py

from backtesting import Strategy
import pandas as pd


# DEFAULT_TRADE_SIZE_PERCENT import removed, passed as param
# import talib # Injected by gui/app.py into module scope

class BollingerBandsStrategy(Strategy):
    """
    Bollinger Bands Mean Reversion Strategy (Requires TA-Lib).
    Parameters `bb_period`, `bb_std_dev`, `trade_size_percent` are set via Backtest constructor.
    """
    # --- Strategy Parameters ---
    bb_period = 20  # Default lookback period for Bollinger Bands
    bb_std_dev = 2  # Default number of standard deviations for the bands
    trade_size_percent = 0.95  # Default trade size as fraction

    def init(self):
        """Initialize Bollinger Bands indicator."""
        if 'talib' not in globals():
            raise ImportError("TA-Lib module not injected before initializing BollingerBandsStrategy")

        # Ensure parameters have correct types
        bb_period_int = int(self.bb_period)
        bb_std_dev_float = float(self.bb_std_dev)

        self.upper, self.middle, self.lower = self.I(
            talib.BBANDS,
            self.data.Close,
            timeperiod=bb_period_int,
            nbdevup=bb_std_dev_float,
            nbdevdn=bb_std_dev_float,
            matype=0  # Moving average type: 0=SMA
        )
        print(f"Initialized BollingerBandsStrategy (Period: {bb_period_int}, StdDev: {bb_std_dev_float})")

    def next(self):
        """Define trading logic based on band interaction."""
        if pd.isna(self.lower[-1]) or pd.isna(self.upper[-1]): return
        price = self.data.Close[-1]

        # Use parameters via self
        if price <= self.lower[-1]:
            if self.position.is_short: self.position.close()
            if not self.position.is_long:
                self.buy(size=self.trade_size_percent)
        elif price >= self.upper[-1]:
            if self.position.is_long:
                self.position.close()
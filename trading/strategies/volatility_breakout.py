# trading/strategies/volatility_breakout.py
# Volatility Breakout Strategy using ATR
# MODIFIED: Use parameters passed by backtesting.py

from backtesting import Strategy
import pandas as pd


# import talib # Injected by gui/app.py into module scope

class VolatilityBreakout(Strategy):
    """
    Volatility Breakout Strategy using ATR (Requires TA-Lib).
    Parameters `atr_period`, `ma_period`, `atr_multiplier`, `trade_size_percent` are set via Backtest constructor.
    """
    # --- Strategy Parameters ---
    atr_period = 14  # Default lookback period for ATR
    ma_period = 20  # Default lookback period for the moving average base
    atr_multiplier = 2  # Default multiplier for the ATR threshold
    trade_size_percent = 0.95  # Default trade size as fraction

    def init(self):
        """Initialize indicators using parameters accessible via self."""
        if 'talib' not in globals():
            raise ImportError("TA-Lib module not injected before initializing VolatilityBreakout")

        # Ensure parameters have correct types
        atr_period_int = int(self.atr_period)
        ma_period_int = int(self.ma_period)
        atr_multiplier_float = float(self.atr_multiplier)

        close = self.data.Close;
        high = self.data.High;
        low = self.data.Low

        self.atr = self.I(talib.ATR, high, low, close, timeperiod=atr_period_int)
        self.ma = self.I(talib.SMA, close, timeperiod=ma_period_int)
        print(
            f"Initialized VolatilityBreakout Strategy (MA{ma_period_int}, ATR{atr_period_int}, Multiplier: {atr_multiplier_float})")

    def next(self):
        """Define trading logic based on volatility breakout."""
        price = self.data.Close[-1]
        if pd.isna(self.ma[-1]) or pd.isna(self.atr[-1]): return

        # Use parameters via self
        upper_band = self.ma[-1] + self.atr[-1] * float(self.atr_multiplier)
        lower_band = self.ma[-1]

        if price > upper_band:
            if self.position.is_short: self.position.close()
            if not self.position.is_long:
                self.buy(size=self.trade_size_percent)
        elif price < lower_band:
            if self.position.is_long:
                self.position.close()
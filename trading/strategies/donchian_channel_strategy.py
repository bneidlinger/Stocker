# trading/strategies/donchian_channel_strategy.py
# Donchian Channel Breakout Strategy
# MODIFIED: Use parameters passed by backtesting.py

from backtesting import Strategy
import pandas as pd


# DEFAULT_TRADE_SIZE_PERCENT import removed, passed as param

class DonchianChannelStrategy(Strategy):
    """
    Trades based on breakouts of the Donchian Channel.
    Parameters `n_high`, `n_low`, `trade_size_percent` are set via Backtest constructor.
    """
    # --- Strategy Parameters ---
    n_high = 20  # Default lookback period for highest high
    n_low = 20  # Default lookback period for lowest low
    trade_size_percent = 0.95  # Default trade size as fraction

    def init(self):
        """Initialize Donchian Channel indicators."""
        # Ensure parameters are integers
        n_high_int = int(self.n_high)
        n_low_int = int(self.n_low)

        high = self.data.High;
        low = self.data.Low
        self.donchian_high = self.I(lambda H=high: pd.Series(H).rolling(n_high_int).max().shift(1), name="DonchianHigh")
        self.donchian_low = self.I(lambda L=low: pd.Series(L).rolling(n_low_int).min().shift(1), name="DonchianLow")
        print(f"Initialized DonchianChannelStrategy (High: {n_high_int}, Low: {n_low_int})")

    def next(self):
        """Define trading logic based on channel breakouts."""
        price = self.data.Close[-1]
        if pd.isna(self.donchian_high[-1]) or pd.isna(self.donchian_low[-1]): return

        # Use parameters via self
        if price > self.donchian_high[-1]:
            if self.position.is_short: self.position.close()
            if not self.position.is_long:
                self.buy(size=self.trade_size_percent)
        elif price < self.donchian_low[-1]:
            if self.position.is_long:
                self.position.close()
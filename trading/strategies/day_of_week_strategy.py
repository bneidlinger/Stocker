# trading/strategies/day_of_week_strategy.py
# Strategy based on simple Day of Week effect
# MODIFIED: Use parameters passed by backtesting.py

from backtesting import Strategy
import pandas as pd


# DEFAULT_TRADE_SIZE_PERCENT import removed, passed as param

class DayOfWeekStrategy(Strategy):
    """
    A simple strategy that trades based on the day of the week.
    Parameters `buy_day`, `sell_day`, `trade_size_percent` are set via Backtest constructor.
    """
    # --- Strategy Parameters ---
    buy_day = 0  # Default: Monday = 0
    sell_day = 4  # Default: Friday = 4
    trade_size_percent = 0.95  # Default trade size as fraction

    def init(self):
        """Initialize the strategy."""
        print("Initialized DayOfWeekStrategy")
        # Use self to access parameters
        print(f"Buy Day: {int(self.buy_day)}, Sell Day: {int(self.sell_day)}")

    def next(self):
        """Define trading logic based on the day of the week."""
        if not isinstance(self.data.index[-1], pd.Timestamp):
            print("Warning: Data index is not Timestamp, skipping DayOfWeekStrategy logic.")
            return

            # Use parameters via self, ensure type conversion
        current_day_of_week = self.data.index[-1].dayofweek
        buy_d = int(self.buy_day)
        sell_d = int(self.sell_day)

        if current_day_of_week == buy_d:
            if self.position.is_short: self.position.close()
            if not self.position.is_long:
                self.buy(size=self.trade_size_percent)
        elif current_day_of_week == sell_d:
            if self.position.is_long:
                self.position.close()
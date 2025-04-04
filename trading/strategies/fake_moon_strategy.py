# trading/strategies/fake_moon_strategy.py
# Conceptual strategy based on day of the month (placeholder for actual lunar phase)
# MODIFIED: Use parameters passed by backtesting.py

from backtesting import Strategy
import pandas as pd


# DEFAULT_TRADE_SIZE_PERCENT import removed, passed as param

class FakeMoonStrategy(Strategy):
    """
    Conceptual strategy based on day of the month (Placeholder).
    Parameters `buy_day_start`, `buy_day_end`, `sell_day_start`, `sell_day_end`, `trade_size_percent` are set via Backtest constructor.
    """
    # --- Strategy Parameters ---
    buy_day_start = 1
    buy_day_end = 5
    sell_day_start = 14
    sell_day_end = 18
    trade_size_percent = 0.95  # Default trade size as fraction

    def init(self):
        """Initialize the strategy."""
        print("Initialized FakeMoonStrategy (Placeholder - Day of Month)")
        # Use self to access parameters
        print(
            f"Buy Days: {int(self.buy_day_start)}-{int(self.buy_day_end)}, Sell Days: {int(self.sell_day_start)}-{int(self.sell_day_end)}")

    def next(self):
        """Define the trading logic based on the day of the month."""
        if not isinstance(self.data.index[-1], pd.Timestamp):
            print("Warning: Data index is not Timestamp, skipping FakeMoonStrategy logic.")
            return
        current_date = self.data.index[-1]
        day_of_month = current_date.day

        # Use parameters via self, ensure type conversion
        buy_start = int(self.buy_day_start)
        buy_end = int(self.buy_day_end)
        sell_start = int(self.sell_day_start)
        sell_end = int(self.sell_day_end)

        if buy_start <= day_of_month <= buy_end:
            if self.position.is_short: self.position.close()
            if not self.position.is_long:
                self.buy(size=self.trade_size_percent)
        elif sell_start <= day_of_month <= sell_end:
            if self.position.is_long:
                self.position.close()
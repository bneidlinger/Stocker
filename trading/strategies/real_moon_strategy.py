# trading/strategies/real_moon_strategy.py
# Strategy using actual moon phase calculations via ephem
# MODIFIED: Use parameters passed by backtesting.py

from backtesting import Strategy
# import ephem # Injected by gui/app.py into module scope
import datetime
import pandas as pd


# DEFAULT_TRADE_SIZE_PERCENT import removed, passed as param

class RealMoonStrategy(Strategy):
    """
    Trades based on calculated moon phases using the ephem library.
    Observer location is set via class attributes before running.
    Parameters `days_after_new_moon_buy`, `buy_window_days`, `days_after_full_moon_sell`, `sell_window_days`, `trade_size_percent` are set via Backtest constructor.
    """
    # --- Strategy Parameters ---
    days_after_new_moon_buy = 2
    buy_window_days = 3
    days_after_full_moon_sell = 2
    sell_window_days = 3
    trade_size_percent = 0.95  # Default trade size as fraction

    # --- Observer Location (Set externally before running via class attributes) ---
    OBSERVER_LAT = None
    OBSERVER_LON = None
    OBSERVER_ELEV = None

    def init(self):
        """Initialize the ephem observer."""
        if 'ephem' not in globals():
            raise ImportError("Ephem module not injected before initializing RealMoonStrategy")
        if self.OBSERVER_LAT is None or self.OBSERVER_LON is None:
            raise ValueError("Observer location not set for RealMoonStrategy")

        self.observer = ephem.Observer()
        self.observer.lat = str(self.OBSERVER_LAT)
        self.observer.lon = str(self.OBSERVER_LON)
        self.observer.elevation = float(self.OBSERVER_ELEV) if self.OBSERVER_ELEV is not None else 0

        print(f"Initialized RealMoonStrategy (Observer: Lat {self.observer.lat}, Lon {self.observer.lon})")
        # Use self to access parameters
        print(
            f"Buy: {int(self.days_after_new_moon_buy)}-{int(self.days_after_new_moon_buy) + int(self.buy_window_days)} days after New Moon")
        print(
            f"Sell: {int(self.days_after_full_moon_sell)}-{int(self.days_after_full_moon_sell) + int(self.sell_window_days)} days after Full Moon")

    def next(self):
        """Define trading logic based on moon phase."""
        if not isinstance(self.data.index[-1], pd.Timestamp):
            print("Warning: Data index is not Timestamp, skipping RealMoonStrategy logic.")
            return
        current_date = self.data.index[-1].date()
        self.observer.date = current_date

        try:
            prev_new = ephem.previous_new_moon(current_date).datetime().date()
            approx_prev_full = prev_new + datetime.timedelta(days=14.765)
            days_since_new = (current_date - prev_new).days
            days_since_full = (current_date - approx_prev_full).days if approx_prev_full < current_date else 999

            # Use parameters via self, ensure type conversion
            buy_trigger_day = int(self.days_after_new_moon_buy)
            buy_window = int(self.buy_window_days)
            sell_trigger_day = int(self.days_after_full_moon_sell)
            sell_window = int(self.sell_window_days)

            # --- Buy Logic ---
            if buy_trigger_day <= days_since_new < (buy_trigger_day + buy_window):
                if self.position.is_short: self.position.close()
                if not self.position.is_long:
                    self.buy(size=self.trade_size_percent)

                    # --- Sell Logic ---
            elif sell_trigger_day <= days_since_full < (sell_trigger_day + sell_window):
                if self.position.is_long:
                    self.position.close()

        except Exception as e:
            print(f"Error calculating moon phase for {current_date}: {type(e).__name__} - {e}")
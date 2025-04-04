# trading/strategies/ichimoku_strategy.py
# Ichimoku Cloud Strategy (using pandas calculations)
# MODIFIED: Use parameters passed by backtesting.py

from backtesting import Strategy
import pandas as pd


# DEFAULT_TRADE_SIZE_PERCENT import removed, passed as param

class IchimokuStrategy(Strategy):
    """
    Trades based on the Ichimoku Kinko Hyo indicator.
    Parameters `tenkan_period`, `kijun_period`, `senkou_b_period`, `chikou_period`,
    `senkou_displacement`, `trade_size_percent` are set via Backtest constructor.
    Calculations done using pandas.
    """
    # --- Strategy Parameters ---
    tenkan_period = 9
    kijun_period = 26
    senkou_b_period = 52
    chikou_period = 26
    senkou_displacement = 26
    trade_size_percent = 0.95  # Default trade size as fraction

    def init(self):
        """Initialize Ichimoku indicators using parameters accessible via self."""

        # Ensure parameters have correct types
        tenkan_p = int(self.tenkan_period)
        kijun_p = int(self.kijun_period)
        senkou_b_p = int(self.senkou_b_period)
        senkou_disp = int(self.senkou_displacement)

        high = self.data.High;
        low = self.data.Low;
        close = self.data.Close

        self.tenkan = self.I(
            lambda H=high, L=low: (pd.Series(H).rolling(tenkan_p).max() + pd.Series(L).rolling(tenkan_p).min()) / 2,
            name="Tenkan")
        self.kijun = self.I(
            lambda H=high, L=low: (pd.Series(H).rolling(kijun_p).max() + pd.Series(L).rolling(kijun_p).min()) / 2,
            name="Kijun")
        senkou_a_intermediate = self.I(lambda: (self.tenkan + self.kijun) / 2, name="SenkouA_Intermediate")
        self.senkou_a = self.I(lambda: pd.Series(senkou_a_intermediate).shift(senkou_disp), name="SenkouA")
        senkou_b_intermediate = self.I(
            lambda H=high, L=low: (pd.Series(H).rolling(senkou_b_p).max() + pd.Series(L).rolling(senkou_b_p).min()) / 2,
            name="SenkouB_Intermediate")
        self.senkou_b = self.I(lambda: pd.Series(senkou_b_intermediate).shift(senkou_disp), name="SenkouB")

        print(
            f"Initialized IchimokuStrategy (Periods: T={tenkan_p}, K={kijun_p}, SB={senkou_b_p}, Displacement={senkou_disp})")

    def next(self):
        """Define trading logic based on Ichimoku signals."""

        # Ensure parameters have correct types for comparison
        chikou_p = int(self.chikou_period)
        senkou_disp = int(self.senkou_displacement)
        kijun_p = int(self.kijun_period)
        senkou_b_p = int(self.senkou_b_period)

        if len(self.data.Close) <= max(kijun_p, senkou_b_p) + senkou_disp: return
        if len(self.data.Close) <= chikou_p: return

        price = self.data.Close[-1]
        try:
            tenkan = self.tenkan[-1];
            kijun = self.kijun[-1]
            senkou_a = self.senkou_a[-1];
            senkou_b = self.senkou_b[-1]
            if pd.isna(tenkan) or pd.isna(kijun) or pd.isna(senkou_a) or pd.isna(senkou_b): return
        except IndexError:
            return

        price_above_kumo = price > max(senkou_a, senkou_b)
        price_below_kumo = price < min(senkou_a, senkou_b)

        if len(self.tenkan) < 2 or len(self.kijun) < 2: return
        if pd.isna(self.tenkan[-2]) or pd.isna(self.kijun[-2]): return
        tk_cross_bullish = self.tenkan[-2] <= self.kijun[-2] and tenkan > kijun
        tk_cross_bearish = self.tenkan[-2] >= self.kijun[-2] and tenkan < kijun

        try:
            price_chikou_periods_ago = self.data.Close[-1 - chikou_p]
            chikou_above_price_history = price > price_chikou_periods_ago
            chikou_below_price_history = price < price_chikou_periods_ago
        except IndexError:
            return

        if price_above_kumo and tk_cross_bullish and chikou_above_price_history:
            if self.position.is_short: self.position.close()
            if not self.position.is_long:
                self.buy(size=self.trade_size_percent)
        elif price_below_kumo and tk_cross_bearish and chikou_below_price_history:
            if self.position.is_long:
                self.position.close()
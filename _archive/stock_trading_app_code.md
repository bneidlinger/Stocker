# Stock Trading App Code Export

## main.py

```python
# main.py
# Entry point for the application

import customtkinter as ctk
from gui.app import App
import os
from dotenv import load_dotenv
from config import ML_MODEL_DIR
from data.data_source_factory import DataSourceFactory

# Load environment variables (optional, good practice for API keys)
load_dotenv()

# --- Theming ---
# Modes: "System" (standard), "Dark", "Light"
ctk.set_appearance_mode("Dark")
# Themes: "blue" (standard), "green", "dark-blue"
# We can create custom themes later, for now let's use dark-blue
# and override colors for the Miami Vice / Retro Fallout feel.
ctk.set_default_color_theme("dark-blue")

# --- Ensure Directories Exist ---
# Create models directory if it doesn't exist
os.makedirs(ML_MODEL_DIR, exist_ok=True)

# --- Main Application ---
if __name__ == "__main__":
    # Initialize the main application window
    app = App()
    # Start the Tkinter event loop
    app.mainloop()
```

## config.py

```python
# config.py
# Configuration settings for the application

# List of stock symbols to track/analyze
# AMZN, NVDA, META, PLTR + AAPL, TSLA
SYMBOLS = ["AMZN", "NVDA", "META", "PLTR", "AAPL", "TSLA"]

# Default time period for fetching historical data (e.g., "1y", "5y", "max")
DEFAULT_DATA_PERIOD = "5y" # Fetch a longer period initially

# Default interval for data (e.g., "1d", "1wk", "1h")
DEFAULT_DATA_INTERVAL = "1d"

# --- Backtesting Defaults ---
DEFAULT_CASH = 10000
DEFAULT_COMMISSION = 0.001 # 0.1% commission per trade
DEFAULT_TRADE_SIZE_PERCENT = 95 # Default trade size as percentage (e.g., 95 for 95%)

# --- Recommendation Engine Parameters ---
REC_SMA_SHORT = 20
REC_SMA_LONG = 50
REC_RSI_PERIOD = 14
REC_RSI_BUY = 55 # RSI threshold suggesting potential buy strength
REC_RSI_SELL = 45 # RSI threshold suggesting potential sell weakness
REC_MACD_FAST = 12
REC_MACD_SLOW = 26
REC_MACD_SIG = 9
REC_BBANDS_PERIOD = 20
REC_BBANDS_STDDEV = 2.0
REC_ADX_PERIOD = 14
REC_ADX_THRESHOLD = 25

# --- Alpha Vantage Configuration ---
ALPHA_VANTAGE_API_KEY = ""  # Your API key here
USE_ALPHA_VANTAGE = False   # Default to False until configured
ALPHA_VANTAGE_CALL_LIMIT_PER_MINUTE = 5  # Free tier limit
ALPHA_VANTAGE_CALL_LIMIT_PER_DAY = 500   # Free tier limit

# --- ML Configuration ---
ML_MODEL_DIR = 'data/models'
ML_DEFAULT_MODEL = 'random_forest'
ML_DEFAULT_HORIZON = 5
ML_TRAIN_TEST_SPLIT = 0.2
ML_ENABLE_HYBRID = True       # Enable hybrid ML + Technical Analysis recommendations
ML_HYBRID_WEIGHT = 0.5        # Default weight for ML vs TA (0.0 = all TA, 1.0 = all ML)

# --- Location for Astronomical Calculations (Ephem) ---
# Used for RealMoonStrategy - Coordinates for Apple Valley, MN
OBSERVER_LAT = '44.73' # Latitude
OBSERVER_LON = '-93.22' # Longitude
OBSERVER_ELEV = 280 # Elevation in meters (approx)

# --- Theme Colors (Miami Vice / Retro Fallout Inspired) ---
# Using hex codes for more control
COLOR_BACKGROUND = "#1a1a2e" # Dark blue/purple
COLOR_FOREGROUND = "#e0fbfc" # Light cyan/near white
COLOR_BUTTON = "#ff69b4"     # Neon Pink
COLOR_BUTTON_HOVER = "#ff85c1" # Lighter Pink
COLOR_DROPDOWN_FG = "#e0fbfc"
COLOR_DROPDOWN_BG = "#2a2a4e" # Slightly lighter dark blue
COLOR_DROPDOWN_BUTTON = "#ff69b4"
COLOR_DROPDOWN_BUTTON_HOVER = "#ff85c1"
COLOR_TEXTBOX_FG = "#e0fbfc"
COLOR_TEXTBOX_BG = "#161625" # Even darker for console feel
COLOR_ACCENT = "#39ff14" # Neon Green (optional accent)
COLOR_CHART_BG = "#161625" # Match textbox background
COLOR_CHART_LINE = "#ff69b4" # Pink line
COLOR_CHART_AXES = "#e0fbfc" # Cyan axes/ticks

# Added colors for positive/negative results
COLOR_POSITIVE = "#39ff14" # Neon Green (BUY)
COLOR_NEGATIVE = "#ff4d6d" # Neon Red/Pink variation (SELL)
COLOR_NEUTRAL = COLOR_FOREGROUND # Default color for HOLD
COLOR_WEAK_POSITIVE = "#00f5d4" # Teal/Cyan (Weak Buy)
COLOR_WEAK_NEGATIVE = "#f77f00" # Orange (Weak Sell)

# Secondary Button Colors (for Chart Period, Info)
COLOR_SECONDARY_BUTTON = "#007f7f" # Dark Cyan/Teal
COLOR_SECONDARY_BUTTON_HOVER = "#00aaaa" # Lighter Cyan/Teal

# --- LED Colors ---
# Slightly less saturated ON colors, distinct OFF colors
COLOR_LED_BORDER_OFF = "#10101a" # Used in app.py WornLED fix
COLOR_LED_PWR_ON = "#E6455E" # Slightly less intense Red/Pink
COLOR_LED_CPU_ON = "#2FC41F" # Slightly less intense Green
COLOR_LED_DATA_ON = "#E1E100" # Slightly less intense Yellow
COLOR_LED_COM_ON = "#00C2C2" # Slightly less intense Cyan
# ERR LED uses PWR colors

# --- Recommendation Matrix Colors --- ADD THESE LINES ---
COLOR_REC_SELL = "#FF4136"       # Red
COLOR_REC_WEAK_SELL = "#FF851B"  # Orange
COLOR_REC_HOLD = "#AAAAAA"       # Gray
COLOR_REC_WEAK_BUY = "#AFFFAD"   # Light Green
COLOR_REC_BUY = "#2ECC40"        # Green
COLOR_REC_DEFAULT = "#00FF00"    # Default matrix green
# --- END ADDED LINES ---

# --- ML LED Colors ---
COLOR_LED_ML_ON = "#7D26CD"      # Purple for ML activity
COLOR_LED_ML_BORDER = "#10101a"  # Same border as other LEDs

# --- ML Visualization Colors ---
COLOR_ML_FEATURE_BAR = "#7D26CD"  # Purple for feature importance bars
COLOR_ML_PREDICTION_UP = "#2ECC40"  # Green for up predictions
COLOR_ML_PREDICTION_DOWN = "#FF4136"  # Red for down predictions
COLOR_ML_CONFIDENCE_HIGH = "#39ff14"  # Neon Green for high confidence
COLOR_ML_CONFIDENCE_MED = "#FFDC00"   # Yellow for medium confidence
COLOR_ML_CONFIDENCE_LOW = "#FF851B"   # Orange for low confidence

# --- Fonts ---
# Using a common monospace font for the console feel
FONT_FAMILY_MONO = "Consolas" # Or "Courier New" or others available
FONT_SIZE_NORMAL = 12
FONT_SIZE_LARGE = 16
FONT_SIZE_TEXTBOX = 14 # Added specific font size for the output textbox
FONT_SIZE_LED = 10 # Smaller font for LED labels
# FONT_SIZE_RECOMMENDATION = 18 # No longer needed for label
```

## data/data_fetcher.py

```python
# data/data_fetcher.py
# Handles fetching financial data

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta


class DataFetcher:
    """
    Class responsible for fetching historical stock data using yfinance.
    """

    def __init__(self):
        """Initializes the DataFetcher."""
        # Could add initialization for other data sources here later
        pass

    def get_historical_data(self, symbol: str, period: str = "5y", interval: str = "1d") -> pd.DataFrame | None:
        """
        Fetches historical stock data for a given symbol.

        Args:
            symbol (str): The stock ticker symbol (e.g., "AAPL").
            period (str): The period for which to fetch data
                          (e.g., "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max").
            interval (str): The data interval
                            (e.g., "1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo").

        Returns:
            pd.DataFrame | None: A pandas DataFrame containing the OHLCV data,
                                 or None if fetching fails.
        """
        print(f"Fetching data for {symbol} | Period: {period} | Interval: {interval}")
        try:
            ticker = yf.Ticker(symbol)
            # Download historical data
            # Note: yfinance might adjust start/end dates based on interval and period
            history = ticker.history(period=period, interval=interval)

            if history.empty:
                print(f"Warning: No data returned for {symbol} with period={period}, interval={interval}")
                return None

            # Basic data cleaning (yfinance usually provides clean data)
            history.dropna(inplace=True)

            # Ensure standard column names (lowercase OHLCV)
            history.columns = history.columns.str.lower()

            # Rename 'adj close' to 'close' if 'close' isn't present - needed for plotting
            # Backtesting libraries often prefer adjusted close, but we need 'close' for plotting standard price
            # If 'adj close' exists, let's keep it, but ensure 'close' is also present.
            # yfinance usually provides both 'Close' and 'Adj Close'.
            if 'close' not in history.columns and 'adj close' in history.columns:
                history.rename(columns={'adj close': 'close'}, inplace=True)
            elif 'close' not in history.columns:
                print(f"Warning: 'close' column missing and could not be derived for {symbol}.")
                # Decide handling: return None or try to proceed without 'close' if possible?
                # Returning None is safer if 'close' is essential downstream.
                # return None
                # For now, let's proceed but be aware plotting might fail.

            # Ensure required columns are present for many backtesting libraries
            required_cols = ['open', 'high', 'low', 'close', 'volume']
            if not all(col in history.columns for col in required_cols):
                print(
                    f"Warning: Missing required OHLCV columns in data for {symbol}. Found: {history.columns.tolist()}")
                # Decide how to handle: return None, fill missing, or raise error
                # For now, let's return what we have but log the warning.

            print(f"Successfully fetched {len(history)} data points for {symbol}")
            return history

        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None

    def get_current_price(self, symbol: str) -> float | None:
        """
        Fetches the last known price for a symbol.
        Note: This is often delayed. Real-time requires different APIs/WebSockets.

        Args:
            symbol (str): The stock ticker symbol.

        Returns:
            float | None: The current price, or None if fetching fails.
        """
        try:
            ticker = yf.Ticker(symbol)
            # Use 'day_high' and 'day_low' to get recent info, or 'fast_info'
            # 'regularMarketPrice' often gives a good recent price
            data = ticker.fast_info
            price = data.get('last_price')  # Or 'regularMarketPrice'
            if price:
                # Successfully got price via fast_info
                return float(price)
            else:
                # Log the failure to get fast_info price here (goes to console) - REMOVED/COMMENTED OUT
                # print(f"Could not retrieve current price for {symbol} from fast_info. Attempting fallback...")

                # Fallback: get last closing price from recent history
                hist = ticker.history(period="2d")  # Get 2 days to ensure we get last close
                if not hist.empty:
                    # Ensure 'Close' column exists before accessing
                    fallback_price = None
                    if 'Close' in hist.columns:
                        fallback_price = hist['Close'].iloc[-1]
                    elif 'close' in hist.columns:  # check lowercase too
                        fallback_price = hist['close'].iloc[-1]

                    if fallback_price is not None:
                        # Keep this log for debugging fallback success
                        print(f"Fallback successful: Using last closing price for {symbol}: {fallback_price}")
                        return fallback_price
                    else:
                        # Keep this log for debugging fallback failure
                        print(f"Fallback failed: 'Close' column not found in fallback history for {symbol}.")
                        return None
                else:
                    # Keep this log for debugging fallback failure
                    print(f"Fallback failed: Could not retrieve history for {symbol}.")
                    return None
        except Exception as e:
            print(f"Error fetching current price for {symbol}: {e}")
            return None
```

## trading/backtester.py

```python
# trading/backtester.py
# Handles running backtests using the backtesting.py library
# MODIFIED: Reinstate workaround using bt._results._trades

from backtesting import Backtest
import pandas as pd

# Dictionary mapping column names expected by backtesting.py to potential lowercase versions
COLUMN_MAPPING = {
    'Open': 'open',
    'High': 'high',
    'Low': 'low',
    'Close': 'close',
    'Volume': 'volume'
}


# Accept **strategy_params again
def run_backtest(strategy_class, data: pd.DataFrame, cash: int = 10000, commission: float = 0.001, **strategy_params):
    """
    Runs a backtest for a given strategy and data.
    Strategy-specific parameters are passed via **strategy_params to bt.run().

    Args:
        strategy_class: The strategy class (inheriting from backtesting.Strategy).
        data (pd.DataFrame): DataFrame with historical OHLCV data (lowercase columns).
        cash (int): Initial cash for the backtest.
        commission (float): Commission rate per trade (e.g., 0.001 for 0.1%).
        **strategy_params: Keyword arguments (parameters) to pass to the strategy for this run.

    Returns:
        tuple: (stats, backtest_object)
               stats (pd.Series): Backtesting statistics including '_trades'.
               backtest_object (Backtest): The Backtest instance for potential plotting.
               Returns (None, None) if backtest fails.
    """
    if data is None or data.empty:
        print("Error: Cannot run backtest with empty data.")
        return None, None
    required_lowercase = list(COLUMN_MAPPING.values())
    if not all(col in data.columns for col in required_lowercase):
        print(
            f"Error: Data missing required columns for backtesting. Need: {required_lowercase}, Found: {data.columns.tolist()}")
        return None, None
    backtest_data = data.copy()
    rename_dict = {v: k for k, v in COLUMN_MAPPING.items()}
    backtest_data.rename(columns=rename_dict, inplace=True)
    required_uppercase = list(COLUMN_MAPPING.keys())
    if not all(col in backtest_data.columns for col in required_uppercase):
        print(f"Error: Column renaming failed. Need: {required_uppercase}, Found: {backtest_data.columns.tolist()}")
        return None, None

    print(f"\n--- Running Backtest ---")
    print(f"Strategy: {strategy_class.__name__}")
    print(f"Initial Cash: {cash:,.2f}")
    print(f"Commission: {commission:.4f}")
    # Print strategy parameters being used
    print(f"Parameters: {strategy_params}")

    try:
        # Initialize Backtest WITHOUT passing strategy_params to constructor
        bt = Backtest(backtest_data, strategy_class, cash=cash, commission=commission)

        # Run backtest WITH strategy_params BUT WITHOUT return_trades argument
        stats = bt.run(**strategy_params)

        # WORKAROUND REINSTATED: Manually add the trades DataFrame to the stats Series
        # Accessing internal _results._trades attribute, necessary due to run() conflict
        try:
            # Attempt to access trades via the internal attribute (note underscore on _trades)
            stats['_trades'] = bt._results._trades
            print("Successfully retrieved trades via bt._results._trades")
        except AttributeError:
            print("Warning: Could not access bt._results._trades. Trade list might be missing.")
            # Ensure the '_trades' key exists even if empty
            stats['_trades'] = pd.DataFrame()

        print("--- Backtest Complete ---")
        return stats, bt
    except Exception as e:
        print(f"Error during backtest execution: {e}")
        # import traceback # Uncomment for full traceback
        # traceback.print_exc()
        return None, None
```

## trading/strategies/sma_cross.py

```python
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
```

## trading/strategies/rsi_oscillator.py

```python
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
```

## trading/strategies/volatility_breakout.py

```python
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
```

## trading/strategies/fake_moon_strategy.py

```python
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
```

## trading/strategies/real_moon_strategy.py

```python
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
```

## trading/strategies/macd_strategy.py

```python
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
```

## trading/strategies/bollinger_bands_strategy.py

```python
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
```

## trading/strategies/ichimoku_strategy.py

```python
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
```

## trading/strategies/donchian_channel_strategy.py

```python
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
```

## trading/strategies/day_of_week_strategy.py

```python
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
```

## trading/ml/__init__.py

```python
# trading/ml/__init__.py
# ML module for enhanced trade recommendations
```

## trading/ml/features.py

```python
# trading/ml/features.py
# Feature engineering for ML stock prediction

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Union, Optional


class FeatureEngineer:
    """Class responsible for generating features from price data for ML models."""

    def __init__(self):
        """Initialize the feature engineer."""
        pass

    @staticmethod
    def add_price_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        Add basic price-derived features to the dataframe.

        Args:
            df: DataFrame with at least OHLCV data

        Returns:
            DataFrame with additional features
        """
        if df is None or df.empty:
            return df

        # Create a copy to avoid modifying the original
        result = df.copy()

        # Ensure we have the necessary columns
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        missing_cols = [col for col in required_cols if col not in result.columns]
        if missing_cols:
            print(f"Warning: Missing columns {missing_cols} for feature engineering")
            # Try to work with what we have

        # Calculate returns if 'close' is available
        if 'close' in result.columns:
            # Daily return
            result['return_1d'] = result['close'].pct_change()

            # Logarithmic return
            result['log_return'] = np.log(result['close']).diff()

            # N-day returns (5, 10, 20)
            for n in [5, 10, 20]:
                if len(result) > n:
                    result[f'return_{n}d'] = result['close'].pct_change(n)

        # High-Low range
        if all(col in result.columns for col in ['high', 'low']):
            result['hl_range'] = (result['high'] - result['low']) / result['low']

        # Open-Close range
        if all(col in result.columns for col in ['open', 'close']):
            result['oc_range'] = (result['close'] - result['open']) / result['open']

        # Volume features if available
        if 'volume' in result.columns:
            # Log volume
            result['log_volume'] = np.log(result['volume'] + 1)  # +1 to handle zeros

            # Volume change
            result['volume_change'] = result['volume'].pct_change()

            # Relative volume (compared to 20-day average)
            if len(result) > 20:
                result['relative_volume'] = result['volume'] / result['volume'].rolling(20).mean()

        return result

    @staticmethod
    def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        Add technical indicators as features to the dataframe.
        Uses pandas built-in functions to avoid TA-Lib dependency at this step.

        Args:
            df: DataFrame with at least 'close' price data

        Returns:
            DataFrame with technical indicators added
        """
        if df is None or df.empty or 'close' not in df.columns:
            return df

        result = df.copy()
        close = result['close']

        # Simple Moving Averages (SMA)
        for period in [5, 10, 20, 50, 200]:
            if len(result) > period:
                result[f'sma_{period}'] = close.rolling(window=period).mean()

                # Distance from SMA (%)
                result[f'close_to_sma_{period}'] = (close / result[f'sma_{period}'] - 1) * 100

        # Exponential Moving Averages (EMA)
        for period in [5, 10, 20, 50, 200]:
            if len(result) > period:
                result[f'ema_{period}'] = close.ewm(span=period, adjust=False).mean()

                # Distance from EMA (%)
                result[f'close_to_ema_{period}'] = (close / result[f'ema_{period}'] - 1) * 100

        # Bollinger Bands (20, 2)
        if len(result) > 20:
            ma = close.rolling(window=20).mean()
            std = close.rolling(window=20).std()
            result['bb_upper'] = ma + (std * 2)
            result['bb_lower'] = ma - (std * 2)
            result['bb_width'] = (result['bb_upper'] - result['bb_lower']) / ma
            # Position within BB (0 = lower band, 1 = upper band)
            result['bb_pos'] = (close - result['bb_lower']) / (result['bb_upper'] - result['bb_lower'])

        # RSI (using Simple Method with pandas)
        if len(result) > 14:
            delta = close.diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(window=14).mean()
            avg_loss = loss.rolling(window=14).mean()
            rs = avg_gain / avg_loss
            result['rsi_14'] = 100 - (100 / (1 + rs))

        # MACD (12, 26, 9)
        if len(result) > 26:
            ema12 = close.ewm(span=12, adjust=False).mean()
            ema26 = close.ewm(span=26, adjust=False).mean()
            result['macd'] = ema12 - ema26
            result['macd_signal'] = result['macd'].ewm(span=9, adjust=False).mean()
            result['macd_hist'] = result['macd'] - result['macd_signal']

        return result

    @staticmethod
    def add_date_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        Add date-related features for time series modeling.

        Args:
            df: DataFrame with DatetimeIndex

        Returns:
            DataFrame with additional date features
        """
        if df is None or df.empty:
            return df

        result = df.copy()

        # Extract date components
        result['day_of_week'] = result.index.dayofweek
        result['day_of_month'] = result.index.day
        result['month'] = result.index.month
        result['year'] = result.index.year
        result['quarter'] = result.index.quarter

        # Is month start/end
        result['is_month_start'] = result.index.is_month_start.astype(int)
        result['is_month_end'] = result.index.is_month_end.astype(int)

        # Is quarter start/end
        result['is_quarter_start'] = result.index.is_quarter_start.astype(int)
        result['is_quarter_end'] = result.index.is_quarter_end.astype(int)

        # Is year start/end
        result['is_year_start'] = result.index.is_year_start.astype(int)
        result['is_year_end'] = result.index.is_year_end.astype(int)

        # Is month start/end
        result['is_month_start'] = result.index.is_month_start.astype(int)
        result['is_month_end'] = result.index.is_month_end.astype(int)

        return result

    @staticmethod
    def engineer_features(df: pd.DataFrame, with_date_features: bool = True) -> pd.DataFrame:
        """
        Complete feature engineering process.

        Args:
            df: DataFrame with at least OHLCV data
            with_date_features: Whether to include date-based features

        Returns:
            DataFrame with all engineered features
        """
        if df is None or df.empty:
            return df

        print("Preparing data: Engineering features...")  # Added print

        # Chain all feature engineering steps
        result = FeatureEngineer.add_price_features(df)
        result = FeatureEngineer.add_technical_indicators(result)

        # Add date features if requested and index is DatetimeIndex
        if with_date_features and isinstance(result.index, pd.DatetimeIndex):
            result = FeatureEngineer.add_date_features(result)

        # --- FIX FutureWarning HERE ---
        # Forward fill NaN values created by lagging features
        # result = result.fillna(method='ffill') # Deprecated
        result = result.ffill()  # Use this instead
        # --- END FIX ---

        # Drop any remaining NaN rows (usually at the beginning)
        result = result.dropna()

        return result

    @staticmethod
    def get_target_variable(df: pd.DataFrame, horizon: int = 5, threshold: float = 0.01) -> pd.DataFrame:
        """
        Create target variable for ML classification or regression.

        Args:
            df: DataFrame with 'close' price data
            horizon: Prediction horizon in days
            threshold: Price change threshold for classification (e.g., 0.01 for 1%)

        Returns:
            DataFrame with target variables added
        """
        if df is None or df.empty or 'close' not in df.columns:
            return df

        result = df.copy()

        # Future returns at specified horizon
        # Ensure we shift correctly; shift(-horizon) looks into the future
        result[f'future_return_{horizon}d'] = result['close'].pct_change(periods=horizon).shift(-horizon)

        # Classification target: 1 for up, 0 for sideways, -1 for down
        # Uses threshold to determine if change is significant
        result[f'target_direction_{horizon}d'] = 0  # Default to neutral (0)

        # Find indices where future return exceeds positive threshold
        up_indices = result[f'future_return_{horizon}d'] > threshold
        result.loc[up_indices, f'target_direction_{horizon}d'] = 1

        # Find indices where future return is below negative threshold
        down_indices = result[f'future_return_{horizon}d'] < -threshold
        result.loc[down_indices, f'target_direction_{horizon}d'] = -1

        # Binary classification: 1 for up, 0 for down/neutral (ignoring threshold for this simple binary)
        # result[f'target_binary_{horizon}d'] = (result[f'future_return_{horizon}d'] > 0).astype(int)
        # Let's keep the focus on the 3-class target for now.

        # Drop the future return column as it introduces lookahead bias if kept during training on features
        # result = result.drop(columns=[f'future_return_{horizon}d'])
        # --> Correction: Don't drop it here. It's needed for regression and excluded during feature prep anyway.

        return result

    @staticmethod
    def prepare_ml_data(df: pd.DataFrame, target_col: str, test_size: float = 0.2,
                        exclude_cols: Optional[List[str]] = None) -> Tuple[
        np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Prepare data for ML modeling, splitting into train/test sets.

        Args:
            df: DataFrame with features and target
            target_col: Target column name
            test_size: Proportion of data to use for testing
            exclude_cols: List of columns to exclude from features

        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        # Validate inputs
        if df is None or df.empty or target_col not in df.columns:
            raise ValueError(f"Invalid dataframe or target column '{target_col}' not found")

        # Remove NaN values from dataset
        clean_df = df.dropna()
        if len(clean_df) == 0:
            raise ValueError("No data left after removing NaN values")

        # Exclude columns
        if exclude_cols is None:
            exclude_cols = []
        exclude_cols.append(target_col)  # Always exclude the target

        # Add all future target columns to exclude list (any that start with 'future_' or 'target_')
        exclude_cols.extend([col for col in clean_df.columns if col.startswith(('future_', 'target_'))])

        # Prepare feature matrix
        feature_cols = [col for col in clean_df.columns if col not in exclude_cols]
        X = clean_df[feature_cols].values
        y = clean_df[target_col].values

        # Time-series train/test split (no random shuffle, use last portion for test)
        split_idx = int(len(X) * (1 - test_size))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]

        return X_train, X_test, y_train, y_test, feature_cols
```

## trading/ml/models.py

```python
# trading/ml/models.py
# ADD/MODIFY in ModelManager class

import numpy as np # Ensure numpy is imported at the top
import joblib # Ensure joblib is imported
import os # Ensure os is imported
import pandas as pd
from datetime import datetime # Ensure datetime is imported
from typing import Dict, List, Tuple, Union, Optional

# scikit-learn imports (ensure these are present)
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score


class ModelManager:
    """Class to manage ML models for stock price prediction."""

    # Dictionary of available classification models
    CLASSIFICATION_MODELS = {
        'random_forest': RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced'), # Added class_weight
        'gradient_boosting': GradientBoostingClassifier(random_state=42),
        'logistic_regression': LogisticRegression(random_state=42, max_iter=1000, class_weight='balanced'), # Added class_weight
        # SVM can be slow and might not give feature importances easily without linear kernel
        # 'svm': SVC(probability=True, random_state=42, class_weight='balanced')
    }

    # Dictionary of available regression models
    REGRESSION_MODELS = {
        'linear_regression': LinearRegression(),
        'gradient_boosting_regressor': GradientBoostingClassifier(random_state=42) # Note: This should likely be GradientBoostingRegressor
        # Consider adding RandomForestRegressor etc.
    }

    def __init__(self, model_dir: str = 'data/models'):
        """
        Initialize the model manager.

        Args:
            model_dir: Directory to store trained models
        """
        self.model_dir = model_dir
        self.scaler = StandardScaler()
        self.current_model = None
        self.current_model_type = None # 'classification' or 'regression'
        self.feature_columns = None # List of feature names used by the model

        # Create model directory if it doesn't exist
        os.makedirs(model_dir, exist_ok=True)

    def train_classification_model(self, X_train: np.ndarray, y_train: np.ndarray,
                                     model_type: str = 'random_forest',
                                     feature_cols: Optional[List[str]] = None) -> Dict:
        """
        Train a classification model for stock price direction prediction.

        Args:
            X_train: Training feature matrix
            y_train: Training target vector
            model_type: Type of model to train (key from CLASSIFICATION_MODELS)
            feature_cols: List of feature column names (for feature importance)

        Returns:
            Dictionary with training results, including the model object and feature importances if available.
        """
        if model_type not in self.CLASSIFICATION_MODELS:
            raise ValueError(
                f"Unknown model type '{model_type}'. Available models: {list(self.CLASSIFICATION_MODELS.keys())}")

        # --- Feature Scaling ---
        # Fit the scaler ONLY on the training data
        X_train_scaled = self.scaler.fit_transform(X_train)
        print(f"Scaler fitted with {self.scaler.n_features_in_} features.")

        # --- Model Initialization ---
        # Create a new instance for each training run
        model = self.CLASSIFICATION_MODELS[model_type]
        print(f"Training classification model: {type(model).__name__}")

        # --- Model Training ---
        try:
            model.fit(X_train_scaled, y_train)
        except Exception as e:
            print(f"Error during model fitting: {e}")
            raise # Re-raise the exception after logging

        # --- Store Current Model Info ---
        self.current_model = model
        self.current_model_type = 'classification'
        # Store feature columns IF they were provided AND match the scaler
        if feature_cols and len(feature_cols) == self.scaler.n_features_in_:
             self.feature_columns = feature_cols
             print(f"Stored {len(self.feature_columns)} feature columns.")
        elif feature_cols:
             print(f"Warning: Provided feature columns ({len(feature_cols)}) don't match scaler features ({self.scaler.n_features_in_}). Not storing column names.")
             self.feature_columns = None # Reset if mismatch
        else:
             self.feature_columns = None # No names provided
             print("No feature column names provided during training.")


        # --- Get Feature Importances (if available) ---
        # This is now handled by get_current_feature_importances after training/loading
        feature_importances_dict = self.get_current_feature_importances()
        if feature_importances_dict:
             print(f"Successfully retrieved feature importances after training.")
        else:
             print(f"Could not retrieve feature importances after training for {type(model).__name__}.")


        return {
            'model': model, # Return the trained model object
            'model_type': model_type,
            'scaler_features': self.scaler.n_features_in_, # Info about scaler
            'feature_importances': feature_importances_dict, # Include importances if found
            'training_samples': len(X_train)
        }

    def predict_classification(self, X: np.ndarray) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """
        Make predictions with the current classification model.
        Ensures data is scaled using the FITTED scaler.

        Args:
            X: Feature matrix to predict (unscaled)

        Returns:
            Tuple of (predicted_classes, prediction_probabilities)
            Probabilities might be None if the model doesn't support predict_proba.
        """
        if self.current_model is None or self.current_model_type != 'classification':
            raise ValueError("No classification model has been trained or loaded yet.")
        if not hasattr(self.scaler, 'n_features_in_') or self.scaler.n_features_in_ is None:
             raise ValueError("Scaler has not been fitted. Train a model first.")

        # --- Validate Input Shape ---
        if X.shape[1] != self.scaler.n_features_in_:
             raise ValueError(f"Input feature count ({X.shape[1]}) does not match scaler/model feature count ({self.scaler.n_features_in_}).")

        # --- Scale Features ---
        # Use transform, NOT fit_transform, on new data
        X_scaled = self.scaler.transform(X)

        # --- Get Predictions ---
        try:
            predictions = self.current_model.predict(X_scaled)
        except Exception as e:
            print(f"Error during prediction: {e}")
            raise

        # --- Get Probabilities (if available) ---
        probabilities = None
        if hasattr(self.current_model, 'predict_proba'):
            try:
                probabilities = self.current_model.predict_proba(X_scaled)
            except Exception as e:
                print(f"Warning: Could not get probabilities from model {type(self.current_model).__name__}: {e}")
                probabilities = None # Ensure it's None on error
        else:
            print(f"Model type {type(self.current_model).__name__} does not support predict_proba.")


        return predictions, probabilities

    def evaluate_classification(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict:
        """
        Evaluate the current classification model on test data.

        Args:
            X_test: Test feature matrix (unscaled)
            y_test: Test target vector

        Returns:
            Dictionary with evaluation metrics
        """
        if self.current_model is None or self.current_model_type != 'classification':
            raise ValueError("No classification model has been trained or loaded for evaluation.")

        # Get predictions (predict_classification handles scaling)
        try:
            y_pred, _ = self.predict_classification(X_test)
        except ValueError as ve: # Catch shape mismatch errors from predict
             print(f"Evaluation Error: {ve}")
             return {"error": str(ve)} # Return error dict
        except Exception as e:
             print(f"Evaluation Error during prediction: {e}")
             return {"error": f"Prediction failed: {e}"}


        # Calculate metrics
        # Use zero_division=0 to handle cases with no predicted/true samples for a class
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, average='weighted', zero_division=0),
            'recall': recall_score(y_test, y_pred, average='weighted', zero_division=0),
            'f1': f1_score(y_test, y_pred, average='weighted', zero_division=0)
        }
        print(f"Evaluation Metrics: {metrics}")

        return metrics

    # --- ADDED METHOD ---
    def get_current_feature_importances(self) -> Optional[Dict[str, float]]:
        """
        Returns feature importances from the currently loaded/trained model, if available.
        Uses absolute values for coefficients for magnitude comparison.

        Returns:
            Optional[Dict[str, float]]: Dictionary mapping feature names to importance scores,
                                        or None if not available or model not loaded/feature names missing.
        """
        if self.current_model is None:
            # print("Debug: No current model in ModelManager.") # Optional debug
            return None
        if self.feature_columns is None:
             # print("Debug: No feature columns stored in ModelManager.") # Optional debug
             return None # Need feature names to create the dictionary

        importances_array = None
        model_type_name = type(self.current_model).__name__

        if hasattr(self.current_model, 'feature_importances_'):
            importances_array = self.current_model.feature_importances_
            # print(f"Debug: Got feature_importances_ from {model_type_name}") # Optional debug
        elif hasattr(self.current_model, 'coef_'):
            # print(f"Debug: Getting coef_ from {model_type_name}") # Optional debug
            coeffs = self.current_model.coef_
            # Use mean of absolute values across classes for a single importance score per feature.
            if coeffs.ndim > 1:
                importances_array = np.mean(np.abs(coeffs), axis=0)
            else: # Binary classification or regression
                 importances_array = np.abs(coeffs)
            # print(f"Debug: Coef shape: {coeffs.shape}, derived importances shape: {importances_array.shape}") # Optional debug
        else:
            print(f"Warning: Could not retrieve feature importances directly for model type {model_type_name}")
            return None # Cannot reliably get importances

        # Validate shapes before zipping
        if importances_array is not None and len(importances_array.flatten()) == len(self.feature_columns):
             importances_array = importances_array.flatten() # Ensure it's 1D
             # print(f"Debug: Zipping {len(self.feature_columns)} columns with {len(importances_array)} importance values.") # Optional debug
             return dict(zip(self.feature_columns, importances_array))
        else:
             print(f"Warning: Mismatch between stored feature columns ({len(self.feature_columns)}) and retrieved importances ({len(importances_array.flatten()) if importances_array is not None else 'None'}) for {model_type_name}.")
             return None # Shape mismatch or no importances retrieved

    def save_model(self, symbol: str, horizon: int = 5, suffix: str = '') -> str:
        """
        Save the current model, scaler, and metadata to disk using joblib.

        Args:
            symbol: Stock symbol the model was trained on
            horizon: Prediction horizon in days
            suffix: Optional suffix for the filename

        Returns:
            Path to the saved model file.
        """
        if self.current_model is None:
            raise ValueError("No model has been trained yet to save.")
        if not hasattr(self.scaler, 'n_features_in_') or self.scaler.n_features_in_ is None:
             raise ValueError("Scaler has not been fitted. Cannot save model without fitted scaler.")

        # Create filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        model_class_name = type(self.current_model).__name__
        filename = f"{symbol}_{model_class_name}_{self.current_model_type}_{horizon}d_{timestamp}{suffix}.joblib"
        filepath = os.path.join(self.model_dir, filename)

        # Data to save
        model_data = {
            'model': self.current_model,
            'scaler': self.scaler, # Save the FITTED scaler
            'model_type': self.current_model_type, # 'classification' or 'regression'
            'feature_columns': self.feature_columns, # List of feature names
            'symbol': symbol,
            'horizon': horizon,
            'timestamp': timestamp,
            'model_class_name': model_class_name # Store the class name for info
        }
        print(f"Saving model to: {filepath}")
        print(f"  Model Class: {model_class_name}")
        print(f"  Model Type: {self.current_model_type}")
        print(f"  Horizon: {horizon}")
        print(f"  Features ({len(self.feature_columns) if self.feature_columns else 'N/A'}): {self.feature_columns}")


        try:
            joblib.dump(model_data, filepath)
            print("Model saved successfully.")
        except Exception as e:
            print(f"Error saving model to {filepath}: {e}")
            raise # Re-raise after logging

        return filepath

    def load_model(self, filepath: str) -> Dict:
        """
        Load a model, scaler, and metadata from a joblib file.

        Args:
            filepath: Path to the saved model file (.joblib)

        Returns:
            Dictionary containing the loaded model data.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: '{filepath}'")
        if not filepath.endswith('.joblib'):
             raise ValueError(f"Invalid file type. Expected .joblib, got: {filepath}")

        print(f"Loading model from: {filepath}")
        try:
            model_data = joblib.load(filepath)
        except Exception as e:
            print(f"Error loading model from {filepath}: {e}")
            raise # Re-raise after logging

        # --- Validate loaded data ---
        required_keys = ['model', 'scaler', 'model_type', 'feature_columns', 'symbol', 'horizon']
        if not all(key in model_data for key in required_keys):
             missing = [key for key in required_keys if key not in model_data]
             raise ValueError(f"Loaded model data is missing required keys: {missing}")

        # --- Restore Manager State ---
        self.current_model = model_data['model']
        self.scaler = model_data['scaler'] # Restore the FITTED scaler
        self.current_model_type = model_data['model_type']
        self.feature_columns = model_data['feature_columns'] # Restore feature names

        # --- Post-Load Checks ---
        if not hasattr(self.scaler, 'n_features_in_') or self.scaler.n_features_in_ is None:
             print("Warning: Loaded scaler appears not to be fitted.")
        elif self.feature_columns and len(self.feature_columns) != self.scaler.n_features_in_:
             print(f"Warning: Loaded feature columns ({len(self.feature_columns)}) mismatch scaler features ({self.scaler.n_features_in_}).")
             # Decide if this is critical - maybe reset feature_columns?
             # self.feature_columns = None
        elif not self.feature_columns:
             print("Warning: No feature names loaded with the model.")


        print(f"Model loaded successfully: {model_data.get('model_class_name', type(self.current_model).__name__)}")
        print(f"  Type: {self.current_model_type}, Horizon: {model_data.get('horizon')}")
        print(f"  Features ({len(self.feature_columns) if self.feature_columns else 'N/A'}): {self.feature_columns}")


        return model_data # Return the full dictionary

    def load_latest_model(self, symbol: str, horizon: int = 5, model_type: str = 'classification') -> Optional[Dict]:
        """
        Load the most recent model file for a given symbol, horizon, and type (classification/regression).

        Args:
            symbol: Stock symbol
            horizon: Prediction horizon in days
            model_type: 'classification' or 'regression'

        Returns:
            Dictionary with model information if found and loaded, otherwise None.
        """
        print(f"Searching for latest '{model_type}' model for {symbol} with {horizon}-day horizon...")
        # Construct expected filename pattern part: _{model_type}_{horizon}d_
        pattern = f"_{model_type}_{horizon}d_"
        try:
            # Find files matching the symbol prefix and the pattern
            files = [f for f in os.listdir(self.model_dir)
                     if f.startswith(f"{symbol}_") and pattern in f and f.endswith('.joblib')]
        except FileNotFoundError:
             print(f"Model directory not found: {self.model_dir}")
             return None
        except Exception as e:
             print(f"Error listing model directory {self.model_dir}: {e}")
             return None


        if not files:
            print(f"No matching '{model_type}' models found for {symbol} (Horizon: {horizon}).")
            return None

        # Sort by timestamp (embedded in filename: YYYYMMDD_HHMMSS)
        # Extract timestamp part carefully
        def get_timestamp_from_filename(fname):
            try:
                # Pattern: SYMBOL_CLASSNAME_MODELTYPE_HORIZONd_YYYYMMDD_HHMMSS[_SUFFIX].joblib
                parts = fname.replace('.joblib', '').split('_')
                # Find the date part (should be the second to last or third to last if suffix exists)
                for i in range(len(parts) - 1, 2, -1): # Search backwards from end
                     if len(parts[i]) == 6 and len(parts[i-1]) == 8 and parts[i-1].isdigit() and parts[i].isdigit():
                          return f"{parts[i-1]}_{parts[i]}" # YYYYMMDD_HHMMSS
            except Exception:
                pass
            return "00000000_000000" # Default for sorting if parsing fails

        files.sort(key=get_timestamp_from_filename, reverse=True)
        latest_file = files[0]
        filepath = os.path.join(self.model_dir, latest_file)

        # Load the most recent model
        try:
            return self.load_model(filepath)
        except (FileNotFoundError, ValueError, Exception) as e:
             # load_model already prints errors, just return None
             print(f"Failed to load latest model '{latest_file}': {e}")
             return None

    def get_model_list(self) -> pd.DataFrame:
        """
        Get a list of all saved models in the model directory.

        Returns:
            pd.DataFrame with model information (symbol, class, type, horizon, timestamp, filename).
            Returns an empty DataFrame if no models are found or directory doesn't exist.
        """
        model_info = []
        try:
            # Get all joblib files in model directory
            files = [f for f in os.listdir(self.model_dir) if f.endswith('.joblib')]
        except FileNotFoundError:
             print(f"Model directory not found: {self.model_dir}")
             return pd.DataFrame()
        except Exception as e:
             print(f"Error accessing model directory {self.model_dir}: {e}")
             return pd.DataFrame()


        if not files:
            return pd.DataFrame()

        # Extract model information from filenames
        for filename in files:
            try:
                # Pattern: SYMBOL_CLASSNAME_MODELTYPE_HORIZONd_YYYYMMDD_HHMMSS[_SUFFIX].joblib
                parts = filename.replace('.joblib', '').split('_')
                if len(parts) < 6: continue # Basic check for enough parts

                symbol = parts[0]
                model_class_name = parts[1]
                model_type = parts[2] # classification or regression
                horizon = int(parts[3].replace('d', ''))

                # Find timestamp (YYYYMMDD_HHMMSS) - might be parts[-2] and parts[-1] before suffix
                timestamp_str = "Unknown"
                for i in range(len(parts) - 1, 2, -1):
                     if len(parts[i]) == 6 and len(parts[i-1]) == 8 and parts[i-1].isdigit() and parts[i].isdigit():
                          timestamp_str = f"{parts[i-1]}_{parts[i]}"
                          break

                # Try to parse timestamp string
                try:
                    timestamp_dt = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                except ValueError:
                    timestamp_dt = None # Assign None if parsing fails

                model_info.append({
                    'symbol': symbol,
                    'model_class': model_class_name,
                    'type': model_type,
                    'horizon': horizon,
                    'timestamp': timestamp_dt, # Store datetime object for sorting
                    'filename': filename,
                    'filepath': os.path.join(self.model_dir, filename)
                })
            except (IndexError, ValueError) as e:
                # Skip files with unexpected format
                print(f"Skipping file with unexpected format '{filename}': {e}")
                continue

        # Create DataFrame
        if not model_info:
             return pd.DataFrame()

        df = pd.DataFrame(model_info)

        # Sort by timestamp (most recent first), handle potential NaT values
        if 'timestamp' in df.columns:
             # Sort NaT values to the end
             df = df.sort_values('timestamp', ascending=False, na_position='last')

        return df

    # Regression methods would go here (train_regression_model, predict_regression, evaluate_regression)
    # Ensure they also handle scaling, feature columns, and persistence correctly.
```

## trading/ml/service.py

```python
# trading/ml/service.py
# Service layer for ML predictions

import os
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Union, Optional # Ensure typing is imported

# Assuming FeatureEngineer and ModelManager are correctly imported
from trading.ml.features import FeatureEngineer
from trading.ml.models import ModelManager
# Import config if needed for default threshold, or define it here
# from config import ML_DEFAULT_THRESHOLD # Example if you add it to config

class MlPredictionService:
    """
    Service layer for managing ML model training, loading, prediction,
    and generating hybrid recommendations for stock analysis.
    """

    # Direction labels for classification results
    DIRECTION_LABELS = {
        1: "UP",
        0: "NEUTRAL",
        -1: "DOWN"
    }

    # Confidence level thresholds
    CONFIDENCE_THRESHOLDS = {
        "STRONG": 0.80,
        "MODERATE": 0.65,
        "WEAK": 0.55
    }

    def __init__(self, model_dir: str = 'data/models'):
        """
        Initialize the ML prediction service.

        Args:
            model_dir: Directory where models are stored and loaded from.
        """
        print("ML Prediction Service Initialized.") # Log initialization
        self.model_manager = ModelManager(model_dir=model_dir)
        self.feature_engineer = FeatureEngineer()
        # self.current_symbol = None # State like current symbol is better managed by the calling UI (App)
        self.loaded_model_info = None # Stores metadata about the currently loaded model

    def prepare_data(self, df: pd.DataFrame, prediction_horizon: int = 5,
                     target_threshold: float = 0.01) -> Optional[pd.DataFrame]:
        """
        Prepare data for ML by engineering features and adding target variables.

        Args:
            df: DataFrame with OHLCV data (lowercase columns expected).
            prediction_horizon: Horizon for target variable calculation in days.
            target_threshold: Threshold for classifying UP/DOWN vs NEUTRAL.

        Returns:
            DataFrame with engineered features and target variables, or None if error.
        """
        if df is None or df.empty:
            print("Error: Cannot prepare data, input DataFrame is empty.")
            return None

        # print(f"Preparing data: Engineering features...") # Verbose logging
        # Engineer features (assuming engineer_features handles NaN/dropna)
        features_df = self.feature_engineer.engineer_features(df)
        if features_df is None or features_df.empty:
             print("Error: Feature engineering resulted in empty DataFrame.")
             return None
        # print(f"Features engineered. Shape: {features_df.shape}") # Verbose logging


        # Add target variable (needed for training, useful context for prediction)
        # print(f"Adding target variables (Horizon: {prediction_horizon}d, Threshold: {target_threshold:.4f})...") # Verbose logging
        if len(features_df) > prediction_horizon:
            # Pass the threshold to the target variable function
            features_df = self.feature_engineer.get_target_variable(
                features_df, horizon=prediction_horizon, threshold=target_threshold)
            # print(f"Target variables added. Shape: {features_df.shape}") # Verbose logging
            # Check if target columns were actually added
            target_col_name = f'target_direction_{prediction_horizon}d'
            if target_col_name not in features_df.columns:
                 print(f"Warning: Target column '{target_col_name}' not found after get_target_variable.")
                 # It might be okay if just predicting, but crucial for training.
        else:
            print(f"Warning: Not enough data ({len(features_df)}) to calculate target for horizon {prediction_horizon}.")
            # Cannot add target, proceed with features only (might fail training later)

        return features_df

    def train_model(self, symbol: str, df: pd.DataFrame, model_type: str = 'random_forest',
                    prediction_type: str = 'classification', prediction_horizon: int = 5,
                    test_size: float = 0.2, target_threshold: float = 0.01) -> Dict:
        """
        Train an ML model, evaluate it, and save it.

        Args:
            symbol: Stock symbol.
            df: DataFrame with OHLCV data.
            model_type: Type of model to train (key from ModelManager.CLASSIFICATION_MODELS/REGRESSION_MODELS).
            prediction_type: 'classification' or 'regression'.
            prediction_horizon: Horizon for predictions in days.
            test_size: Portion of data to use for testing (e.g., 0.2 for 20%).
            target_threshold: Threshold for classifying UP/DOWN vs NEUTRAL (used in data prep).

        Returns:
            Dictionary containing 'model_info', 'train_results', and 'metrics'.

        Raises:
            ValueError: If data preparation fails, target column is missing, or prediction_type is invalid.
            Exception: If errors occur during data splitting, training, evaluation, or saving.
        """
        # print(f"\n--- Starting ML Training for {symbol} ---") # Logging handled by App
        # print(f"Model: {model_type}, Type: {prediction_type}, Horizon: {prediction_horizon}d, Test Size: {test_size:.1%}, Threshold: {target_threshold:.4f}")

        # 1. Prepare Data (including target variable)
        prepared_data = self.prepare_data(df, prediction_horizon=prediction_horizon, target_threshold=target_threshold)
        if prepared_data is None or prepared_data.empty:
            # Logged in prepare_data
            raise ValueError(f"Failed to prepare data for {symbol}")

        # 2. Define Target Column
        if prediction_type == 'classification':
            target_col = f'target_direction_{prediction_horizon}d'
        elif prediction_type == 'regression':
            target_col = f'future_return_{prediction_horizon}d'
        else:
             raise ValueError(f"Invalid prediction_type: {prediction_type}")

        # Make sure the target column exists after data prep (crucial for training)
        if target_col not in prepared_data.columns:
            raise ValueError(f"Target column '{target_col}' not found in prepared data. Insufficient data for horizon?")

        # 3. Split Data into Train/Test
        # print("Splitting data into training and testing sets...") # Logging handled by App
        try:
            X_train, X_test, y_train, y_test, feature_cols = self.feature_engineer.prepare_ml_data(
                prepared_data, target_col=target_col, test_size=test_size)
            # print(f"Data split: Train shape {X_train.shape}, Test shape {X_test.shape}") # Logging handled by App
            # print(f"Using {len(feature_cols)} features: {feature_cols}") # Logging handled by App
        except Exception as e:
             print(f"Error during data splitting: {e}")
             raise # Re-raise

        # 4. Train Model & Evaluate
        train_results = {}
        metrics = {}
        model_path = None
        try:
            if prediction_type == 'classification':
                print(f"Training classification model: {model_type}") # Log action
                train_results = self.model_manager.train_classification_model(
                    X_train, y_train, model_type=model_type, feature_cols=feature_cols)
                print("Evaluating classification model...") # Log action
                metrics = self.model_manager.evaluate_classification(X_test, y_test)
                print(f"Evaluation Metrics: {metrics}") # Log result
            # --- Add Regression Training/Evaluation Here ---
            # elif prediction_type == 'regression':
            #     print(f"Training regression model: {model_type}")
            #     train_results = self.model_manager.train_regression_model(X_train, y_train, model_type=model_type, feature_cols=feature_cols)
            #     print("Evaluating regression model...")
            #     metrics = self.model_manager.evaluate_regression(X_test, y_test)
            #     print(f"Evaluation Metrics: {metrics}")
            else:
                 raise ValueError(f"Training not implemented for prediction_type: {prediction_type}")

            # 5. Save Model
            print(f"Saving model to: {self.model_manager.model_dir}") # Log action
            model_path = self.model_manager.save_model(symbol, horizon=prediction_horizon)
            print(f"Model saved successfully.") # Log result

        except Exception as e:
            print(f"An error occurred during model training, evaluation, or saving: {e}")
            # Reset current model in manager on error to prevent inconsistent state
            self.model_manager.current_model = None
            self.model_manager.feature_columns = None
            raise # Re-raise the exception

        # 6. Update Service State (Store metadata about the successfully trained model)
        # This info will be used by predict() if this model remains loaded.
        self.loaded_model_info = {
            'symbol': symbol,
            'model_class_name': type(self.model_manager.current_model).__name__,
            'model_config_name': model_type, # Store the key used ('random_forest')
            'prediction_type': prediction_type, # Store 'classification' or 'regression'
            'horizon': prediction_horizon,
            'path': model_path,
            'metrics': metrics, # Store evaluation metrics from this training run
            'feature_columns': self.model_manager.feature_columns, # Store feature names used
            'timestamp': datetime.now().strftime('%Y%m%d_%H%M%S') # Add training time
        }
        # print("--- ML Training Complete ---") # Logging handled by App

        # 7. Combine Results for Return to Caller (App)
        results = {
            'model_info': self.loaded_model_info, # Metadata just created
            'train_results': train_results, # Contains model object, raw importances etc. from manager
            'metrics': metrics # Pass metrics back explicitly
        }

        return results

    def load_model_for_symbol(self, symbol: str, prediction_horizon: int = 5, model_type: str = 'classification') -> bool:
        """
        Load the latest pre-trained model for a symbol, horizon, and type.
        Updates the service's internal state (`self.loaded_model_info`).

        Args:
            symbol: Stock symbol.
            prediction_horizon: Prediction horizon in days.
            model_type: 'classification' or 'regression'. Determines model filename pattern.

        Returns:
            True if a model was successfully loaded, False otherwise.
        """
        # print(f"Attempting to load latest '{model_type}' model for {symbol} (Horizon: {prediction_horizon}d)...") # Logging handled by App
        self.loaded_model_info = None # Clear previous info before attempting load

        # Use the model manager to find and load the latest model file
        # NOTE: Assumes ModelManager.load_latest_model is updated to accept/use model_type for filtering filenames
        model_data = self.model_manager.load_latest_model(symbol, horizon=prediction_horizon, model_type=model_type)

        if model_data is None:
            # print(f"No suitable pre-trained model found.") # Logging handled by App
            return False

        # Store metadata about the loaded model in the service's state
        self.loaded_model_info = {
            'symbol': symbol,
            # Get class name from the actual loaded model object in the manager
            'model_class_name': type(self.model_manager.current_model).__name__,
             # Get model type ('classification'/'regression') from manager state after load
            'prediction_type': self.model_manager.current_model_type,
            # Get horizon from the loaded model data if available, otherwise use requested horizon
            'horizon': model_data.get('horizon', prediction_horizon),
            # Get path from the loaded model data (added by load_latest_model/load_model)
            'path': model_data.get('filepath'),
            'metrics': None, # Metrics aren't stored with the model file
             # Get feature columns from the manager state after load
            'feature_columns': self.model_manager.feature_columns,
            # Get timestamp from the loaded model data
            'timestamp': model_data.get('timestamp')
        }
        # print(f"Successfully loaded model: {self.loaded_model_info.get('model_class_name')}") # Logging handled by App
        return True

    # --- predict method with target_threshold fix ---
    def predict(self, df: pd.DataFrame, target_threshold: float = 0.01) -> Dict:
        """
        Make predictions using the currently loaded model.
        Requires a model to be loaded first via load_model_for_symbol or train_model.

        Args:
            df: DataFrame with OHLCV data (must contain necessary history for feature eng).
            target_threshold (float): The significance threshold used for preparing data
                                      (ensures consistency, though not directly used in prediction logic itself).

        Returns:
            Dictionary with prediction results (direction, confidence, etc.).

        Raises:
            ValueError: If no model is loaded, data is invalid, or features are missing.
        """
        if self.loaded_model_info is None or self.model_manager.current_model is None:
            raise ValueError("No model has been loaded or trained. Call load_model_for_symbol or train_model first.")
        if df is None or df.empty:
            raise ValueError("No data provided for prediction.")

        current_symbol_for_log = self.loaded_model_info.get('symbol', 'Unknown')
        # print(f"\n--- Generating ML Prediction for {current_symbol_for_log} ---") # Logging handled by App
        # print(f"Using model: {self.loaded_model_info.get('model_class_name')}, Horizon: {self.loaded_model_info.get('horizon')}d") # Logging handled by App

        # 1. Prepare Features for the *entire* dataframe needed for context
        prepared_data = self.prepare_data(
            df,
            prediction_horizon=self.loaded_model_info.get('horizon', 5),
            target_threshold=target_threshold # Pass the threshold
            )
        if prepared_data is None or prepared_data.empty:
            raise ValueError("Failed to prepare data for prediction (feature engineering failed).")

        # 2. Get the *last* row of features needed for prediction
        required_features = self.loaded_model_info.get('feature_columns')
        if not required_features:
             raise ValueError("Model was loaded without feature column information. Cannot make predictions.")

        # Check if all required features exist in the prepared data
        missing_features = [f for f in required_features if f not in prepared_data.columns]
        if missing_features:
             # Provide more context in the error
             raise ValueError(f"Prepared data (shape {prepared_data.shape}) is missing required features for the loaded model: {missing_features}. Available columns: {prepared_data.columns.tolist()}")

        # Select the last row and only the required feature columns
        try:
             last_feature_vector = prepared_data[required_features].iloc[-1:] # Keep as DataFrame row initially
             X_predict = last_feature_vector.values # Convert to numpy array for prediction
        except IndexError:
             raise ValueError("Could not select the last row of features. Prepared data might be empty after processing.")
        except KeyError as e:
             raise ValueError(f"Error selecting required features for prediction: {e}")


        # 3. Make Prediction based on loaded model type
        prediction_type = self.loaded_model_info.get('prediction_type', 'classification')
        prediction_result = {}

        try:
            if prediction_type == 'classification':
                pred_class, pred_proba = self.model_manager.predict_classification(X_predict)
                prediction = int(pred_class[0]) # Get the single prediction
                prediction_label = self.DIRECTION_LABELS.get(prediction, "UNKNOWN")

                # Get confidence from probabilities
                confidence = None
                confidence_label = "UNKNOWN"
                probabilities_list = None
                if pred_proba is not None and len(pred_proba) > 0:
                    probabilities = pred_proba[0] # Probabilities for the single prediction
                    probabilities_list = probabilities.tolist() # Convert to list for storage/display
                    confidence = float(np.max(probabilities)) # Highest probability as confidence

                    # Determine confidence level string
                    if confidence >= self.CONFIDENCE_THRESHOLDS["STRONG"]: confidence_label = "STRONG"
                    elif confidence >= self.CONFIDENCE_THRESHOLDS["MODERATE"]: confidence_label = "MODERATE"
                    elif confidence >= self.CONFIDENCE_THRESHOLDS["WEAK"]: confidence_label = "WEAK"
                    else: confidence_label = "UNCERTAIN"
                else:
                     # Handle cases where probabilities aren't available
                     confidence_label = "N/A" # Indicate not applicable


                prediction_result = {
                    'prediction': prediction, # -1, 0, or 1
                    'direction': prediction_label, # 'UP', 'NEUTRAL', 'DOWN'
                    'confidence': confidence, # Float (highest probability) or None
                    'confidence_level': confidence_label, # 'STRONG', 'MODERATE', etc.
                    'probabilities': probabilities_list, # List of probabilities per class or None
                    # Safely get date and format
                    'date': prepared_data.index[-1].strftime('%Y-%m-%d') if isinstance(prepared_data.index[-1], pd.Timestamp) else str(prepared_data.index[-1]),
                    'horizon': self.loaded_model_info.get('horizon', 5)
                }
                # print(f"ML Prediction: {prediction_label}, Confidence: {confidence:.3f if confidence is not None else 'N/A'} ({confidence_label})") # Logging handled by App

            # --- Add Regression Prediction Here ---
            # elif prediction_type == 'regression':
            #     predicted_value = self.model_manager.predict_regression(X_predict)
            #     # ... process regression output ...
            #     prediction_result = { ... }
            else:
                 raise ValueError(f"Prediction not implemented for model type: {prediction_type}")

        except Exception as e:
             print(f"Error during ML prediction execution: {e}")
             # Return an error structure or re-raise
             prediction_result = { 'error': str(e) } # Indicate error in result

        return prediction_result


    def get_loaded_feature_importances(self) -> Optional[Dict[str, float]]:
         """Gets feature importances from the currently loaded model via ModelManager."""
         if not self.model_manager or self.model_manager.current_model is None:
             # print("Debug: No model manager or current model in service.") # Optional debug
             return None
         # print("Debug: Calling model_manager.get_current_feature_importances()") # Optional debug
         return self.model_manager.get_current_feature_importances()

    def get_loaded_model_metadata(self) -> Optional[Dict]:
        """Returns metadata about the currently loaded model."""
        # Returns the dictionary stored during load or train
        return self.loaded_model_info

    def get_hybrid_recommendation(self, df: pd.DataFrame, technical_score: float,
                                  adx_value: Optional[float] = None,
                                  target_threshold: float = 0.01) -> Dict: # Added threshold
        """
        Generate a hybrid recommendation combining ML predictions with technical indicators.
        Assumes an ML model has been loaded and a prediction can be made.

        Args:
            df: DataFrame with OHLCV data (for ML prediction).
            technical_score: Pre-calculated technical analysis score (e.g., -3 to 3).
            adx_value: Optional ADX value for trend strength adjustment.
            target_threshold: Threshold used for preparing data for the predict call.

        Returns:
            Dictionary with hybrid recommendation details.
        """
        # print("\n--- Generating Hybrid Recommendation ---") # Logging handled by App
        ml_prediction = None
        hybrid_recommendation = "ERROR" # Default in case of issues
        hybrid_score = 0.0
        ml_weight = 0.0
        tech_weight = 1.0 # Default to all technical if ML fails
        ml_score = 0.0
        trend_strength = "WEAK" # Default

        # 1. Get ML Prediction
        try:
            # Use the predict method which uses the currently loaded model
            # Pass the threshold for consistent data prep
            ml_prediction = self.predict(df, target_threshold=target_threshold)
            if 'error' in ml_prediction:
                 raise ValueError(f"ML Prediction failed: {ml_prediction['error']}")

        except Exception as e:
            print(f"Error getting ML prediction for hybrid: {e}")
            ml_prediction = None # Ensure it's None if prediction fails

        # 2. Calculate Hybrid Score (if ML prediction succeeded)
        if ml_prediction:
            try:
                # ML directional signal (-1, 0, 1)
                ml_signal = ml_prediction.get('prediction', 0)
                ml_score = ml_signal * 3.0 # Scale ML signal

                # ML confidence weight (0.4 to 0.7 based on confidence level)
                confidence_level = ml_prediction.get('confidence_level', 'UNCERTAIN')
                if confidence_level == 'STRONG': ml_weight = 0.70
                elif confidence_level == 'MODERATE': ml_weight = 0.60
                elif confidence_level == 'WEAK': ml_weight = 0.50
                else: ml_weight = 0.40 # UNCERTAIN or N/A

                # Adjust ML weight based on ADX (trend strength) if available
                trend_adjustment = 1.0
                if adx_value is not None:
                    if adx_value > 30: trend_adjustment = 1.15; trend_strength = "STRONG"
                    elif adx_value > 20: trend_adjustment = 1.05; trend_strength = "MODERATE"
                    else: trend_adjustment = 0.90; trend_strength = "WEAK" # Keep WEAK as default otherwise
                    ml_weight *= trend_adjustment
                    # Cap weight between reasonable bounds (e.g., 0.3 to 0.8)
                    ml_weight = max(0.3, min(0.8, ml_weight))

                # Calculate technical weight
                tech_weight = 1.0 - ml_weight

                # Calculate final hybrid score
                hybrid_score = (ml_score * ml_weight) + (technical_score * tech_weight)

                # Generate recommendation string based on hybrid score
                if hybrid_score >= 2.0: hybrid_recommendation = "BUY"
                elif hybrid_score >= 0.5: hybrid_recommendation = "WEAK BUY"
                elif hybrid_score <= -2.0: hybrid_recommendation = "SELL"
                elif hybrid_score <= -0.5: hybrid_recommendation = "WEAK SELL"
                else: hybrid_recommendation = "HOLD"

                # print(f"Hybrid Score: {hybrid_score:.2f} (ML: {ml_score:.1f} * {ml_weight:.2f}, TA: {technical_score:.1f} * {tech_weight:.2f}) -> {hybrid_recommendation}") # Logging handled by App

            except Exception as e:
                 print(f"Error calculating hybrid score: {e}")
                 # Fallback to technical score if hybrid calculation fails
                 hybrid_recommendation = "ERROR" # Indicate calculation error
                 hybrid_score = technical_score # Report TA score as the score
                 ml_weight = 0.0
                 tech_weight = 1.0
                 if adx_value is not None: # Still determine trend strength if possible
                      if adx_value > 30: trend_strength = "STRONG"
                      elif adx_value > 20: trend_strength = "MODERATE"

        else:
            # ML Prediction failed, use only technical score
            # print("ML Prediction failed, using Technical Recommendation only.") # Logging handled by App
            hybrid_score = technical_score # Use TA score
            if technical_score >= 2.0: hybrid_recommendation = "BUY"
            elif technical_score >= 0.5: hybrid_recommendation = "WEAK BUY"
            elif technical_score <= -2.0: hybrid_recommendation = "SELL"
            elif technical_score <= -0.5: hybrid_recommendation = "WEAK SELL"
            else: hybrid_recommendation = "HOLD"
            ml_weight = 0.0
            tech_weight = 1.0
            if adx_value is not None: # Still determine trend strength
                 if adx_value > 30: trend_strength = "STRONG"
                 elif adx_value > 20: trend_strength = "MODERATE"


        # 3. Build the result dictionary
        result = {
            'recommendation': hybrid_recommendation,
            'hybrid_score': hybrid_score,
            'ml_prediction': ml_prediction, # Include the raw ML prediction dict (or None)
            'ml_score': ml_score if ml_prediction and 'error' not in ml_prediction else None, # Use calculated ml_score
            'ml_weight': ml_weight,
            'technical_score': technical_score,
            'technical_weight': tech_weight,
            'trend_strength': trend_strength,
            'horizon': ml_prediction.get('horizon', 5) if ml_prediction and 'error' not in ml_prediction else 5 # Use ML horizon or default
        }

        return result

```

## gui/app.py

```python
# gui/app.py
# Main application window class - Refactored

# ... (Keep all imports and other class code the same as the previous version) ...
import customtkinter as ctk
from tkinter import font as tkfont, ttk
import tkinter as tk # For TclError handling
import pandas as pd
import numpy as np
import importlib
import datetime
import random
import traceback
import os
from typing import Dict, List, Tuple, Union, Optional # Typing import
from data.data_source_factory import DataSourceFactory

# Matplotlib imports
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates

# Configuration Imports
from config import (SYMBOLS, DEFAULT_DATA_PERIOD, DEFAULT_DATA_INTERVAL,
                    DEFAULT_CASH, DEFAULT_COMMISSION, DEFAULT_TRADE_SIZE_PERCENT,
                    # Recommendation Params for TA Calc
                    REC_SMA_SHORT, REC_SMA_LONG, REC_RSI_PERIOD, REC_RSI_BUY, REC_RSI_SELL,
                    REC_MACD_FAST, REC_MACD_SLOW, REC_MACD_SIG, # Keep if needed later
                    REC_BBANDS_PERIOD, REC_BBANDS_STDDEV, # Keep if needed later
                    REC_ADX_PERIOD, REC_ADX_THRESHOLD,
                    # Observer Location
                    OBSERVER_LAT, OBSERVER_LON, OBSERVER_ELEV,
                    # Colors & Fonts
                    COLOR_BACKGROUND, COLOR_FOREGROUND, COLOR_BUTTON, COLOR_BUTTON_HOVER,
                    COLOR_DROPDOWN_FG, COLOR_DROPDOWN_BG, COLOR_DROPDOWN_BUTTON, COLOR_DROPDOWN_BUTTON_HOVER,
                    COLOR_TEXTBOX_FG, COLOR_TEXTBOX_BG, FONT_FAMILY_MONO, FONT_SIZE_NORMAL, FONT_SIZE_LARGE,
                    FONT_SIZE_TEXTBOX, FONT_SIZE_LED,
                    COLOR_CHART_BG, COLOR_CHART_LINE, COLOR_CHART_AXES, COLOR_ACCENT,
                    COLOR_POSITIVE, COLOR_NEGATIVE, COLOR_NEUTRAL, COLOR_WEAK_POSITIVE, COLOR_WEAK_NEGATIVE,
                    COLOR_SECONDARY_BUTTON, COLOR_SECONDARY_BUTTON_HOVER,
                    # LED Colors
                    COLOR_LED_PWR_ON, COLOR_LED_CPU_ON, COLOR_LED_DATA_ON, COLOR_LED_COM_ON,
                    # --- Direct Hex Colors for Recommendations ---
                    COLOR_REC_SELL, COLOR_REC_WEAK_SELL, COLOR_REC_HOLD,
                    COLOR_REC_WEAK_BUY, COLOR_REC_BUY, COLOR_REC_DEFAULT,
                    # --- End Direct Hex Colors ---
                    # ML Colors & Config
                    COLOR_LED_ML_ON, COLOR_LED_ML_BORDER, ML_MODEL_DIR, ML_DEFAULT_HORIZON,
                    ML_ENABLE_HYBRID, ML_HYBRID_WEIGHT, ML_TRAIN_TEST_SPLIT, # Import split default
                    # Import threshold default if defined, e.g.:
                    # ML_DEFAULT_THRESHOLD
                    )

# Local Application Imports
from data.data_fetcher import DataFetcher
from gui.widgets.vintage_indicators import WornLED
from gui.widgets.dot_matrix import MatrixText # Import MatrixText
from trading.backtester import run_backtest
from trading.ml.service import MlPredictionService
# Import models needed for ML parameter UI
from trading.ml.models import ModelManager


# --- Strategy Imports & Definitions ---
# ... (Omitted for Brevity - Keep as before) ...
# Direct imports for non-dependency strategies
from trading.strategies.sma_cross import SmaCross
from trading.strategies.fake_moon_strategy import FakeMoonStrategy
from trading.strategies.ichimoku_strategy import IchimokuStrategy
from trading.strategies.donchian_channel_strategy import DonchianChannelStrategy
from trading.strategies.day_of_week_strategy import DayOfWeekStrategy

# String paths for strategies requiring dynamic loading (TA-Lib, Ephem)
STRATEGY_LOADERS = {
    "SMA Crossover": SmaCross,
    "Ichimoku Cloud": IchimokuStrategy,
    "Donchian Channel": DonchianChannelStrategy,
    "Day of Week Effect": DayOfWeekStrategy,
    "Fake Moon (Day of Month)": FakeMoonStrategy,
    "RSI Oscillator": "trading.strategies.rsi_oscillator.RsiOscillator",
    "Volatility Breakout": "trading.strategies.volatility_breakout.VolatilityBreakout",
    "MACD": "trading.strategies.macd_strategy.MacdStrategy",
    "Bollinger Bands": "trading.strategies.bollinger_bands_strategy.BollingerBandsStrategy",
    "Real Moon (Ephem)": "trading.strategies.real_moon_strategy.RealMoonStrategy"
}

# Strategy Parameter Definitions (Ensure trade_size_percent is always first)
PARAM_CONFIG = {
    "SMA Crossover": [("n1", 10), ("n2", 30)],
    "Ichimoku Cloud": [("tenkan_period", 9), ("kijun_period", 26), ("senkou_b_period", 52), ("chikou_period", 26), ("senkou_displacement", 26)],
    "Donchian Channel": [("n_high", 20), ("n_low", 20)],
    "Day of Week Effect": [("buy_day", 0), ("sell_day", 4)],
    "Fake Moon (Day of Month)": [("buy_day_start", 1), ("buy_day_end", 5), ("sell_day_start", 14), ("sell_day_end", 18)],
    "RSI Oscillator": [("rsi_period", 14), ("upper_bound", 70), ("lower_bound", 30)],
    "Volatility Breakout": [("atr_period", 14), ("ma_period", 20), ("atr_multiplier", 2.0)],
    "MACD": [("fast_period", 12), ("slow_period", 26), ("signal_period", 9)],
    "Bollinger Bands": [("bb_period", 20), ("bb_std_dev", 2.0)],
    "Real Moon (Ephem)": [("days_after_new_moon_buy", 2), ("buy_window_days", 3), ("days_after_full_moon_sell", 2), ("sell_window_days", 3)],
}
# Add default trade size parameter to all strategies
for params in PARAM_CONFIG.values():
     params.insert(0, ("trade_size_percent", DEFAULT_TRADE_SIZE_PERCENT))

# Strategy Descriptions (Keep as before)
STRATEGY_DESCRIPTIONS = {
    "SMA Crossover": "Simple Moving Average Crossover...", # Omitted for brevity
    "Ichimoku Cloud": "Ichimoku Kinko Hyo...",
    "Donchian Channel": "Donchian Channel Breakout...",
    "Day of Week Effect": "Calendar-Based Strategy...",
    "Fake Moon (Day of Month)": "Placeholder Lunar Strategy...",
    "RSI Oscillator": "Relative Strength Index Oscillator...",
    "Volatility Breakout": "Volatility Breakout using ATR...",
    "MACD": "Moving Average Convergence Divergence...",
    "Bollinger Bands": "Bollinger Bands Mean Reversion...",
    "Real Moon (Ephem)": "Lunar Cycle Strategy (Astronomical)...",
}

# Easter Egg Art (Keep as before)
EASTER_EGG_ART = """ ... """ # Omitted for brevity

# --- Constants for Dot Matrix Display ---
MATRIX_COLS = 12
MATRIX_CHAR_WIDTH = 5
MATRIX_SPACING = 1
MATRIX_TOTAL_COLS = MATRIX_COLS * (MATRIX_CHAR_WIDTH + MATRIX_SPACING) - MATRIX_SPACING # Adjusted calculation
MATRIX_ROWS = 7
MATRIX_PIXEL_SIZE = 6
MATRIX_BG = "#050505" # Use config color? COLOR_MATRIX_BG if defined

# --- NEW: Recommendation Color Mapping (Using HEX codes) ---
RECOMMENDATION_HEX_COLORS = {
    'BUY': COLOR_REC_BUY,
    'WEAK BUY': COLOR_REC_WEAK_BUY,
    'HOLD': COLOR_REC_HOLD,
    'WEAK SELL': COLOR_REC_WEAK_SELL,
    'SELL': COLOR_REC_SELL,
    'DEFAULT': COLOR_REC_DEFAULT, # For price display
    'N/A': COLOR_REC_HOLD,
    'ERROR': COLOR_REC_SELL,
    'LOADING...': COLOR_REC_WEAK_SELL, # Or maybe HOLD color?
    'CALC...': COLOR_REC_WEAK_SELL, # Or maybe HOLD color?
    'NO DATA': COLOR_REC_HOLD,
    'NO TA-LIB': COLOR_REC_SELL,
    # Add blank space mapping to background or a very dim color if needed
    ' ': COLOR_REC_HOLD, # Default blank space to HOLD color (or choose another)
}


# ==============================================================================
# Main Application Class
# ==============================================================================
class App(ctk.CTk):
    """ Main application window """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # --- Core Application State ---
        self.current_symbol = ""
        self.current_data = None # Stores the full fetched OHLCV data
        self.plotted_data = None # Reference to data currently shown on chart
        self.latest_price = None
        self._loading_data = False # Flag used by clear_display
        self._predicting_ml = False # Flag used by generate_ml_prediction

        # --- TA State ---
        self.talib_module = None # Loaded TA-Lib module
        self.ephem_module = None # Loaded Ephem module
        self.latest_ta_results = None # Stores dict from _calculate_ta_indicators
        # --- FIX: Initialize recommendation state to blank ---
        self.latest_recommendation = " " # String: BUY, SELL, HOLD etc. *** RENAMED & INITIALIZED BLANK ***
        self.latest_technical_score = 0.0 # Float score from TA calc
        self.latest_adx = None # Float ADX value from TA calc

        # --- ML State ---
        self.ml_service = None # Initialized in init_ml_components
        self.ml_model_loaded = False # Flag if a model is loaded for current symbol
        self.ml_prediction = None # Stores the dict result from ml_service.predict
        self.latest_feature_importances = None # Stores dict of feature importances
        # ML UI Variables (initialized in update_ml_controls_frame)
        self.ml_horizon_var = None
        self.ml_model_type_var = None
        self.ml_threshold_var = None
        self.ml_test_split_var = None
        # Add config defaults for ML UI vars
        self.ml_default_horizon = ML_DEFAULT_HORIZON
        self.ml_enable_hybrid = ML_ENABLE_HYBRID
        self.ml_hybrid_weight = ML_HYBRID_WEIGHT
        # Get default threshold from config if defined, else use 1.0
        self.ml_default_threshold_pct = 1.0 # Default 1%
        # if 'ML_DEFAULT_THRESHOLD' in globals():
        #     self.ml_default_threshold_pct = ML_DEFAULT_THRESHOLD * 100.0


        # --- Backtesting State ---
        self.param_entries = {} # Stores CTkStringVars for strategy parameters

        # --- UI Update Job IDs ---
        self.activity_led_job = None
        self.matrix_update_job = None
        self.matrix_shows_price = False # Toggles between price/recommendation

        # --- Initialize Core Components ---
        self.data_fetcher = DataSourceFactory.get_data_fetcher()
        self._load_optional_modules() # Load TA-Lib, Ephem
        self._configure_window()
        self._configure_fonts()
        self._create_widgets()
        self.init_ml_components() # Initialize ML service and related UI state
        self.update_ml_controls_frame() # Create ML control widgets
        self.initialize_leds() # Set initial LED states and start loops
        self._update_feature_importance_button_state() # Ensure button is initially disabled
        self.update_param_widgets(self.strategy_var.get()) # Initial params for default strategy
        self.protocol("WM_DELETE_WINDOW", self.on_closing) # Graceful shutdown

        print("Application Initialized.")

    # --------------------------------------------------------------------------
    # Initialization and Configuration Methods
    # --------------------------------------------------------------------------
    # ... (Methods _configure_window, _configure_fonts, _load_optional_modules, _create_widgets,
    #      init_ml_components, update_ml_controls_frame, initialize_leds remain the same
    #      as the previous full version) ...
    def _configure_window(self):
        """Sets up the main window properties."""
        self.title("Retro Trading Console")
        self.geometry("1100x850") # Adjust size as needed
        self.configure(fg_color=COLOR_BACKGROUND)
        # Configure grid layout
        self.grid_columnconfigure(0, weight=3) # Chart area column
        self.grid_columnconfigure(1, weight=1) # Console/Controls column
        self.grid_rowconfigure(0, weight=0) # Header Controls
        self.grid_rowconfigure(1, weight=0) # Chart Controls
        self.grid_rowconfigure(2, weight=0) # Dot Matrix
        self.grid_rowconfigure(3, weight=1) # Main Content (Chart/Console)
        self.grid_rowconfigure(4, weight=0) # Chart Info Label
        self.grid_rowconfigure(5, weight=0) # Backtest Controls
        self.grid_rowconfigure(6, weight=0) # Parameter/ML Controls Frame
        self.grid_rowconfigure(7, weight=0) # LED Frame

    def _configure_fonts(self):
        """Configures fonts used throughout the application."""
        available_fonts = list(tkfont.families())
        # Fallback font if preferred monospace isn't available
        self.mono_font_family = FONT_FAMILY_MONO if FONT_FAMILY_MONO in available_fonts else "Courier"
        print(f"Using font: {self.mono_font_family}")

        self.font_normal = ctk.CTkFont(family=self.mono_font_family, size=FONT_SIZE_NORMAL)
        self.font_large = ctk.CTkFont(family=self.mono_font_family, size=FONT_SIZE_LARGE)
        self.font_button = ctk.CTkFont(family=self.mono_font_family, size=FONT_SIZE_NORMAL, weight="bold")
        self.font_textbox = ctk.CTkFont(family=self.mono_font_family, size=FONT_SIZE_TEXTBOX)
        self.font_led = ctk.CTkFont(family=self.mono_font_family, size=FONT_SIZE_LED)

    def _load_optional_modules(self):
        """Attempts to load optional TA-Lib and Ephem modules."""
        try:
            import talib
            self.talib_module = talib
            print("TA-Lib imported successfully.")
        except ImportError:
            print("Failed to import TA-Lib. Some features might be unavailable.")
            # Log to console as well?
            # self.after(100, lambda: self.log_message("Warning: TA-Lib not found. RSI, MACD, BBands, ADX calculations disabled.", tag="negative"))

        try:
            import ephem
            self.ephem_module = ephem
            print("Ephem imported successfully.")
        except ImportError:
            print("Failed to import Ephem. RealMoonStrategy will be unavailable.")
            # self.after(100, lambda: self.log_message("Warning: Ephem not found. RealMoonStrategy disabled.", tag="negative"))


    def _create_widgets(self):
        """Creates and grids all the main UI widgets."""

        # --- Header / Data Controls Frame (Row 0) ---
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 5), sticky="ew")
        # Symbol Select
        ctk.CTkLabel(self.controls_frame, text="Symbol:", font=self.font_normal, text_color=COLOR_FOREGROUND).pack(side="left", padx=(0, 5))
        self.symbol_var = ctk.StringVar(value=SYMBOLS[0])
        self.symbol_dropdown = ctk.CTkComboBox(
            self.controls_frame, values=SYMBOLS, variable=self.symbol_var, width=100,
            font=self.font_normal, text_color=COLOR_DROPDOWN_FG, fg_color=COLOR_DROPDOWN_BG,
            dropdown_fg_color=COLOR_DROPDOWN_BG, button_color=COLOR_DROPDOWN_BUTTON,
            button_hover_color=COLOR_DROPDOWN_BUTTON_HOVER, border_color=COLOR_BUTTON, border_width=1,
            command=self.on_symbol_change
        )
        self.symbol_dropdown.pack(side="left", padx=(0, 10))
        # Custom Symbol Input
        ctk.CTkLabel(self.controls_frame, text="Custom:", font=self.font_normal, text_color=COLOR_FOREGROUND).pack(side="left", padx=(10, 5))
        self.custom_symbol_entry = ctk.CTkEntry(
            self.controls_frame, width=70, font=self.font_normal,
            text_color=COLOR_DROPDOWN_FG, fg_color=COLOR_DROPDOWN_BG,
            border_color=COLOR_BUTTON, border_width=1
        )
        # Bind Enter key in custom entry to load data
        self.custom_symbol_entry.bind("<Return>", lambda event: self.fetch_and_display_data())
        self.custom_symbol_entry.pack(side="left", padx=(0, 20))
        # Load Data Button
        self.fetch_button = ctk.CTkButton(
            self.controls_frame, text="Load Data", command=self.fetch_and_display_data,
            font=self.font_button, text_color=COLOR_BACKGROUND,
            fg_color=COLOR_BUTTON, hover_color=COLOR_BUTTON_HOVER
        )
        self.fetch_button.pack(side="left", padx=(0, 30))

        # --- Chart Controls Frame (Row 1) ---
        self.chart_controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.chart_controls_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 5), sticky="ew")
        ctk.CTkLabel(self.chart_controls_frame, text="Chart Period:", font=self.font_normal, text_color=COLOR_FOREGROUND).pack(side="left", padx=(0, 10))
        lookback_periods = ["ALL", "YTD", "1Y", "6M", "3M", "1M"]
        self.chart_period_buttons = {} # Store buttons for highlighting
        for period in lookback_periods:
            btn = ctk.CTkButton(
                self.chart_controls_frame, text=period,
                font=self.font_normal, width=40, height=24, text_color=COLOR_FOREGROUND,
                fg_color=COLOR_SECONDARY_BUTTON, hover_color=COLOR_SECONDARY_BUTTON_HOVER
            )
            # Use lambda with default arguments to capture current period and button instance
            btn.configure(command=lambda p=period, b=btn: self._handle_chart_period_click(p, b))
            btn.pack(side="left", padx=(0, 5))
            self.chart_period_buttons[period] = btn
        # Highlight the default 'ALL' button initially
        self._highlight_chart_period_button("ALL")


        # --- Dot Matrix Recommendation Display (Row 2) ---
        self.recommendation_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.recommendation_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=(10, 10), sticky="") # Centered
        self.recommendation_display = MatrixText(
            self.recommendation_frame, rows=MATRIX_ROWS, cols=MATRIX_TOTAL_COLS,
            pixel_size=MATRIX_PIXEL_SIZE, char_spacing=MATRIX_SPACING, bg_color=MATRIX_BG,
            default_on_color=RECOMMENDATION_HEX_COLORS['DEFAULT'] # Pass default HEX color
        )
        self.recommendation_display.get_frame().pack()
        # self.recommendation_display.display_text(" " * MATRIX_COLS) # Initial blank display done by clear() in init flow

        # --- Chart Area (Row 3, Column 0) ---
        self.chart_frame = ctk.CTkFrame(self, fg_color=COLOR_CHART_BG, border_color=COLOR_BUTTON, border_width=1)
        self.chart_frame.grid(row=3, column=0, rowspan=1, padx=(20, 10), pady=5, sticky="nsew")
        self.chart_frame.grid_rowconfigure(0, weight=1)
        self.chart_frame.grid_columnconfigure(0, weight=1)
        # Setup Matplotlib Figure and Axes
        self.fig, self.ax = plt.subplots()
        self.fig.set_facecolor(COLOR_CHART_BG)
        self._style_chart_axes() # Apply axes styling
        # Initial placeholder text
        self.ax.text(0.5, 0.5, 'Select symbol and click Load Data',
                     horizontalalignment='center', verticalalignment='center',
                     transform=self.ax.transAxes, color=COLOR_CHART_AXES,
                     fontsize=self.font_large.cget('size'))
        # Embed chart in Tkinter
        self.chart_canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.chart_canvas_widget = self.chart_canvas.get_tk_widget()
        self.chart_canvas_widget.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.chart_canvas.draw()
        self.chart_canvas.mpl_connect('motion_notify_event', self.on_chart_motion) # Hover effect

        # --- Console Output Textbox (Row 3, Column 1) ---
        self.output_textbox = ctk.CTkTextbox(
            self, font=self.font_textbox, text_color=COLOR_TEXTBOX_FG, fg_color=COLOR_TEXTBOX_BG,
            border_color=COLOR_BUTTON, border_width=1, wrap="word", # Enable word wrap
            activate_scrollbars=True
        )
        self.output_textbox.grid(row=3, column=1, rowspan=1, padx=(10, 20), pady=5, sticky="nsew")
        # Configure tags for colored text
        self.output_textbox.tag_config("positive", foreground=COLOR_POSITIVE)
        self.output_textbox.tag_config("negative", foreground=COLOR_NEGATIVE)
        self.output_textbox.tag_config("neutral", foreground=COLOR_NEUTRAL)
        self.output_textbox.tag_config("weak_positive", foreground=COLOR_WEAK_POSITIVE)
        self.output_textbox.tag_config("weak_negative", foreground=COLOR_WEAK_NEGATIVE)
        # Initial message
        self.log_message("Retro Trading Console Initialized.", clear_first=True)
        self.log_message("Select symbol, load data, then select and run a backtest or train ML.")
        self.output_textbox.configure(state="disabled") # Make read-only initially

        # --- Chart Info Label (Row 4) ---
        self.chart_info_label = ctk.CTkLabel(self, text="", font=self.font_normal, text_color=COLOR_FOREGROUND, anchor="w")
        self.chart_info_label.grid(row=4, column=0, columnspan=2, padx=20, pady=(0, 5), sticky="ew")

        # --- Backtesting Controls Frame (Row 5) ---
        self.backtest_controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.backtest_controls_frame.grid(row=5, column=0, columnspan=2, padx=20, pady=(0, 5), sticky="ew")
        # Strategy Select
        ctk.CTkLabel(self.backtest_controls_frame, text="Strategy:", font=self.font_normal, text_color=COLOR_FOREGROUND).pack(side="left", padx=(0, 10))
        self.strategy_var = ctk.StringVar(value=list(STRATEGY_LOADERS.keys())[0])
        self.strategy_dropdown = ctk.CTkComboBox(
            self.backtest_controls_frame, values=list(STRATEGY_LOADERS.keys()), variable=self.strategy_var,
            font=self.font_normal, text_color=COLOR_DROPDOWN_FG, fg_color=COLOR_DROPDOWN_BG,
            dropdown_fg_color=COLOR_DROPDOWN_BG, button_color=COLOR_DROPDOWN_BUTTON,
            button_hover_color=COLOR_DROPDOWN_BUTTON_HOVER, border_color=COLOR_BUTTON, border_width=1,
            command=self.update_param_widgets # Update params when strategy changes
        )
        self.strategy_dropdown.pack(side="left", padx=(0, 15))
        # Info Button
        self.info_button = ctk.CTkButton(
            self.backtest_controls_frame, text="Info", command=self.show_strategy_info,
            font=self.font_button, text_color=COLOR_FOREGROUND, width=50,
            fg_color=COLOR_SECONDARY_BUTTON, hover_color=COLOR_SECONDARY_BUTTON_HOVER
        )
        self.info_button.pack(side="left", padx=(0,15))
        # Run Backtest Button (Pack to the right)
        self.run_backtest_button = ctk.CTkButton(
            self.backtest_controls_frame, text="Run Backtest", command=self.run_selected_backtest,
            font=self.font_button, text_color=COLOR_BACKGROUND,
            fg_color=COLOR_ACCENT, hover_color=COLOR_BUTTON_HOVER # Use accent color
        )
        self.run_backtest_button.pack(side="right", padx=(15, 0))

        # --- Parameter & ML Controls Frame Container (Row 6) ---
        self.param_ml_container = ctk.CTkFrame(self, fg_color="transparent")
        self.param_ml_container.grid(row=6, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="ew")
        self.param_ml_container.grid_columnconfigure(0, weight=1) # Parameters area stretches
        self.param_ml_container.grid_columnconfigure(1, weight=0) # ML controls area fixed size

        # --- Parameter Frame (Inside Container, Column 0) ---
        self.param_frame = ctk.CTkFrame(self.param_ml_container, fg_color="transparent")
        self.param_frame.grid(row=0, column=0, sticky="w")
        # Initial parameters will be populated by update_param_widgets

        # --- ML Controls Frame (Inside Container, Column 1) ---
        self.ml_controls_frame = ctk.CTkFrame(self.param_ml_container, fg_color="transparent")
        self.ml_controls_frame.grid(row=0, column=1, sticky="e")
        # Widgets populated by update_ml_controls_frame


        # --- LED Frame (Row 7) ---
        self.led_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.led_frame.grid(row=7, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew") # Increased bottom padding
        self.leds = {} # Dictionary to hold LED widgets
        led_configs = [
            ("PWR", COLOR_LED_PWR_ON), ("CPU", COLOR_LED_CPU_ON), ("DATA", COLOR_LED_DATA_ON),
            ("COM", COLOR_LED_COM_ON), ("ERR", COLOR_LED_PWR_ON) # ERR uses PWR color
        ]
        app_bg_color = self.cget("fg_color") # Get actual background color
        for name, on_color in led_configs:
            led_container = ctk.CTkFrame(self.led_frame, fg_color="transparent")
            led_container.pack(side="left", padx=10) # Space out LEDs
            led_label = ctk.CTkLabel(led_container, text=name, font=self.font_led, text_color=COLOR_FOREGROUND)
            led_label.pack(side="top")
            led_indicator = WornLED(
                led_container, color=on_color, size=20,
                explicit_canvas_bg=app_bg_color # Pass background for better look
            )
            led_indicator.pack(side="top", pady=(2,0))
            led_indicator.set_wear_level(0.7) # Set default wear
            self.leds[name.upper()] = led_indicator # Use upper case key
            # Add easter egg binding only to PWR LED
            if name == "PWR":
                led_indicator.bind("<Button-1>", self.show_easter_egg)
                led_label.bind("<Button-1>", self.show_easter_egg) # Bind label too

    def init_ml_components(self):
        """Initialize ML service and add ML LED."""
        print("Initializing ML components...")
        self.ml_service = MlPredictionService(model_dir=ML_MODEL_DIR)
        self.ml_model_loaded = False
        self.ml_prediction = None
        self.latest_feature_importances = None

        # Add the ML LED dynamically if frame exists
        if hasattr(self, 'led_frame') and self.led_frame.winfo_exists():
            app_bg_color = self.cget("fg_color")
            led_container = ctk.CTkFrame(self.led_frame, fg_color="transparent")
            led_container.pack(side="left", padx=10)
            led_label = ctk.CTkLabel(led_container, text="ML", font=self.font_led, text_color=COLOR_FOREGROUND)
            led_label.pack(side="top")
            led_indicator = WornLED(
                led_container, color=COLOR_LED_ML_ON, size=20,
                explicit_canvas_bg=app_bg_color
            )
            led_indicator.pack(side="top", pady=(2, 0))
            led_indicator.set_wear_level(0.7)
            self.leds["ML"] = led_indicator # Add to dict using upper case key
        else:
             print("Warning: LED frame not ready for ML LED initialization.")


    def update_ml_controls_frame(self):
        """Creates or updates the widgets within the ML controls frame."""
        # Clear existing widgets first
        if hasattr(self, 'ml_controls_frame'):
            for widget in self.ml_controls_frame.winfo_children():
                widget.destroy()
        else:
             print("Error: ml_controls_frame not found during update.")
             return

        # --- Train Button ---
        train_btn = ctk.CTkButton(
            self.ml_controls_frame, text="Train ML Model", command=self.train_ml_model,
            font=self.font_button, text_color=COLOR_BACKGROUND, width=130,
            fg_color=COLOR_LED_ML_ON, hover_color=COLOR_SECONDARY_BUTTON_HOVER
        )
        train_btn.grid(row=0, column=0, padx=(0, 10), pady=2)

        # --- Show Features Button ---
        self.show_features_button = ctk.CTkButton(
            self.ml_controls_frame, text="Show Features", command=self.show_feature_importance_popup,
            font=self.font_button, text_color=COLOR_FOREGROUND, width=120,
            fg_color=COLOR_SECONDARY_BUTTON, hover_color=COLOR_SECONDARY_BUTTON_HOVER,
            state="disabled" # Initially disabled
        )
        self.show_features_button.grid(row=0, column=1, padx=(0, 10), pady=2)

        # --- ML Parameters Row ---
        param_row_frame = ctk.CTkFrame(self.ml_controls_frame, fg_color="transparent")
        param_row_frame.grid(row=1, column=0, columnspan=2, pady=(5, 2), sticky="ew")

        # Horizon
        ctk.CTkLabel(param_row_frame, text="Horizon:", font=self.font_normal, text_color=COLOR_FOREGROUND).pack(side="left", padx=(0, 5))
        self.ml_horizon_var = ctk.StringVar(value=str(self.ml_default_horizon))
        ctk.CTkEntry(
            param_row_frame, textvariable=self.ml_horizon_var, width=40, font=self.font_normal,
            text_color=COLOR_DROPDOWN_FG, fg_color=COLOR_DROPDOWN_BG,
            border_color=COLOR_BUTTON, border_width=1
        ).pack(side="left", padx=(0, 2))
        ctk.CTkLabel(param_row_frame, text="d", font=self.font_normal, text_color=COLOR_FOREGROUND).pack(side="left", padx=(0, 10))

        # Model Type
        ctk.CTkLabel(param_row_frame, text="Model:", font=self.font_normal, text_color=COLOR_FOREGROUND).pack(side="left", padx=(0, 5))
        # Ensure ModelManager class is available to get model types
        try:
            model_types = list(ModelManager.CLASSIFICATION_MODELS.keys())
        except AttributeError:
            model_types = ["random_forest"] # Fallback
            print("Warning: Could not get model types from ModelManager.")
        self.ml_model_type_var = ctk.StringVar(value=model_types[0] if model_types else "")
        ctk.CTkComboBox(
            param_row_frame, values=model_types, variable=self.ml_model_type_var, width=140,
            font=self.font_normal, text_color=COLOR_DROPDOWN_FG, fg_color=COLOR_DROPDOWN_BG,
            dropdown_fg_color=COLOR_DROPDOWN_BG, button_color=COLOR_DROPDOWN_BUTTON,
            button_hover_color=COLOR_DROPDOWN_BUTTON_HOVER, border_color=COLOR_BUTTON, border_width=1
        ).pack(side="left", padx=(0, 10))

        # Threshold
        ctk.CTkLabel(param_row_frame, text="Thr(%):", font=self.font_normal, text_color=COLOR_FOREGROUND).pack(side="left", padx=(0, 5))
        self.ml_threshold_var = ctk.StringVar(value=str(self.ml_default_threshold_pct)) # Use initialized default
        ctk.CTkEntry(
            param_row_frame, textvariable=self.ml_threshold_var, width=40, font=self.font_normal,
            text_color=COLOR_DROPDOWN_FG, fg_color=COLOR_DROPDOWN_BG,
            border_color=COLOR_BUTTON, border_width=1
        ).pack(side="left", padx=(0, 10))

        # Test Split
        ctk.CTkLabel(param_row_frame, text="Test(%):", font=self.font_normal, text_color=COLOR_FOREGROUND).pack(side="left", padx=(0, 5))
        self.ml_test_split_var = ctk.StringVar(value=str(ML_TRAIN_TEST_SPLIT * 100)) # Default from config
        ctk.CTkEntry(
            param_row_frame, textvariable=self.ml_test_split_var, width=40, font=self.font_normal,
            text_color=COLOR_DROPDOWN_FG, fg_color=COLOR_DROPDOWN_BG,
            border_color=COLOR_BUTTON, border_width=1
        ).pack(side="left", padx=(0, 0))


    def initialize_leds(self):
        """Sets initial LED states and starts background loops."""
        print("Initializing LEDs...")
        for name, led_widget in self.leds.items():
            # Ensure widget exists before configuring
            if led_widget and led_widget.winfo_exists():
                if name == "PWR":
                    print("Setting PWR LED ON")
                    led_widget.set_state("on")
                    led_widget.enable_flicker(True)
                else:
                    led_widget.set_state("off")
                    led_widget.enable_flicker(False) # Ensure others don't flicker initially
            else:
                print(f"Warning: LED widget '{name}' not found or destroyed during initialization.")

        # Start background loops if they aren't running
        if self.activity_led_job is None:
            # print("Starting activity LED loop...") # Debug
            self._update_activity_leds()
        if self.matrix_update_job is None:
            # print("Starting matrix display loop...") # Debug
            # Use _start_matrix_loop_if_needed to prevent multiple loops if called again
            self._start_matrix_loop_if_needed()


    # --------------------------------------------------------------------------
    # Core Application Logic Methods
    # --------------------------------------------------------------------------

    def fetch_and_display_data(self):
        """Fetches data, handles timezone, plots, calculates TA, and triggers prediction."""
        custom_symbol = self.custom_symbol_entry.get().strip().upper()
        selected_symbol = custom_symbol if custom_symbol else self.symbol_var.get()

        # --- REMOVED CHECK: Allow reloading the same symbol ---
        # if selected_symbol == self.current_symbol and self.current_data is not None:
        #      print(f"Data for {self.current_symbol} already loaded.")
        #      return # Avoid redundant processing
        # --- END REMOVED CHECK ---

        self.current_symbol = selected_symbol

        if not self.current_symbol:
            self.log_message("Error: No symbol selected or entered.", clear_first=True, tag="negative")
            return

        self._loading_data = True # Flag for placeholder text
        self.clear_display() # Show "Loading data...", clears matrix, restarts loop
        self.log_message(f"--- Loading data for {self.current_symbol} ---", clear_first=True)
        self.set_led_state("CPU", "on", flicker=False) # Solid CPU light during load
        self.update_idletasks() # Ensure "Loading..." text appears

        # Reset states for new load
        self.current_data = None
        self.plotted_data = None
        self.latest_price = None
        self.latest_ta_results = None
        self.latest_recommendation = "LOADING..." # Update matrix state
        self.latest_technical_score = 0.0
        self.latest_adx = None
        self.latest_feature_importances = None
        self._update_feature_importance_button_state() # Disable feature button
        self.ml_prediction = None
        self.ml_model_loaded = False

        self._update_matrix_display(force_update=True) # Show "LOADING..."
        # No need to restart loop here, clear_display already did

        try:
            # --- Fetch Data ---
            self.current_data = self.data_fetcher.get_historical_data(
                self.current_symbol,
                period=DEFAULT_DATA_PERIOD,
                interval=DEFAULT_DATA_INTERVAL
            )

            if self.current_data is not None and not self.current_data.empty:
                # --- Process Data ---
                if isinstance(self.current_data.index, pd.DatetimeIndex) and self.current_data.index.tz is not None:
                    self.current_data.index = self.current_data.index.tz_localize(None)
                self.log_message(f"Successfully loaded {len(self.current_data)} data points.")
                self.log_message(f"Data range: {self.current_data.index.min().strftime('%Y-%m-%d')} to {self.current_data.index.max().strftime('%Y-%m-%d')}")

                # --- Plot Data ---
                self.plot_data(self.current_data, title_suffix=f" ({DEFAULT_DATA_PERIOD})")
                self.log_message("Chart updated.")
                self.update_idletasks() # Force UI update after plot

                # --- Calculate and Log TA Indicators ---
                self.latest_ta_results = self._calculate_ta_indicators()
                if self.latest_ta_results:
                    self.latest_recommendation = self.latest_ta_results['recommendation'] # Update main rec variable
                    self.latest_technical_score = self.latest_ta_results['score']
                    self.latest_adx = self.latest_ta_results['adx']
                    self.log_message(f"\n--- Technical Analysis ---")
                    self.log_message(f"TA Recommendation: {self.latest_recommendation} (Score: {self.latest_technical_score:.1f}, ADX: {self.latest_adx:.1f})")
                else:
                    self.log_message("Could not calculate TA indicators.", tag="negative")
                    self.latest_recommendation = "N/A" # Set state if TA fails
                self._update_matrix_display(force_update=True) # Update matrix with TA result
                # --- Restart matrix loop after forced update ---
                self._start_matrix_loop_if_needed()


                # --- Get Current Price ---
                current_price = self.data_fetcher.get_current_price(self.current_symbol)
                self.latest_price = current_price
                if current_price: self.log_message(f"Approx. Current Price: {current_price:.2f}")

                # --- Trigger ML Prediction/Load AFTER TA ---
                self.generate_ml_prediction() # This might call hybrid, which forces matrix update again

            else:
                # Handle no data case
                self.log_message(f"Failed to load data or no data available for {self.current_symbol}.", tag="negative")
                self.plot_data(None)
                self.latest_recommendation = "NO DATA" # Update main rec variable
                self._update_matrix_display(force_update=True)
                self._start_matrix_loop_if_needed() # Ensure loop restarts even on failure


        except Exception as e:
            self.log_message(f"An error occurred during data fetch/display: {e}", tag="negative")
            print(f"Error during data fetch/display: {e}")
            traceback.print_exc()
            self.plot_data(None)
            self.current_data = None
            self.latest_recommendation = "ERROR" # Update main rec variable
            self._update_matrix_display(force_update=True)
            self._start_matrix_loop_if_needed() # Ensure loop restarts even on error


        finally:
            self._loading_data = False
            self.set_led_state("CPU", "off")


    def plot_data(self, data_to_plot: pd.DataFrame | None, title_suffix: str = ""):
        """Plots the given data on the main chart canvas."""
        # --- (Implementation from previous fix - app_py_plot_update_fix) ---
        self.ax.clear()
        self.plotted_data = None
        self._style_chart_axes() # Apply base styling

        if data_to_plot is None or data_to_plot.empty:
            self.ax.text(0.5, 0.5, f"No data to plot for {self.current_symbol}",
                         color=COLOR_CHART_AXES, ha='center', va='center',
                         transform=self.ax.transAxes, fontsize=self.font_large.cget('size'))
            self.ax.set_xticks([]); self.ax.set_yticks([]) # Clear ticks for placeholder
        elif 'close' not in data_to_plot.columns:
            self.log_message("Error: 'close' column not found in data. Cannot plot chart.", tag="negative")
            self.ax.text(0.5, 0.5, "Error plotting data", color=COLOR_ACCENT,
                         ha='center', va='center', transform=self.ax.transAxes,
                         fontsize=self.font_large.cget('size'))
            self.ax.set_xticks([]); self.ax.set_yticks([])
        else:
            try:
                # Plotting Logic
                self.ax.plot(data_to_plot.index, data_to_plot['close'], color=COLOR_CHART_LINE, linewidth=1.5)
                self.ax.set_title(f"{self.current_symbol} Price{title_suffix}", color=COLOR_CHART_AXES)
                self.ax.set_ylabel("Price (USD)", color=COLOR_CHART_AXES)
                self.ax.set_xlabel("Date", color=COLOR_CHART_AXES)

                # Formatting
                self.fig.autofmt_xdate()
                date_range = data_to_plot.index.max() - data_to_plot.index.min()
                if date_range.days > 365 * 2: formatter = mdates.DateFormatter('%Y')
                elif date_range.days > 90: formatter = mdates.DateFormatter('%b %Y')
                else: formatter = mdates.DateFormatter('%Y-%m-%d')
                self.ax.xaxis.set_major_formatter(formatter)
                self.ax.tick_params(axis='x', colors=COLOR_CHART_AXES, rotation=30)
                self.ax.tick_params(axis='y', colors=COLOR_CHART_AXES)
                self.ax.grid(True, color=COLOR_DROPDOWN_BG, linestyle='--', linewidth=0.5)
                self.plotted_data = data_to_plot # Store reference after plotting

            except Exception as plot_err:
                 self.log_message(f"Error during plotting: {plot_err}", tag="negative")
                 print(f"Error plotting data: {plot_err}")
                 traceback.print_exc()
                 self.ax.text(0.5, 0.5, "Error during plotting", color=COLOR_ACCENT,
                              ha='center', va='center', transform=self.ax.transAxes,
                              fontsize=self.font_large.cget('size'))
                 self.ax.set_xticks([]); self.ax.set_yticks([])

        # Redraw Canvas
        if hasattr(self, 'chart_canvas'):
            try:
                self.chart_canvas.draw_idle()
            except Exception as e:
                print(f"Error redrawing chart canvas: {e}")


    def _style_chart_axes(self):
        """Helper to apply consistent styling to chart axes."""
        self.ax.set_facecolor(COLOR_CHART_BG)
        self.ax.tick_params(axis='x', colors=COLOR_CHART_AXES)
        self.ax.tick_params(axis='y', colors=COLOR_CHART_AXES)
        self.ax.yaxis.label.set_color(COLOR_CHART_AXES)
        self.ax.xaxis.label.set_color(COLOR_CHART_AXES)
        self.ax.title.set_color(COLOR_CHART_AXES)
        for spine in self.ax.spines.values():
            spine.set_color(COLOR_CHART_AXES)


    def clear_display(self):
        """Clears the chart and info label, showing placeholder text."""
        self.ax.clear()
        self.plotted_data = None
        self._style_chart_axes() # Apply base styling

        placeholder = 'Loading data...' if hasattr(self, '_loading_data') and self._loading_data else 'Select symbol and click Load Data'
        self.ax.text(0.5, 0.5, placeholder,
                     horizontalalignment='center', verticalalignment='center',
                     transform=self.ax.transAxes, color=COLOR_CHART_AXES,
                     fontsize=self.font_large.cget('size'))

        self.ax.set_xlabel("")
        self.ax.set_ylabel("")
        self.ax.set_title("")
        self.ax.set_xticks([])
        self.ax.set_yticks([])

        if hasattr(self, 'chart_canvas'):
            try:
                self.chart_canvas.draw_idle()
            except Exception as e:
                print(f"Error redrawing chart canvas during clear: {e}")
        if hasattr(self, 'chart_info_label'):
             self.chart_info_label.configure(text="")

        # --- FIX: Call clear() on the matrix display ---
        if hasattr(self, 'recommendation_display') and self.recommendation_display.get_frame().winfo_exists():
             if self.matrix_update_job: # Cancel loop first
                  try: self.after_cancel(self.matrix_update_job); self.matrix_update_job = None
                  except tk.TclError: pass
             self.recommendation_display.clear() # Use the clear method
             # Ensure loop restarts after clear display forces update
             self._start_matrix_loop_if_needed()
        # --- END FIX ---


    # --------------------------------------------------------------------------
    # Technical Analysis Logic
    # --------------------------------------------------------------------------

    def _calculate_ta_indicators(self) -> Optional[Dict]:
        """
        Calculates standard TA indicators and generates a recommendation score.
        Uses self.current_data.

        Returns:
            A dictionary containing 'recommendation', 'score', 'adx',
            and potentially other calculated indicators, or None if calculation fails.
        """
        # --- (Full implementation from previous fix - app_py_ta_log_fix) ---
        if self.current_data is None or self.current_data.empty: return None
        if self.talib_module is None:
            # Attempt import if needed
            try:
                import talib
                self.talib_module = talib
            except ImportError:
                self.log_message("TA-Lib not loaded. Cannot calculate TA.", tag="negative")
                return None

        required_length = max(REC_SMA_LONG, REC_ADX_PERIOD, REC_RSI_PERIOD)
        if len(self.current_data) < required_length:
            self.log_message(f"Insufficient data ({len(self.current_data)}) for TA (need {required_length}).", tag="negative")
            return None

        try:
            required_cols = ['close', 'high', 'low']
            if not all(col in self.current_data.columns for col in required_cols):
                 missing_cols_str = ", ".join([c for c in required_cols if c not in self.current_data.columns])
                 self.log_message(f"TA Calc Error: Missing required columns: {missing_cols_str}", tag="negative")
                 return None

            close_prices = self.current_data['close']
            high_prices = self.current_data['high']
            low_prices = self.current_data['low']

            # Calculate Indicators
            sma_short = self.talib_module.SMA(close_prices, timeperiod=REC_SMA_SHORT)
            sma_long = self.talib_module.SMA(close_prices, timeperiod=REC_SMA_LONG)
            rsi = self.talib_module.RSI(close_prices, timeperiod=REC_RSI_PERIOD)
            adx = self.talib_module.ADX(high_prices, low_prices, close_prices, timeperiod=REC_ADX_PERIOD)

            # Get latest values safely
            latest_sma_short = sma_short.iloc[-1] if not sma_short.empty else np.nan
            latest_sma_long = sma_long.iloc[-1] if not sma_long.empty else np.nan
            latest_rsi = rsi.iloc[-1] if not rsi.empty else np.nan
            latest_adx = adx.iloc[-1] if not adx.empty else np.nan

            if pd.isna(latest_sma_short) or pd.isna(latest_sma_long) or pd.isna(latest_rsi) or pd.isna(latest_adx):
                self.log_message("TA Calc Warning: Incomplete indicator calculation.", tag="negative")
                return None

            # Scoring Logic
            score = 0.0; trend_score = 0.0
            if latest_sma_short > latest_sma_long: trend_score += 1.0
            elif latest_sma_short < latest_sma_long: trend_score -= 1.0
            is_trending = latest_adx > REC_ADX_THRESHOLD
            score += trend_score * (1.5 if is_trending else 0.5)
            if latest_rsi > REC_RSI_BUY: score += 1.0
            elif latest_rsi < REC_RSI_SELL: score -= 1.0

            # Determine recommendation string
            recommendation = "HOLD"
            if score >= 2.0: recommendation = "BUY"
            elif score >= 0.5: recommendation = "WEAK BUY"
            elif score <= -2.0: recommendation = "SELL"
            elif score <= -0.5: recommendation = "WEAK SELL"

            results = {
                'recommendation': recommendation, 'score': score, 'adx': latest_adx,
                'rsi': latest_rsi, 'sma_short': latest_sma_short, 'sma_long': latest_sma_long
            }
            return results

        except Exception as e:
            self.log_message(f"Error calculating TA indicators: {e}", tag="negative")
            print(f"Error calculating TA indicators: {e}"); traceback.print_exc()
            return None


    # --------------------------------------------------------------------------
    # Machine Learning Logic Methods
    # --------------------------------------------------------------------------

    def generate_ml_prediction(self):
        """Loads ML model if needed, runs prediction, and triggers hybrid recommendation."""
        # --- (Implementation from previous fix - app_py_ta_log_fix) ---
        self.latest_feature_importances = None
        self._update_feature_importance_button_state()
        self._predicting_ml = True

        custom_symbol = self.custom_symbol_entry.get().strip().upper()
        symbol_used = custom_symbol if custom_symbol else self.symbol_var.get()

        # Load Model
        if not self.ml_model_loaded:
            try:
                horizon = int(self.ml_horizon_var.get())
            except ValueError: horizon = self.ml_default_horizon
            try:
                self.log_message(f"\n--- Machine Learning ---")
                self.log_message(f"Attempting to load model for {symbol_used} (Horizon: {horizon}d)...")
                model_loaded = self.ml_service.load_model_for_symbol(symbol_used, prediction_horizon=horizon)
                if not model_loaded:
                    self.log_message(f"No pre-trained model found. Proceeding with TA only.")
                    self._predicting_ml = False; self._update_matrix_display(force_update=True); self._start_matrix_loop_if_needed(); return # Restart loop on fail
                self.ml_model_loaded = True
                loaded_meta = self.ml_service.get_loaded_model_metadata()
                model_name = loaded_meta.get('model_class_name', 'Unknown') if loaded_meta else 'Unknown'
                self.log_message(f"Successfully loaded model: {model_name}")
                self.latest_feature_importances = self.ml_service.get_loaded_feature_importances()
                self._update_feature_importance_button_state()
            except Exception as e:
                self.log_message(f"Error loading ML model: {e}", tag="negative")
                self._predicting_ml = False; self._update_matrix_display(force_update=True); self._start_matrix_loop_if_needed(); return # Restart loop on fail

        # Run Prediction
        if self.current_data is None or self.current_data.empty:
            self.log_message("Error: No data loaded. Cannot generate ML prediction.", tag="negative")
            self._predicting_ml = False; return

        loaded_meta = self.ml_service.get_loaded_model_metadata()
        model_name = loaded_meta.get('model_class_name', 'Unknown') if loaded_meta else 'Unknown'
        horizon = loaded_meta.get('horizon', '?') if loaded_meta else '?'
        self.log_message(f"Generating ML Prediction (Model: {model_name}, Horizon: {horizon}d)...")
        self.set_led_state("ML", "on", flicker=False)
        self.update_idletasks()

        try:
            try:
                 significance_pct = float(self.ml_threshold_var.get())
                 threshold = significance_pct / 100.0
            except ValueError: threshold = 0.01 # Fallback

            self.ml_prediction = self.ml_service.predict(self.current_data.copy(), target_threshold=threshold)

            if 'error' in self.ml_prediction:
                 self.log_message(f"ML Prediction Error: {self.ml_prediction['error']}", tag="negative")
                 self.ml_prediction = None
            else:
                 self.log_message(f"ML Direction: {self.ml_prediction.get('direction')}")
                 confidence = self.ml_prediction.get('confidence')
                 confidence_str = f"{confidence:.3f}" if confidence is not None else "N/A"
                 self.log_message(f"ML Confidence: {confidence_str}")
                 self.log_message(f"ML Confidence Level: {self.ml_prediction.get('confidence_level', 'UNKNOWN')}")

            if self.ml_enable_hybrid and self.ml_prediction and self.latest_ta_results:
                self.generate_hybrid_recommendation() # This will force update matrix and restart loop
            else:
                 self._update_matrix_display(force_update=True) # Show TA result if hybrid off/failed
                 self._start_matrix_loop_if_needed() # Restart loop

        except Exception as e:
            self.log_message(f"Error during ML prediction step: {e}", tag="negative")
            print(f"Error during ML prediction step: {e}"); traceback.print_exc()
            self.ml_prediction = None; self._update_matrix_display(force_update=True); self._start_matrix_loop_if_needed(); # Restart loop
        finally:
            self.set_led_state("ML", "off"); self._predicting_ml = False


    def generate_hybrid_recommendation(self):
        """Gets hybrid recommendation using stored TA and ML results."""
        # --- (Implementation from previous fix - app_py_ta_log_fix) ---
        if not self.ml_enable_hybrid: return
        if self.ml_prediction is None or 'error' in self.ml_prediction:
            self._update_matrix_display(force_update=True); self._start_matrix_loop_if_needed(); return # Restart loop
        if self.latest_ta_results is None: return

        self.log_message(f"\n--- Hybrid Recommendation ---")
        self.set_led_state("CPU", "on", flicker=True)
        self.update_idletasks()

        try:
            try:
                 significance_pct = float(self.ml_threshold_var.get())
                 threshold = significance_pct / 100.0
            except ValueError: threshold = 0.01 # Fallback

            hybrid_result = self.ml_service.get_hybrid_recommendation(
                df=self.current_data.copy(), technical_score=self.latest_technical_score,
                adx_value=self.latest_adx, target_threshold=threshold
            )

            self.log_message(f"Hybrid Recommendation: {hybrid_result.get('recommendation')}")
            self.log_message(f"Hybrid Score: {hybrid_result.get('hybrid_score'):.2f}")

            self.latest_recommendation = hybrid_result.get('recommendation', 'ERROR').upper() # Update main rec variable
            self._update_matrix_display(force_update=True)
            self._start_matrix_loop_if_needed() # Restart loop


        except Exception as e:
            self.log_message(f"Error generating hybrid recommendation: {e}", tag="negative")
            print(f"Error generating hybrid recommendation: {e}"); traceback.print_exc()
            self.latest_recommendation = self.latest_ta_recommendation # Fallback to TA
            self._update_matrix_display(force_update=True)
            self._start_matrix_loop_if_needed() # Restart loop
        finally:
            self.set_led_state("CPU", "off")


    def train_ml_model(self):
        """Trains, evaluates, and saves an ML model."""
        custom_symbol = self.custom_symbol_entry.get().strip().upper()
        symbol_used = custom_symbol if custom_symbol else self.symbol_var.get()

        if self.current_data is None or self.current_data.empty:
            self.log_message("Error: No data loaded. Please load data first.", tag="negative"); return

        self.latest_feature_importances = None; self._update_feature_importance_button_state()
        self.log_message(f"\n--- Starting ML Training for {symbol_used} ---", clear_first=True)
        self.set_led_state("ML", "on", flicker=True); self.update_idletasks() # Flicker during train

        try:
            # Get parameters
            horizon = int(self.ml_horizon_var.get()); selected_model_type = self.ml_model_type_var.get()
            test_size_pct = float(self.ml_test_split_var.get()); significance_pct = float(self.ml_threshold_var.get())

            # Validate and convert
            if not (0 < test_size_pct < 100): raise ValueError("Test Size % must be between 0 and 100.")
            if significance_pct <= 0: raise ValueError("Significance Threshold % must be positive.")
            if horizon < 1 or horizon > 60: raise ValueError("Horizon must be between 1 and 60 days.")
            test_size = test_size_pct / 100.0; threshold = significance_pct / 100.0

            self.log_message(f"Model: {selected_model_type}, Type: classification, Horizon: {horizon}d, Test Size: {test_size_pct:.1f}%, Threshold: {threshold:.4f}")

            # Call service
            results = self.ml_service.train_model(
                symbol=symbol_used, df=self.current_data.copy(), model_type=selected_model_type,
                prediction_type='classification', prediction_horizon=horizon,
                test_size=test_size, target_threshold=threshold
            )

            # Process results
            model_info = results.get('model_info', {}); metrics = results.get('metrics', {})
            self.log_message("\n--- Training Complete ---")
            self.log_message(f"Model saved: {os.path.basename(model_info.get('path','N/A'))}")
            self.log_message("\n--- Model Performance (Test Set) ---")
            metrics_str = "\n".join([f"{k}: {v:.4f}" for k, v in metrics.items()])
            self.log_message(metrics_str)

            # Store importances and update button
            self.latest_feature_importances = self.ml_service.get_loaded_feature_importances()
            self._update_feature_importance_button_state()
            if self.latest_feature_importances: self.log_message("Feature importances captured. Use 'Show Features' button.")
            else: self.log_message("Feature importances not available for this model type.")

            self.ml_model_loaded = True

            # --- ML LED Change: Keep solid ON after successful train ---
            self.set_led_state("ML", "on", flicker=False)

            # Redraw chart
            self.log_message("Updating chart display after training...")
            self.plot_data(self.current_data)
            self.update_idletasks()

        except ValueError as ve:
             self.log_message(f"Parameter Error: {ve}", tag="negative"); print(f"ML Training Parameter Error: {ve}")
             self.set_led_state("ML", "off") # Turn off on error
        except Exception as e:
            self.log_message(f"Error training ML model: {type(e).__name__} - {e}", tag="negative")
            print("\n--- ML Training Error Traceback ---"); traceback.print_exc(); print("--- End Traceback ---\n")
            self.latest_feature_importances = None; self._update_feature_importance_button_state()
            self.set_led_state("ML", "off") # Turn off on error
        # --- ML LED Change: REMOVED finally block turning ML off ---


    # --------------------------------------------------------------------------
    # Backtesting Logic Methods
    # --------------------------------------------------------------------------

    def run_selected_backtest(self):
        """Runs the backtest using the selected strategy, data, and GUI parameters."""
        # --- (Implementation from previous context - app_py_ta_log_fix) ---
        selected_strategy_name = self.strategy_var.get()
        strategy_loader = STRATEGY_LOADERS.get(selected_strategy_name)
        custom_symbol = self.custom_symbol_entry.get().strip().upper()
        symbol_used = custom_symbol if custom_symbol else self.symbol_var.get()

        if strategy_loader is None:
            self.log_message(f"Error: Strategy loader not found for {selected_strategy_name}.", tag="negative"); return
        if self.current_data is None or self.current_data.empty:
            self.log_message(f"Error: No data loaded for {symbol_used} to run backtest.", tag="negative"); return

        # Collect parameters
        strategy_params = {}; default_params = {name: default for name, default in PARAM_CONFIG.get(selected_strategy_name, [])}
        param_log_list = []
        for param_name, param_var in self.param_entries.items():
            value = None; default_val = default_params.get(param_name)
            try:
                value_str = param_var.get()
                if isinstance(default_val, float): value = float(value_str)
                elif isinstance(default_val, int): value = int(value_str)
                else: value = value_str
            except (ValueError, TypeError):
                value = default_val; self.log_message(f"Warning: Invalid value for '{param_name}'. Using default '{value}'.")
            except Exception as e:
                value = default_val; self.log_message(f"Error processing param '{param_name}': {e}. Using default.")

            if param_name == 'trade_size_percent':
                try:
                    size_percent = float(value)
                    if 0 < size_percent <= 100: strategy_params[param_name] = size_percent / 100.0
                    else: raise ValueError("Percentage out of range")
                except (ValueError, TypeError):
                    default_fraction = DEFAULT_TRADE_SIZE_PERCENT / 100.0
                    strategy_params[param_name] = default_fraction
                    self.log_message(f"Warning: Invalid trade size % ({value}). Using default {default_fraction:.1%}")
            else: strategy_params[param_name] = value
            param_log_list.append(f"{param_name}={strategy_params.get(param_name, value)}")

        self.log_message(f"\n--- Running Backtest: {selected_strategy_name} on {symbol_used} ---", clear_first=True)
        self.log_message(f"Params: {', '.join(param_log_list)}")
        self.set_led_state("CPU", "on", flicker=True); self.update_idletasks()

        selected_strategy_class = None; stats = None; bt_results = None
        try:
            # Dynamic Loading
            if isinstance(strategy_loader, str):
                module_path, class_name = strategy_loader.rsplit('.', 1)
                needs_talib = any(s in strategy_loader for s in ["rsi_oscillator", "volatility_breakout", "macd_strategy", "bollinger_bands_strategy"])
                needs_ephem = "real_moon_strategy" in strategy_loader
                if needs_talib and self.talib_module is None: self._load_optional_modules();
                if needs_ephem and self.ephem_module is None: self._load_optional_modules();
                if needs_talib and self.talib_module is None: raise ImportError("TA-Lib is required but failed to load.")
                if needs_ephem and self.ephem_module is None: raise ImportError("Ephem is required but failed to load.")
                strategy_module = importlib.import_module(module_path)
                if needs_talib: setattr(strategy_module, 'talib', self.talib_module)
                if needs_ephem: setattr(strategy_module, 'ephem', self.ephem_module)
                selected_strategy_class = getattr(strategy_module, class_name)
                if class_name == "RealMoonStrategy":
                    if not OBSERVER_LAT or not OBSERVER_LON: raise ValueError("Observer Lat/Lon not set for RealMoonStrategy")
                    selected_strategy_class.OBSERVER_LAT = OBSERVER_LAT
                    selected_strategy_class.OBSERVER_LON = OBSERVER_LON
                    selected_strategy_class.OBSERVER_ELEV = OBSERVER_ELEV
            else: selected_strategy_class = strategy_loader

            if selected_strategy_class is None: raise ValueError("Could not load strategy class.")

            # Run Backtest
            stats, bt_results = run_backtest(
                strategy_class=selected_strategy_class, data=self.current_data.copy(),
                cash=DEFAULT_CASH, commission=DEFAULT_COMMISSION, **strategy_params
            )

            # Log Results
            if stats is not None:
                self.log_message("--- Backtest Results ---"); self._log_backtest_stats(stats)
            else: self.log_message("Backtest failed to produce results.", tag="negative")

        except ImportError as e: self.log_message(f"ImportError: {e}.", tag="negative")
        except Exception as e:
            self.log_message(f"Backtesting Error: {type(e).__name__} - {e}", tag="negative")
            print("\n--- Backtesting Error Traceback ---"); traceback.print_exc(); print("--- End Traceback ---\n")
        finally: self.set_led_state("CPU", "off")


    def _log_backtest_stats(self, stats: pd.Series):
        """Formats and logs backtesting statistics to the console."""
        # --- (Implementation from previous context - app_py_ta_log_fix) ---
        if stats is None or stats.empty: return
        self.output_textbox.configure(state="normal")
        try:
            stats_to_display = stats.drop(index=['_strategy', '_equity_curve', '_trades'], errors='ignore')
            max_key_len = max(len(str(idx)) for idx in stats_to_display.index) if not stats_to_display.empty else 25
            key_width = max(25, max_key_len)
            for idx, value in stats_to_display.items():
                tag = None; value_str = ""; line = ""; idx_str = str(idx)
                if isinstance(value, pd.Timedelta):
                    value_str = str(value).split('.')[0] if not pd.isna(value) else "NaT"
                    line = f"{idx_str:<{key_width}}: {value_str}\n"; tags_to_apply = ()
                else:
                    try:
                        is_numeric = isinstance(value, (int, float, np.number)); numeric_value = float(value) if is_numeric else 0
                        percent_keys = ["Return", "CAGR", "Alpha", "Volatility", "Drawdown", "Trade [%]", "Expectancy [%]", "Win Rate", "Exposure Time"]
                        is_percent = any(pk in idx_str for pk in percent_keys)
                        positive_good_keys = ["Return", "Equity Final", "Profit Factor", "Ratio", "Alpha", "CAGR", "Expectancy", "SQN", "Best Trade", "Avg. Trade", "Win Rate"]
                        is_positive_good = any(pgk in idx_str for pgk in positive_good_keys)
                        if is_numeric:
                            if "Drawdown" in idx_str or "Worst Trade" in idx_str: tag = "negative" if numeric_value < 0 else None
                            elif is_positive_good: tag = "positive" if numeric_value > 0 else ("negative" if numeric_value < 0 else None)
                            elif "Profit Factor" in idx_str: tag = "positive" if numeric_value > 1 else ("negative" if numeric_value < 1 else None)
                        if is_percent: value_str = f"{value:>{14}.2%}"
                        elif "Equity" in idx_str or "Commissions" in idx_str: value_str = f"{value:>{15},.2f}"
                        elif "Ratio" in idx_str or "Beta" in idx_str or "SQN" in idx_str or "Factor" in idx_str: value_str = f"{value:>{15}.2f}"
                        elif isinstance(value, pd.Timestamp): value_str = f"{value.strftime('%Y-%m-%d'):>15}"
                        elif isinstance(value, (int)): value_str = f"{value:>15,}"
                        elif isinstance(value, (float, np.number)): value_str = f"{value:>15.2f}"
                        else: value_str = f"{str(value):>15}"
                    except Exception as fmt_e: print(f"Fmt Err: {fmt_e}"); value_str = "[FMT_ERR]"
                    line = f"{idx_str:<{key_width}}: {value_str:>15}\n"; tags_to_apply = (tag,) if tag else ()
                self.output_textbox.insert("end", line, tags_to_apply)
            trades = stats.get('_trades')
            if trades is not None and not trades.empty:
                self.output_textbox.insert("end", "\n--- Trades --- \n")
                trades_display = trades[['Size', 'EntryTime', 'ExitTime', 'EntryPrice', 'ExitPrice', 'PnL', 'ReturnPct']].copy()
                trades_display.rename(columns={'EntryTime': 'Entry', 'ExitTime': 'Exit', 'ReturnPct': 'Return %'}, inplace=True)
                trades_display['PnL'] = trades_display['PnL'].map('{:,.2f}'.format); trades_display['Return %'] = trades_display['Return %'].map('{:.2%}'.format)
                trades_display['EntryPrice'] = trades_display['EntryPrice'].map('{:.2f}'.format); trades_display['ExitPrice'] = trades_display['ExitPrice'].map('{:.2f}'.format)
                trades_display['Entry'] = pd.to_datetime(trades_display['Entry']).dt.strftime('%Y-%m-%d'); trades_display['Exit'] = pd.to_datetime(trades_display['Exit']).dt.strftime('%Y-%m-%d')
                pd.set_option('display.width', 1000); trades_str = trades_display.to_string(index=False, justify='right'); self.output_textbox.insert("end", trades_str + "\n"); pd.reset_option('display.width')
            else: self.output_textbox.insert("end", "\n--- No Trades Executed --- \n")
        except Exception as log_e: print(f"Log Err: {log_e}"); self.output_textbox.insert("end", f"\nErr display stats: {log_e}\n")
        finally: self.output_textbox.configure(state="disabled"); self.output_textbox.see("end")


    # --------------------------------------------------------------------------
    # UI Update and Event Handler Methods
    # --------------------------------------------------------------------------

    def update_param_widgets(self, strategy_name: str):
        """Clears and repopulates the strategy parameter entry widgets."""
        # --- (Implementation from previous context - app_py_ta_log_fix) ---
        for widget in self.param_frame.winfo_children(): widget.destroy()
        self.param_entries.clear(); params = PARAM_CONFIG.get(strategy_name, [])
        if not params:
            ctk.CTkLabel(self.param_frame, text="No parameters for this strategy.", font=self.font_normal, text_color=COLOR_FOREGROUND).pack(anchor="w"); return
        for param_name, default_value in params:
            entry_frame = ctk.CTkFrame(self.param_frame, fg_color="transparent"); entry_frame.pack(side="left", padx=10, pady=2)
            ctk.CTkLabel(entry_frame, text=f"{param_name}:", font=self.font_normal, text_color=COLOR_FOREGROUND).pack(side="left", padx=(0, 5))
            param_var = ctk.StringVar(value=str(default_value))
            ctk.CTkEntry(entry_frame, textvariable=param_var, width=60, font=self.font_normal, text_color=COLOR_DROPDOWN_FG, fg_color=COLOR_DROPDOWN_BG, border_color=COLOR_BUTTON, border_width=1).pack(side="left")
            self.param_entries[param_name] = param_var


    def on_symbol_change(self, selected_symbol: str = None):
        """Handles symbol change from dropdown or custom entry."""
        # --- (Implementation from previous fix - app_py_ta_log_fix, removed reload check) ---
        custom_symbol = self.custom_symbol_entry.get().strip().upper()
        symbol_to_use = custom_symbol if custom_symbol else self.symbol_var.get()
        if custom_symbol and custom_symbol in SYMBOLS: self.symbol_var.set(custom_symbol)
        # Allow reloading same symbol
        self.current_symbol = symbol_to_use
        self.log_message(f"Symbol changed to: {self.current_symbol}. Click 'Load Data'.", clear_first=True)
        self.clear_display() # This now calls .clear() on matrix and restarts loop
        self.current_data = None; self.plotted_data = None; self.latest_price = None
        self.latest_ta_results = None; self.latest_recommendation = " "; self.latest_technical_score = 0.0; self.latest_adx = None # Init rec to blank
        self.ml_model_loaded = False; self.ml_prediction = None; self.latest_feature_importances = None
        self._update_feature_importance_button_state()
        self.set_led_state("CPU", "off"); self.set_led_state("ERR", "off"); self.set_led_state("ML", "off") # Turn ML off on symbol change
        self._highlight_chart_period_button("ALL")


    def _handle_chart_period_click(self, period: str, button_widget: ctk.CTkButton):
        """Calls update function and handles button highlighting."""
        # --- (Implementation from previous context - app_py_ta_log_fix) ---
        self.update_chart_lookback(period)
        self._highlight_chart_period_button(period, button_widget.master)


    def _highlight_chart_period_button(self, active_period: str, parent_frame=None):
         """Highlights the active chart period button."""
         # --- (Implementation from previous context - app_py_ta_log_fix) ---
         container = parent_frame or self.chart_controls_frame
         if not container or not hasattr(container, 'winfo_children'): return
         # Use the stored dictionary if available
         if hasattr(self, 'chart_period_buttons'):
             for period, button in self.chart_period_buttons.items():
                 if button and button.winfo_exists():
                     if period == active_period:
                         button.configure(fg_color=COLOR_ACCENT, text_color=COLOR_BACKGROUND)
                     else:
                         button.configure(fg_color=COLOR_SECONDARY_BUTTON, text_color=COLOR_FOREGROUND)
         else: # Fallback if dictionary wasn't created
             for widget in container.winfo_children():
                  if isinstance(widget, ctk.CTkButton) and hasattr(widget, 'cget'):
                       button_text = widget.cget("text")
                       if button_text == active_period: widget.configure(fg_color=COLOR_ACCENT, text_color=COLOR_BACKGROUND)
                       else: widget.configure(fg_color=COLOR_SECONDARY_BUTTON, text_color=COLOR_FOREGROUND)


    def update_chart_lookback(self, period: str):
        """Filters the currently loaded data and updates the chart view."""
        # --- (Implementation from previous context - app_py_ta_log_fix) ---
        if self.current_data is None or self.current_data.empty: self.log_message("No data loaded to filter."); return
        self.log_message(f"Updating chart view to: {period}"); filtered_data = None; now_dt = datetime.datetime.now()
        try:
            full_data = self.current_data; end_date = full_data.index.max()
            if period == "ALL": filtered_data = full_data
            elif period == "YTD": start_of_year = pd.Timestamp(year=now_dt.year, month=1, day=1); filtered_data = full_data[full_data.index >= start_of_year]
            else:
                offset_map = {"1Y": pd.Timedelta(days=365), "6M": pd.Timedelta(days=183), "3M": pd.Timedelta(days=91), "1M": pd.Timedelta(days=30)}
                offset = offset_map.get(period)
                if offset: start_date = end_date - offset; filtered_data = full_data[full_data.index >= start_date]
                else: self.log_message(f"Unknown period: {period}"); filtered_data = full_data
            if filtered_data is None or filtered_data.empty:
                self.log_message(f"No data available for period: {period}"); self.plot_data(None, title_suffix=f" (No data for {period})")
            else: self.plot_data(filtered_data, title_suffix=f" ({period})")
        except Exception as e:
            self.log_message(f"Error filtering data for period {period}: {e}", tag="negative"); traceback.print_exc(); self.plot_data(self.current_data)


    def on_chart_motion(self, event):
        """Handles mouse hover events on the chart to display price info."""
        # --- (Implementation from previous fix - app_py_plot_update_fix) ---
        if event.inaxes != self.ax or event.xdata is None or self.plotted_data is None or self.plotted_data.empty:
             if hasattr(self, 'chart_info_label'): self.chart_info_label.configure(text=""); return
        try:
            dt_naive = mdates.num2date(event.xdata).replace(tzinfo=None)
            nearest_index = self.plotted_data.index.get_indexer([dt_naive], method='nearest')[0]
            actual_date = self.plotted_data.index[nearest_index]
            row_data = self.plotted_data.iloc[nearest_index]
            open_price = row_data.get('open', float('nan')); high_price = row_data.get('high', float('nan'))
            low_price = row_data.get('low', float('nan')); close_price = row_data.get('close', float('nan'))
            volume = row_data.get('volume', 0)
            date_str = actual_date.strftime('%Y-%m-%d')
            info_text = f"Date: {date_str}, O: {open_price:.2f}, H: {high_price:.2f}, L: {low_price:.2f}, C: {close_price:.2f}, Vol: {volume:,.0f}"
            self.chart_info_label.configure(text=info_text)
        except Exception as e:
            if hasattr(self, 'chart_info_label'): self.chart_info_label.configure(text="")


    def show_strategy_info(self):
        """Displays strategy description in a popup window."""
        # --- (Implementation from previous context - app_py_ta_log_fix) ---
        selected_strategy_name = self.strategy_var.get()
        description = STRATEGY_DESCRIPTIONS.get(selected_strategy_name, "No description available.")
        info_window = ctk.CTkToplevel(self); info_window.title(f"{selected_strategy_name} - Info"); info_window.geometry("450x350")
        info_window.configure(fg_color=COLOR_BACKGROUND); info_window.transient(self); info_window.grab_set()
        info_frame = ctk.CTkFrame(info_window, fg_color="transparent"); info_frame.pack(padx=15, pady=15, fill="both", expand=True)
        ctk.CTkLabel(info_frame, text=selected_strategy_name, font=self.font_large, text_color=COLOR_FOREGROUND).pack(pady=(0, 10))
        desc_textbox = ctk.CTkTextbox(info_frame, font=self.font_normal, text_color=COLOR_TEXTBOX_FG, fg_color=COLOR_TEXTBOX_BG, border_width=1, border_color=COLOR_BUTTON, wrap="word")
        desc_textbox.pack(fill="both", expand=True); desc_textbox.insert("1.0", description); desc_textbox.configure(state="disabled")
        ctk.CTkButton(info_frame, text="Close", command=info_window.destroy, font=self.font_button, text_color=COLOR_BACKGROUND, fg_color=COLOR_BUTTON, hover_color=COLOR_BUTTON_HOVER).pack(pady=(10, 0))


    def show_feature_importance_popup(self):
        """Displays feature importances in a popup window with a chart."""
        # --- MODIFIED: Remove redundant get_loaded_feature_importances call ---
        print("DEBUG: show_feature_importance_popup called") # Debug print
        if not self.ml_model_loaded or self.ml_service is None:
            self.log_message("No ML model loaded. Train or load a model first.", tag="negative")
            return

        # Rely on the state variable set during training/loading
        # self.latest_feature_importances = self.ml_service.get_loaded_feature_importances() # REMOVED

        print(f"DEBUG: Importance data available: {bool(self.latest_feature_importances)}") # Debug print
        if not self.latest_feature_importances:
            self.log_message("Feature importance data not available for the loaded model.", tag="negative")
            # Optionally try fetching again as a fallback?
            # self.latest_feature_importances = self.ml_service.get_loaded_feature_importances()
            # if not self.latest_feature_importances:
            #      return # Still nothing, exit
            return # Exit if not available

        if not isinstance(self.latest_feature_importances, dict) or not self.latest_feature_importances:
             self.log_message("Feature importance data is invalid.", tag="negative")
             return

        try:
             sorted_features = sorted(
                 self.latest_feature_importances.items(),
                 key=lambda item: abs(item[1]), reverse=True
             )
        except Exception as e:
             self.log_message(f"Error sorting feature importances: {e}", tag="negative")
             return

        top_n = 20; top_features = sorted_features[:top_n]; feature_names = [item[0] for item in top_features]; importance_scores = [abs(item[1]) for item in top_features] # Use absolute for plotting magnitude
        metadata = self.ml_service.get_loaded_model_metadata(); symbol = metadata.get('symbol', self.current_symbol) if metadata else self.current_symbol
        model_name = metadata.get('model_class_name', 'Unknown Model') if metadata else 'Unknown Model'
        popup = ctk.CTkToplevel(self); popup.geometry("700x650"); popup.title(f"Feature Importance - {symbol} ({model_name})")
        popup.configure(fg_color=COLOR_BACKGROUND); popup.transient(self); popup.grab_set()
        popup.grid_columnconfigure(0, weight=1); popup.grid_rowconfigure(0, weight=0); popup.grid_rowconfigure(1, weight=1); popup.grid_rowconfigure(2, weight=0)
        info_frame = ctk.CTkFrame(popup, fg_color="transparent"); info_frame.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="ew")
        ctk.CTkLabel(info_frame, text="Feature Importance indicates relative contribution. Chart shows top features by absolute score.", font=self.font_normal, text_color=COLOR_FOREGROUND, wraplength=650, justify="left").pack(anchor="w")
        chart_frame = ctk.CTkFrame(popup, fg_color=COLOR_CHART_BG); chart_frame.grid(row=1, column=0, padx=15, pady=5, sticky="nsew")
        chart_frame.grid_rowconfigure(0, weight=1); chart_frame.grid_columnconfigure(0, weight=1)
        fig_feat, ax_feat = plt.subplots(figsize=(6, 5)); fig_feat.set_facecolor(COLOR_CHART_BG); ax_feat.set_facecolor(COLOR_CHART_BG)
        y_pos = np.arange(len(feature_names)); ax_feat.barh(y_pos, importance_scores[::-1], align='center', color=COLOR_ACCENT)
        ax_feat.set_yticks(y_pos); ax_feat.set_yticklabels(feature_names[::-1]); ax_feat.invert_yaxis()
        ax_feat.set_xlabel('Importance Score (Absolute)', color=COLOR_CHART_AXES); ax_feat.set_title('Top Feature Importances', color=COLOR_CHART_AXES)
        ax_feat.tick_params(axis='x', colors=COLOR_CHART_AXES); ax_feat.tick_params(axis='y', colors=COLOR_CHART_AXES)
        for spine in ax_feat.spines.values(): spine.set_color(COLOR_CHART_AXES)
        ax_feat.grid(axis='x', color=COLOR_DROPDOWN_BG, linestyle='--', linewidth=0.5); plt.tight_layout()
        canvas_feat = FigureCanvasTkAgg(fig_feat, master=chart_frame); canvas_feat_widget = canvas_feat.get_tk_widget()
        canvas_feat_widget.pack(fill="both", expand=True, padx=5, pady=5); canvas_feat.draw()
        ctk.CTkButton(popup, text="Close", command=popup.destroy, font=self.font_button, text_color=COLOR_BACKGROUND, fg_color=COLOR_BUTTON, hover_color=COLOR_BUTTON_HOVER).grid(row=2, column=0, pady=(5, 15))


    def show_easter_egg(self, event=None):
        """Displays the easter egg art."""
        # --- (Implementation from previous context - app_py_ta_log_fix) ---
        print("DEBUG: show_easter_egg triggered"); egg_window = ctk.CTkToplevel(self); egg_window.title("WOW"); egg_window.geometry("600x400")
        egg_window.configure(fg_color=COLOR_BACKGROUND); egg_window.transient(self); egg_window.grab_set()
        egg_frame = ctk.CTkFrame(egg_window, fg_color="transparent"); egg_frame.pack(padx=10, pady=10, fill="both", expand=True)
        art_textbox = ctk.CTkTextbox(egg_frame, font=self.font_normal, text_color=COLOR_ACCENT, fg_color=COLOR_TEXTBOX_BG, border_width=1, border_color=COLOR_BUTTON, wrap="none")
        art_textbox.pack(fill="both", expand=True, padx=5, pady=5); art_textbox.insert("1.0", EASTER_EGG_ART); art_textbox.configure(state="disabled")
        ctk.CTkButton(egg_frame, text="Much Close", command=egg_window.destroy, font=self.font_button, text_color=COLOR_BACKGROUND, fg_color=COLOR_BUTTON, hover_color=COLOR_BUTTON_HOVER).pack(pady=(10, 0))


    # --------------------------------------------------------------------------
    # Utility and Helper Methods
    # --------------------------------------------------------------------------

    def log_message(self, message: str, clear_first: bool = False, tag: str | None = None):
        """Logs a message to the output textbox, optionally clearing first."""
        # --- (Implementation from previous context - app_py_ta_log_fix) ---
        is_error_warning = "error" in message.lower() or "warning" in message.lower() or "failed" in message.lower()
        if is_error_warning and "ML Prediction Error:" not in message : self.set_led_state("ERR", "on", flicker=True);
        if self.winfo_exists(): self.after(1500, lambda name="ERR": self.set_led_state(name, "off"))
        if hasattr(self, 'output_textbox') and self.output_textbox.winfo_exists():
            try:
                self.output_textbox.configure(state="normal")
                if clear_first: self.output_textbox.delete("1.0", "end")
                tags_to_apply = (tag,) if tag else (); self.output_textbox.insert("end", f"{message}\n", tags_to_apply)
                self.output_textbox.see("end"); self.output_textbox.configure(state="disabled")
            except tk.TclError as e: print(f"Error updating output_textbox: {e}")
        else: print(f"Log message skipped, output_textbox not available: {message}")


    def set_led_state(self, name: str, state: str, flicker: bool | None = None):
        """Sets the state ('on'/'off') and flicker status of a specific LED."""
        # --- (Implementation from previous context - app_py_ta_log_fix) ---
        name_upper = name.upper()
        if name_upper in self.leds:
            led_widget = self.leds[name_upper]
            if led_widget and led_widget.winfo_exists(): # Check if widget exists
                led_widget.set_state(state)
                should_flicker = (state == "on") if flicker is None else (flicker and state == "on")
                led_widget.enable_flicker(should_flicker)


    def _update_activity_leds(self):
        """Randomly flickers DATA and COM LEDs."""
        # --- (Implementation from previous context - app_py_ta_log_fix) ---
        if not self.winfo_exists(): return
        # Check if LED exists before getting state
        data_led = self.leds.get("DATA")
        if data_led and data_led.winfo_exists() and random.random() < 0.2: # Check exists
             self.set_led_state("DATA", "off" if data_led.get_state() == "on" else "on")
        com_led = self.leds.get("COM")
        if com_led and com_led.winfo_exists() and random.random() < 0.15: # Check exists
             self.set_led_state("COM", "off" if com_led.get_state() == "on" else "on")

        delay = random.randint(150, 550)
        if self.winfo_exists(): self.activity_led_job = self.after(delay, self._update_activity_leds)
        else: self.activity_led_job = None


    def _update_matrix_display(self, force_update=False):
        """Updates the dot matrix display, optionally forcing immediate redraw."""
        # Add debug print
        # print(f"MATRIX DEBUG: _update_matrix_display called. force={force_update}, job={self.matrix_update_job}, rec='{self.latest_recommendation}'")
        if not self.winfo_exists(): return

        # Cancel existing loop only if forcing update
        if force_update and self.matrix_update_job:
             try:
                 self.after_cancel(self.matrix_update_job)
                 # print("MATRIX DEBUG: Loop cancelled by force_update") # Debug
             except tk.TclError: pass
             self.matrix_update_job = None # Ensure job ID is cleared

        # Use the state variable that is initialized in __init__
        display_text = self.latest_recommendation # This holds TA or Hybrid result
        rec_key = display_text.strip().upper()
        # --- Use HEX COLOR map ---
        hex_color = RECOMMENDATION_HEX_COLORS.get(rec_key, RECOMMENDATION_HEX_COLORS['HOLD'])

        # Determine if showing price or recommendation
        should_show_price = False
        if not force_update:
             # Toggle only if not forced
             self.matrix_shows_price = not self.matrix_shows_price
             should_show_price = self.matrix_shows_price
             # print(f"MATRIX DEBUG: Toggled matrix_shows_price to {self.matrix_shows_price}") # Debug

        # Prepare display text
        if should_show_price and self.latest_price is not None:
             price_str = f"{self.latest_price:.2f}"
             display_text_final = price_str.rjust(MATRIX_COLS)
             hex_color = RECOMMENDATION_HEX_COLORS['DEFAULT'] # Price uses default color
             # print(f"MATRIX DEBUG: Displaying Price: '{display_text_final}'") # Debug
        else:
             # Use recommendation text (already in display_text)
             display_text_final = display_text.center(MATRIX_COLS)
             # print(f"MATRIX DEBUG: Displaying Rec: '{display_text_final}' Color: {hex_color}") # Debug
             # hex_color is already set based on recommendation

        # Update the display widget
        if hasattr(self, 'recommendation_display') and self.recommendation_display.get_frame().winfo_exists():
            display_text_final = display_text_final[:MATRIX_COLS] # Truncate
            # Pass HEX color code
            self.recommendation_display.display_text(display_text_final, color=hex_color)

        # --- MODIFIED: Always reschedule loop if not forced update ---
        if not force_update:
             delay = 3500
             if self.winfo_exists():
                  # print(f"MATRIX DEBUG: Scheduling next matrix update in {delay}ms...") # Debug
                  # Clear previous job ID before setting new one to prevent duplicates if called rapidly
                  if self.matrix_update_job:
                       try: self.after_cancel(self.matrix_update_job)
                       except tk.TclError: pass
                  self.matrix_update_job = self.after(delay, self._update_matrix_display)
             # else: print("MATRIX DEBUG: Window closed, not rescheduling matrix.") # Debug


    def _start_matrix_loop_if_needed(self):
        """Starts the matrix update loop if it's not already scheduled."""
        # Add debug print
        # print(f"MATRIX DEBUG: _start_matrix_loop_if_needed called. matrix_update_job={self.matrix_update_job}")
        # Check if window exists before scheduling
        if self.matrix_update_job is None and self.winfo_exists():
            # print("MATRIX DEBUG: Restarting matrix update loop...") # Debug
            # Schedule the *next* update, which will then continue the loop
            delay = 3500 # Standard delay
            self.matrix_update_job = self.after(delay, self._update_matrix_display)
        # elif self.matrix_update_job is not None:
            # print("MATRIX DEBUG: Loop already running, not restarting.") # Debug


    def _update_feature_importance_button_state(self):
        """Enables or disables the feature importance button."""
        # --- (Implementation from previous context - app_py_ta_log_fix) ---
        if hasattr(self, 'show_features_button') and self.show_features_button.winfo_exists():
            state = "normal" if self.ml_model_loaded and self.latest_feature_importances else "disabled"
            try: self.show_features_button.configure(state=state)
            except tk.TclError as e: print(f"Error updating feature button state: {e}")


    def _get_feature_explanation(self, feature_name: str) -> str:
        """Provides a simple explanation for common feature name patterns."""
        # --- (Implementation from previous context - app_py_ta_log_fix) ---
        name = feature_name.lower()
        if name.startswith("return_"): return f"{name.split('_')[-1]} return %"
        if name.startswith("log_return"): return "Logarithmic return"
        if name.startswith("sma_"): return f"{name.split('_')[-1]}-period Simple Moving Avg"
        if name.startswith("ema_"): return f"{name.split('_')[-1]}-period Exponential Moving Avg"
        if name == "hl_range": return "High-Low Range %"; # ... (add rest of explanations) ...
        if name == "oc_range": return "Open-Close Range %"
        if name == "log_volume": return "Log of Volume"
        if name == "volume_change": return "Volume % Change"
        if name == "relative_volume": return "Volume vs Rolling Avg"
        if name == "bb_upper": return "Bollinger Band Upper"
        if name == "bb_lower": return "Bollinger Band Lower"
        if name == "bb_width": return "Bollinger Band Width %"
        if name == "bb_pos": return "Position within Bollinger Bands (0-1)"
        if name.startswith("rsi_"): return f"{name.split('_')[-1]}-period RSI"
        if name == "macd": return "MACD Line"
        if name == "macd_signal": return "MACD Signal Line"
        if name == "macd_hist": return "MACD Histogram"
        if name == "day_of_week": return "Day of Week (0=Mon)"
        if name == "day_of_month": return "Day of Month"
        if name == "month": return "Month of Year"
        if name == "year": return "Year"
        if name == "quarter": return "Quarter"
        if name.startswith("is_month_"): return f"Is {name.split('_')[-1]} of Month? (1=Yes)"
        if name.startswith("is_quarter_"): return f"Is {name.split('_')[-1]} of Quarter? (1=Yes)"
        if name.startswith("is_year_"): return f"Is {name.split('_')[-1]} of Year? (1=Yes)"
        return feature_name


    # --------------------------------------------------------------------------
    # Application Exit Method
    # --------------------------------------------------------------------------

    def on_closing(self):
        """Handles graceful shutdown procedures."""
        print("Closing application gracefully...")
        # Stop background loops
        if self.activity_led_job:
            try: self.after_cancel(self.activity_led_job)
            except tk.TclError: pass
            # --- CORRECTED SYNTAX ---
            self.activity_led_job = None
        if self.matrix_update_job:
            try: self.after_cancel(self.matrix_update_job)
            except tk.TclError: pass
            # --- CORRECTED SYNTAX ---
            self.matrix_update_job = None

        # Stop individual LED flickers
        for led_widget in self.leds.values():
            # Check widget exists before calling methods
            if led_widget and led_widget.winfo_exists():
                led_widget.enable_flicker(False) # This also cancels internal job

        # Close Matplotlib figure
        try:
            # Check if fig exists before trying to close
            if hasattr(self, 'fig') and self.fig is not None:
                plt.close(self.fig)
                print("Matplotlib figure closed.")
                self.fig = None # Clear reference
        except Exception as e:
            print(f"Error closing matplotlib figure: {e}")

        # Allow UI to update before destroying
        self.update_idletasks()
        print("Destroying application window...")
        self.destroy()
        print("Application window destroyed.")
```

## gui/widgets/dot_matrix.py

```python
# gui/widgets/dot_matrix.py
# Dot Matrix display widgets adapted from provided code.
# Added dynamic color support and flicker enabling.
# Fixed blank display issue.

import customtkinter as ctk
import math
import random
import tkinter as tk # For TclError

# --- Helper Functions ---

def darken_color(hex_color, factor=0.5):
    """Darkens a hex color string."""
    if not isinstance(hex_color, str) or len(hex_color) != 7 or not hex_color.startswith('#'):
        # print(f"Warning: darken_color received invalid input: {hex_color}")
        return "#000000" # Fallback black
    try:
        r = int(hex_color[1:3], 16); g = int(hex_color[3:5], 16); b = int(hex_color[5:7], 16)
        r = max(0, int(r * factor)); g = max(0, int(g * factor)); b = max(0, int(b * factor))
        return f"#{r:02x}{g:02x}{b:02x}"
    except ValueError:
        # print(f"Warning: darken_color failed for: {hex_color}")
        return "#000000"

def lighten_color(hex_color, factor=0.5):
    """Lightens a hex color string by mixing with white."""
    if not isinstance(hex_color, str) or len(hex_color) != 7 or not hex_color.startswith('#'):
        # print(f"Warning: lighten_color received invalid input: {hex_color}")
        return "#ffffff" # Fallback white
    try:
        r = int(hex_color[1:3], 16); g = int(hex_color[3:5], 16); b = int(hex_color[5:7], 16)
        r = min(255, int(r + (255 - r) * factor)); g = min(255, int(g + (255 - g) * factor)); b = min(255, int(b + (255 - b) * factor))
        return f"#{r:02x}{g:02x}{b:02x}"
    except ValueError:
        # print(f"Warning: lighten_color failed for: {hex_color}")
        return "#ffffff"

# --- MatrixPixel Class ---
class MatrixPixel(ctk.CTkFrame):
    """Simulates a single pixel in a dot matrix display."""
    def __init__(self, master, color="#00ff00", size=8, explicit_canvas_bg="#050505", **kwargs):
        super().__init__(master, width=size, height=size, fg_color="transparent", **kwargs)

        self.size = size
        self.base_color = color # Store the intended 'on' color (should be hex)
        self.state = "off"
        self.burn_in_level = 0.0
        self.flicker_enabled = False
        self.flicker_job = None
        self.pixel_obj = None
        self.on_color = "#000000" # Initialize calculated colors
        # Store explicit background, defaulting if None
        self.explicit_canvas_bg = explicit_canvas_bg if explicit_canvas_bg else "#050505"
        self.off_color = self.explicit_canvas_bg # Off color should match background initially

        # Calculate initial on/off colors based on potential burn-in
        self._update_colors()

        self.canvas = ctk.CTkCanvas(self, width=size, height=size,
                                      highlightthickness=0, borderwidth=0,
                                      bg=self.explicit_canvas_bg) # Use stored background
        self.canvas.pack(fill="both", expand=True)
        self.after(10, self.draw) # Defer first draw slightly

    def _update_colors(self):
        """Calculates on/off colors based on base color and burn-in."""
        # Calculate 'on' color based on base_color and burn-in
        on_dim_factor = 1.0 - (self.burn_in_level * 0.3)
        self.on_color = darken_color(self.base_color, on_dim_factor)

        # Calculate 'off' color - should match the background
        # Apply burn-in effect by slightly lightening the background
        off_bright_factor = self.burn_in_level * 0.10 # Less brightening for off state
        self.off_color = lighten_color(self.explicit_canvas_bg, off_bright_factor)


    def set_base_color(self, new_color):
        """Sets a new base color (HEX) for the pixel and updates."""
        # Basic validation for hex color
        if not isinstance(new_color, str) or len(new_color) != 7 or not new_color.startswith('#'):
             # print(f"Warning: Invalid hex color passed to set_base_color: {new_color}")
             new_color = "#ff00ff" # Fallback to magenta if invalid

        if new_color != self.base_color:
            self.base_color = new_color
            self._update_colors()
            # Redraw immediately if the widget exists to reflect new on/off colors
            if self.winfo_exists():
                self.draw()

    def draw(self):
        """Draws the matrix pixel."""
        if not hasattr(self, 'canvas') or not self.canvas.winfo_exists(): return
        self.canvas.delete("all")
        inset = 1; # Adjust inset if needed
        x0, y0 = inset, inset;
        x1, y1 = self.size - inset, self.size - inset

        if self.state == "on":
            current_color = self.on_color # Use calculated on color
            self.pixel_obj = self.canvas.create_rectangle(x0, y0, x1, y1, fill=current_color, outline="")
            # Add glow effect only if pixel is meant to be bright (optional)
            # if self.burn_in_level < 0.8: # Example: Less glow for heavily burnt-in pixels
            #     glow_color = lighten_color(self.on_color, 0.4)
            #     self.canvas.create_rectangle(x0 - 1, y0 - 1, x1 + 1, y1 + 1, fill="", outline=glow_color, width=1, stipple="gray25")
            #     self.canvas.lift(self.pixel_obj) # Ensure pixel is above glow
        else:
            # --- FIX: Use calculated off_color (background + burn-in) ---
            current_color = self.off_color
            # Draw the rectangle filled with the calculated off color
            self.pixel_obj = self.canvas.create_rectangle(x0, y0, x1, y1, fill=current_color, outline="")
            # --- END FIX ---

        # Manage flicker state after drawing
        if self.state == 'on' and self.flicker_enabled:
            self._start_flicker()
        elif self.state == 'off' and self.flicker_job:
            # Stop flicker if state is off
            if self.flicker_job:
                try: self.after_cancel(self.flicker_job)
                except tk.TclError: pass
                self.flicker_job = None

    def _start_flicker(self):
        """Handles pixel flickering."""
        if self.flicker_job:
            try: self.after_cancel(self.flicker_job)
            except tk.TclError: pass
            self.flicker_job = None
        if not self.flicker_enabled or self.state != "on" or not self.winfo_exists(): return

        intensity = random.uniform(0.75, 1.0)
        # Flicker the calculated on_color
        flicker_color = darken_color(self.on_color, intensity)

        try:
            if self.pixel_obj and self.canvas.winfo_exists() and self.pixel_obj in self.canvas.find_all():
                 self.canvas.itemconfig(self.pixel_obj, fill=flicker_color)
            else:
                 self.flicker_job = None; return # Stop if object invalid
        except tk.TclError:
            self.flicker_job = None; return # Stop if error

        delay = random.randint(100, 600)
        if self.flicker_enabled and self.state == "on" and self.winfo_exists():
            self.flicker_job = self.after(delay, self._start_flicker)
        else:
             self.flicker_job = None

    def set_state(self, state):
        """Sets the pixel state ('on' or 'off')."""
        new_state = "on" if state == "on" else "off"
        if new_state != self.state:
            self.state = new_state
            if self.winfo_exists(): self.draw()

    def toggle(self):
        """Toggles the pixel state."""
        self.set_state("off" if self.state == "on" else "on")

    def set_burn_in(self, level):
        """Sets the burn-in level (0.0 to 1.0)."""
        try:
            new_level = max(0.0, min(1.0, float(level)))
            if abs(new_level - self.burn_in_level) > 1e-6:
                self.burn_in_level = new_level
                self._update_colors() # Recalculate on/off colors
                if self.winfo_exists(): self.draw()
        except (ValueError, TypeError):
            print(f"MatrixPixel: Invalid level passed to set_burn_in: {level}")

    def enable_flicker(self, enabled=True):
        """Enables or disables flickering."""
        new_flicker_state = bool(enabled)
        if new_flicker_state != self.flicker_enabled:
            self.flicker_enabled = new_flicker_state
            if self.flicker_enabled and self.state == "on":
                 # If enabling and 'on', draw solid first then schedule flicker
                 if self.winfo_exists():
                      self.draw()
                      self.after(10, self._start_flicker)
            elif not self.flicker_enabled:
                # If disabling, cancel job and redraw solid color if 'on'
                if self.flicker_job:
                    try: self.after_cancel(self.flicker_job)
                    except tk.TclError: pass
                    self.flicker_job = None
                if self.state == 'on' and self.winfo_exists():
                    self.draw()


# --- MatrixText Class ---
class MatrixText:
    """Helper class for creating text displays using matrix pixels."""
    def __init__(self, parent, rows=7, cols=60, pixel_size=4, char_spacing=1, bg_color="#050505", default_on_color="#00ff00"):
        self.frame = ctk.CTkFrame(parent, fg_color=bg_color)
        self.pixels = [] # 2D array [row][col] of MatrixPixel widgets
        self.rows = rows
        self.cols = cols # Total pixel columns
        self.pixel_size = pixel_size
        self.char_spacing = char_spacing
        self.bg_color = bg_color
        self.default_on_color = default_on_color
        self.current_color = default_on_color # Track the current color for the text

        self._char_map = self._create_char_map()

        for r in range(rows):
            pixel_row = []
            row_frame = ctk.CTkFrame(self.frame, fg_color=bg_color)
            # Reduce padding between rows
            row_frame.pack(pady=0, fill="x", expand=False)
            for c in range(cols):
                # Apply random burn-in for vintage effect
                burn_in = random.uniform(0.1, 0.7)
                # Pass explicit bg and default on color
                pixel = MatrixPixel(row_frame, color=self.default_on_color, size=pixel_size, explicit_canvas_bg=self.bg_color)
                # Reduce padding between pixels
                pixel.pack(side="left", padx=0, pady=0)
                pixel.set_burn_in(burn_in)
                pixel_row.append(pixel)
            self.pixels.append(pixel_row)

    def _create_char_map(self): # (remains the same as previous version)
        """Creates the 5x7 character map."""
        # --- (Character map dictionary omitted for brevity - keep as before) ---
        return {
            'A': [[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,1,1,1,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1]],
            'B': [[1,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,1,1,1,0]],
            'C': [[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,1],[0,1,1,1,0]],
            'D': [[1,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,1,1,1,0]],
            'E': [[1,1,1,1,1],[1,0,0,0,0],[1,0,0,0,0],[1,1,1,1,0],[1,0,0,0,0],[1,0,0,0,0],[1,1,1,1,1]],
            'F': [[1,1,1,1,1],[1,0,0,0,0],[1,0,0,0,0],[1,1,1,1,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0]],
            'G': [[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,0],[1,0,1,1,1],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
            'H': [[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,1,1,1,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1]],
            'I': [[1,1,1,1,1],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[1,1,1,1,1]],
            'J': [[0,0,1,1,1],[0,0,0,0,1],[0,0,0,0,1],[0,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
            'K': [[1,0,0,1,0],[1,0,1,0,0],[1,1,0,0,0],[1,1,0,0,0],[1,0,1,0,0],[1,0,0,1,0],[1,0,0,0,1]],
            'L': [[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[1,1,1,1,1]],
            'M': [[1,0,0,0,1],[1,1,0,1,1],[1,0,1,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1]],
            'N': [[1,0,0,0,1],[1,1,0,0,1],[1,0,1,0,1],[1,0,0,1,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1]],
            'O': [[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
            'P': [[1,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,1,1,1,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0]],
            'Q': [[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,1,0,1],[1,0,0,1,0],[0,1,1,0,1]],
            'R': [[1,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,1,1,1,0],[1,0,1,0,0],[1,0,0,1,0],[1,0,0,0,1]],
            'S': [[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,0],[0,1,1,1,0],[0,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
            'T': [[1,1,1,1,1],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0]],
            'U': [[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
            'V': [[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[0,1,0,1,0],[0,0,1,0,0]],
            'W': [[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,1,0,1],[1,1,0,1,1],[1,1,0,1,1],[1,0,0,0,1]],
            'X': [[1,0,0,0,1],[1,0,0,0,1],[0,1,0,1,0],[0,0,1,0,0],[0,1,0,1,0],[1,0,0,0,1],[1,0,0,0,1]],
            'Y': [[1,0,0,0,1],[1,0,0,0,1],[0,1,0,1,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0]],
            'Z': [[1,1,1,1,1],[0,0,0,0,1],[0,0,0,1,0],[0,0,1,0,0],[0,1,0,0,0],[1,0,0,0,0],[1,1,1,1,1]],
            '0': [[0,1,1,1,0],[1,0,0,1,1],[1,0,1,0,1],[1,1,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
            '1': [[0,0,1,0,0],[0,1,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,1,1,1,0]],
            '2': [[0,1,1,1,0],[1,0,0,0,1],[0,0,0,0,1],[0,0,0,1,0],[0,0,1,0,0],[0,1,0,0,0],[1,1,1,1,1]],
            '3': [[1,1,1,1,0],[0,0,0,0,1],[0,0,0,1,0],[0,0,1,1,0],[0,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
            '4': [[0,0,0,1,0],[0,0,1,1,0],[0,1,0,1,0],[1,0,0,1,0],[1,1,1,1,1],[0,0,0,1,0],[0,0,0,1,0]],
            '5': [[1,1,1,1,1],[1,0,0,0,0],[1,1,1,1,0],[0,0,0,0,1],[0,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
            '6': [[0,0,1,1,0],[0,1,0,0,0],[1,0,0,0,0],[1,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
            '7': [[1,1,1,1,1],[0,0,0,0,1],[0,0,0,1,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0]],
            '8': [[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
            '9': [[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,1],[0,0,0,0,1],[0,0,0,1,0],[0,1,1,0,0]],
            ' ': [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]],
            '.': [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,1,0,0],[0,0,1,0,0]],
            ':': [[0,0,0,0,0],[0,0,0,0,0],[0,0,1,0,0],[0,0,0,0,0],[0,0,1,0,0],[0,0,0,0,0],[0,0,0,0,0]],
            '-': [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[1,1,1,1,1],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]],
            '_': [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[1,1,1,1,1]],
            '?': [[0,1,1,1,0],[1,0,0,0,1],[0,0,0,0,1],[0,0,0,1,0],[0,0,1,0,0],[0,0,0,0,0],[0,0,1,0,0]],
            '!': [[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,0,0,0],[0,0,1,0,0]],
        }

    def display_text(self, text, color=None):
        """
        Displays text on the matrix, using the provided HEX color.

        Args:
            text (str): The text string to display.
            color (str | None): The HEX color code (e.g., '#FF0000') for the text.
                                If None, uses default_on_color.
        """
        # self.clear() # Clear is handled separately now for blank state
        # Update current color, fallback to default if None or invalid
        hex_color = color if (color and isinstance(color, str) and color.startswith('#')) else self.default_on_color
        self.current_color = hex_color

        char_width_total = 5 + self.char_spacing
        current_col = 0
        line = text.split('\n')[0] # Process first line only

        # Turn off all pixels initially before drawing new text
        for r_idx in range(self.rows):
             for c_idx in range(self.cols):
                 if r_idx < len(self.pixels) and c_idx < len(self.pixels[r_idx]):
                      pixel = self.pixels[r_idx][c_idx]
                      if pixel.winfo_exists():
                           pixel.set_state("off")
                           pixel.enable_flicker(False) # Ensure flicker is off for off pixels

        # Draw the characters
        for char in line:
            if current_col + 5 <= self.cols:
                self.display_char(char, current_col) # display_char uses self.current_color
                current_col += char_width_total
            else: break # Stop if text exceeds display width


    def display_char(self, char, start_col):
        """Displays a single character pattern at the specified column using current color."""
        default_pattern = [[1]*5]*7 # Solid block for unknown chars
        pattern = self._char_map.get(char.upper(), default_pattern)

        for r_idx, row_pattern in enumerate(pattern):
            if r_idx < self.rows:
                for c_idx, is_on in enumerate(row_pattern):
                    target_col = start_col + c_idx
                    if target_col < self.cols:
                        if r_idx < len(self.pixels) and target_col < len(self.pixels[r_idx]):
                            pixel = self.pixels[r_idx][target_col]
                            if pixel.winfo_exists():
                                # Set the base color for the pixel first (should be hex)
                                pixel.set_base_color(self.current_color)
                                # Set the state (this will draw with updated on/off colors)
                                pixel.set_state("on" if is_on else "off")
                                # Enable flicker only for 'on' pixels
                                pixel.enable_flicker(is_on)


    def clear(self):
        """Turns off all pixels and disables their flicker, making the display blank."""
        # print("DEBUG: MatrixText clear called") # Debug
        for row in self.pixels:
            for pixel in row:
                if pixel.winfo_exists():
                    pixel.enable_flicker(False) # Disable flicker first
                    pixel.set_state("off")      # Then turn off (draws background color)

    def get_frame(self):
        """Returns the main frame containing the pixels."""
        return self.frame
```

## gui/widgets/vintage_indicators.py

```python
# gui/widgets/vintage_indicators.py
# Contains custom vintage-style indicator widgets like WornLED and NeonLight

import customtkinter as ctk
import math
import random
# --- Added tkinter import for TclError handling ---
import tkinter as tk


class WornLED(ctk.CTkFrame):
    """
    A CustomTkinter widget simulating a worn, flickering LED indicator.
    """
    def __init__(self, master, color="#ff0000", size=30, explicit_canvas_bg=None, **kwargs):
        """
        Initializes the WornLED widget.

        Args:
            master: The parent widget.
            color (str): The base hex color for the LED when 'on'.
            size (int): The diameter of the LED widget.
            explicit_canvas_bg (str | None): Explicit hex color for the canvas background.
                                            If None, uses theme default.
            **kwargs: Additional arguments for the CTkFrame.
        """
        super().__init__(master, width=size, height=size, fg_color="transparent", **kwargs)

        self.size = size
        self.original_color = color
        self.color = self._dull_color(color)
        self._state = "off"
        self.wear_level = 0.7
        self.flicker_enabled = False
        self.flicker_job = None
        self.led_obj = None

        if explicit_canvas_bg is not None:
            canvas_bg_color = explicit_canvas_bg
        else:
            default_bg_color = ctk.ThemeManager.theme["CTkFrame"]["fg_color"]
            canvas_bg_color = self._apply_appearance_mode(default_bg_color)

        self.canvas = ctk.CTkCanvas(self, width=size, height=size,
                                    highlightthickness=0,
                                    borderwidth=0,
                                    bg=canvas_bg_color)
        self.canvas.pack(fill="both", expand=True)
        self.draw()

    def _dull_color(self, hex_color):
        """ Makes the input hex color more dull by mixing it with gray. """
        try:
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            gray = 128; mix_factor = 0.6
            r = int(r * (1 - mix_factor) + gray * mix_factor)
            g = int(g * (1 - mix_factor) + gray * mix_factor)
            b = int(b * (1 - mix_factor) + gray * mix_factor)
            r = max(0, min(255, r)); g = max(0, min(255, g)); b = max(0, min(255, b))
            return f"#{r:02x}{g:02x}{b:02x}"
        except ValueError: return "#808080"

    def _darken_color(self, hex_color, factor=0.5):
        """ Darkens the input hex color by a given factor. """
        try:
            r = int(hex_color[1:3], 16); g = int(hex_color[3:5], 16); b = int(hex_color[5:7], 16)
            r = max(0, min(255, int(r * factor))); g = max(0, min(255, int(g * factor))); b = max(0, min(255, int(b * factor)))
            return f"#{r:02x}{g:02x}{b:02x}"
        except ValueError: return "#333333"

    def _lighten_color(self, hex_color, factor=0.5):
        """ Lightens the input hex color by mixing it with white. """
        try:
            r = int(hex_color[1:3], 16); g = int(hex_color[3:5], 16); b = int(hex_color[5:7], 16)
            r = min(255, int(r + (255 - r) * factor)); g = min(255, int(g + (255 - g) * factor)); b = min(255, int(b + (255 - b) * factor))
            return f"#{r:02x}{g:02x}{b:02x}"
        except ValueError: return "#cccccc"

    def draw(self):
        """ Clears the canvas and redraws the LED based on its current state. """
        if not hasattr(self, 'canvas') or not self.canvas.winfo_exists(): return
        self.canvas.delete("all")

        cx, cy = self.size / 2, self.size / 2
        casing_fill = self._apply_appearance_mode("#333333")
        casing_outline = self._apply_appearance_mode("#222222")
        ring_outline = self._apply_appearance_mode("#555555")
        off_indent_outline = self._apply_appearance_mode("#222222")

        self.canvas.create_oval(2, 2, self.size - 2, self.size - 2, fill=casing_fill, outline=casing_outline, width=2)
        self.canvas.create_oval(4, 4, self.size - 4, self.size - 4, fill="", outline=ring_outline, width=1)
        if self.wear_level > 0.3: self._add_wear_marks()

        light_size = self.size * 0.6
        x0, y0 = cx - light_size / 2, cy - light_size / 2
        x1, y1 = cx + light_size / 2, cy + light_size / 2

        if self._state == "on":
            # --- Draw 'On' State ---
            # --- FURTHER MODIFIED Glow Effect ---
            for i in range(1, 3): # Reduced layers from 3 to 2
                expand = i * 1.5 # Reduced expansion from i*2
                stipple_pattern = "gray75" if i == 1 else "gray50"
                # Use even dimmer lighter versions of the original color for outer glow
                glow_color = self._lighten_color(self.original_color, 0.10 * i) # Further reduced lightening factor
                self.canvas.create_oval(x0 - expand, y0 - expand, x1 + expand, y1 + expand,
                                        fill="", outline=glow_color, width=1.0, # Thinner glow line
                                        stipple=stipple_pattern)
            # --- End FURTHER MODIFIED Glow Effect ---

            self.led_obj = self.canvas.create_oval(x0, y0, x1, y1, fill=self.color, outline="")
            self._add_led_texture(x0, y0, x1, y1)
            spot_size = light_size * 0.25
            self.canvas.create_oval(x0 + light_size * 0.15, y0 + light_size * 0.15,
                                    x0 + light_size * 0.15 + spot_size, y0 + light_size * 0.15 + spot_size,
                                    fill="white", outline="", stipple="gray50")
            if self.flicker_enabled: self._start_flicker()
        else:
            # --- Draw 'Off' State ---
            dark_color = self._darken_color(self.color, 0.3)
            self.led_obj = self.canvas.create_oval(x0, y0, x1, y1, fill=dark_color, outline="")
            self.canvas.create_oval(x0 + 1, y0 + 1, x1 - 1, y1 - 1, fill="", outline=off_indent_outline, width=1)
            if self.flicker_job:
                self.after_cancel(self.flicker_job)
                self.flicker_job = None

    def _add_led_texture(self, x0, y0, x1, y1):
        """ Adds small specks inside the lit LED area to simulate dust/imperfections. """
        width = x1 - x0; height = y1 - y0
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        radius_squared = (width / 2) ** 2
        texture_color = self._apply_appearance_mode("#444444")
        for _ in range(int(5 * self.wear_level)):
            x = x0 + random.uniform(0, width); y = y0 + random.uniform(0, height)
            if (x - cx) ** 2 + (y - cy) ** 2 <= radius_squared:
                speck_size = random.uniform(0.5, 1.5)
                self.canvas.create_oval(x, y, x + speck_size, y + speck_size, fill=texture_color, outline="")

    def _add_wear_marks(self):
        """ Adds dust specks and scratches to the LED casing. """
        speck_colors = [self._apply_appearance_mode(c) for c in ["#555555", "#666666", "#777777"]]
        for _ in range(int(10 * self.wear_level)):
            x = random.uniform(3, self.size - 3); y = random.uniform(3, self.size - 3)
            speck_size = random.uniform(1, 2); color = random.choice(speck_colors)
            self.canvas.create_oval(x, y, x + speck_size, y + speck_size, fill=color, outline="")
        scratch_color = self._apply_appearance_mode("#333333")
        for _ in range(int(5 * self.wear_level)):
            x1 = random.uniform(3, self.size - 3); y1 = random.uniform(3, self.size - 3)
            length = random.uniform(2, 8); angle = random.uniform(0, math.pi * 2)
            x2 = x1 + length * math.cos(angle); y2 = y1 + length * math.sin(angle)
            x2 = max(3, min(self.size - 3, x2)); y2 = max(3, min(self.size - 3, y2))
            self.canvas.create_line(x1, y1, x2, y2, fill=scratch_color, width=0.5, dash=(2, 2))

    def _start_flicker(self):
        """ Initiates the flickering effect if the LED is 'on'. """
        if self.flicker_job: self.after_cancel(self.flicker_job); self.flicker_job = None
        if self._state != "on" or not self.flicker_enabled:
            if self.led_obj and self.canvas.winfo_exists():
                 try:
                     current_fill = self.canvas.itemcget(self.led_obj, "fill")
                     if current_fill != self.color: self.canvas.itemconfig(self.led_obj, fill=self.color)
                 except tk.TclError: pass
            return
        intensity = random.uniform(0.75, 1.0); flicker_color = self._darken_color(self.color, intensity)
        if self.led_obj and self.canvas.winfo_exists():
            try: self.canvas.itemconfig(self.led_obj, fill=flicker_color)
            except tk.TclError: pass
        base_delay = 400 if random.random() < 0.8 else 100; jitter = random.randint(0, 500); delay = base_delay + jitter
        if self.winfo_exists(): self.flicker_job = self.after(delay, self._start_flicker)
        else: self.flicker_job = None

    def set_state(self, state: str):
        """ Sets the state of the LED ('on' or 'off'). """
        new_state = state.lower()
        if new_state not in ["on", "off"]: return
        old_state = self._state
        self._state = new_state
        if old_state != self._state: self.draw()

    def get_state(self) -> str:
        """ Returns the current state ('on' or 'off') of the LED. """
        return self._state

    def toggle(self):
        """ Toggles the LED state between 'on' and 'off'. """
        self.set_state("off" if self._state == "on" else "on")

    def set_wear_level(self, level: float):
        """ Sets the wear level, affecting dust and scratches. """
        self.wear_level = max(0.0, min(1.0, level))
        self.draw()

    def enable_flicker(self, enabled: bool = True):
        """ Enables or disables the flickering effect. """
        flicker_state_changed = self.flicker_enabled != enabled
        self.flicker_enabled = enabled
        if flicker_state_changed or self._state == "on":
            if enabled and self._state == "on": self._start_flicker()
            elif not enabled:
                if self.flicker_job: self.after_cancel(self.flicker_job); self.flicker_job = None
                self.draw()

# --- NeonLight Class (Remains the same as previous version) ---
class NeonLight(ctk.CTkFrame):
    """
    A CustomTkinter widget simulating a flickering neon tube light.
    (Provided by user, not integrated into the main trading app currently)
    """
    def __init__(self, master, color="#ff00ff", width=100, height=30, explicit_canvas_bg=None, **kwargs):
        super().__init__(master, width=width, height=height, fg_color="transparent", **kwargs)
        self.width = width; self.height = height; self.original_color = color; self.color = color
        self._state = "off"; self.wear_level = 0.7; self.flicker_enabled = False
        self.flicker_job = None; self.tube_obj = None
        if explicit_canvas_bg is not None: canvas_bg_color = explicit_canvas_bg
        else:
            default_bg_color = ctk.ThemeManager.theme["CTkFrame"]["fg_color"]
            canvas_bg_color = self._apply_appearance_mode(default_bg_color)
        self.canvas = ctk.CTkCanvas(self, width=width, height=height, highlightthickness=0, borderwidth=0, bg=canvas_bg_color)
        self.canvas.pack(fill="both", expand=True)
        self.draw()
    def _darken_color(self, hex_color, factor=0.5):
        try:
            r = int(hex_color[1:3], 16); g = int(hex_color[3:5], 16); b = int(hex_color[5:7], 16)
            r = max(0, min(255, int(r * factor))); g = max(0, min(255, int(g * factor))); b = max(0, min(255, int(b * factor)))
            return f"#{r:02x}{g:02x}{b:02x}"
        except ValueError: return "#333333"
    def _lighten_color(self, hex_color, factor=0.5):
        try:
            r = int(hex_color[1:3], 16); g = int(hex_color[3:5], 16); b = int(hex_color[5:7], 16)
            r = min(255, int(r + (255 - r) * factor)); g = min(255, int(g + (255 - g) * factor)); b = min(255, int(b + (255 - b) * factor))
            return f"#{r:02x}{g:02x}{b:02x}"
        except ValueError: return "#cccccc"
    def draw(self):
        if not hasattr(self, 'canvas') or not self.canvas.winfo_exists(): return
        self.canvas.delete("all")
        tube_width = self.width * 0.8; tube_height = self.height * 0.4
        cx, cy = self.width / 2, self.height / 2
        bracket_width = self.width * 0.08; bracket_height = self.height * 0.7
        bracket_fill = self._apply_appearance_mode("#555555"); bracket_outline = self._apply_appearance_mode("#333333")
        self.canvas.create_rectangle(cx - tube_width / 2 - bracket_width, cy - bracket_height / 2, cx - tube_width / 2, cy + bracket_height / 2, fill=bracket_fill, outline=bracket_outline)
        self.canvas.create_rectangle(cx + tube_width / 2, cy - bracket_height / 2, cx + tube_width / 2 + bracket_width, cy + bracket_height / 2, fill=bracket_fill, outline=bracket_outline)
        self._add_wear_marks()
        tube_left = cx - tube_width / 2; tube_right = cx + tube_width / 2; tube_top = cy - tube_height / 2; tube_bottom = cy + tube_height / 2
        cap_width = tube_height * 1.2; cap_fill = self._apply_appearance_mode("#777777"); cap_outline = self._apply_appearance_mode("#333333")
        self.canvas.create_rectangle(tube_left - cap_width, tube_top, tube_left, tube_bottom, fill=cap_fill, outline=cap_outline)
        self.canvas.create_rectangle(tube_right, tube_top, tube_right + cap_width, tube_bottom, fill=cap_fill, outline=cap_outline)
        if self._state == "on":
            for i in range(1, 5):
                expand_x = i * 2.0; expand_y = i * 1.0; glow_color = self._lighten_color(self.original_color, 0.15 * i)
                stipple_pattern = "";
                if i == 1: stipple_pattern = "gray75"
                elif i == 2: stipple_pattern = "gray50"
                elif i == 3: stipple_pattern = "gray25"
                else: stipple_pattern = "gray12"
                self.canvas.create_rectangle(tube_left - expand_x, tube_top - expand_y, tube_right + expand_x, tube_bottom + expand_y, fill="", outline=glow_color, width=1, stipple=stipple_pattern)
            self.tube_obj = self.canvas.create_rectangle(tube_left, tube_top, tube_right, tube_bottom, fill=self.color, outline="")
            highlight_height = tube_height * 0.3; highlight_color = self._lighten_color(self.color, 0.6)
            self.canvas.create_rectangle(tube_left, tube_top + tube_height*0.1, tube_right, tube_top + tube_height*0.1 + highlight_height, fill=highlight_color, outline="", stipple="gray75")
            if self.flicker_enabled: self._start_flicker()
        else:
            dark_color = self._darken_color(self.color, 0.15)
            self.tube_obj = self.canvas.create_rectangle(tube_left, tube_top, tube_right, tube_bottom, fill=dark_color, outline=self._apply_appearance_mode("#222222"))
            reflection_color = self._apply_appearance_mode("#AAAAAA")
            self.canvas.create_rectangle(tube_left + tube_width*0.1, tube_top + tube_height*0.1, tube_right - tube_width*0.1, tube_top + tube_height * 0.4, fill=reflection_color, outline="", stipple="gray50")
            if self.flicker_job: self.after_cancel(self.flicker_job); self.flicker_job = None
    def _add_wear_marks(self):
        speck_colors = [self._apply_appearance_mode(c) for c in ["#444444", "#555555", "#666666"]]
        for _ in range(int(15 * self.wear_level)):
            x = random.uniform(0, self.width); y = random.uniform(0, self.height); speck_size = random.uniform(1, 3); color = random.choice(speck_colors)
            self.canvas.create_oval(x, y, x + speck_size, y + speck_size, fill=color, outline="")
        scratch_color = self._apply_appearance_mode("#333333")
        for _ in range(int(6 * self.wear_level)):
            x1 = random.uniform(0, self.width); y1 = random.uniform(0, self.height); length = random.uniform(3, 10); angle = random.uniform(0, math.pi*2)
            x2 = x1 + length * math.cos(angle); y2 = y1 + length * math.sin(angle); x2 = max(0, min(self.width, x2)); y2 = max(0, min(self.height, y2))
            self.canvas.create_line(x1, y1, x2, y2, fill=scratch_color, width=0.5, dash=(3, 3))
    def _start_flicker(self):
        if self.flicker_job: self.after_cancel(self.flicker_job); self.flicker_job = None
        if self._state != "on" or not self.flicker_enabled:
            if self.tube_obj and self.canvas.winfo_exists():
                 try:
                     current_fill = self.canvas.itemcget(self.tube_obj, "fill")
                     if current_fill != self.color: self.canvas.itemconfig(self.tube_obj, fill=self.color)
                 except tk.TclError: pass
            return
        flicker_type = random.choices(["minor", "major", "off", "normal"], weights=[0.6, 0.25, 0.1, 0.05], k=1)[0]
        flicker_color = self.color
        if flicker_type == "minor": intensity = random.uniform(0.75, 0.9); flicker_color = self._darken_color(self.color, intensity)
        elif flicker_type == "major": intensity = random.uniform(0.4, 0.65); flicker_color = self._darken_color(self.color, intensity)
        elif flicker_type == "off": flicker_color = self._darken_color(self.color, 0.1)
        if self.tube_obj and self.canvas.winfo_exists():
            try: self.canvas.itemconfig(self.tube_obj, fill=flicker_color)
            except tk.TclError: pass
        if flicker_type in ["major", "off"]: delay = random.randint(40, 120)
        else: base = 800 if random.random() < 0.6 else 250; jitter = random.randint(0, 600); delay = base + jitter
        if self.winfo_exists(): self.flicker_job = self.after(delay, self._start_flicker)
        else: self.flicker_job = None
    def set_state(self, state: str):
        new_state = state.lower();
        if new_state not in ["on", "off"]: return
        old_state = self._state; self._state = new_state
        if old_state != self._state: self.draw()
    def get_state(self) -> str: return self._state
    def toggle(self): self.set_state("off" if self._state == "on" else "on")
    def set_wear_level(self, level: float): self.wear_level = max(0.0, min(1.0, level)); self.draw()
    def enable_flicker(self, enabled: bool = True):
        flicker_state_changed = self.flicker_enabled != enabled; self.flicker_enabled = enabled
        if flicker_state_changed or self._state == "on":
            if enabled and self._state == "on": self._start_flicker()
            elif not enabled:
                if self.flicker_job: self.after_cancel(self.flicker_job); self.flicker_job = None
                self.draw()

# --- Example Usage (Remains the same) ---
if __name__ == "__main__":
    ctk.set_appearance_mode("dark"); ctk.set_default_color_theme("blue")
    app = ctk.CTk(); app.title("Vintage Indicators Demo"); app.geometry("600x450")
    title_label = ctk.CTkLabel(app, text="Vintage Indicators Demo", font=("Roboto", 20)); title_label.pack(pady=20)
    led_frame = ctk.CTkFrame(app); led_frame.pack(pady=10)
    led_label_title = ctk.CTkLabel(led_frame, text="Worn LEDs", font=("Roboto", 14)); led_label_title.pack(pady=(0, 5))
    led_indicators_frame = ctk.CTkFrame(led_frame, fg_color="transparent"); led_indicators_frame.pack()
    leds = []; led_colors = ["#ff0000", "#00ff00", "#0088ff", "#ffff00", "#ff00ff"]
    app_bg = app.cget("fg_color")
    for i, color in enumerate(led_colors):
        wear = random.uniform(0.6, 0.9)
        led = WornLED(led_indicators_frame, color=color, size=40, explicit_canvas_bg=app_bg); led.pack(side="left", padx=10)
        led.set_wear_level(wear)
        if i % 2 == 0: led.set_state("on")
        if i % 3 != 1: led.enable_flicker(True)
        leds.append(led)
    neon_frame = ctk.CTkFrame(app); neon_frame.pack(pady=20)
    neon_label_title = ctk.CTkLabel(neon_frame, text="Neon Lights", font=("Roboto", 14)); neon_label_title.pack(pady=(0, 5))
    neon_indicators_frame = ctk.CTkFrame(neon_frame, fg_color="transparent"); neon_indicators_frame.pack()
    neons = []; neon_colors = ["#ff00ff", "#00ffff", "#ff6600", "#39ff14"]
    for i, color in enumerate(neon_colors):
        neon = NeonLight(neon_indicators_frame, color=color, width=120, height=30, explicit_canvas_bg=app_bg); neon.pack(side="top", pady=8)
        neon.set_wear_level(random.uniform(0.5, 0.8))
        if i % 2 == 0: neon.set_state("on"); neon.enable_flicker(True)
        neons.append(neon)
    control_frame = ctk.CTkFrame(app); control_frame.pack(pady=10, fill="x", padx=20); control_frame.grid_columnconfigure((0, 1, 2), weight=1)
    led_control = ctk.CTkFrame(control_frame, fg_color="transparent"); led_control.grid(row=0, column=0, padx=10)
    def toggle_leds():
        for led in leds: led.toggle()
    led_toggle = ctk.CTkButton(led_control, text="Toggle LEDs", command=toggle_leds); led_toggle.pack(pady=5)
    neon_control = ctk.CTkFrame(control_frame, fg_color="transparent"); neon_control.grid(row=0, column=1, padx=10)
    def toggle_neons():
        for neon in neons: neon.toggle()
    neon_toggle = ctk.CTkButton(neon_control, text="Toggle Neons", command=toggle_neons); neon_toggle.pack(pady=5)
    flicker_control = ctk.CTkFrame(control_frame, fg_color="transparent"); flicker_control.grid(row=0, column=2, padx=10)
    flicker_var = ctk.BooleanVar(value=True)
    def toggle_all_flicker():
        enabled = flicker_var.get()
        for led in leds: led.enable_flicker(enabled)
        for neon in neons: neon.enable_flicker(enabled)
    flicker_switch = ctk.CTkSwitch(flicker_control, text="Flicker", variable=flicker_var, command=toggle_all_flicker); flicker_switch.pack(pady=5)
    toggle_all_flicker()
    app.mainloop()

```


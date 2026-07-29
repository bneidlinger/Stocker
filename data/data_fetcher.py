# data/data_fetcher.py
# Handles fetching financial data

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time
import random
import os


class DataFetcher:
    """
    Class responsible for fetching historical stock data using yfinance.
    """

    def __init__(self, cache_dir: str = None):
        """Initializes the DataFetcher.

        Args:
            cache_dir: Override the cache directory (used by tests). Defaults
                       to <repo>/data/cache.
        """
        self.cache_dir = cache_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        self.max_retries = 3
        self.retry_delay = 5  # seconds

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
        # Try to load from cache first
        cache_file = os.path.join(self.cache_dir, f"{symbol}_{period}_{interval}.csv")
        
        # Check if cache exists and is recent (less than 24 hours old)
        if os.path.exists(cache_file):
            cache_age = time.time() - os.path.getmtime(cache_file)
            if cache_age < 86400:  # 24 hours in seconds
                try:
                    print(f"Loading {symbol} data from cache")
                    history = pd.read_csv(cache_file, index_col=0, parse_dates=True)
                    return history
                except Exception as e:
                    print(f"Error reading cache for {symbol}: {e}")
                    # Continue to fetch from API if cache read fails
            else:
                print(f"Cache for {symbol} is outdated")
        
        print(f"Fetching data for {symbol} | Period: {period} | Interval: {interval}")
        
        # Add jitter to prevent synchronized API requests
        jitter = random.uniform(0.5, 2.0)
        time.sleep(jitter)
        
        # Implement retry logic
        for attempt in range(self.max_retries):
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
                if 'close' not in history.columns and 'adj close' in history.columns:
                    history.rename(columns={'adj close': 'close'}, inplace=True)
                elif 'close' not in history.columns:
                    print(f"Warning: 'close' column missing and could not be derived for {symbol}.")

                # Ensure required columns are present for many backtesting libraries
                required_cols = ['open', 'high', 'low', 'close', 'volume']
                if not all(col in history.columns for col in required_cols):
                    print(
                        f"Warning: Missing required OHLCV columns in data for {symbol}. Found: {history.columns.tolist()}")

                # Save to cache
                try:
                    history.to_csv(cache_file)
                    print(f"Saved {symbol} data to cache")
                except Exception as e:
                    print(f"Error saving cache for {symbol}: {e}")
                
                print(f"Successfully fetched {len(history)} data points for {symbol}")
                return history

            except Exception as e:
                if "Too Many Requests" in str(e) or "Rate limit" in str(e):
                    wait_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    print(f"Rate limit hit for {symbol}. Retrying in {wait_time} seconds... (Attempt {attempt+1}/{self.max_retries})")
                    time.sleep(wait_time)
                else:
                    print(f"Error fetching data for {symbol}: {e}")
                    return None
        
        print(f"Failed to fetch data for {symbol} after {self.max_retries} attempts")
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
        # Check if we have cached price data less than 15 minutes old
        cache_file = os.path.join(self.cache_dir, f"{symbol}_current_price.csv")
        if os.path.exists(cache_file):
            cache_age = time.time() - os.path.getmtime(cache_file)
            if cache_age < 900:  # 15 minutes in seconds
                cached_price = self._read_price_cache(cache_file)
                if cached_price is not None:
                    print(f"Using cached current price for {symbol}: {cached_price}")
                    return cached_price
                # Continue to fetch from API if cache read fails
        
        # Add jitter to prevent synchronized API requests
        jitter = random.uniform(0.1, 0.5)
        time.sleep(jitter)
        
        # Implement retry logic
        for attempt in range(self.max_retries):
            try:
                ticker = yf.Ticker(symbol)
                # Try fast_info first (attribute access works across yfinance versions;
                # the dict-style keys changed to camelCase in yfinance 1.x)
                try:
                    price = ticker.fast_info.last_price
                except (AttributeError, KeyError):
                    price = None

                if price:
                    # Successfully got price via fast_info
                    price = float(price)
                    self._write_price_cache(cache_file, price)
                    return price
                else:
                    # Fallback: get last closing price from recent history
                    hist = ticker.history(period="2d")  # Get 2 days to ensure we get last close
                    if not hist.empty:
                        # Use the last non-NaN close (today's partial row can be NaN)
                        fallback_price = None
                        close_col = 'Close' if 'Close' in hist.columns else ('close' if 'close' in hist.columns else None)
                        if close_col is not None:
                            valid_closes = hist[close_col].dropna()
                            if not valid_closes.empty:
                                fallback_price = float(valid_closes.iloc[-1])

                        if fallback_price is not None:
                            print(f"Fallback successful: Using last closing price for {symbol}: {fallback_price}")
                            self._write_price_cache(cache_file, fallback_price)
                            return fallback_price
                        else:
                            print(f"Fallback failed: 'Close' column not found in fallback history for {symbol}.")
                            if attempt < self.max_retries - 1:
                                wait_time = self.retry_delay * (2 ** attempt)
                                print(f"Retrying in {wait_time} seconds... (Attempt {attempt+1}/{self.max_retries})")
                                time.sleep(wait_time)
                            continue
                    else:
                        print(f"Fallback failed: Could not retrieve history for {symbol}.")
                        if attempt < self.max_retries - 1:
                            wait_time = self.retry_delay * (2 ** attempt)
                            print(f"Retrying in {wait_time} seconds... (Attempt {attempt+1}/{self.max_retries})")
                            time.sleep(wait_time)
                        continue
                        
            except Exception as e:
                if "Too Many Requests" in str(e) or "Rate limit" in str(e):
                    wait_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    print(f"Rate limit hit for {symbol}. Retrying in {wait_time} seconds... (Attempt {attempt+1}/{self.max_retries})")
                    time.sleep(wait_time)
                else:
                    print(f"Error fetching current price for {symbol}: {e}")
                    return None
        
        print(f"Failed to fetch current price for {symbol} after {self.max_retries} attempts")
        return None

    @staticmethod
    def _write_price_cache(cache_file: str, price: float):
        """Writes a single price value to the cache file (no header)."""
        try:
            pd.DataFrame([float(price)]).to_csv(cache_file, index=False, header=False)
        except Exception as e:
            print(f"Error saving price cache to {cache_file}: {e}")

    @staticmethod
    def _read_price_cache(cache_file: str) -> float | None:
        """Reads a single price value from the cache file, or None if unreadable.

        The file is written without a header (see _write_price_cache), so it
        must be read with header=None -- reading with the default header=0
        consumes the value as a column name and leaves an empty frame.
        """
        try:
            price_df = pd.read_csv(cache_file, header=None)
            return float(price_df.iloc[0, 0])
        except Exception as e:
            print(f"Error reading cached price from {cache_file}: {e}")
            return None
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
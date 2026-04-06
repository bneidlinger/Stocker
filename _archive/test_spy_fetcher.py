# Test script for enhanced ETF data fetching
# Specifically for troubleshooting SPY and other problematic ETFs

import os
import sys
import pandas as pd
from config import ALPHA_VANTAGE_API_KEY
from data.alpha_vantage_fetcher import AlphaVantageDataFetcher

def main():
    """Test SPY data fetching with the enhanced AlphaVantageDataFetcher"""
    print("Testing enhanced AlphaVantage fetcher with problematic ETFs...")
    
    # Create fetcher
    av_fetcher = AlphaVantageDataFetcher(ALPHA_VANTAGE_API_KEY)
    
    # Set up cache directory 
    cache_dir = av_fetcher.cache_dir
    os.makedirs(cache_dir, exist_ok=True)
    
    print(f"Checking cache directory: {cache_dir}")
    
    # Force fresh fetches by clearing cache for test symbols
    symbols_to_test = ['SPY', 'QQQ', 'DIA']
    
    if os.path.exists(cache_dir):
        # List cached files
        try:
            cached_files = [f for f in os.listdir(cache_dir) if f.endswith('.csv')]
            print(f"Found {len(cached_files)} cached files")
            
            # Look for ETF cache files
            for symbol in symbols_to_test:
                symbol_caches = [f for f in cached_files if symbol.upper() in f]
                if symbol_caches:
                    print(f"{symbol} cache files found: {symbol_caches}")
                    
                    # Auto delete for test purposes
                    for cache_file in symbol_caches:
                        try:
                            os.remove(os.path.join(cache_dir, cache_file))
                            print(f"Deleted {cache_file}")
                        except Exception as e:
                            print(f"Could not delete {cache_file}: {e}")
        except Exception as e:
            print(f"Error accessing cache directory: {e}")
    
    # Test each ETF
    for symbol in symbols_to_test:
        print("\n" + "="*50)
        print(f"Testing {symbol} data fetch...")
        print("="*50)
        
        try:
            # Fetch with default settings
            print(f"\nFetching {symbol} with default settings...")
            df = av_fetcher.get_historical_data(symbol, period="1mo", interval="1d")
            
            if df is not None and not df.empty:
                print(f"SUCCESS! Fetched {len(df)} data points for {symbol}")
                print(f"Date range: {df.index.min()} to {df.index.max()}")
                print(f"Columns: {list(df.columns)}")
                print("\nSample data:")
                print(df.head(3).to_string())
            else:
                print(f"Failed to fetch {symbol} data")
        except Exception as e:
            print(f"Error during {symbol} test: {e}")
    
    # Special test for SPY with longer period
    try:
        print("\n" + "="*50)
        print("Testing SPY with 5y period...")
        print("="*50)
        
        df = av_fetcher.get_historical_data("SPY", period="5y", interval="1d")
        
        if df is not None and not df.empty:
            print(f"SUCCESS! Fetched {len(df)} data points for SPY (5y)")
            print(f"Date range: {df.index.min()} to {df.index.max()}")
        else:
            print("Failed to fetch SPY data with 5y period")
    except Exception as e:
        print(f"Error during SPY 5y test: {e}")
    
    print("\nTest complete!")

if __name__ == "__main__":
    main()
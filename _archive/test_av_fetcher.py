#!/usr/bin/env python3
"""
Test script for Alpha Vantage Data Fetcher
Directly tests fetching SPY data from Alpha Vantage
"""

import pandas as pd
import sys
import os
import requests

# Import our fetcher
from data.data_source_factory import DataSourceFactory
from data.alpha_vantage_fetcher import AlphaVantageDataFetcher
from config import ALPHA_VANTAGE_API_KEY

def test_direct_api_call(symbol):
    """Make a direct API call to Alpha Vantage for the symbol"""
    print(f"\n[TEST] Direct API call for {symbol}")
    
    base_url = "https://www.alphavantage.co/query"
    
    # Try different symbol formats
    symbols_to_try = [
        symbol,
        f"{symbol}.US",
        f"{symbol}:US",
        f"ARCX:{symbol}",
    ]
    
    for test_symbol in symbols_to_try:
        print(f"\nTrying symbol: {test_symbol}")
        
        # Set up parameters
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": test_symbol,
            "apikey": ALPHA_VANTAGE_API_KEY,
            "outputsize": "compact",
        }
        
        # Make request
        try:
            response = requests.get(base_url, params=params)
            print(f"Status code: {response.status_code}")
            
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
            
            # Check if we got time series data
            if "Time Series (Daily)" in data:
                time_series = data["Time Series (Daily)"]
                print(f"Successfully fetched data. Found {len(time_series)} data points")
                # Print first data point
                first_date = list(time_series.keys())[0]
                print(f"First data point ({first_date}): {time_series[first_date]}")
                return True
            elif "Error Message" in data:
                print(f"Error: {data['Error Message']}")
            elif "Information" in data:
                print(f"Information: {data['Information']}")
            elif "Note" in data:
                print(f"Note: {data['Note']}")
            else:
                print("Unknown response format")
        
        except Exception as e:
            print(f"Exception during API call: {e}")
    
    return False

def test_via_fetcher(symbol):
    """Test fetching data via our AlphaVantageDataFetcher class"""
    print(f"\n[TEST] Via AlphaVantageDataFetcher for {symbol}")
    
    # Create fetcher
    fetcher = AlphaVantageDataFetcher(ALPHA_VANTAGE_API_KEY)
    
    # Try to fetch data
    try:
        data = fetcher.get_historical_data(symbol, period="1mo", interval="1d")
        
        if data is not None and not data.empty:
            print(f"Successfully fetched {len(data)} data points")
            print(f"Columns: {data.columns.tolist()}")
            print("\nFirst 3 rows:")
            print(data.head(3))
            return True
        else:
            print("No data returned from fetcher")
            return False
            
    except Exception as e:
        print(f"Exception during fetcher test: {e}")
        return False

def test_via_factory(symbol):
    """Test fetching data via the factory"""
    print(f"\n[TEST] Via DataSourceFactory for {symbol}")
    
    # Get fetcher from factory
    try:
        fetcher = DataSourceFactory.get_data_fetcher()
        
        # Check if it's Alpha Vantage
        if not isinstance(fetcher, AlphaVantageDataFetcher):
            print("Warning: Factory returned non-Alpha Vantage fetcher")
            
        # Try to fetch data
        data = fetcher.get_historical_data(symbol, period="1mo", interval="1d")
        
        if data is not None and not data.empty:
            print(f"Successfully fetched {len(data)} data points")
            print(f"Columns: {data.columns.tolist()}")
            print("\nFirst 3 rows:")
            print(data.head(3))
            return True
        else:
            print("No data returned from factory-provided fetcher")
            return False
            
    except Exception as e:
        print(f"Exception during factory test: {e}")
        return False

def main():
    """Run tests for a given symbol or default to SPY"""
    # Get symbol from command line or use default
    symbol = sys.argv[1] if len(sys.argv) > 1 else "SPY"
    
    print(f"Testing Alpha Vantage fetcher with symbol: {symbol}")
    print(f"Using API key: {ALPHA_VANTAGE_API_KEY[:4]}...{ALPHA_VANTAGE_API_KEY[-4:]}")
    
    # Run tests
    direct_result = test_direct_api_call(symbol)
    fetcher_result = test_via_fetcher(symbol)
    factory_result = test_via_factory(symbol)
    
    # Report results
    print("\n===== TEST RESULTS =====")
    print(f"Direct API call: {'SUCCESS' if direct_result else 'FAILED'}")
    print(f"Via AlphaVantageDataFetcher: {'SUCCESS' if fetcher_result else 'FAILED'}")
    print(f"Via DataSourceFactory: {'SUCCESS' if factory_result else 'FAILED'}")

if __name__ == "__main__":
    main()
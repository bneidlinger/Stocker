#!/usr/bin/env python3
# Direct test of Alpha Vantage API

import requests
import json
import time
from config import ALPHA_VANTAGE_API_KEY

def test_direct_api_call(symbol="AMZN"):
    """Test a direct API call to Alpha Vantage"""
    # Alpha Vantage API URL and parameters
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": ALPHA_VANTAGE_API_KEY,
        "outputsize": "full"
    }
    
    print(f"Testing direct API call to Alpha Vantage for {symbol}")
    print(f"API Key: {ALPHA_VANTAGE_API_KEY}")
    print(f"URL: {url}")
    print(f"Params: {params}")
    
    # Custom headers to reduce chance of being blocked
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Make the API request
        response = requests.get(url, params=params, headers=headers)
        print(f"Response Status Code: {response.status_code}")
        
        # Check for successful response
        if response.status_code == 200:
            data = response.json()
            print(f"Response Data Keys: {list(data.keys())}")
            
            # Check for error messages
            if "Error Message" in data:
                print(f"API Error: {data['Error Message']}")
                return False
            
            # Check for rate limit messages
            if "Note" in data:
                print(f"API Note: {data['Note']}")
                if "call frequency" in data["Note"]:
                    print("API rate limit reached")
                    return False
                
            # Check for time series data
            time_series_key = "Time Series (Daily)"
            if time_series_key in data:
                time_series = data[time_series_key]
                print(f"Found {len(time_series)} days of data")
                
                # Display first few entries
                print("\nSample Data:")
                for i, (date, values) in enumerate(time_series.items()):
                    print(f"{date}: {json.dumps(values)}")
                    if i >= 2:  # Show just first 3 entries
                        break
                
                # Check if data seems valid
                if len(time_series) > 100:
                    print("\nSUCCESS: API returned sufficient data for analysis")
                    return True
                else:
                    print(f"\nWARNING: API returned only {len(time_series)} data points")
                    return True
            else:
                print(f"Time series key '{time_series_key}' not found in response")
                print(f"Available keys: {list(data.keys())}")
                return False
        else:
            print(f"Error: API call failed with status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Exception during API call: {e}")
        return False

def test_multiple_symbols():
    """Test API with multiple symbols"""
    symbols = ["AMZN", "AAPL", "NVDA", "SPY", "QQQ"]
    
    for symbol in symbols:
        print("\n" + "="*60)
        print(f"Testing symbol: {symbol}")
        print("="*60)
        success = test_direct_api_call(symbol)
        print(f"Result for {symbol}: {'SUCCESS' if success else 'FAILED'}")
        
        # Wait between calls to avoid rate limits
        time.sleep(15)

if __name__ == "__main__":
    print("Direct Alpha Vantage API Test")
    test_multiple_symbols()
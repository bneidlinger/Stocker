# Factory for creating data fetcher instances

from data.data_fetcher import DataFetcher
from data.alpha_vantage_fetcher import AlphaVantageDataFetcher
from config import ALPHA_VANTAGE_API_KEY, USE_ALPHA_VANTAGE


class DataSourceFactory:
    """
    Factory class for creating data fetcher instances.
    Allows switching between different data sources.
    """

    @staticmethod
    def get_data_fetcher(source: str = None, fetch_advanced_features: bool = False):
        """
        Returns a data fetcher instance based on the specified source.

        Args:
            source (str, optional): The data source to use.
                                    If None, uses the default from config.
            fetch_advanced_features (bool): Whether to fetch advanced features like technical
                                            indicators directly from Alpha Vantage.

        Returns:
            A data fetcher instance.
        """
        # If no source specified, use the default from config
        if source is None:
            source = "alpha_vantage" if USE_ALPHA_VANTAGE else "yfinance"

        # Create the appropriate fetcher
        if source.lower() == "alpha_vantage":
            if not ALPHA_VANTAGE_API_KEY:
                print("Warning: Alpha Vantage API key not set in config. Falling back to yfinance.")
                return DataFetcher()
            
            # Create Alpha Vantage fetcher with specified configuration
            fetcher = AlphaVantageDataFetcher(ALPHA_VANTAGE_API_KEY)
            
            # Store a flag on the fetcher indicating advanced features preference
            fetcher.fetch_advanced_features = fetch_advanced_features
            
            return fetcher
        else:
            # Default to yfinance
            return DataFetcher()
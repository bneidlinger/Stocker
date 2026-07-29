# Factory for creating data fetcher instances

from data.data_fetcher import DataFetcher


class DataSourceFactory:
    """
    Factory class for creating data fetcher instances.
    Allows adding alternative data sources later without touching callers.
    """

    _FETCHERS = {
        "yfinance": DataFetcher,
    }

    @staticmethod
    def get_data_fetcher(source: str = None):
        """
        Returns a data fetcher instance for the requested source.

        Args:
            source (str, optional): The data source to use. Defaults to yfinance.

        Returns:
            A data fetcher instance.
        """
        key = (source or "yfinance").lower()
        fetcher_class = DataSourceFactory._FETCHERS.get(key)
        if fetcher_class is None:
            print(f"Warning: Unknown data source '{source}'. Falling back to yfinance.")
            fetcher_class = DataFetcher
        return fetcher_class()

# Tests for the DataFetcher 15-minute price cache round-trip.
# Locks in the fix for the original bug: the cache was written header-less but
# read with pandas' default header=0, so the value became a column name and the
# cache never produced a hit.

import os

from data.data_fetcher import DataFetcher


def test_price_cache_round_trip(tmp_path):
    fetcher = DataFetcher(cache_dir=str(tmp_path))
    cache_file = os.path.join(fetcher.cache_dir, "TEST_current_price.csv")

    fetcher._write_price_cache(cache_file, 123.45)
    assert os.path.exists(cache_file)
    assert fetcher._read_price_cache(cache_file) == 123.45


def test_price_cache_read_returns_float(tmp_path):
    fetcher = DataFetcher(cache_dir=str(tmp_path))
    cache_file = os.path.join(fetcher.cache_dir, "TEST_current_price.csv")
    fetcher._write_price_cache(cache_file, 740)
    value = fetcher._read_price_cache(cache_file)
    assert isinstance(value, float)
    assert value == 740.0


def test_price_cache_corrupt_file_returns_none(tmp_path):
    fetcher = DataFetcher(cache_dir=str(tmp_path))
    cache_file = os.path.join(fetcher.cache_dir, "BAD_current_price.csv")
    with open(cache_file, "w") as f:
        f.write("")  # empty file
    assert fetcher._read_price_cache(cache_file) is None


def test_price_cache_missing_file_returns_none(tmp_path):
    fetcher = DataFetcher(cache_dir=str(tmp_path))
    missing = os.path.join(fetcher.cache_dir, "NOPE_current_price.csv")
    assert fetcher._read_price_cache(missing) is None

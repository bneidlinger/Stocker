# Regression tests for the historical-data CSV cache round trip.
#
# yfinance indexes are tz-aware with mixed UTC offsets across DST transitions
# (EST -05:00 / EDT -04:00). pandas 2 cannot parse such a column back into a
# DatetimeIndex from CSV -- it silently returns an object index, which broke
# the backtester ("Data index is not datetime") and dropped every date-based
# ML feature on any cache hit. Found live; locked in here.

import os

import pandas as pd

from data.data_fetcher import DataFetcher


def _fetcher(tmp_path):
    return DataFetcher(cache_dir=str(tmp_path))


def test_legacy_mixed_offset_cache_recovers_datetimeindex(tmp_path):
    fetcher = _fetcher(tmp_path)
    cache_file = os.path.join(fetcher.cache_dir, "MIX_5y_1d.csv")
    with open(cache_file, "w") as f:
        f.write("Date,open,high,low,close,volume\n"
                "2024-01-05 00:00:00-05:00,1.0,1.1,0.9,1.0,100\n"  # EST
                "2024-07-05 00:00:00-04:00,2.0,2.1,1.9,2.0,200\n")  # EDT

    df = fetcher._read_cached_history(cache_file)
    assert isinstance(df.index, pd.DatetimeIndex)
    assert df.index.tz is None
    # Wall-clock dates preserved across the DST boundary
    assert df.index[0].date().isoformat() == "2024-01-05"
    assert df.index[1].date().isoformat() == "2024-07-05"


def test_naive_cache_round_trip_stays_datetimeindex(tmp_path):
    fetcher = _fetcher(tmp_path)
    cache_file = os.path.join(fetcher.cache_dir, "CLEAN_5y_1d.csv")
    idx = pd.bdate_range("2024-01-02", periods=5)
    original = pd.DataFrame({"open": 1.0, "high": 1.1, "low": 0.9,
                             "close": 1.0, "volume": 100.0}, index=idx)
    original.to_csv(cache_file)

    df = fetcher._read_cached_history(cache_file)
    assert isinstance(df.index, pd.DatetimeIndex)
    assert df.index.tz is None
    assert list(df.index) == list(idx)

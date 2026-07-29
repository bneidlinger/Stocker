# Shared fixtures for the Stocker test suite.
# Rule: no network, no Tk, no real cache dirs in any test.

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def ohlcv_df() -> pd.DataFrame:
    """Seeded synthetic OHLCV frame: 300 business days, lowercase columns,
    DatetimeIndex -- the same shape the data layer hands to the rest of the app."""
    rng = np.random.default_rng(42)
    n = 300
    idx = pd.bdate_range("2023-01-02", periods=n)

    rets = rng.normal(0.0005, 0.015, n)
    close = 100.0 * np.cumprod(1.0 + rets)
    open_ = np.concatenate([[100.0], close[:-1]])
    high = np.maximum(open_, close) * (1.0 + rng.uniform(0.001, 0.01, n))
    low = np.minimum(open_, close) * (1.0 - rng.uniform(0.001, 0.01, n))
    volume = rng.integers(1_000_000, 5_000_000, n).astype(float)

    return pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "volume": volume},
        index=idx,
    )

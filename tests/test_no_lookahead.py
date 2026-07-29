# Lookahead-leakage property test for feature engineering.
#
# Property: computing features on a truncated history (df.iloc[:n]) must give
# exactly the same values for the last row as computing on the full history and
# reading row n-1. If any feature "sees the future" (backfill, global medians,
# forward-shifted windows), the two disagree and this test fails.

import numpy as np
import pandas as pd

from trading.ml.features import FeatureEngineer


def test_features_identical_with_and_without_future_data(ohlcv_df):
    n = 250  # leave 50 rows of "future" beyond the truncation point

    full = FeatureEngineer.engineer_features(ohlcv_df, with_date_features=True,
                                             min_required_samples=50)
    truncated = FeatureEngineer.engineer_features(ohlcv_df.iloc[:n], with_date_features=True,
                                                  min_required_samples=50)

    assert not truncated.empty
    cutoff_date = truncated.index[-1]
    assert cutoff_date in full.index, "truncation-point row missing from full run"

    row_full = full.loc[cutoff_date]
    row_trunc = truncated.iloc[-1]

    shared_cols = [c for c in truncated.columns if c in full.columns]
    assert shared_cols, "no shared feature columns to compare"

    mismatches = []
    for col in shared_cols:
        a, b = row_trunc[col], row_full[col]
        if isinstance(a, (int, float, np.floating, np.integer)):
            if not np.isclose(float(a), float(b), rtol=1e-9, atol=1e-12, equal_nan=True):
                mismatches.append((col, a, b))
        elif a != b:
            mismatches.append((col, a, b))

    assert mismatches == [], f"features leak future data: {mismatches[:5]}"


def test_no_absolute_price_level_features(ohlcv_df):
    features = FeatureEngineer.engineer_features(ohlcv_df, with_date_features=True,
                                                 min_required_samples=50)
    banned_prefixes = ("sma_", "ema_")
    banned_exact = {"bb_upper", "bb_lower", "year", "capital gains"}
    offenders = [c for c in features.columns
                 if c.startswith(banned_prefixes) or c in banned_exact]
    assert offenders == [], f"absolute-level/regime features present: {offenders}"


def test_warmup_rows_dropped_not_filled(ohlcv_df):
    features = FeatureEngineer.engineer_features(ohlcv_df, with_date_features=True,
                                                 min_required_samples=50)
    # No NaNs anywhere (they must be dropped, not filled with future data)
    assert not features.isna().any().any()
    # The 200-period window means roughly the first 200 rows cannot be complete
    assert features.index[0] > ohlcv_df.index[150]

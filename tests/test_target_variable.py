# Tests for FeatureEngineer.get_target_variable: future-return math,
# threshold classification, and trailing-NaN handling.

import numpy as np
import pandas as pd

from trading.ml.features import FeatureEngineer


def _make_close_df(closes):
    idx = pd.bdate_range("2024-01-01", periods=len(closes))
    return pd.DataFrame({"close": closes}, index=idx)


def test_future_return_math(ohlcv_df):
    horizon = 5
    result = FeatureEngineer.get_target_variable(ohlcv_df, horizon=horizon, threshold=0.01)
    col = f"future_return_{horizon}d"
    assert col in result.columns

    close = ohlcv_df["close"]
    for t in [0, 37, 150, len(close) - horizon - 1]:
        expected = close.iloc[t + horizon] / close.iloc[t] - 1.0
        assert np.isclose(result[col].iloc[t], expected), f"row {t} future return wrong"


def test_trailing_rows_have_nan_future_return(ohlcv_df):
    horizon = 5
    result = FeatureEngineer.get_target_variable(ohlcv_df, horizon=horizon, threshold=0.01)
    col = f"future_return_{horizon}d"
    assert result[col].iloc[-horizon:].isna().all()
    assert result[col].iloc[:-horizon].notna().all()


def test_threshold_classification():
    # horizon=1, threshold=1%: constructed moves -> known classes
    closes = [100.0, 102.0, 101.5, 90.0, 90.5]
    df = _make_close_df(closes)
    result = FeatureEngineer.get_target_variable(df, horizon=1, threshold=0.01)
    target = result["target_direction_1d"]

    assert target.iloc[0] == 1    # 100 -> 102 = +2.0%  (> +1%)
    assert target.iloc[1] == 0    # 102 -> 101.5 = -0.49% (within band)
    assert target.iloc[2] == -1   # 101.5 -> 90 = -11.3% (< -1%)
    assert target.iloc[3] == 0    # 90 -> 90.5 = +0.56% (within band)
    # Last row has no future data; the NaN comparison leaves the neutral default.
    assert target.iloc[4] == 0

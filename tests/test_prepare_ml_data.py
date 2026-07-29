# Tests for FeatureEngineer.prepare_ml_data: chronological split and
# exclusion of target/future columns from the feature matrix.

from trading.ml.features import FeatureEngineer


def _prepared(ohlcv_df, horizon=5, threshold=0.01):
    features = FeatureEngineer.engineer_features(ohlcv_df, with_date_features=True,
                                                 min_required_samples=50)
    return FeatureEngineer.get_target_variable(features, horizon=horizon, threshold=threshold)


def test_split_is_chronological_and_sized(ohlcv_df):
    prepared = _prepared(ohlcv_df)
    target_col = "target_direction_5d"
    X_train, X_test, y_train, y_test, feature_cols = FeatureEngineer.prepare_ml_data(
        prepared, target_col=target_col, test_size=0.2)

    total = len(X_train) + len(X_test)
    clean_rows = len(prepared.dropna())
    assert total == clean_rows
    # No shuffle: split index is a simple 80/20 cut of the time-ordered rows
    assert len(X_train) == int(clean_rows * 0.8)
    assert len(y_train) == len(X_train)
    assert len(y_test) == len(X_test)
    assert X_train.shape[1] == len(feature_cols)


def test_future_and_target_columns_excluded(ohlcv_df):
    prepared = _prepared(ohlcv_df)
    _, _, _, _, feature_cols = FeatureEngineer.prepare_ml_data(
        prepared, target_col="target_direction_5d", test_size=0.2)

    leaky = [c for c in feature_cols if c.startswith(("future_", "target_"))]
    assert leaky == [], f"target/future columns leaked into features: {leaky}"

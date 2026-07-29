# Tests for trading.backtester.run_backtest: column mapping, stats shape,
# and the _trades payload.

from trading.backtester import run_backtest
from trading.strategies.sma_cross import SmaCross


def test_run_backtest_returns_stats_with_trades(ohlcv_df):
    stats, bt = run_backtest(SmaCross, ohlcv_df, cash=10_000, commission=0.001,
                             n1=5, n2=15, trade_size_percent=0.95)
    assert stats is not None
    assert bt is not None
    assert "_trades" in stats.index
    assert "Return [%]" in stats.index
    # A 5/15 cross on a 300-day random walk should actually trade
    assert len(stats["_trades"]) > 0


def test_run_backtest_rejects_missing_columns(ohlcv_df):
    incomplete = ohlcv_df.drop(columns=["volume"])
    stats, bt = run_backtest(SmaCross, incomplete, cash=10_000, commission=0.001)
    assert stats is None
    assert bt is None


def test_run_backtest_rejects_empty_data(ohlcv_df):
    stats, bt = run_backtest(SmaCross, ohlcv_df.iloc[0:0], cash=10_000, commission=0.001)
    assert stats is None
    assert bt is None

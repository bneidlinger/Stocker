# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Stocker is a retro-themed (Miami Vice / Fallout) stock trading desktop app built with customtkinter. It fetches historical data via yfinance, runs strategy backtests via the `backtesting` library, produces TA + ML trading recommendations, includes Claude-powered sentiment analysis, and has an AI auto-trader that trades through Alpaca (paper by default) with Claude approving each trade.

## Running the App

```bash
pip install -r requirements.txt
python main.py
```

**TA-Lib** requires its C library before `pip install TA-Lib`. On Windows use a pre-built wheel; on macOS `brew install ta-lib`. See `TALIB_INSTALLATION.md`.

**API keys** come exclusively from environment variables / `.env` (see `.env.example`): `ANTHROPIC_API_KEY` (sentiment + trade decisions), `ALPACA_API_KEY`/`ALPACA_API_SECRET` (auto-trading), `DISCORD_WEBHOOK_URL` (optional). `main.py` calls `load_dotenv()` at startup. Never hardcode keys in config.py.

## Tests

```bash
python -m pytest
```

`tests/` covers target-variable math, the no-lookahead feature-engineering property, model cloning, the backtester, the price cache, and the auto-trader (budget accounting, kill-switch ordering, stop-loss sizing) via `FakeBroker`/`FakeClaude`. Tests use no network and no Tk. No linter is configured.

## Architecture

**Entry point**: `main.py` -- sets the customtkinter theme, creates `App()`, starts mainloop.

**`gui/app.py` (`App` class)** -- the monolithic main window: chart rendering (matplotlib via `FigureCanvasTkAgg`), strategy selection, backtest execution, recommendation display, ML controls, and the kill switch. Largest file.

- **Threading rule**: every slow operation (data fetch, backtest, ML training, sentiment, broker connect) runs through `App.run_in_background(fn, on_done, on_error, busy_widgets, led)`. `fn` executes on a daemon thread and must never touch Tk objects -- snapshot inputs (`df.copy()`, Tk var values) on the main thread before submitting, return plain data (plus `(message, tag)` log tuples where needed), and do all UI work in `on_done`/`on_error` (marshaled via `self.after`).

**Data layer** (`data/`):
- `DataSourceFactory` returns a `DataFetcher` (yfinance -- the only source; the factory exists so others can be added).
- `DataFetcher` caches CSVs in `data/cache/` with a 24-hour TTL; retry sleeps are interruptible via a shutdown event set in `App.on_closing`.
- Data uses **lowercase OHLCV columns** (`open`, `high`, `low`, `close`, `volume`). The backtester renames to title-case for `backtesting.py`.

**Trading strategies** (`trading/strategies/`):
- 10 strategies inheriting `backtesting.Strategy` with `init()`/`next()`.
- Strategies depending on TA-Lib or `ephem` load dynamically via string paths in `STRATEGY_LOADERS` (`gui/app.py`, resolved by `App._load_strategy_class`); others import directly.
- Parameters live in `PARAM_CONFIG`; `trade_size_percent` is auto-inserted first. To add a strategy: create the class, then add entries to `STRATEGY_LOADERS`, `PARAM_CONFIG`, and `STRATEGY_DESCRIPTIONS`.

**Backtester** (`trading/backtester.py`): `run_backtest()` wraps `backtesting.Backtest`, returns `(stats, backtest_object)`; `stats['_trades']` is always present.

**ML pipeline** (`trading/ml/`):
- `FeatureEngineer` -- emits scale-free features only (`close_to_sma_*`, `bb_width`, `bb_pos`, returns, RSI, MACD -- no absolute price levels, no `year`). NaN policy is forward-fill only with warm-up rows dropped; **never** backfill or median-fill (lookahead leakage -- `tests/test_no_lookahead.py` enforces the property).
- `ModelManager` -- sklearn models saved to `data/models/`. The `CLASSIFICATION_MODELS` registry holds unfitted templates; training always fits a `clone()`, never the template.
- `MlPredictionService` -- orchestrates training/prediction/hybrid; internally RLock'd because it is shared between the Tk thread and the auto-trader thread.

**Auto-trader** (`trading/auto_trader.py` + `broker/`, `ai/`, `notifications/`, `gui/auto_trader_tab.py`):
- `AlpacaBrokerClient` (`broker/alpaca_client.py`) wraps **alpaca-py**. Invariants: IEX data feed (free plan), `get_bars` always passes an explicit `start` (the API otherwise silently truncates to today), and `liquidate_position` cancels the symbol's open orders first (a resting stop leg holds the shares and Alpaca rejects the close otherwise).
- `AutoTrader` runs cycles on a daemon thread: reconcile budget from the broker's actual position -> software stop-loss check -> daily bars (400) for ML prediction -> Claude approves/rejects -> execute with actual-fill accounting (`_await_fill` polls to a terminal state; cancel-then-fetch on timeout). Whole-share buys carry a broker-side OTO stop leg with GTC; fractional entries rely on the per-cycle software stop.
- **Kill-switch ordering is load-bearing**: `stop(liquidate=)` returns immediately; the shutdown worker joins the in-flight cycle FIRST and liquidates after, with stop-event guards before any order submission. Never reorder this -- a cycle blocked in the Claude call could otherwise re-open the position right after liquidation.
- Paper trading is the default. The Claude model id is single-sourced from `config.CLAUDE_MODEL`.

**Sentiment** (`sentiment/`): `MarketSentimentAnalyzer` calls the Claude API (via `ai/claude_client.py`); HTML reports escape all model-derived strings and are written to `%TEMP%/stocker_reports/`, swept on the next analyzer init. `SentimentModule` provides the UI tab; the Claude call runs through `run_in_background`.

**Config** (`config.py`): constants only -- symbols, backtest defaults, recommendation parameters, theme colors, fonts, ML settings, `CLAUDE_MODEL`, observer coordinates (moon strategy). API keys are read from env vars here, never stored.

## Key Patterns

- **Column conventions**: raw data lowercase; the backtester maps to title-case.
- **Worker rule**: background functions never call `log_message`, plot, or touch widgets -- return data and log tuples, apply them in `on_done`.
- **Virtual environment**: `.venv/` (Python 3.13). Dependencies pinned in `requirements.txt`; dev tools in `requirements-dev.txt`.

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Stocker is a retro-themed (Miami Vice / Fallout) stock trading backtesting desktop app built with customtkinter. It fetches historical data, runs strategy backtests via the `backtesting` library, provides trading recommendations, trains ML models for prediction, and includes OpenAI-powered sentiment analysis.

## Running the App

```bash
pip install -r requirements.txt
python main.py
```

**TA-Lib** requires a C library installed separately before `pip install TA-Lib`. On Windows, use pre-compiled wheels. On macOS: `brew install ta-lib`. See `TALIB_INSTALLATION.md`.

There is no test suite. No linter or formatter is configured.

## Architecture

**Entry point**: `main.py` -- sets customtkinter theme, creates `App()`, starts mainloop.

**`gui/app.py` (`App` class)** -- The monolithic main window. Owns the entire UI: chart rendering (matplotlib embedded via `FigureCanvasTkAgg`), strategy selection, backtest execution, recommendation engine, and ML controls. Imports everything else. This is the largest and most complex file.

**Data layer** (`data/`):
- `DataSourceFactory` selects between `DataFetcher` (yfinance) and `AlphaVantageDataFetcher` based on `config.USE_ALPHA_VANTAGE`.
- `DataFetcher` caches responses as CSV in `data/cache/` with 24-hour TTL.
- Data uses **lowercase OHLCV columns** (`open`, `high`, `low`, `close`, `volume`). The backtester renames to title-case for `backtesting.py` compatibility.

**Trading strategies** (`trading/strategies/`):
- Each strategy inherits from `backtesting.Strategy` with `init()` and `next()` methods.
- 10 strategies: SMA Cross, RSI, MACD, Bollinger Bands, Volatility Breakout, Ichimoku, Donchian, Day of Week, Fake Moon, Real Moon (requires `ephem`).
- **Dynamic loading**: Strategies that depend on TA-Lib or `ephem` are loaded via string paths in `STRATEGY_LOADERS` (in `gui/app.py`) using `importlib`. Non-dependency strategies are imported directly.
- Strategy parameters are defined in `PARAM_CONFIG` dict in `gui/app.py`. Every strategy gets `trade_size_percent` auto-inserted as the first parameter.

**Backtester** (`trading/backtester.py`):
- `run_backtest()` function wraps `backtesting.Backtest`. Renames lowercase columns to title-case, runs the strategy, returns `(stats, backtest_object)`.

**ML pipeline** (`trading/ml/`):
- `FeatureEngineer` -- computes technical features from OHLCV data.
- `ModelManager` -- trains/saves/loads scikit-learn models (stored in `data/models/`).
- `MlPredictionService` -- orchestrates feature engineering, model training, and prediction. Produces direction (UP/NEUTRAL/DOWN) with confidence levels.
- Hybrid mode (`ML_ENABLE_HYBRID`) blends ML predictions with technical analysis recommendations.

**Sentiment** (`sentiment/`):
- `MarketSentimentAnalyzer` uses OpenAI API for sentiment analysis.
- `SentimentModule` provides the UI integration (frame with controls embedded in main app).

**Config** (`config.py`):
- All constants: stock symbols, data periods, backtest defaults, recommendation engine parameters, API keys, theme colors, font settings, ML settings, observer coordinates (for moon strategy).
- Theme colors are referenced by name throughout the GUI (e.g., `COLOR_BACKGROUND`, `COLOR_BUTTON`).

## Key Patterns

- **API keys**: Alpha Vantage key is in `config.py`. OpenAI key can be set via env var or `config.py`. The app calls `load_dotenv()` at startup.
- **Column conventions**: Raw data uses lowercase columns. `backtesting.py` requires title-case. The backtester handles the mapping.
- **Strategy registration**: To add a strategy, create the class in `trading/strategies/`, then add entries to `STRATEGY_LOADERS`, `PARAM_CONFIG`, and `STRATEGY_DESCRIPTIONS` in `gui/app.py`.
- **Virtual environment**: Located at `.venv/`.

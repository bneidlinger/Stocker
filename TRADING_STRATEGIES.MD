# Retro Trading Console: Trading Strategies Guide

## Introduction

This document provides detailed information on each trading strategy implemented in the Retro Trading Console. Understanding these strategies and their parameters will help you create more effective backtests and improve your trading decisions.

## Available Strategies

### 1. SMA Crossover Strategy

**Description:** A simple trend-following strategy using two Simple Moving Averages (SMA) of different periods. When the short-term SMA crosses above the long-term SMA, it generates a buy signal. When the short-term SMA crosses below the long-term SMA, it generates a sell signal.

**Parameters:**
- `n1` (default: 10): Short-term SMA period
- `n2` (default: 30): Long-term SMA period
- `trade_size_percent` (default: 95): Percentage of available cash to use for each trade

**Best For:** Trend-following in markets with clear directional movements. Performs poorly in sideways or choppy markets.

**Example Scenario:** If 20-day SMA crosses above 50-day SMA, buy the stock. If 20-day SMA crosses below 50-day SMA, sell the position.

### 2. RSI Oscillator Strategy

**Description:** A mean-reversion strategy based on the Relative Strength Index (RSI) indicator. RSI measures the speed and change of price movements on a scale from 0 to 100. Traditionally, an RSI above 70 indicates overbought conditions, while an RSI below 30 indicates oversold conditions.

**Parameters:**
- `rsi_period` (default: 14): Period used to calculate RSI
- `upper_bound` (default: 70): RSI threshold for overbought conditions
- `lower_bound` (default: 30): RSI threshold for oversold conditions
- `trade_size_percent` (default: 95): Percentage of available cash to use for each trade

**Best For:** Range-bound markets where prices tend to oscillate between support and resistance levels.

**Example Scenario:** When RSI drops below 30 and then rises back above 30, buy the stock. When RSI rises above 70 and then drops back below 70, sell the position.

### 3. MACD Strategy

**Description:** A trend-following momentum strategy using the Moving Average Convergence Divergence (MACD) indicator. MACD consists of the MACD line (difference between two EMAs), signal line (EMA of MACD), and histogram (difference between MACD and signal line).

**Parameters:**
- `fast_period` (default: 12): Fast EMA period for MACD calculation
- `slow_period` (default: 26): Slow EMA period for MACD calculation
- `signal_period` (default: 9): Period for the signal line EMA
- `trade_size_percent` (default: 95): Percentage of available cash to use for each trade

**Best For:** Capturing trend changes and momentum shifts in trending markets.

**Example Scenario:** When the MACD line crosses above the signal line, buy the stock. When the MACD line crosses below the signal line, sell the position.

### 4. Bollinger Bands Strategy

**Description:** A mean-reversion strategy using Bollinger Bands, which consist of a middle band (typically a 20-day SMA) and two outer bands placed 2 standard deviations away from the middle band.

**Parameters:**
- `bb_period` (default: 20): Period for the middle band SMA
- `bb_std_dev` (default: 2): Number of standard deviations for the outer bands
- `trade_size_percent` (default: 95): Percentage of available cash to use for each trade

**Best For:** Identifying overbought and oversold conditions in range-bound markets.

**Example Scenario:** When price touches or crosses below the lower band, buy the stock. When price touches or crosses above the upper band, sell the position.

### 5. Volatility Breakout Strategy

**Description:** A trend-following strategy that triggers entries based on significant price movements relative to the Average True Range (ATR) indicator, which measures market volatility.

**Parameters:**
- `atr_period` (default: 14): Period for ATR calculation
- `ma_period` (default: 20): Period for the moving average base
- `atr_multiplier` (default: 2): Multiplier applied to ATR for determining breakout thresholds
- `trade_size_percent` (default: 95): Percentage of available cash to use for each trade

**Best For:** Catching strong directional moves in volatile markets.

**Example Scenario:** If price closes above the (MA + ATR*multiplier), buy the stock. If price closes below the MA, sell the position.

### 6. Ichimoku Cloud Strategy

**Description:** A comprehensive trend-following system using multiple components: Tenkan-sen (conversion line), Kijun-sen (base line), Senkou Span A & B (cloud), and Chikou Span (lagging span).

**Parameters:**
- `tenkan_period` (default: 9): Period for Tenkan-sen calculation
- `kijun_period` (default: 26): Period for Kijun-sen calculation
- `senkou_b_period` (default: 52): Period for Senkou Span B calculation
- `chikou_period` (default: 26): Period for Chikou Span
- `senkou_displacement` (default: 26): Forward displacement for the cloud
- `trade_size_percent` (default: 95): Percentage of available cash to use for each trade

**Best For:** Identifying trend direction, momentum, and potential reversal points.

**Example Scenario:** Buy when price is above the cloud, Tenkan-sen crosses above Kijun-sen, and price is above its value from 26 periods ago. Sell when the opposite conditions occur.

### 7. Donchian Channel Strategy

**Description:** A trend-following breakout strategy using Donchian Channels, which plot the highest high and lowest low over a specified period.

**Parameters:**
- `n_high` (default: 20): Lookback period for highest high
- `n_low` (default: 20): Lookback period for lowest low
- `trade_size_percent` (default: 95): Percentage of available cash to use for each trade

**Best For:** Capturing new trends when prices break out of their recent range.

**Example Scenario:** When price breaks above the highest high of the last 20 periods, buy the stock. When price breaks below the lowest low of the last 20 periods, sell the position.

### 8. Day of Week Strategy

**Description:** A simple calendar-based strategy that trades based on the day of the week, exploiting potential day-of-week effects in the market.

**Parameters:**
- `buy_day` (default: 0): Day to buy (0=Monday, 4=Friday)
- `sell_day` (default: 4): Day to sell (0=Monday, 4=Friday)
- `trade_size_percent` (default: 95): Percentage of available cash to use for each trade

**Best For:** Testing simple calendar effects and market anomalies.

**Example Scenario:** Buy at close on Monday, sell at close on Friday.

### 9. Fake Moon Strategy (Day of Month)

**Description:** A placeholder lunar strategy that trades based on the day of the month as a proxy for moon phases.

**Parameters:**
- `buy_day_start` (default: 1): Start day for buying
- `buy_day_end` (default: 5): End day for buying window
- `sell_day_start` (default: 14): Start day for selling
- `sell_day_end` (default: 18): End day for selling window
- `trade_size_percent` (default: 95): Percentage of available cash to use for each trade

**Best For:** Testing simplistic monthly cycle theories.

**Example Scenario:** Buy during days 1-5 of the month, sell during days 14-18.

### 10. Real Moon Strategy (Ephem)

**Description:** A more sophisticated lunar strategy that uses actual astronomical calculations via the ephem library to determine moon phases.

**Parameters:**
- `days_after_new_moon_buy` (default: 2): Days after New Moon to start buying
- `buy_window_days` (default: 3): Duration of buying window
- `days_after_full_moon_sell` (default: 2): Days after Full Moon to start selling
- `sell_window_days` (default: 3): Duration of selling window
- `trade_size_percent` (default: 95): Percentage of available cash to use for each trade

**Best For:** Testing lunar cycle theories with accurate astronomical data.

**Example Scenario:** Buy 2-5 days after New Moon, sell 2-5 days after Full Moon.

## Recommendation Engine

The application includes a recommendation engine that considers multiple technical indicators to provide trading suggestions. The engine calculates a score based on the following factors:

- Short-term vs. long-term SMA positions
- Trend strength (ADX indicator)
- MACD signal line crossovers
- RSI values
- Price position relative to Bollinger Bands

Recommendations are displayed on the dot matrix display and color-coded:
- BUY (Green): Strong bullish signals
- WEAK BUY (Light Green): Moderate bullish signals
- HOLD (Gray): Neutral signals
- WEAK SELL (Orange): Moderate bearish signals
- SELL (Red): Strong bearish signals

## Performance Metrics

When evaluating backtest results, pay attention to these key metrics:

- **Return [%]**: Total percentage return of the strategy
- **Exposure [%]**: Percentage of time invested in the market
- **Equity Final [$]**: Final equity after running the strategy
- **Equity Peak [$]**: Maximum equity achieved during the backtest
- **Return (Ann.) [%]**: Annualized return percentage
- **Volatility (Ann.) [%]**: Annualized volatility
- **Sharpe Ratio**: Return/risk ratio (higher is better)
- **Sortino Ratio**: Similar to Sharpe but only considers downside risk
- **Win Rate [%]**: Percentage of winning trades
- **SQN**: System Quality Number (measures strategy robustness)

## Tips for Strategy Optimization

1. **Avoid Over-Optimization:** Strategies that perform too perfectly on historical data often fail in live trading due to curve-fitting.

2. **Consider Transaction Costs:** The default commission rate is 0.1% per trade. Adjust this to match your broker's fees.

3. **Test Multiple Market Conditions:** A good strategy should perform reasonably well in both bull and bear markets.

4. **Compare Against Buy-and-Hold:** Your strategy should outperform a simple buy-and-hold approach to justify the complexity.

5. **Look Beyond Return:** High returns mean nothing without considering risk metrics like maximum drawdown and Sharpe ratio.

6. **Mix Strategies:** Consider creating hybrid strategies that combine multiple approaches for more robust performance.

# Alpaca Broker Setup Guide

This guide walks through setting up Alpaca for use with Stocker's AI auto-trading feature.

## What is Alpaca?

[Alpaca](https://alpaca.markets) is a commission-free stock trading API. It supports:

- Paper trading (simulated, no real money)
- Live trading (real orders, real money)
- Fractional shares (critical for small budgets like $100)
- REST API + WebSocket streaming
- Official Python SDK

## 1. Create an Alpaca Account

1. Go to [https://app.alpaca.markets/signup](https://app.alpaca.markets/signup)
2. Sign up with email -- no minimum deposit required for paper trading
3. You'll get access to both Paper and Live environments

## 2. Get Your API Keys

1. Log in to [https://app.alpaca.markets](https://app.alpaca.markets)
2. In the left sidebar, click **Paper Trading** (start here)
3. Click **View** next to "API Keys"
4. Click **Regenerate** to create a new key pair
5. Copy both the **API Key ID** and **Secret Key** -- the secret is only shown once

You'll have two separate key pairs:
- **Paper keys** -- for simulated trading (safe to experiment with)
- **Live keys** -- for real money (only use when you're confident in the system)

## 3. Configure Stocker

### Option A: Environment Variables (Recommended)

Add to your `.env` file in the project root:

```env
ALPACA_API_KEY=PKXXXXXXXXXXXXXXXX
ALPACA_API_SECRET=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

These are loaded automatically when the app starts.

### Option B: Enter in the App

1. Open Stocker and go to the **Auto-Trade** tab
2. Enter your API Key and Secret in the masked fields
3. Check "Paper" for paper trading (default)
4. Click **Connect**

The status label will show your account equity if the connection succeeds.

## 4. Paper vs Live Trading

| | Paper | Live |
|---|---|---|
| **Money** | Simulated $100K | Real money |
| **API URL** | `paper-api.alpaca.markets` | `api.alpaca.markets` |
| **Risk** | None | Real financial risk |
| **Keys** | Separate paper keys | Separate live keys |

**Always start with paper trading.** The app defaults to paper mode. To switch to live:

1. Uncheck the "Paper" checkbox in the Auto-Trade tab
2. Enter your **live** API keys (different from paper keys)
3. Click Connect
4. A warning will appear -- confirm you understand the risk

## 5. How the Auto-Trader Uses Alpaca

Each hourly cycle, the auto-trader:

1. **Fetches bars** -- Gets recent 1-hour OHLCV candles via `get_bars()`
2. **Gets quotes** -- Checks current bid/ask via `get_latest_quote()`
3. **Checks position** -- Looks for existing position via `get_position()`
4. **Submits orders** -- If Claude approves, submits via `submit_order()` with:
   - Market orders (default) for immediate execution
   - Fractional shares for small budgets
   - Day time-in-force (expires at market close if unfilled)
5. **Checks market hours** -- Sleeps when market is closed via `get_clock()`

## 6. Budget Tracking

The budget ($100 by default) is a **soft limit** tracked in the app, not an Alpaca account restriction. This means:

- Your Alpaca account can hold more money for other purposes
- The auto-trader only uses the amount you allocate
- Budget remaining updates after each trade
- Closing a position reclaims the budget

## 7. Kill Switch

The red **KILL SWITCH** button in the header bar is always accessible. When clicked:

- **Stop & Liquidate** -- Stops the auto-trader AND closes your position (sells shares)
- **Stop Only** -- Stops the auto-trader but keeps your position open
- **Cancel** -- Returns to trading

The kill switch also sends a Discord notification if configured.

## 8. Account Requirements

| Requirement | Details |
|---|---|
| Minimum deposit | $0 for paper, $1 for live |
| Pattern Day Trader | Not triggered with $100 budget (requires $25K+) |
| Fractional shares | Supported for most liquid stocks |
| Market hours | 9:30 AM - 4:00 PM ET, weekdays |
| Commission | $0 |

## 9. Troubleshooting

**"Connection Failed"**
- Check that your API key and secret are correct
- Paper keys only work with the paper URL (and vice versa)
- Check your internet connection

**"Insufficient buying power"**
- Your Alpaca paper account starts with $100K but the auto-trader only uses your allocated budget
- If budget is depleted, the auto-trader will PASS until you stop and restart with a new budget

**"Market is closed"**
- The auto-trader automatically waits for market open
- US stock market hours: 9:30 AM - 4:00 PM Eastern, Monday-Friday
- Closed on US holidays

**"Order rejected"**
- Some penny stocks or illiquid symbols can't be traded
- Alpaca may reject orders for stocks it doesn't support
- Check the console log for the specific error message

## 10. API Rate Limits

Alpaca's rate limits are generous:

- **REST API**: 200 requests/minute
- **Data API**: 200 requests/minute
- **WebSocket**: 1 connection, unlimited messages

With hourly cycles, the auto-trader uses approximately 5-10 API calls per cycle, well within limits.

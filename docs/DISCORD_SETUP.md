# Discord Notifications Setup Guide

This guide walks through setting up Discord webhook notifications for Stocker's AI auto-trading feature.

## What You Get

The auto-trader sends rich embed notifications to a Discord channel for:

| Event | Color | When |
|-------|-------|------|
| Auto-trader started | Cyan | On startup with configuration summary |
| Trade executed (buy) | Neon green | When a buy order fills |
| Trade executed (sell) | Red/pink | When a sell order fills |
| Cycle evaluated (pass) | Gray | When Claude decides not to trade |
| Kill switch activated | Red | Emergency stop triggered |
| Error occurred | Orange | API failures, network issues |

All embeds include timestamps, paper/live mode badge, and are styled to match the app's retro theme.

## 1. Create a Discord Webhook

1. Open Discord and go to the server where you want notifications
2. Right-click the channel -> **Edit Channel**
3. Go to **Integrations** -> **Webhooks**
4. Click **New Webhook**
5. Name it something like "Retro Trading Console"
6. (Optional) Upload a custom avatar
7. Click **Copy Webhook URL**

The URL looks like:
```
https://discord.com/api/webhooks/1234567890/abcdefghijklmnop...
```

## 2. Configure Stocker

### Option A: Environment Variable

Add to your `.env` file:

```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/1234567890/abcdefghijklmnop...
```

### Option B: Enter in the App

1. Go to the **Auto-Trade** tab
2. Paste the webhook URL in the "Discord Webhook" field
3. Click **Test** to verify -- you should see a test message in your Discord channel

## 3. Notification Examples

### Trade Executed

```
TRADE EXECUTED: BUY AAPL
AI auto-trader executed an order

Symbol:            AAPL
Side:              BUY
Quantity:          0.5500 shares
Price:             $182.34
Total Cost:        $100.29
Budget Remaining:  $0.00
AI Confidence:     0.82
ML Direction:      UP
Reasoning:         Strong bullish signal confirmed by ML and technical...

Paper Trading | Retro Trading Console
```

### Cycle Summary (Pass)

```
CYCLE #5: PASS on AAPL
Hourly evaluation complete

Symbol:            AAPL
Decision:          PASS
Cycle #:           5
ML Direction:      NEUTRAL
ML Confidence:     0.520
AI Confidence:     0.35
Reasoning:         Insufficient signal strength. ML and TA signals...

Paper Trading | Retro Trading Console
```

### Kill Switch

```
KILL SWITCH ACTIVATED
Auto-trader has been emergency stopped

Action:            Stopped & Liquidated
Positions Closed:  1
Closed: AAPL       Qty: 0.55 | Status: accepted

Retro Trading Console
```

## 4. Controlling Notification Volume

With hourly cycles, you'll get approximately:

- **1 notification per hour** during market hours (6.5 hours/day)
- **~6-7 notifications per trading day** for cycle summaries
- **Additional notifications** for actual trades and errors

If this is too noisy, you can:

- **Mute the channel** in Discord but keep notifications for @mentions
- **Create a dedicated channel** just for trading alerts
- **Leave the webhook URL empty** to disable Discord entirely (in-app notifications still work via LEDs, matrix display, and console log)

## 5. Discord Channel Tips

**Dedicated channel setup:**

1. Create a channel like `#trading-alerts`
2. Set it to read-only for everyone except the webhook
3. Pin the startup notification for quick reference
4. Use Discord's thread feature to discuss individual trades

**Mobile notifications:**

Discord mobile apps deliver push notifications by default. This means you'll get trade alerts on your phone without any additional setup. To fine-tune:

1. Open Discord mobile
2. Long-press the channel -> **Notification Settings**
3. Choose "All Messages" for every alert or "Only @mentions" for less noise

## 6. Webhook Security

- **Don't share your webhook URL publicly** -- anyone with it can post to your channel
- If compromised, delete the webhook in Discord and create a new one
- The webhook URL is stored in your `.env` file which should be in `.gitignore`
- Stocker never logs the webhook URL to the console

## 7. Troubleshooting

**"Test" button shows "Failed"**
- Verify the URL starts with `https://discord.com/api/webhooks/`
- Check your internet connection
- Make sure the webhook hasn't been deleted in Discord

**Notifications stop arriving**
- Discord may have rate-limited the webhook (unlikely with hourly cycles)
- Check if the webhook still exists in the channel settings
- Look for errors in the app's console log

**Embeds look broken**
- Discord embed limits: title 256 chars, description 4096 chars, field value 1024 chars
- The notifier truncates long reasoning text to stay within limits

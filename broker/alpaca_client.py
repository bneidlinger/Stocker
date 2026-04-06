# broker/alpaca_client.py
# Alpaca broker wrapper for auto-trading

import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional

import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import APIError


class AlpacaBrokerClient:
    """
    Wraps the alpaca-trade-api SDK into a clean interface for the auto-trader.
    Supports both paper and live trading.
    """

    def __init__(self, api_key: str, api_secret: str,
                 base_url: str = "https://paper-api.alpaca.markets",
                 paper: bool = True):
        """
        Initialize the Alpaca broker client.

        Args:
            api_key: Alpaca API key.
            api_secret: Alpaca API secret.
            base_url: API base URL (paper or live).
            paper: Whether this is a paper trading account.
        """
        self.paper = paper
        self.api = tradeapi.REST(api_key, api_secret, base_url, api_version='v2')

        # Validate connection
        account = self.api.get_account()
        mode = "Paper" if paper else "LIVE"
        print(f"Alpaca connected ({mode}): {account.status} | Equity: ${float(account.equity):,.2f}")

    @property
    def is_market_open(self) -> bool:
        """Check if the market is currently open."""
        clock = self.api.get_clock()
        return clock.is_open

    @property
    def next_market_open(self) -> datetime:
        """Get the next market open time."""
        clock = self.api.get_clock()
        return clock.next_open.replace(tzinfo=None)

    @property
    def next_market_close(self) -> datetime:
        """Get the next market close time."""
        clock = self.api.get_clock()
        return clock.next_close.replace(tzinfo=None)

    def get_account(self) -> Dict:
        """Get account info as a clean dict."""
        account = self.api.get_account()
        return {
            "equity": float(account.equity),
            "buying_power": float(account.buying_power),
            "cash": float(account.cash),
            "status": account.status,
            "pattern_day_trader": account.pattern_day_trader,
            "trading_blocked": account.trading_blocked,
        }

    def get_position(self, symbol: str) -> Optional[Dict]:
        """Get current position for a symbol, or None if no position."""
        try:
            pos = self.api.get_position(symbol)
            return {
                "symbol": pos.symbol,
                "qty": float(pos.qty),
                "side": pos.side,
                "avg_entry_price": float(pos.avg_entry_price),
                "current_price": float(pos.current_price),
                "market_value": float(pos.market_value),
                "unrealized_pl": float(pos.unrealized_pl),
                "unrealized_plpc": float(pos.unrealized_plpc),
            }
        except APIError:
            return None

    def get_all_positions(self) -> List[Dict]:
        """Get all current positions."""
        positions = self.api.list_positions()
        return [
            {
                "symbol": p.symbol,
                "qty": float(p.qty),
                "side": p.side,
                "avg_entry_price": float(p.avg_entry_price),
                "current_price": float(p.current_price),
                "market_value": float(p.market_value),
                "unrealized_pl": float(p.unrealized_pl),
            }
            for p in positions
        ]

    def submit_order(self, symbol: str, qty: float, side: str,
                     order_type: str = "market", time_in_force: str = "day",
                     limit_price: float = None) -> Dict:
        """
        Submit an order to Alpaca.

        Args:
            symbol: Stock ticker.
            qty: Number of shares (supports fractional).
            side: "buy" or "sell".
            order_type: "market" or "limit".
            time_in_force: "day", "gtc", "ioc", etc.
            limit_price: Required for limit orders.

        Returns:
            Order confirmation dict.
        """
        kwargs = {
            "symbol": symbol,
            "qty": qty,
            "side": side,
            "type": order_type,
            "time_in_force": time_in_force,
        }
        if order_type == "limit" and limit_price is not None:
            kwargs["limit_price"] = limit_price

        order = self.api.submit_order(**kwargs)
        return {
            "order_id": order.id,
            "symbol": order.symbol,
            "qty": order.qty,
            "side": order.side,
            "type": order.type,
            "status": order.status,
            "submitted_at": str(order.submitted_at),
            "filled_at": str(order.filled_at) if order.filled_at else None,
            "filled_avg_price": float(order.filled_avg_price) if order.filled_avg_price else None,
        }

    def get_order(self, order_id: str) -> Dict:
        """Get order status by ID."""
        order = self.api.get_order(order_id)
        return {
            "order_id": order.id,
            "symbol": order.symbol,
            "qty": order.qty,
            "side": order.side,
            "type": order.type,
            "status": order.status,
            "filled_at": str(order.filled_at) if order.filled_at else None,
            "filled_avg_price": float(order.filled_avg_price) if order.filled_avg_price else None,
            "filled_qty": float(order.filled_qty) if order.filled_qty else 0,
        }

    def cancel_order(self, order_id: str) -> bool:
        """Cancel a pending order."""
        try:
            self.api.cancel_order(order_id)
            return True
        except APIError as e:
            print(f"Error canceling order {order_id}: {e}")
            return False

    def cancel_all_orders(self) -> int:
        """Cancel all open orders. Returns count of cancelled orders."""
        cancelled = self.api.cancel_all_orders()
        return len(cancelled) if cancelled else 0

    def liquidate_position(self, symbol: str) -> Optional[Dict]:
        """Close a position for a symbol."""
        try:
            order = self.api.close_position(symbol)
            return {
                "order_id": order.id,
                "symbol": order.symbol,
                "qty": order.qty,
                "side": order.side,
                "status": order.status,
            }
        except APIError as e:
            print(f"Error liquidating {symbol}: {e}")
            return None

    def liquidate_all_positions(self) -> List[Dict]:
        """Close all positions."""
        try:
            orders = self.api.close_all_positions()
            return [
                {"order_id": o.id, "symbol": o.symbol, "status": o.status}
                for o in (orders or [])
            ]
        except APIError as e:
            print(f"Error liquidating all positions: {e}")
            return []

    def get_latest_quote(self, symbol: str) -> Dict:
        """Get the latest quote for a symbol."""
        quote = self.api.get_latest_quote(symbol)
        return {
            "bid": float(quote.bp) if quote.bp else None,
            "ask": float(quote.ap) if quote.ap else None,
            "bid_size": quote.bs,
            "ask_size": quote.as_,
            "timestamp": str(quote.t),
        }

    def get_bars(self, symbol: str, timeframe: str = "1Hour",
                 limit: int = 100) -> pd.DataFrame:
        """
        Fetch recent OHLCV bars from Alpaca.

        Args:
            symbol: Stock ticker.
            timeframe: Bar timeframe (e.g., "1Min", "5Min", "1Hour", "1Day").
            limit: Number of bars to fetch.

        Returns:
            DataFrame with OHLCV columns (lowercase).
        """
        bars = self.api.get_bars(symbol, timeframe, limit=limit).df
        if bars.empty:
            return bars

        # Normalize column names to lowercase
        bars.columns = [c.lower() for c in bars.columns]

        # Ensure we have the standard columns
        rename_map = {}
        for col in ['open', 'high', 'low', 'close', 'volume']:
            if col not in bars.columns:
                # Try title case
                title = col.capitalize()
                if title in bars.columns:
                    rename_map[title] = col
        if rename_map:
            bars.rename(columns=rename_map, inplace=True)

        return bars

# broker/alpaca_client.py
# Alpaca broker wrapper for auto-trading, built on the supported alpaca-py SDK
# (replaces the deprecated alpaca-trade-api). Public surface is unchanged so
# trading/auto_trader.py and gui/auto_trader_tab.py call it exactly as before.

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

import pandas as pd

from alpaca.common.exceptions import APIError
from alpaca.data.enums import DataFeed
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, StockLatestQuoteRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderClass, OrderSide, QueryOrderStatus, TimeInForce
from alpaca.trading.requests import (GetOrdersRequest, LimitOrderRequest,
                                     MarketOrderRequest, StopLossRequest)

# Timeframe strings accepted by get_bars (case-insensitive)
_TIMEFRAMES = {
    "1min": TimeFrame.Minute,
    "5min": TimeFrame(5, TimeFrameUnit.Minute),
    "15min": TimeFrame(15, TimeFrameUnit.Minute),
    "30min": TimeFrame(30, TimeFrameUnit.Minute),
    "1hour": TimeFrame.Hour,
    "1day": TimeFrame.Day,
}

# Calendar minutes of lookback per requested bar, generous enough to span
# nights/weekends/holidays. get_bars must pass an explicit start: without one
# the API defaults to the current day and a limit of e.g. 120 hourly bars
# silently truncates to today's handful.
_LOOKBACK_MINUTES = {
    "1min": 5,
    "5min": 25,
    "15min": 75,
    "30min": 150,
    "1hour": 60 * 6,
    "1day": 60 * 24 * 2,
}

_TIME_IN_FORCE = {
    "day": TimeInForce.DAY,
    "gtc": TimeInForce.GTC,
    "ioc": TimeInForce.IOC,
    "fok": TimeInForce.FOK,
    "opg": TimeInForce.OPG,
    "cls": TimeInForce.CLS,
}


class AlpacaBrokerClient:
    """
    Wraps alpaca-py into a clean interface for the auto-trader.
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
            base_url: Kept for signature compatibility; alpaca-py selects the
                      endpoint from `paper` itself.
            paper: Whether this is a paper trading account.
        """
        self.paper = paper
        self.trading = TradingClient(api_key, api_secret, paper=paper)
        # Market data uses the free IEX feed; the SIP feed raises subscription
        # errors on free accounts.
        self.data = StockHistoricalDataClient(api_key, api_secret)

        # Validate connection
        account = self.trading.get_account()
        mode = "Paper" if paper else "LIVE"
        print(f"Alpaca connected ({mode}): {self._enum_value(account.status)} | "
              f"Equity: ${float(account.equity):,.2f}")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _enum_value(value):
        """Returns the plain string for alpaca-py enums, passing through None."""
        if value is None:
            return None
        return value.value if hasattr(value, "value") else str(value)

    def _order_dict(self, order) -> Dict:
        """Normalizes an alpaca-py Order into the dict shape callers expect."""
        return {
            "order_id": str(order.id),
            "symbol": order.symbol,
            "qty": float(order.qty) if order.qty is not None else None,
            "side": self._enum_value(order.side),
            "type": self._enum_value(order.order_type),
            "status": self._enum_value(order.status),
            "submitted_at": str(order.submitted_at),
            "filled_at": str(order.filled_at) if order.filled_at else None,
            "filled_avg_price": float(order.filled_avg_price) if order.filled_avg_price else None,
            "filled_qty": float(order.filled_qty) if order.filled_qty else 0.0,
        }

    @staticmethod
    def _position_dict(pos) -> Dict:
        return {
            "symbol": pos.symbol,
            "qty": float(pos.qty),
            "side": AlpacaBrokerClient._enum_value(pos.side),
            "avg_entry_price": float(pos.avg_entry_price),
            "current_price": float(pos.current_price),
            "market_value": float(pos.market_value),
            "unrealized_pl": float(pos.unrealized_pl),
            "unrealized_plpc": float(pos.unrealized_plpc),
        }

    # ------------------------------------------------------------------
    # Market clock
    # ------------------------------------------------------------------

    @property
    def is_market_open(self) -> bool:
        """Check if the market is currently open."""
        return self.trading.get_clock().is_open

    @property
    def next_market_open(self) -> datetime:
        """Next market open as a timezone-AWARE datetime (compare with aware now)."""
        return self.trading.get_clock().next_open

    @property
    def next_market_close(self) -> datetime:
        """Next market close as a timezone-AWARE datetime."""
        return self.trading.get_clock().next_close

    # ------------------------------------------------------------------
    # Account and positions
    # ------------------------------------------------------------------

    def get_account(self) -> Dict:
        """Get account info as a clean dict."""
        account = self.trading.get_account()
        return {
            "equity": float(account.equity),
            "buying_power": float(account.buying_power),
            "cash": float(account.cash),
            "status": self._enum_value(account.status),
            "pattern_day_trader": account.pattern_day_trader,
            "trading_blocked": account.trading_blocked,
        }

    def get_position(self, symbol: str) -> Optional[Dict]:
        """Get current position for a symbol, or None if no position."""
        try:
            return self._position_dict(self.trading.get_open_position(symbol))
        except APIError:
            return None

    def get_all_positions(self) -> List[Dict]:
        """Get all current positions."""
        return [self._position_dict(p) for p in self.trading.get_all_positions()]

    # ------------------------------------------------------------------
    # Orders
    # ------------------------------------------------------------------

    def submit_order(self, symbol: str, qty: float, side: str,
                     order_type: str = "market", time_in_force: str = "day",
                     limit_price: float = None,
                     stop_loss_price: float = None) -> Dict:
        """
        Submit an order to Alpaca.

        Args:
            symbol: Stock ticker.
            qty: Number of shares (fractional allowed for simple orders only).
            side: "buy" or "sell".
            order_type: "market" or "limit".
            time_in_force: "day", "gtc", "ioc", etc.
            limit_price: Required for limit orders.
            stop_loss_price: When set, attaches a broker-side stop-loss leg via
                an OTO order. Alpaca requires whole-share qty for advanced
                order classes -- callers enforce that (see AutoTrader).

        Returns:
            Order confirmation dict. "legs" lists attached leg order ids
            (e.g. the stop-loss) so they can be tracked or cancelled.
        """
        side_enum = OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL
        tif = _TIME_IN_FORCE.get(time_in_force.lower(), TimeInForce.DAY)

        kwargs = dict(symbol=symbol, qty=qty, side=side_enum, time_in_force=tif)
        if stop_loss_price is not None:
            kwargs["order_class"] = OrderClass.OTO
            kwargs["stop_loss"] = StopLossRequest(stop_price=round(float(stop_loss_price), 2))

        if order_type == "limit":
            if limit_price is None:
                raise ValueError("Limit orders require limit_price.")
            request = LimitOrderRequest(limit_price=float(limit_price), **kwargs)
        else:
            request = MarketOrderRequest(**kwargs)

        order = self.trading.submit_order(order_data=request)
        result = self._order_dict(order)
        result["legs"] = [str(leg.id) for leg in (order.legs or [])]
        return result

    def get_order(self, order_id: str) -> Dict:
        """Get order status by ID."""
        return self._order_dict(self.trading.get_order_by_id(order_id))

    def get_open_orders(self, symbol: str = None) -> List[Dict]:
        """List open orders, optionally filtered to one symbol."""
        request = GetOrdersRequest(status=QueryOrderStatus.OPEN,
                                   symbols=[symbol] if symbol else None)
        orders = self.trading.get_orders(filter=request)
        return [self._order_dict(o) for o in orders]

    def cancel_order(self, order_id: str) -> bool:
        """Cancel a pending order."""
        try:
            self.trading.cancel_order_by_id(order_id)
            return True
        except APIError as e:
            print(f"Error canceling order {order_id}: {e}")
            return False

    def cancel_all_orders(self) -> int:
        """Cancel all open orders. Returns count of cancelled orders."""
        cancelled = self.trading.cancel_orders()
        return len(cancelled) if cancelled else 0

    # ------------------------------------------------------------------
    # Liquidation
    # ------------------------------------------------------------------

    def liquidate_position(self, symbol: str) -> Optional[Dict]:
        """Close a position for a symbol.

        Open orders for the symbol are cancelled first: a resting stop/limit
        leg keeps the shares 'held for orders' and Alpaca rejects
        close_position while any remain.
        """
        try:
            for open_order in self.get_open_orders(symbol):
                self.cancel_order(open_order["order_id"])
            order = self.trading.close_position(symbol)
            return {
                "order_id": str(order.id),
                "symbol": order.symbol,
                "qty": float(order.qty) if order.qty is not None else None,
                "side": self._enum_value(order.side),
                "status": self._enum_value(order.status),
            }
        except APIError as e:
            print(f"Error liquidating {symbol}: {e}")
            return None

    def liquidate_all_positions(self) -> List[Dict]:
        """Close all positions (cancelling open orders first)."""
        try:
            responses = self.trading.close_all_positions(cancel_orders=True)
            results = []
            for response in (responses or []):
                body = getattr(response, "body", None)
                if body is not None and getattr(body, "id", None) is not None:
                    results.append({
                        "order_id": str(body.id),
                        "symbol": getattr(body, "symbol", getattr(response, "symbol", "?")),
                        "status": self._enum_value(getattr(body, "status", None)),
                    })
                else:
                    results.append({
                        "order_id": None,
                        "symbol": getattr(response, "symbol", "?"),
                        "status": str(getattr(response, "status", "?")),
                    })
            return results
        except APIError as e:
            print(f"Error liquidating all positions: {e}")
            return []

    # ------------------------------------------------------------------
    # Market data
    # ------------------------------------------------------------------

    def get_latest_quote(self, symbol: str) -> Dict:
        """Get the latest quote for a symbol (IEX feed)."""
        request = StockLatestQuoteRequest(symbol_or_symbols=symbol, feed=DataFeed.IEX)
        quote = self.data.get_stock_latest_quote(request)[symbol]
        return {
            "bid": float(quote.bid_price) if quote.bid_price else None,
            "ask": float(quote.ask_price) if quote.ask_price else None,
            "bid_size": quote.bid_size,
            "ask_size": quote.ask_size,
            "timestamp": str(quote.timestamp),
        }

    def get_bars(self, symbol: str, timeframe: str = "1Hour",
                 limit: int = 100) -> pd.DataFrame:
        """
        Fetch the most recent OHLCV bars from Alpaca (IEX feed).

        Args:
            symbol: Stock ticker.
            timeframe: Bar timeframe ("1Min", "5Min", "15Min", "30Min",
                       "1Hour", "1Day").
            limit: Number of most-recent bars to return.

        Returns:
            DataFrame with lowercase OHLCV columns. Daily bars get a naive
            date index (US/Eastern trading date) so date-derived ML features
            match models trained on yfinance daily data.
        """
        tf_key = timeframe.lower()
        tf = _TIMEFRAMES.get(tf_key)
        if tf is None:
            print(f"Unknown timeframe '{timeframe}', defaulting to 1Hour.")
            tf_key, tf = "1hour", _TIMEFRAMES["1hour"]

        lookback = timedelta(minutes=limit * _LOOKBACK_MINUTES.get(tf_key, 360))
        start = datetime.now(timezone.utc) - lookback

        request = StockBarsRequest(symbol_or_symbols=symbol, timeframe=tf,
                                   start=start, feed=DataFeed.IEX)
        bars = self.data.get_stock_bars(request).df
        if bars.empty:
            return bars

        if isinstance(bars.index, pd.MultiIndex):
            bars = bars.droplevel("symbol")
        bars = bars.tail(limit)

        # alpaca-py already returns lowercase columns
        # (open/high/low/close/volume/trade_count/vwap)
        if tf_key == "1day":
            bars.index = (bars.index.tz_convert("America/New_York")
                          .normalize().tz_localize(None))
        return bars

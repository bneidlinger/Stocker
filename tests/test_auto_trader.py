# Auto-trader hardening tests: truthful budget accounting, kill-switch
# ordering, stop-loss enforcement, position sizing, and market-hours math.
# All broker/AI interaction goes through fakes -- no network, no Tk.

import threading
import time
from datetime import datetime, timedelta, timezone

import pandas as pd

import config as app_config
from trading.auto_trader import AutoTrader
from trading.auto_trader_config import AutoTraderConfig


class FakeBroker:
    """Scripted broker with an ordered call log."""

    def __init__(self, fill_mode="full"):
        self.calls = []
        self.position = None
        self.orders = {}
        self.fill_mode = fill_mode  # "full" | "partial" | "none"
        self.market_open = True
        self._seq = 0

    @property
    def is_market_open(self):
        return self.market_open

    @property
    def next_market_open(self):
        return datetime.now(timezone.utc) + timedelta(seconds=1800)

    def get_position(self, symbol):
        self.calls.append("get_position")
        return dict(self.position) if self.position else None

    def get_bars(self, symbol, timeframe="1Hour", limit=100):
        self.calls.append(f"get_bars:{timeframe}")
        n = min(limit, 250)
        idx = pd.bdate_range("2024-01-02", periods=n)
        close = pd.Series([100.0 + i * 0.1 for i in range(n)], index=idx)
        return pd.DataFrame({"open": close, "high": close * 1.01,
                             "low": close * 0.99, "close": close,
                             "volume": 1_000_000.0}, index=idx)

    def get_latest_quote(self, symbol):
        self.calls.append("get_latest_quote")
        return {"ask": 100.0, "bid": 99.9}

    def submit_order(self, symbol, qty, side, order_type="market",
                     time_in_force="day", limit_price=None, stop_loss_price=None):
        self.calls.append("submit_order")
        self._seq += 1
        oid = f"o{self._seq}"
        if self.fill_mode == "full":
            filled_qty, filled_price, status = qty, 100.0, "filled"
        elif self.fill_mode == "partial":
            filled_qty, filled_price, status = qty / 2, 100.0, "partially_filled"
        else:
            filled_qty, filled_price, status = 0.0, None, "new"
        self.orders[oid] = {
            "order_id": oid, "symbol": symbol, "qty": qty, "side": side,
            "status": status, "filled_qty": filled_qty,
            "filled_avg_price": filled_price,
            "time_in_force": time_in_force, "stop_loss_price": stop_loss_price,
        }
        return dict(self.orders[oid], legs=[])

    def get_order(self, order_id):
        self.calls.append("get_order")
        return dict(self.orders[order_id])

    def cancel_order(self, order_id):
        self.calls.append("cancel_order")
        order = self.orders[order_id]
        if order["status"] != "filled":
            order["status"] = "canceled"
        return True

    def liquidate_position(self, symbol):
        self.calls.append("liquidate_position")
        self._seq += 1
        oid = f"o{self._seq}"
        qty = abs(self.position["qty"]) if self.position else 0.0
        price = self.position["current_price"] if self.position else 0.0
        self.orders[oid] = {"order_id": oid, "symbol": symbol, "qty": qty,
                            "side": "sell", "status": "filled",
                            "filled_qty": qty, "filled_avg_price": price}
        self.position = None
        return {"order_id": oid, "symbol": symbol, "qty": qty,
                "side": "sell", "status": "filled"}


class FakeClaude:
    """Scripted AI client; can block on an event to simulate an in-flight call."""

    def __init__(self, decision=None, block_event=None):
        self.decision = decision or {
            "decision": "PASS", "confidence": 0.5, "reasoning": "test",
            "suggested_action": {"side": "buy", "qty": 0,
                                 "order_type": "market", "limit_price": None},
        }
        self.block_event = block_event
        self.calls = 0

    def evaluate_trade_signal(self, *args, **kwargs):
        self.calls += 1
        if self.block_event is not None:
            self.block_event.wait(timeout=10)
        return dict(self.decision)


def make_trader(broker, claude=None, **config_kwargs):
    config_kwargs.setdefault("symbol", "TEST")
    config_kwargs.setdefault("budget", 1000.0)
    config_kwargs.setdefault("cycle_interval_minutes", 1)
    cfg = AutoTraderConfig(**config_kwargs)
    trader = AutoTrader(broker=broker, claude=claude or FakeClaude(),
                        ml_service=None, notifier=None, config=cfg)
    trader.fill_timeout_s = 1  # keep fill polls fast in tests
    return trader


def _buy_decision(qty):
    return {"decision": "EXECUTE", "confidence": 0.9, "reasoning": "test",
            "suggested_action": {"side": "buy", "qty": qty,
                                 "order_type": "market", "limit_price": None}}


def _sell_decision(qty):
    return {"decision": "EXECUTE", "confidence": 0.9, "reasoning": "test",
            "suggested_action": {"side": "sell", "qty": qty,
                                 "order_type": "market", "limit_price": None}}


# ---------------------------------------------------------------------------
# Budget accounting
# ---------------------------------------------------------------------------

def test_full_fill_deducts_actual_cost():
    broker = FakeBroker(fill_mode="full")
    trader = make_trader(broker)
    result = trader._execute_trade(_buy_decision(5), latest_price=100.0)
    assert result["filled_qty"] == 5.0
    assert result["total_cost"] == 500.0
    assert trader.budget_spent == 500.0
    assert trader.budget_remaining == 500.0


def test_unfilled_order_is_cancelled_and_budget_unchanged():
    broker = FakeBroker(fill_mode="none")
    trader = make_trader(broker)
    result = trader._execute_trade(_buy_decision(5), latest_price=100.0)
    assert result["filled_qty"] == 0.0
    assert result["total_cost"] == 0.0
    assert trader.budget_spent == 0.0
    assert trader.budget_remaining == 1000.0
    assert "cancel_order" in broker.calls


def test_partial_fill_deducts_partial_cost():
    broker = FakeBroker(fill_mode="partial")
    trader = make_trader(broker)
    result = trader._execute_trade(_buy_decision(4), latest_price=100.0)
    assert result["filled_qty"] == 2.0
    assert trader.budget_spent == 200.0
    assert trader.budget_remaining == 800.0


def test_execute_sell_credits_budget():
    broker = FakeBroker(fill_mode="full")
    trader = make_trader(broker, direction="both")
    trader.budget_spent = 500.0
    trader.budget_remaining = 500.0
    trader._execute_trade(_sell_decision(2), latest_price=100.0)
    assert trader.budget_spent == 300.0
    assert trader.budget_remaining == 700.0


def test_close_releases_basis_and_records_realized_pnl():
    broker = FakeBroker()
    broker.position = {"symbol": "TEST", "qty": 3.0, "side": "long",
                       "avg_entry_price": 90.0, "current_price": 100.0,
                       "market_value": 300.0, "unrealized_pl": 30.0,
                       "unrealized_plpc": 0.111}
    trader = make_trader(broker)
    trader._reconcile_budget(broker.position)
    assert trader.budget_spent == 270.0

    trader._close_position(reason="test")
    assert trader.budget_spent == 0.0
    assert trader.budget_remaining == 1000.0
    assert trader.realized_pnl == 30.0  # sold 3 @ 100 with basis 90


def test_reconcile_budget_matches_broker_position():
    broker = FakeBroker()
    trader = make_trader(broker)
    trader._reconcile_budget({"qty": 2.0, "avg_entry_price": 50.0})
    assert trader.budget_spent == 100.0
    assert trader.budget_remaining == 900.0
    trader._reconcile_budget(None)
    assert trader.budget_spent == 0.0
    assert trader.budget_remaining == 1000.0


# ---------------------------------------------------------------------------
# Position sizing and broker-side stop-loss
# ---------------------------------------------------------------------------

def test_whole_share_buy_gets_oto_stop_leg_and_gtc():
    broker = FakeBroker(fill_mode="full")
    trader = make_trader(broker, stop_loss_pct=0.05)
    trader._execute_trade(_buy_decision(5), latest_price=100.0)
    order = broker.orders["o1"]
    assert order["qty"] == 5.0
    assert order["stop_loss_price"] == 95.0  # 100 * (1 - 0.05)
    assert order["time_in_force"] == "gtc"   # DAY entry would drop the leg at close


def test_fractional_buy_has_no_stop_leg():
    broker = FakeBroker(fill_mode="full")
    # budget 100, max 25% per trade at $100/share -> 0.25 shares
    trader = make_trader(broker, budget=100.0, max_position_pct=0.25)
    trader._execute_trade(_buy_decision(0), latest_price=100.0)
    order = broker.orders["o1"]
    assert order["qty"] == 0.25
    assert order["stop_loss_price"] is None
    assert order["time_in_force"] == "day"


def test_sell_never_gets_stop_leg():
    broker = FakeBroker(fill_mode="full")
    trader = make_trader(broker, direction="both")
    trader._execute_trade(_sell_decision(3), latest_price=100.0)
    assert broker.orders["o1"]["stop_loss_price"] is None


# ---------------------------------------------------------------------------
# Software stop-loss backstop (cycle step 0)
# ---------------------------------------------------------------------------

def test_software_stop_loss_closes_position_before_ai():
    broker = FakeBroker()
    broker.position = {"symbol": "TEST", "qty": 2.0, "side": "long",
                       "avg_entry_price": 100.0, "current_price": 90.0,
                       "market_value": 180.0, "unrealized_pl": -20.0,
                       "unrealized_plpc": -0.10}
    claude = FakeClaude()
    trader = make_trader(broker, claude, stop_loss_pct=0.05)
    trader._run_cycle()
    assert "liquidate_position" in broker.calls
    assert claude.calls == 0  # stop-loss preempts the AI evaluation


def test_position_within_stop_does_not_trigger_close():
    broker = FakeBroker()
    broker.position = {"symbol": "TEST", "qty": 2.0, "side": "long",
                       "avg_entry_price": 100.0, "current_price": 98.0,
                       "market_value": 196.0, "unrealized_pl": -4.0,
                       "unrealized_plpc": -0.02}
    claude = FakeClaude()  # PASS decision
    trader = make_trader(broker, claude, stop_loss_pct=0.05)
    trader._run_cycle()
    assert "liquidate_position" not in broker.calls
    assert claude.calls == 1


# ---------------------------------------------------------------------------
# Kill-switch ordering
# ---------------------------------------------------------------------------

def test_stop_returns_immediately_and_liquidates_only_after_cycle():
    broker = FakeBroker(fill_mode="full")
    release_claude = threading.Event()
    claude = FakeClaude(decision=_buy_decision(1), block_event=release_claude)
    trader = make_trader(broker, claude)

    trader.start(ui_callback=None)
    try:
        # Wait until the cycle is blocked inside the Claude call
        deadline = time.time() + 5
        while claude.calls == 0 and time.time() < deadline:
            time.sleep(0.01)
        assert claude.calls == 1, "cycle never reached the AI evaluation"

        t0 = time.time()
        trader.stop(liquidate=True)
        assert time.time() - t0 < 0.1, "stop() must not block the caller"

        # Nothing may be liquidated while the cycle is still in flight
        time.sleep(0.2)
        assert "liquidate_position" not in broker.calls

        # Let the Claude call return an EXECUTE decision
        release_claude.set()

        deadline = time.time() + 10
        while "liquidate_position" not in broker.calls and time.time() < deadline:
            time.sleep(0.02)
        assert "liquidate_position" in broker.calls, "shutdown never liquidated"

        # The EXECUTE decision arrived after stop: the guard must have
        # prevented any order submission
        assert "submit_order" not in broker.calls
        assert not trader._thread.is_alive()
    finally:
        release_claude.set()
        trader._stop_event.set()


# ---------------------------------------------------------------------------
# Market hours
# ---------------------------------------------------------------------------

def test_market_hours_wait_uses_aware_datetimes():
    broker = FakeBroker()
    broker.market_open = False
    trader = make_trader(broker)
    is_open, wait = trader._check_market_hours()
    assert not is_open
    # next_market_open is 1800s from aware-utc now; wait must be close to that
    # regardless of the local wall clock
    assert 1700 <= wait <= 1800


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def test_claude_model_single_sourced_from_config():
    assert AutoTraderConfig().claude_model == app_config.CLAUDE_MODEL

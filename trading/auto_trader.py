# trading/auto_trader.py
# Core AI auto-trading engine with background thread loop

import time
import threading
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional, Callable

import pandas as pd

from broker.alpaca_client import AlpacaBrokerClient
from ai.claude_client import ClaudeAIClient
from notifications.discord_notifier import DiscordNotifier
from trading.auto_trader_config import AutoTraderConfig
from trading.ml.service import MlPredictionService


class AutoTrader:
    """
    AI auto-trading engine that runs on a background daemon thread.
    Evaluates positions hourly using ML predictions reviewed by Claude.
    """

    def __init__(self, broker: AlpacaBrokerClient, claude: ClaudeAIClient,
                 ml_service: MlPredictionService,
                 notifier: Optional[DiscordNotifier],
                 config: AutoTraderConfig):
        self.broker = broker
        self.claude = claude
        self.ml_service = ml_service
        self.notifier = notifier
        self.config = config

        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

        # Budget tracking. budget_spent is defined as the cost basis of the
        # bot's open position and is reconciled against the broker's actual
        # position every cycle (see _reconcile_budget), so it self-heals any
        # drift from partial fills, stop-leg executions, or manual trades.
        self.budget_total = config.budget
        self.budget_spent = 0.0
        self.budget_remaining = config.budget
        self.realized_pnl = 0.0

        # How long to poll an order for fills before cancelling (tests shrink this)
        self.fill_timeout_s = 30

        # State
        self.cycle_count = 0
        self.trade_log: List[Dict] = []
        self.last_decision: Optional[Dict] = None
        self._ui_callback: Optional[Callable] = None

    @property
    def is_running(self) -> bool:
        return self._running

    def get_state(self) -> Dict:
        """Thread-safe snapshot of current state.

        The broker call is a network request and deliberately happens OUTSIDE
        the lock -- holding the lock across it would block the trading thread's
        budget updates for the duration of an HTTP round trip.
        """
        position = None
        try:
            position = self.broker.get_position(self.config.symbol)
        except Exception:
            pass

        with self._lock:
            return {
                "running": self._running,
                "symbol": self.config.symbol,
                "cycle_count": self.cycle_count,
                "budget_total": self.budget_total,
                "budget_spent": self.budget_spent,
                "budget_remaining": self.budget_remaining,
                "realized_pnl": self.realized_pnl,
                "last_decision": self.last_decision,
                "position": position,
                "trade_count": len(self.trade_log),
            }

    def start(self, ui_callback: Callable = None):
        """
        Start the auto-trading loop on a background thread.

        Args:
            ui_callback: Function to call with update dicts.
                         Will be wrapped in app.after() by the caller.
        """
        if self._running:
            print("Auto-trader is already running.")
            return

        self._ui_callback = ui_callback
        self._stop_event.clear()
        self._running = True

        self._thread = threading.Thread(target=self._trading_loop, daemon=True)
        self._thread.start()

        # Notify
        self._notify_ui({"type": "started", "config": {
            "symbol": self.config.symbol,
            "budget": self.budget_total,
            "direction": self.config.direction,
            "mode": "Paper" if self.config.paper_trading else "LIVE",
        }})

        if self.notifier:
            try:
                self.notifier.send_startup_alert({
                    "symbol": self.config.symbol,
                    "budget": self.budget_total,
                    "direction": self.config.direction,
                    "cycle_minutes": self.config.cycle_interval_minutes,
                    "mode": "Paper" if self.config.paper_trading else "LIVE",
                    "max_position_pct": self.config.max_position_pct,
                })
            except Exception as e:
                print(f"Discord startup notification failed: {e}")

    def stop(self, liquidate: bool = False):
        """
        Signal the trading loop to stop. Returns immediately.

        Shutdown ordering matters: liquidation happens only AFTER the cycle
        thread has ended -- an in-flight cycle (e.g. blocked on the Claude
        call) could otherwise open a new position right after we closed it.
        The join + liquidation run on a shutdown worker so the Tk thread never
        blocks; the UI is finalized by the resulting 'stopped' notification.
        """
        self._stop_event.set()
        self._running = False
        threading.Thread(target=self._shutdown_worker, args=(liquidate,),
                         daemon=True).start()

    def _shutdown_worker(self, liquidate: bool):
        """Waits for the trading loop to end, then liquidates and notifies."""
        cycle_thread = self._thread
        if cycle_thread and cycle_thread.is_alive():
            # Worst case for a cycle is one Claude call plus order fill polling
            cycle_thread.join(timeout=120)
            if cycle_thread.is_alive():
                print("Warning: trading loop did not stop within 120s; proceeding "
                      "(pre-submit stop-event guards prevent new orders).")

        positions_closed = []
        if liquidate:
            try:
                result = self.broker.liquidate_position(self.config.symbol)
                if result:
                    positions_closed.append(result)
                    self._notify_ui({"type": "liquidated", "result": result})
            except Exception as e:
                print(f"Error liquidating during stop: {e}")

        self._notify_ui({"type": "stopped", "liquidated": liquidate,
                         "positions_closed": positions_closed})

        if self.notifier:
            try:
                action = "Stopped & Liquidated" if liquidate else "Stopped"
                self.notifier.send_kill_switch_alert(action, positions_closed)
            except Exception as e:
                print(f"Discord stop notification failed: {e}")

    def _trading_loop(self):
        """Main trading loop running on a background thread."""
        print(f"Auto-trader loop started for {self.config.symbol}")

        while not self._stop_event.is_set():
            try:
                # Check market hours
                is_open, wait_seconds = self._check_market_hours()

                if not is_open:
                    self._notify_ui({"type": "market_closed",
                                     "wait_seconds": wait_seconds})
                    self._interruptible_sleep(min(wait_seconds, 300))
                    continue

                # Run one evaluation cycle
                self._run_cycle()
                self.cycle_count += 1

                # Sleep until next cycle
                sleep_secs = self.config.cycle_interval_minutes * 60
                self._notify_ui({"type": "waiting",
                                 "next_cycle_seconds": sleep_secs})
                self._interruptible_sleep(sleep_secs)

            except Exception as e:
                error_msg = f"Trading loop error: {e}"
                print(error_msg)
                traceback.print_exc()
                self._notify_ui({"type": "error", "message": error_msg})
                if self.notifier:
                    try:
                        self.notifier.send_error_alert(str(e), "trading_loop")
                    except Exception:
                        pass
                # Sleep before retry
                self._interruptible_sleep(60)

        print("Auto-trader loop ended.")

    def _run_cycle(self):
        """Execute one evaluation cycle."""
        symbol = self.config.symbol
        self._notify_ui({"type": "cycle_start", "cycle": self.cycle_count + 1})

        # 0. Reconcile budget with broker truth, then enforce the software
        #    stop-loss. This backstop covers fractional positions (no broker
        #    stop leg possible), expired/cancelled stop legs, and positions
        #    opened outside the bot.
        position = self.broker.get_position(symbol)
        self._reconcile_budget(position)
        if position and position.get("unrealized_plpc", 0.0) <= -self.config.stop_loss_pct:
            print(f"STOP-LOSS: {symbol} unrealized {position['unrealized_plpc']:.2%} "
                  f"breaches -{self.config.stop_loss_pct:.2%}; closing position.")
            trade_result = self._close_position(reason="STOP-LOSS")
            self._notify_ui({
                "type": "cycle_end", "cycle": self.cycle_count + 1,
                "decision": "STOP-LOSS", "confidence": 1.0,
                "reasoning": (f"Unrealized P/L {position['unrealized_plpc']:.2%} breached "
                              f"the -{self.config.stop_loss_pct:.2%} stop-loss threshold."),
                "ml_direction": "N/A", "ml_confidence": 0.0,
                "trade_result": trade_result,
                "budget_remaining": self.budget_remaining,
                "position": self.broker.get_position(symbol),
            })
            return

        # 1. Fetch bars. ML models are trained on DAILY data, so predictions
        #    use daily bars (400 clears the 200-day feature warm-up); a small
        #    hourly fetch supplies intraday context for the Claude prompt.
        try:
            bars_ml = self.broker.get_bars(symbol, timeframe="1Day", limit=400)
            if bars_ml.empty:
                self._notify_ui({"type": "cycle_end", "decision": "PASS",
                                 "reasoning": "No bar data available"})
                return
        except Exception as e:
            self._notify_ui({"type": "error",
                             "message": f"Failed to fetch bars: {e}"})
            return

        try:
            bars_intraday = self.broker.get_bars(symbol, timeframe="1Hour", limit=24)
            if bars_intraday.empty:
                bars_intraday = bars_ml
        except Exception:
            bars_intraday = bars_ml

        if self._stop_event.is_set():
            return

        # 2. Run ML prediction (daily bars)
        ml_result = self._get_ml_prediction(bars_ml)

        # 3. Get latest quote
        try:
            quote = self.broker.get_latest_quote(symbol)
            latest_price = quote.get("ask") or quote.get("bid") or float(bars_intraday['close'].iloc[-1])
        except Exception:
            latest_price = float(bars_ml['close'].iloc[-1])

        # 4. Refresh position for the prompt context
        position = self.broker.get_position(symbol)

        # 5. Build context dicts
        signal = {
            "ml_direction": ml_result.get("direction", "NEUTRAL"),
            "ml_confidence": ml_result.get("confidence", 0.0),
            "confidence_level": ml_result.get("confidence_level", "UNCERTAIN"),
            "technical_score": ml_result.get("technical_score", 0.0),
            "hybrid_recommendation": ml_result.get("hybrid_recommendation", "HOLD"),
        }

        market_context = {
            "latest_price": latest_price,
            "volume": int(bars_intraday['volume'].iloc[-1]) if 'volume' in bars_intraday.columns else 0,
            "intraday_summary": self._summarize_bars(bars_intraday),
        }

        portfolio_state = {
            "budget_total": self.budget_total,
            "budget_remaining": self.budget_remaining,
            "current_position": f"{position['qty']} shares @ ${position['avg_entry_price']:.2f}" if position else "None",
            "unrealized_pl": position["unrealized_pl"] if position else 0.0,
        }

        risk_params = {
            "allowed_directions": self.config.direction,
            "max_position_pct": self.config.max_position_pct,
            "stop_loss_pct": self.config.stop_loss_pct,
        }

        # 6. Ask Claude for decision
        if self._stop_event.is_set():
            return
        self._notify_ui({"type": "ai_evaluating"})
        decision = self.claude.evaluate_trade_signal(
            symbol, signal, market_context, portfolio_state, risk_params,
            paper=self.config.paper_trading,
        )

        with self._lock:
            self.last_decision = decision

        # A stop may have been requested while the Claude call was in flight
        # (this is the kill-switch race) -- never act on the decision then
        if self._stop_event.is_set():
            return

        # 7. Act on decision
        trade_result = None
        if decision["decision"] == "EXECUTE" and self.budget_remaining > 0:
            trade_result = self._execute_trade(decision, latest_price)
        elif decision["decision"] == "CLOSE" and position:
            trade_result = self._close_position()

        # 8. Notify
        cycle_data = {
            "type": "cycle_end",
            "cycle": self.cycle_count + 1,
            "decision": decision["decision"],
            "confidence": decision.get("confidence", 0),
            "reasoning": decision.get("reasoning", ""),
            "ml_direction": signal["ml_direction"],
            "ml_confidence": signal["ml_confidence"],
            "trade_result": trade_result,
            "budget_remaining": self.budget_remaining,
            "position": self.broker.get_position(symbol),
        }
        self._notify_ui(cycle_data)

        if self.notifier:
            try:
                mode = "Paper" if self.config.paper_trading else "LIVE"
                if trade_result:
                    self.notifier.send_trade_alert({
                        "symbol": symbol,
                        "side": trade_result.get("side", ""),
                        "qty": trade_result.get("qty", 0),
                        "price": trade_result.get("filled_avg_price", latest_price),
                        "total_cost": trade_result.get("total_cost", 0),
                        "budget_remaining": self.budget_remaining,
                        "ai_confidence": decision.get("confidence", 0),
                        "ml_direction": signal["ml_direction"],
                        "reasoning": decision.get("reasoning", ""),
                        "mode": mode,
                    })
                else:
                    self.notifier.send_cycle_summary({
                        "symbol": symbol,
                        "decision": decision["decision"],
                        "cycle_number": self.cycle_count + 1,
                        "ml_direction": signal["ml_direction"],
                        "ml_confidence": signal["ml_confidence"],
                        "ai_confidence": decision.get("confidence", 0),
                        "reasoning": decision.get("reasoning", ""),
                        "mode": mode,
                    })
            except Exception as e:
                print(f"Discord notification failed: {e}")

    def _get_ml_prediction(self, bars: pd.DataFrame) -> Dict:
        """Run ML prediction on the latest bar data."""
        try:
            if not self.ml_service or not self.ml_service.loaded_model_info:
                return {"direction": "NEUTRAL", "confidence": 0.0,
                        "confidence_level": "UNCERTAIN",
                        "technical_score": 0.0,
                        "hybrid_recommendation": "HOLD"}

            prediction = self.ml_service.predict(bars)
            if prediction:
                return {
                    "direction": prediction.get("direction", "NEUTRAL"),
                    "confidence": prediction.get("confidence", 0.0),
                    "confidence_level": prediction.get("confidence_level", "UNCERTAIN"),
                    "technical_score": 0.0,
                    "hybrid_recommendation": "HOLD",
                }
        except Exception as e:
            print(f"ML prediction error: {e}")

        return {"direction": "NEUTRAL", "confidence": 0.0,
                "confidence_level": "UNCERTAIN",
                "technical_score": 0.0,
                "hybrid_recommendation": "HOLD"}

    def _execute_trade(self, decision: Dict, latest_price: float) -> Optional[Dict]:
        """Execute a trade based on AI decision. Budget updates use the actual
        fill (filled_qty x filled_avg_price), never an assumed price."""
        action = decision.get("suggested_action", {})
        side = action.get("side", "buy")

        # Direction validation
        if self.config.direction == "long_only" and side == "sell":
            print("Direction restricted to long_only, skipping sell.")
            return None
        if self.config.direction == "short_only" and side == "buy":
            print("Direction restricted to short_only, skipping buy.")
            return None

        # Calculate position size
        qty = action.get("qty", 0)
        if qty <= 0:
            qty = self._calculate_position_size(latest_price)
        if qty <= 0:
            print("Calculated qty is 0, skipping trade.")
            return None

        # Budget check
        estimated_cost = qty * latest_price
        if side == "buy" and estimated_cost > self.budget_remaining:
            qty = self.budget_remaining / latest_price
            if qty < 0.001:
                print("Insufficient budget for trade.")
                return None

        # Broker-side stop-loss: Alpaca rejects fractional qty on advanced
        # order classes, so whole-share BUY entries get an OTO stop leg. The
        # entry must be GTC -- a DAY entry's stop leg dies at the close.
        # Fractional entries (and shorts) rely on the per-cycle software stop.
        stop_loss_price = None
        time_in_force = "day"
        if side == "buy" and self.config.stop_loss_pct > 0 and int(qty) >= 1:
            qty = float(int(qty))
            stop_loss_price = latest_price * (1 - self.config.stop_loss_pct)
            time_in_force = "gtc"

        # Final guard: a stop may have been requested during the Claude call
        if self._stop_event.is_set():
            print("Stop requested; skipping order submission.")
            return None

        try:
            order_type = action.get("order_type", "market")
            limit_price = action.get("limit_price")

            result = self.broker.submit_order(
                symbol=self.config.symbol,
                qty=round(qty, 4),
                side=side,
                order_type=order_type,
                time_in_force=time_in_force,
                limit_price=limit_price,
                stop_loss_price=stop_loss_price,
            )

            # Wait for the actual fill; on timeout the order is cancelled and
            # whatever partially filled is what gets accounted
            fill = self._await_fill(result["order_id"])
            filled_qty = fill.get("filled_qty") or 0.0
            filled_price = fill.get("filled_avg_price") or 0.0
            total_cost = filled_qty * filled_price

            with self._lock:
                if side == "buy":
                    self.budget_spent += total_cost
                else:
                    self.budget_spent -= total_cost
                self.budget_remaining = self.budget_total - self.budget_spent

            result["total_cost"] = total_cost
            result["filled_qty"] = filled_qty
            result["filled_avg_price"] = filled_price
            result["status"] = fill.get("status", result.get("status"))
            result["stop_loss_price"] = stop_loss_price

            if filled_qty == 0:
                print("Order did not fill within the wait window; budget unchanged.")

            self.trade_log.append({
                "timestamp": datetime.now().isoformat(),
                "symbol": self.config.symbol,
                "side": side,
                "qty": filled_qty,
                "price": filled_price,
                "total_cost": total_cost,
                "order_id": result["order_id"],
                "stop_leg_ids": result.get("legs", []),
                "decision": decision,
            })

            return result

        except Exception as e:
            print(f"Order execution failed: {e}")
            traceback.print_exc()
            if self.notifier:
                try:
                    self.notifier.send_error_alert(str(e), "execute_trade")
                except Exception:
                    pass
            return None

    def _close_position(self, reason: str = "AI decision") -> Optional[Dict]:
        """Close the current position, releasing its actual cost basis from
        the budget and recording realized P/L."""
        try:
            position_before = self.broker.get_position(self.config.symbol)
            result = self.broker.liquidate_position(self.config.symbol)
            if result:
                fill = self._await_fill(result["order_id"]) if result.get("order_id") else {}
                filled_qty = abs(fill.get("filled_qty") or
                                 (position_before["qty"] if position_before else 0.0))
                filled_price = (fill.get("filled_avg_price") or
                                (position_before["current_price"] if position_before else 0.0))
                proceeds = filled_qty * filled_price
                basis = (filled_qty * position_before["avg_entry_price"]
                         if position_before else 0.0)

                with self._lock:
                    self.budget_spent = max(0.0, self.budget_spent - basis)
                    self.budget_remaining = self.budget_total - self.budget_spent
                    self.realized_pnl += proceeds - basis

                self.trade_log.append({
                    "timestamp": datetime.now().isoformat(),
                    "symbol": self.config.symbol,
                    "side": "close",
                    "qty": filled_qty,
                    "price": filled_price,
                    "reason": reason,
                    "order_id": result.get("order_id"),
                })
            return result
        except Exception as e:
            print(f"Position close failed: {e}")
            return None

    def _reconcile_budget(self, position: Optional[Dict]):
        """Anchor deployed budget to the broker's actual position.

        Deriving budget_spent from the broker each cycle self-heals every
        drift source at once: assumed prices, partial fills, stop-leg
        executions between cycles, manual intervention. Assumes the bot owns
        this symbol's whole position (same assumption as the liquidation
        paths).
        """
        basis = abs(position["qty"]) * position["avg_entry_price"] if position else 0.0
        with self._lock:
            self.budget_spent = basis
            self.budget_remaining = self.budget_total - self.budget_spent

    def _await_fill(self, order_id: str, timeout_s: Optional[int] = None) -> Dict:
        """Polls an order until it reaches a terminal state or the timeout.

        On timeout the order is cancelled, then fetched one final time -- the
        cancel can race a fill, and the last fetch is the truth either way, so
        budget updates always reflect what actually filled (possibly nothing,
        possibly partially).
        """
        timeout_s = self.fill_timeout_s if timeout_s is None else timeout_s
        terminal = ("filled", "canceled", "cancelled", "expired", "rejected")
        deadline = time.time() + timeout_s
        status: Dict = {}
        while time.time() < deadline:
            try:
                status = self.broker.get_order(order_id)
            except Exception as e:
                print(f"Order status poll failed: {e}")
                break
            if status.get("status") in terminal:
                return status
            if self._stop_event.is_set():
                break
            time.sleep(min(1.0, max(0.05, timeout_s / 10)))

        try:
            self.broker.cancel_order(order_id)
        except Exception as e:
            print(f"Cancel after fill-timeout failed: {e}")
        try:
            status = self.broker.get_order(order_id)
        except Exception as e:
            print(f"Final order fetch failed: {e}")
        return status

    def _calculate_position_size(self, price: float) -> float:
        """Calculate position size respecting budget and max position limits."""
        max_by_budget = self.budget_remaining / price if price > 0 else 0
        max_by_pct = (self.budget_total * self.config.max_position_pct) / price if price > 0 else 0
        qty = min(max_by_budget, max_by_pct)
        return round(max(qty, 0), 4)

    def _check_market_hours(self) -> tuple:
        """
        Check if market is open.

        Returns:
            (is_open, seconds_to_wait) -- seconds_to_wait is time until next open if closed.
        """
        try:
            if self.broker.is_market_open:
                return True, 0

            # next_market_open is timezone-aware; compare with aware UTC now so
            # the wait is correct regardless of the local wall clock
            next_open = self.broker.next_market_open
            wait = max((next_open - datetime.now(timezone.utc)).total_seconds(), 0)
            return False, wait
        except Exception as e:
            print(f"Market hours check failed: {e}")
            return False, 60  # Retry in 60s

    def _interruptible_sleep(self, total_seconds: float):
        """Sleep in small chunks, checking stop_event each iteration."""
        elapsed = 0.0
        chunk = 5.0
        while elapsed < total_seconds and not self._stop_event.is_set():
            time.sleep(min(chunk, total_seconds - elapsed))
            elapsed += chunk

    def _summarize_bars(self, bars: pd.DataFrame) -> str:
        """Create a brief text summary of recent bar data."""
        if bars.empty or len(bars) < 2:
            return "Insufficient data"

        recent = bars.tail(10)
        first_close = float(recent['close'].iloc[0])
        last_close = float(recent['close'].iloc[-1])
        change_pct = ((last_close - first_close) / first_close) * 100 if first_close > 0 else 0

        if change_pct > 0.5:
            trend = "Uptrend"
        elif change_pct < -0.5:
            trend = "Downtrend"
        else:
            trend = "Sideways"

        high = float(recent['high'].max())
        low = float(recent['low'].min())

        return f"{trend} ({change_pct:+.2f}%) | Range: ${low:.2f}-${high:.2f}"

    def _notify_ui(self, update_data: Dict):
        """Push an update to the UI callback (thread-safe via app.after)."""
        if self._ui_callback:
            try:
                self._ui_callback(update_data)
            except Exception as e:
                print(f"UI callback error: {e}")

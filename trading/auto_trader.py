# trading/auto_trader.py
# Core AI auto-trading engine with background thread loop

import time
import threading
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable

import pytz
import pandas as pd

from broker.alpaca_client import AlpacaBrokerClient
from ai.claude_client import ClaudeAIClient
from notifications.discord_notifier import DiscordNotifier
from trading.auto_trader_config import AutoTraderConfig
from trading.ml.service import MlPredictionService


ET = pytz.timezone("US/Eastern")


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

        # Budget tracking (soft limit -- not Alpaca-side)
        self.budget_total = config.budget
        self.budget_spent = 0.0
        self.budget_remaining = config.budget

        # State
        self.cycle_count = 0
        self.trade_log: List[Dict] = []
        self.last_decision: Optional[Dict] = None
        self._ui_callback: Optional[Callable] = None

    @property
    def is_running(self) -> bool:
        return self._running

    def get_state(self) -> Dict:
        """Thread-safe snapshot of current state."""
        with self._lock:
            position = None
            try:
                position = self.broker.get_position(self.config.symbol)
            except Exception:
                pass

            return {
                "running": self._running,
                "symbol": self.config.symbol,
                "cycle_count": self.cycle_count,
                "budget_total": self.budget_total,
                "budget_spent": self.budget_spent,
                "budget_remaining": self.budget_remaining,
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
        Stop the auto-trading loop.

        Args:
            liquidate: If True, close all positions for the symbol.
        """
        self._stop_event.set()
        self._running = False

        positions_closed = []
        if liquidate:
            try:
                result = self.broker.liquidate_position(self.config.symbol)
                if result:
                    positions_closed.append(result)
                    self._notify_ui({"type": "liquidated", "result": result})
            except Exception as e:
                print(f"Error liquidating during stop: {e}")

        # Wait for thread to finish
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=10)

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

        # 1. Fetch latest bars from Alpaca
        try:
            bars = self.broker.get_bars(symbol, timeframe="1Hour", limit=120)
            if bars.empty:
                self._notify_ui({"type": "cycle_end", "decision": "PASS",
                                 "reasoning": "No bar data available"})
                return
        except Exception as e:
            self._notify_ui({"type": "error",
                             "message": f"Failed to fetch bars: {e}"})
            return

        # 2. Run ML prediction
        ml_result = self._get_ml_prediction(bars)

        # 3. Get latest quote
        try:
            quote = self.broker.get_latest_quote(symbol)
            latest_price = quote.get("ask") or quote.get("bid") or float(bars['close'].iloc[-1])
        except Exception:
            latest_price = float(bars['close'].iloc[-1])

        # 4. Get current position
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
            "volume": int(bars['volume'].iloc[-1]) if 'volume' in bars.columns else 0,
            "intraday_summary": self._summarize_bars(bars),
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
        self._notify_ui({"type": "ai_evaluating"})
        decision = self.claude.evaluate_trade_signal(
            symbol, signal, market_context, portfolio_state, risk_params,
            paper=self.config.paper_trading,
        )

        with self._lock:
            self.last_decision = decision

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
        """Execute a trade based on AI decision."""
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

        try:
            order_type = action.get("order_type", "market")
            limit_price = action.get("limit_price")

            result = self.broker.submit_order(
                symbol=self.config.symbol,
                qty=round(qty, 4),
                side=side,
                order_type=order_type,
                limit_price=limit_price,
            )

            # Wait briefly for fill
            filled_price = latest_price
            for _ in range(5):
                time.sleep(1)
                order_status = self.broker.get_order(result["order_id"])
                if order_status["status"] == "filled":
                    filled_price = order_status.get("filled_avg_price", latest_price)
                    break

            # Update budget
            total_cost = qty * filled_price
            if side == "buy":
                with self._lock:
                    self.budget_spent += total_cost
                    self.budget_remaining = self.budget_total - self.budget_spent

            result["total_cost"] = total_cost
            result["filled_avg_price"] = filled_price

            # Log
            self.trade_log.append({
                "timestamp": datetime.now().isoformat(),
                "symbol": self.config.symbol,
                "side": side,
                "qty": qty,
                "price": filled_price,
                "total_cost": total_cost,
                "order_id": result["order_id"],
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

    def _close_position(self) -> Optional[Dict]:
        """Close the current position."""
        try:
            result = self.broker.liquidate_position(self.config.symbol)
            if result:
                # Reclaim budget from the sale
                position = self.broker.get_position(self.config.symbol)
                if position is None:
                    # Position fully closed
                    with self._lock:
                        self.budget_spent = 0.0
                        self.budget_remaining = self.budget_total

                self.trade_log.append({
                    "timestamp": datetime.now().isoformat(),
                    "symbol": self.config.symbol,
                    "side": "close",
                    "order_id": result.get("order_id"),
                })
            return result
        except Exception as e:
            print(f"Position close failed: {e}")
            return None

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

            next_open = self.broker.next_market_open
            now = datetime.now()
            wait = max((next_open - now).total_seconds(), 0)
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

# gui/auto_trader_tab.py
# Auto-Trader UI tab for the retro trading console

import os
import customtkinter as ctk
from typing import Dict, Optional

from config import (
    COLOR_BACKGROUND, COLOR_FOREGROUND, COLOR_BUTTON, COLOR_BUTTON_HOVER,
    COLOR_DROPDOWN_FG, COLOR_DROPDOWN_BG, COLOR_ACCENT,
    COLOR_SECONDARY_BUTTON, COLOR_SECONDARY_BUTTON_HOVER,
    COLOR_POSITIVE, COLOR_NEGATIVE,
    COLOR_KILL_SWITCH, COLOR_KILL_SWITCH_HOVER,
    ALPACA_API_KEY, ALPACA_API_SECRET, ALPACA_BASE_URL_PAPER, ALPACA_BASE_URL_LIVE,
    CLAUDE_API_KEY, CLAUDE_MODEL,
    DISCORD_WEBHOOK_URL,
    AUTO_TRADER_DEFAULT_BUDGET,
)

from broker.alpaca_client import AlpacaBrokerClient
from ai.claude_client import ClaudeAIClient
from notifications.discord_notifier import DiscordNotifier
from trading.auto_trader import AutoTrader
from trading.auto_trader_config import AutoTraderConfig


class AutoTraderTab:
    """Auto-Trade tab UI within the notebook control."""

    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.broker: Optional[AlpacaBrokerClient] = None
        self.claude: Optional[ClaudeAIClient] = None
        self.notifier: Optional[DiscordNotifier] = None
        self.auto_trader: Optional[AutoTrader] = None
        self._countdown_job = None

        # Fonts
        self.font_normal = app.font_normal if hasattr(app, 'font_normal') else ctk.CTkFont(family='Courier New', size=12)
        self.font_button = app.font_button if hasattr(app, 'font_button') else ctk.CTkFont(family='Courier New', size=12, weight="bold")

        self._create_widgets()

    def _create_widgets(self):
        """Create all auto-trader tab widgets."""
        self.frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Alpaca Connection Section ---
        conn_frame = ctk.CTkFrame(self.frame, fg_color=COLOR_BACKGROUND)
        conn_frame.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(conn_frame, text="Alpaca Key:", font=self.font_normal,
                     text_color=COLOR_FOREGROUND).pack(side="left", padx=(10, 5))
        self.alpaca_key_var = ctk.StringVar(value=ALPACA_API_KEY)
        ctk.CTkEntry(conn_frame, textvariable=self.alpaca_key_var, width=140,
                     font=self.font_normal, show="*",
                     text_color=COLOR_DROPDOWN_FG, fg_color=COLOR_DROPDOWN_BG,
                     border_color=COLOR_BUTTON, border_width=1).pack(side="left", padx=(0, 5))

        ctk.CTkLabel(conn_frame, text="Secret:", font=self.font_normal,
                     text_color=COLOR_FOREGROUND).pack(side="left", padx=(5, 5))
        self.alpaca_secret_var = ctk.StringVar(value=ALPACA_API_SECRET)
        ctk.CTkEntry(conn_frame, textvariable=self.alpaca_secret_var, width=140,
                     font=self.font_normal, show="*",
                     text_color=COLOR_DROPDOWN_FG, fg_color=COLOR_DROPDOWN_BG,
                     border_color=COLOR_BUTTON, border_width=1).pack(side="left", padx=(0, 5))

        self.paper_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(conn_frame, text="Paper", variable=self.paper_var,
                        font=self.font_normal, text_color=COLOR_FOREGROUND,
                        fg_color=COLOR_BUTTON, hover_color=COLOR_BUTTON_HOVER
                        ).pack(side="left", padx=(5, 5))

        self.connect_button = ctk.CTkButton(
            conn_frame, text="Connect", command=self.connect_broker,
            font=self.font_button, text_color=COLOR_BACKGROUND,
            fg_color=COLOR_SECONDARY_BUTTON, hover_color=COLOR_SECONDARY_BUTTON_HOVER,
            width=80)
        self.connect_button.pack(side="left", padx=(5, 5))

        self.broker_status_label = ctk.CTkLabel(conn_frame, text="Disconnected",
                                                 font=self.font_normal, text_color=COLOR_NEGATIVE)
        self.broker_status_label.pack(side="left", padx=(5, 10))

        # --- Config Section ---
        config_frame = ctk.CTkFrame(self.frame, fg_color=COLOR_BACKGROUND)
        config_frame.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(config_frame, text="Budget: $", font=self.font_normal,
                     text_color=COLOR_FOREGROUND).pack(side="left", padx=(10, 0))
        self.budget_var = ctk.StringVar(value=str(AUTO_TRADER_DEFAULT_BUDGET))
        ctk.CTkEntry(config_frame, textvariable=self.budget_var, width=70,
                     font=self.font_normal, text_color=COLOR_DROPDOWN_FG,
                     fg_color=COLOR_DROPDOWN_BG, border_color=COLOR_BUTTON,
                     border_width=1).pack(side="left", padx=(0, 10))

        ctk.CTkLabel(config_frame, text="Direction:", font=self.font_normal,
                     text_color=COLOR_FOREGROUND).pack(side="left", padx=(5, 5))
        self.direction_var = ctk.StringVar(value="Long Only")
        ctk.CTkComboBox(config_frame, values=["Long Only", "Short Only", "Both"],
                        variable=self.direction_var, width=110,
                        font=self.font_normal, text_color=COLOR_DROPDOWN_FG,
                        fg_color=COLOR_DROPDOWN_BG, dropdown_fg_color=COLOR_DROPDOWN_BG,
                        button_color=COLOR_BUTTON, button_hover_color=COLOR_BUTTON_HOVER,
                        border_color=COLOR_BUTTON, border_width=1).pack(side="left", padx=(0, 10))

        ctk.CTkLabel(config_frame, text="Claude Key:", font=self.font_normal,
                     text_color=COLOR_FOREGROUND).pack(side="left", padx=(5, 5))
        self.claude_key_var = ctk.StringVar(value=CLAUDE_API_KEY)
        ctk.CTkEntry(config_frame, textvariable=self.claude_key_var, width=140,
                     font=self.font_normal, show="*",
                     text_color=COLOR_DROPDOWN_FG, fg_color=COLOR_DROPDOWN_BG,
                     border_color=COLOR_BUTTON, border_width=1).pack(side="left", padx=(0, 5))

        # --- Discord Section ---
        discord_frame = ctk.CTkFrame(self.frame, fg_color=COLOR_BACKGROUND)
        discord_frame.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(discord_frame, text="Discord Webhook:", font=self.font_normal,
                     text_color=COLOR_FOREGROUND).pack(side="left", padx=(10, 5))
        self.discord_url_var = ctk.StringVar(value=DISCORD_WEBHOOK_URL)
        ctk.CTkEntry(discord_frame, textvariable=self.discord_url_var, width=350,
                     font=self.font_normal, text_color=COLOR_DROPDOWN_FG,
                     fg_color=COLOR_DROPDOWN_BG, border_color=COLOR_BUTTON,
                     border_width=1).pack(side="left", padx=(0, 5))

        ctk.CTkButton(discord_frame, text="Test", command=self.test_discord,
                      font=self.font_button, text_color=COLOR_BACKGROUND,
                      fg_color=COLOR_SECONDARY_BUTTON, hover_color=COLOR_SECONDARY_BUTTON_HOVER,
                      width=60).pack(side="left", padx=(5, 10))

        self.discord_status_label = ctk.CTkLabel(discord_frame, text="",
                                                  font=self.font_normal, text_color=COLOR_FOREGROUND)
        self.discord_status_label.pack(side="left")

        # --- Controls Section ---
        controls_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        controls_frame.pack(fill="x", pady=(5, 5))

        self.start_button = ctk.CTkButton(
            controls_frame, text="START AUTO-TRADER", command=self.start_trading,
            font=ctk.CTkFont(family='Consolas', size=14, weight="bold"),
            text_color=COLOR_BACKGROUND, fg_color=COLOR_POSITIVE,
            hover_color="#2ECC40", height=36, width=200,
        )
        self.start_button.pack(side="left", padx=(10, 10))

        self.stop_button = ctk.CTkButton(
            controls_frame, text="STOP TRADING", command=self.stop_trading,
            font=ctk.CTkFont(family='Consolas', size=14, weight="bold"),
            text_color="#FFFFFF", fg_color=COLOR_KILL_SWITCH,
            hover_color=COLOR_KILL_SWITCH_HOVER, height=36, width=200,
            state="disabled",
        )
        self.stop_button.pack(side="left", padx=(0, 10))

        self.status_label = ctk.CTkLabel(
            controls_frame, text="IDLE", font=self.font_button, text_color=COLOR_FOREGROUND
        )
        self.status_label.pack(side="left", padx=(10, 0))

        # --- Live Status Section ---
        status_frame = ctk.CTkFrame(self.frame, fg_color=COLOR_BACKGROUND)
        status_frame.pack(fill="x", pady=(5, 0))

        self.cycle_label = ctk.CTkLabel(status_frame, text="Cycles: 0",
                                         font=self.font_normal, text_color=COLOR_FOREGROUND)
        self.cycle_label.pack(side="left", padx=(10, 15))

        self.budget_label = ctk.CTkLabel(status_frame, text=f"Budget: ${AUTO_TRADER_DEFAULT_BUDGET:.2f}",
                                          font=self.font_normal, text_color=COLOR_FOREGROUND)
        self.budget_label.pack(side="left", padx=(0, 15))

        self.pl_label = ctk.CTkLabel(status_frame, text="P/L: $0.00",
                                      font=self.font_normal, text_color=COLOR_FOREGROUND)
        self.pl_label.pack(side="left", padx=(0, 15))

        self.decision_label = ctk.CTkLabel(status_frame, text="Last: --",
                                            font=self.font_normal, text_color=COLOR_FOREGROUND)
        self.decision_label.pack(side="left", padx=(0, 15))

        self.countdown_label = ctk.CTkLabel(status_frame, text="Next: --:--",
                                             font=self.font_normal, text_color=COLOR_FOREGROUND)
        self.countdown_label.pack(side="left", padx=(0, 10))

    # --- Actions ---

    def connect_broker(self):
        """Connect to Alpaca (network calls run on a background worker)."""
        key = self.alpaca_key_var.get().strip()
        secret = self.alpaca_secret_var.get().strip()
        if not key or not secret:
            self.app.log_message("Error: Alpaca API key and secret are required.", tag="negative")
            return

        paper = self.paper_var.get()
        base_url = ALPACA_BASE_URL_PAPER if paper else ALPACA_BASE_URL_LIVE
        self.broker_status_label.configure(text="Connecting...", text_color=COLOR_FOREGROUND)

        def connect_worker():
            broker = AlpacaBrokerClient(key, secret, base_url, paper=paper)
            return broker, broker.get_account()

        def on_done(result):
            broker, account = result
            self.broker = broker
            mode = "Paper" if paper else "LIVE"
            self.broker_status_label.configure(
                text=f"{mode} | ${account['equity']:,.2f}",
                text_color=COLOR_POSITIVE
            )
            self.app.log_message(f"Alpaca connected ({mode}). Equity: ${account['equity']:,.2f}", tag="positive")

        def on_error(exc):
            self.broker_status_label.configure(text="Connection Failed", text_color=COLOR_NEGATIVE)
            self.app.log_message(f"Alpaca connection failed: {exc}", tag="negative")

        self.app.run_in_background(connect_worker, on_done=on_done, on_error=on_error,
                                   busy_widgets=(self.connect_button,))

    def test_discord(self):
        """Send a test Discord webhook."""
        url = self.discord_url_var.get().strip()
        if not url:
            self.app.log_message("Error: Discord webhook URL is required.", tag="negative")
            return
        try:
            notifier = DiscordNotifier(url)
            if notifier.send_test_message():
                self.discord_status_label.configure(text="Sent!", text_color=COLOR_POSITIVE)
                self.app.log_message("Discord test message sent.", tag="positive")
            else:
                self.discord_status_label.configure(text="Failed", text_color=COLOR_NEGATIVE)
        except Exception as e:
            self.discord_status_label.configure(text="Error", text_color=COLOR_NEGATIVE)
            self.app.log_message(f"Discord test failed: {e}", tag="negative")

    def start_trading(self):
        """Start the auto-trader."""
        if not self.broker:
            self.app.log_message("Error: Connect to Alpaca first.", tag="negative")
            return

        # Get symbol from main app
        symbol = self.app.current_symbol
        if not symbol:
            self.app.log_message("Error: Load a stock symbol first.", tag="negative")
            return

        # Initialize Claude client
        claude_key = self.claude_key_var.get().strip()
        if not claude_key:
            self.app.log_message("Error: Claude API key is required.", tag="negative")
            return

        try:
            self.claude = ClaudeAIClient(api_key=claude_key, model=CLAUDE_MODEL)
        except Exception as e:
            self.app.log_message(f"Claude initialization failed: {e}", tag="negative")
            return

        # Initialize Discord (optional)
        discord_url = self.discord_url_var.get().strip()
        self.notifier = None
        if discord_url:
            try:
                self.notifier = DiscordNotifier(discord_url)
            except Exception as e:
                self.app.log_message(f"Discord setup failed (continuing without): {e}", tag="negative")

        # Build config
        try:
            budget = float(self.budget_var.get())
        except ValueError:
            budget = AUTO_TRADER_DEFAULT_BUDGET

        direction_map = {"Long Only": "long_only", "Short Only": "short_only", "Both": "both"}
        direction = direction_map.get(self.direction_var.get(), "long_only")

        config = AutoTraderConfig(
            symbol=symbol,
            budget=budget,
            direction=direction,
            paper_trading=self.paper_var.get(),
        )

        # Create and start auto-trader
        self.auto_trader = AutoTrader(
            broker=self.broker,
            claude=self.claude,
            ml_service=self.app.ml_service,
            notifier=self.notifier,
            config=config,
        )

        def ui_callback(update_data):
            """Bridge from background thread to Tkinter main thread."""
            self.app.after(0, lambda d=update_data: self.on_update(d))

        self.auto_trader.start(ui_callback=ui_callback)

        # Update UI
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.status_label.configure(text="RUNNING", text_color=COLOR_POSITIVE)

        # Enable kill switch in main app
        if hasattr(self.app, 'kill_switch_button'):
            self.app.kill_switch_button.configure(state="normal")

        # Set LEDs
        self.app.set_led_state("AUTO", "on", flicker=False)
        self.app.log_message(f"--- AUTO-TRADER STARTED: {symbol} | ${budget:.2f} | {direction} ---", tag="positive")

    def stop_trading(self, liquidate: bool = False):
        """Stop the auto-trader."""
        if self.auto_trader and self.auto_trader.is_running:
            self.auto_trader.stop(liquidate=liquidate)

        # Cancel countdown
        if self._countdown_job:
            try:
                self.app.after_cancel(self._countdown_job)
            except Exception:
                pass
            self._countdown_job = None

        # Update UI
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.status_label.configure(text="STOPPED", text_color=COLOR_NEGATIVE)
        self.countdown_label.configure(text="Next: --:--")

        # Disable kill switch
        if hasattr(self.app, 'kill_switch_button'):
            self.app.kill_switch_button.configure(state="disabled")

        # Reset LEDs
        self.app.set_led_state("AUTO", "off")
        self.app.set_led_state("AI", "off")

        action = "Stopped & liquidated" if liquidate else "Stopped"
        self.app.log_message(f"--- AUTO-TRADER {action.upper()} ---", tag="negative")

    def on_update(self, data: Dict):
        """Handle update from background thread (runs on main thread via app.after)."""
        update_type = data.get("type", "")

        if update_type == "started":
            self.status_label.configure(text="RUNNING", text_color=COLOR_POSITIVE)

        elif update_type == "cycle_start":
            cycle = data.get("cycle", 0)
            self.status_label.configure(text=f"CYCLE #{cycle}", text_color=COLOR_ACCENT)
            self.cycle_label.configure(text=f"Cycles: {cycle}")
            self.app.set_led_state("AUTO", "on", flicker=True)
            self.app.log_message(f"--- AUTO-TRADER: Cycle #{cycle} Starting ---")

        elif update_type == "ai_evaluating":
            self.status_label.configure(text="AI EVALUATING", text_color="#00BFFF")
            self.app.set_led_state("AI", "on", flicker=True)
            self.app.recommendation_display.display_text("ANALYZING", color="#00BFFF")

        elif update_type == "cycle_end":
            decision = data.get("decision", "PASS")
            reasoning = data.get("reasoning", "")
            budget_remaining = data.get("budget_remaining", 0)
            confidence = data.get("confidence", 0)

            self.app.set_led_state("AI", "off")
            self.app.set_led_state("AUTO", "on", flicker=False)

            # Update labels
            self.decision_label.configure(text=f"Last: {decision}")
            self.budget_label.configure(text=f"Budget: ${budget_remaining:.2f}")

            # Update P/L from position
            position = data.get("position")
            if position:
                pl = position.get("unrealized_pl", 0)
                pl_color = COLOR_POSITIVE if pl >= 0 else COLOR_NEGATIVE
                self.pl_label.configure(text=f"P/L: ${pl:+.2f}", text_color=pl_color)

            # Matrix display
            if decision == "EXECUTE":
                trade = data.get("trade_result", {})
                side = trade.get("side", "buy").upper() if trade else "BUY"
                color = "#39ff14" if side == "BUY" else "#ff4d6d"
                self.app.recommendation_display.display_text(side, color=color)
                self.app.log_message(f"AI Decision: {decision} ({confidence:.2f}) - {reasoning}", tag="positive")
            elif decision == "CLOSE":
                self.app.recommendation_display.display_text("CLOSED", color="#ff4d6d")
                self.app.log_message(f"AI Decision: CLOSE - {reasoning}", tag="negative")
            else:
                self.app.recommendation_display.display_text("AI:PASS", color="#AAAAAA")
                self.app.log_message(f"AI Decision: PASS ({confidence:.2f}) - {reasoning}")

            self.status_label.configure(text="RUNNING", text_color=COLOR_POSITIVE)

        elif update_type == "waiting":
            secs = data.get("next_cycle_seconds", 0)
            self._start_countdown(secs)

        elif update_type == "market_closed":
            wait = data.get("wait_seconds", 0)
            mins = int(wait / 60)
            self.status_label.configure(text="MKT CLOSED", text_color=COLOR_FOREGROUND)
            self.countdown_label.configure(text=f"Opens in: {mins}m")
            self.app.recommendation_display.display_text("MKT CLOSED", color="#AAAAAA")

        elif update_type == "error":
            msg = data.get("message", "Unknown error")
            self.app.log_message(f"AUTO-TRADER ERROR: {msg}", tag="negative")
            self.app.set_led_state("ERR", "on", flicker=True)
            self.app.after(3000, lambda: self.app.set_led_state("ERR", "off"))

        elif update_type == "stopped":
            self.status_label.configure(text="STOPPED", text_color=COLOR_NEGATIVE)
            self.app.set_led_state("AUTO", "off")
            self.app.set_led_state("AI", "off")

        elif update_type == "liquidated":
            self.app.log_message("Position liquidated by auto-trader.", tag="negative")

    def _start_countdown(self, total_seconds: int):
        """Start a countdown timer display."""
        if self._countdown_job:
            try:
                self.app.after_cancel(self._countdown_job)
            except Exception:
                pass

        self._remaining = total_seconds
        self._tick_countdown()

    def _tick_countdown(self):
        """Update countdown display each second."""
        if self._remaining <= 0 or not (self.auto_trader and self.auto_trader.is_running):
            self.countdown_label.configure(text="Next: NOW")
            return

        mins = self._remaining // 60
        secs = self._remaining % 60
        self.countdown_label.configure(text=f"Next: {mins:02d}:{secs:02d}")
        self._remaining -= 1
        self._countdown_job = self.app.after(1000, self._tick_countdown)

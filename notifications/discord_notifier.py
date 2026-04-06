# notifications/discord_notifier.py
# Discord webhook notifications with retro-themed embeds

import json
import time
import requests
from datetime import datetime, timezone
from typing import Dict, List, Optional


class DiscordNotifier:
    """
    Sends rich embed notifications to a Discord channel via webhook.
    All embeds use the app's retro Miami Vice / Fallout theme colors.
    """

    # Retro theme colors (as Discord int values)
    COLOR_BUY = 0x39FF14       # Neon green
    COLOR_SELL = 0xFF4D6D      # Neon red/pink
    COLOR_PASS = 0xAAAAAA      # Gray
    COLOR_STARTUP = 0x00C2C2   # Cyan
    COLOR_ERROR = 0xFF851B     # Orange
    COLOR_KILL = 0xFF0000      # Pure red
    COLOR_THEME = 0xFF69B4     # Neon pink (app accent)

    def __init__(self, webhook_url: str):
        """
        Initialize the Discord notifier.

        Args:
            webhook_url: Discord webhook URL.
        """
        if not webhook_url or "discord" not in webhook_url:
            raise ValueError("Invalid Discord webhook URL")
        self.webhook_url = webhook_url

    def send_trade_alert(self, trade_data: Dict) -> bool:
        """Send a rich embed for a trade execution."""
        side = trade_data.get("side", "buy").upper()
        symbol = trade_data.get("symbol", "???")
        color = self.COLOR_BUY if side == "BUY" else self.COLOR_SELL

        fields = [
            {"name": "Symbol", "value": symbol, "inline": True},
            {"name": "Side", "value": side, "inline": True},
            {"name": "Quantity", "value": f"{trade_data.get('qty', 0):.4f} shares", "inline": True},
            {"name": "Price", "value": f"${trade_data.get('price', 0):.2f}", "inline": True},
            {"name": "Total Cost", "value": f"${trade_data.get('total_cost', 0):.2f}", "inline": True},
            {"name": "Budget Remaining", "value": f"${trade_data.get('budget_remaining', 0):.2f}", "inline": True},
            {"name": "AI Confidence", "value": f"{trade_data.get('ai_confidence', 0):.2f}", "inline": True},
            {"name": "ML Direction", "value": trade_data.get("ml_direction", "N/A"), "inline": True},
        ]
        reasoning = trade_data.get("reasoning", "")
        if reasoning:
            fields.append({"name": "Reasoning", "value": reasoning[:1024], "inline": False})

        return self._send_embed(
            title=f"TRADE EXECUTED: {side} {symbol}",
            description="AI auto-trader executed an order",
            color=color,
            fields=fields,
            footer_extra=trade_data.get("mode", "Paper Trading"),
        )

    def send_cycle_summary(self, cycle_data: Dict) -> bool:
        """Send a summary of an evaluation cycle."""
        decision = cycle_data.get("decision", "PASS")
        symbol = cycle_data.get("symbol", "???")

        color_map = {"EXECUTE": self.COLOR_BUY, "CLOSE": self.COLOR_SELL, "PASS": self.COLOR_PASS}
        color = color_map.get(decision, self.COLOR_PASS)

        fields = [
            {"name": "Symbol", "value": symbol, "inline": True},
            {"name": "Decision", "value": decision, "inline": True},
            {"name": "Cycle #", "value": str(cycle_data.get("cycle_number", 0)), "inline": True},
            {"name": "ML Direction", "value": cycle_data.get("ml_direction", "N/A"), "inline": True},
            {"name": "ML Confidence", "value": f"{cycle_data.get('ml_confidence', 0):.3f}", "inline": True},
            {"name": "AI Confidence", "value": f"{cycle_data.get('ai_confidence', 0):.2f}", "inline": True},
        ]
        reasoning = cycle_data.get("reasoning", "")
        if reasoning:
            fields.append({"name": "Reasoning", "value": reasoning[:1024], "inline": False})

        return self._send_embed(
            title=f"CYCLE #{cycle_data.get('cycle_number', 0)}: {decision} on {symbol}",
            description="Hourly evaluation complete",
            color=color,
            fields=fields,
            footer_extra=cycle_data.get("mode", "Paper Trading"),
        )

    def send_kill_switch_alert(self, action: str, positions_closed: List[Dict]) -> bool:
        """Send an urgent notification when the kill switch is activated."""
        fields = [
            {"name": "Action", "value": action, "inline": True},
            {"name": "Positions Closed", "value": str(len(positions_closed)), "inline": True},
        ]
        for pos in positions_closed[:5]:
            fields.append({
                "name": f"Closed: {pos.get('symbol', '?')}",
                "value": f"Qty: {pos.get('qty', 0)} | Status: {pos.get('status', '?')}",
                "inline": False
            })

        return self._send_embed(
            title="KILL SWITCH ACTIVATED",
            description="Auto-trader has been emergency stopped",
            color=self.COLOR_KILL,
            fields=fields,
        )

    def send_error_alert(self, error_message: str, context: str = "") -> bool:
        """Send an error notification."""
        fields = [
            {"name": "Error", "value": error_message[:1024], "inline": False},
        ]
        if context:
            fields.append({"name": "Context", "value": context[:1024], "inline": False})

        return self._send_embed(
            title="AUTO-TRADER ERROR",
            description="An error occurred during auto-trading",
            color=self.COLOR_ERROR,
            fields=fields,
        )

    def send_startup_alert(self, config_data: Dict) -> bool:
        """Send a notification when the auto-trader starts."""
        fields = [
            {"name": "Symbol", "value": config_data.get("symbol", "???"), "inline": True},
            {"name": "Budget", "value": f"${config_data.get('budget', 0):.2f}", "inline": True},
            {"name": "Direction", "value": config_data.get("direction", "long_only"), "inline": True},
            {"name": "Cycle Interval", "value": f"{config_data.get('cycle_minutes', 60)} min", "inline": True},
            {"name": "Mode", "value": config_data.get("mode", "Paper"), "inline": True},
            {"name": "Max Position", "value": f"{config_data.get('max_position_pct', 0.25) * 100:.0f}%", "inline": True},
        ]

        return self._send_embed(
            title="AUTO-TRADER STARTED",
            description="AI auto-trading system is now active",
            color=self.COLOR_STARTUP,
            fields=fields,
            footer_extra=config_data.get("mode", "Paper Trading"),
        )

    def send_test_message(self) -> bool:
        """Send a test message to verify webhook configuration."""
        return self._send_embed(
            title="RETRO TRADING CONSOLE",
            description="Discord webhook connected successfully. Auto-trader notifications will appear here.",
            color=self.COLOR_THEME,
            fields=[{"name": "Status", "value": "Connection verified", "inline": False}],
        )

    def _send_embed(self, title: str, description: str, color: int,
                    fields: List[Dict], footer_extra: str = "") -> bool:
        """Build and send a Discord embed."""
        footer_text = "Retro Trading Console"
        if footer_extra:
            footer_text = f"{footer_extra} | {footer_text}"

        embed = {
            "title": title,
            "description": description,
            "color": color,
            "fields": fields,
            "footer": {"text": footer_text},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        payload = {"embeds": [embed]}
        return self._send_webhook(payload)

    def _send_webhook(self, payload: Dict) -> bool:
        """Send a webhook payload with retry logic for rate limits."""
        for attempt in range(3):
            try:
                resp = requests.post(
                    self.webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=10,
                )
                if resp.status_code == 204:
                    return True
                if resp.status_code == 429:
                    retry_after = resp.json().get("retry_after", 1)
                    print(f"Discord rate limited, retrying in {retry_after}s...")
                    time.sleep(retry_after)
                    continue
                print(f"Discord webhook error: {resp.status_code} {resp.text[:200]}")
                return False
            except requests.RequestException as e:
                print(f"Discord webhook request failed: {e}")
                if attempt < 2:
                    time.sleep(1)
        return False

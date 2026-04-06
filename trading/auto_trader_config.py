# trading/auto_trader_config.py
# Configuration dataclass for the auto-trading engine

from dataclasses import dataclass, field


@dataclass
class AutoTraderConfig:
    """Configuration for the AI auto-trading engine."""
    symbol: str = ""
    budget: float = 100.0
    direction: str = "long_only"          # "long_only", "short_only", "both"
    cycle_interval_minutes: int = 60
    max_position_pct: float = 0.25        # Max 25% of budget per trade
    stop_loss_pct: float = 0.05           # 5% stop loss
    paper_trading: bool = True
    claude_model: str = "claude-sonnet-4-20250514"

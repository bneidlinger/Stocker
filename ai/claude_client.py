# ai/claude_client.py
# Unified Claude API client for sentiment analysis and trade decisions

import json
import re
import anthropic
import pandas as pd
from typing import Dict, Optional


class ClaudeAIClient:
    """
    Claude API client used for both sentiment analysis (replacing OpenAI)
    and AI trade decision approval for the auto-trader.
    """

    SENTIMENT_SYSTEM_PROMPT = """You are a Stock Market Sentiment Analyzer specializing in providing nuanced sentiment analysis
and actionable insights based on technical indicators, price data, and machine learning predictions.

When analyzing data:
1. Examine all technical indicators (RSI, MACD, moving averages, etc.) and highlight key signals
2. Analyze the recent price action and volume patterns
3. Consider the ML prediction probability and confidence levels
4. Provide an overall sentiment: POSITIVE, NEUTRAL, or NEGATIVE
5. Summarize 3-5 key factors that support your sentiment conclusion
6. Suggest potential trade considerations based on the horizon period
7. Note any significant risks or contrary indicators that traders should be aware of

Respond ONLY with valid JSON matching this structure:
{
    "symbol": "TICKER",
    "sentiment": "POSITIVE/NEUTRAL/NEGATIVE",
    "confidence": "HIGH/MEDIUM/LOW",
    "horizon_days": 5,
    "analysis_date": "YYYY-MM-DD",
    "key_indicators": [
        {"indicator": "RSI", "value": 68.5, "interpretation": "Approaching overbought but still bullish"}
    ],
    "price_action": {
        "trend": "UPTREND/DOWNTREND/SIDEWAYS",
        "key_levels": {"support": [150.25], "resistance": [155.30]},
        "pattern": "Breaking out of consolidation"
    },
    "ml_prediction": {
        "direction": "UP/DOWN/NEUTRAL",
        "probability": 0.75,
        "interpretation": "Moderately confident bullish signal"
    },
    "summary": "Brief overall assessment",
    "key_factors": ["Factor 1", "Factor 2", "Factor 3"],
    "risks": ["Risk 1", "Risk 2"],
    "trade_considerations": "Specific considerations for traders"
}"""

    TRADE_EVAL_SYSTEM_PROMPT = """You are a disciplined, risk-aware trading analyst for an automated stock trading system.
You receive ML predictions, technical analysis signals, and market context for a single stock.
Your role is to make a final go/no-go decision on whether to execute a trade.

CRITICAL RULES:
1. You must respond ONLY with valid JSON. No explanation text outside the JSON.
2. When in doubt, always choose "PASS". Capital preservation is paramount.
3. Never recommend trades that exceed the remaining budget.
4. Respect the allowed trading direction (long_only, short_only, or both).
5. Consider the current position -- don't double down recklessly.
6. A confidence below 0.6 from ML should make you skeptical.
7. If technical and ML signals disagree, lean toward PASS.
8. This is {mode} trading. {caution}

Respond with this exact JSON structure:
{{
    "decision": "EXECUTE" | "PASS" | "CLOSE",
    "confidence": 0.0-1.0,
    "reasoning": "2-3 sentence explanation",
    "suggested_action": {{
        "side": "buy" | "sell",
        "qty": 0.0,
        "order_type": "market" | "limit",
        "limit_price": null
    }},
    "risk_assessment": "brief risk note",
    "market_conditions_note": "brief market conditions observation"
}}"""

    def __init__(self, api_key: str, model: str = "claude-sonnet-5"):
        """
        Initialize the Claude AI client.

        Args:
            api_key: Anthropic API key.
            model: Claude model ID to use.
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def analyze_sentiment(self, symbol: str, price_data: pd.DataFrame,
                          technical_data: Dict, ml_prediction: Dict,
                          horizon_days: int) -> Dict:
        """
        Analyze market sentiment using Claude, replacing the OpenAI Assistants flow.

        Returns the same JSON structure as the old MarketSentimentAnalyzer for
        backward compatibility with ui_integration.py.
        """
        import datetime

        user_message = self._build_sentiment_message(
            symbol, price_data, technical_data, ml_prediction, horizon_days
        )

        try:
            # Current Claude models think adaptively by default, and max_tokens
            # caps thinking + response together -- keep generous headroom so
            # the JSON answer is never truncated mid-structure
            response = self.client.messages.create(
                model=self.model,
                max_tokens=8192,
                system=self.SENTIMENT_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_message}]
            )
            response_text = response.content[0].text
            return self._parse_json_response(response_text)

        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return {
                "symbol": symbol,
                "sentiment": "ERROR",
                "error_message": str(e),
                "analysis_date": datetime.datetime.now().strftime("%Y-%m-%d")
            }

    def evaluate_trade_signal(self, symbol: str, signal: Dict,
                              market_context: Dict, portfolio_state: Dict,
                              risk_params: Dict,
                              paper: bool = True) -> Dict:
        """
        AI trade approval/rejection for the auto-trader.

        Args:
            symbol: Stock ticker.
            signal: ML direction, confidence, technical score, hybrid recommendation.
            market_context: Latest price, volume, intraday summary.
            portfolio_state: Budget total/remaining, current position, unrealized P/L.
            risk_params: Allowed directions, max position %, stop loss %.
            paper: Whether this is paper trading.

        Returns:
            Dict with decision, confidence, reasoning, suggested_action, risk_assessment.
        """
        mode = "PAPER" if paper else "LIVE"
        caution = "" if paper else "Exercise extreme caution with real money."
        system = self.TRADE_EVAL_SYSTEM_PROMPT.format(mode=mode, caution=caution)

        user_message = self._build_trade_eval_message(
            symbol, signal, market_context, portfolio_state, risk_params
        )

        try:
            # max_tokens covers adaptive thinking + the JSON decision; a tight
            # cap here risks a truncated (unparseable) decision
            response = self.client.messages.create(
                model=self.model,
                max_tokens=8192,
                system=system,
                messages=[{"role": "user", "content": user_message}]
            )
            response_text = response.content[0].text
            result = self._parse_json_response(response_text)

            # Validate required fields
            required = ["decision", "confidence", "reasoning", "suggested_action"]
            for field in required:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")

            if result["decision"] not in ("EXECUTE", "PASS", "CLOSE"):
                result["decision"] = "PASS"

            return result

        except Exception as e:
            print(f"Error evaluating trade signal: {e}")
            return {
                "decision": "PASS",
                "confidence": 0.0,
                "reasoning": f"AI evaluation failed: {e}",
                "suggested_action": {"side": "buy", "qty": 0, "order_type": "market", "limit_price": None},
                "risk_assessment": "Error occurred, defaulting to PASS for safety.",
                "market_conditions_note": "Unable to assess."
            }

    def _build_sentiment_message(self, symbol: str, price_data: pd.DataFrame,
                                  technical_data: Dict, ml_prediction: Dict,
                                  horizon_days: int) -> str:
        recent = price_data.tail(30).copy()
        price_json = recent.reset_index().to_json(orient='records', date_format='iso')

        return f"""Please analyze the following stock market data for {symbol} with a prediction horizon of {horizon_days} days.

Recent Price Data (last 30 days):
```json
{price_json}
```

Technical Indicators:
```json
{json.dumps(technical_data, indent=2)}
```

Machine Learning Prediction:
```json
{json.dumps(ml_prediction, indent=2)}
```

Based on this data, provide a comprehensive sentiment analysis with your assessment of whether the sentiment is POSITIVE, NEUTRAL, or NEGATIVE.
Include key supporting indicators, potential risks, and trading considerations for a {horizon_days}-day horizon.
Respond with the JSON structure described in your instructions."""

    def _build_trade_eval_message(self, symbol: str, signal: Dict,
                                   market_context: Dict, portfolio_state: Dict,
                                   risk_params: Dict) -> str:
        return f"""Evaluate this trading signal for {symbol}:

SIGNAL:
- ML Direction: {signal.get('ml_direction', 'N/A')}
- ML Confidence: {signal.get('ml_confidence', 0):.3f} ({signal.get('confidence_level', 'N/A')})
- Technical Score: {signal.get('technical_score', 0):.2f}
- Hybrid Recommendation: {signal.get('hybrid_recommendation', 'N/A')}

MARKET CONTEXT:
- Current Price: ${market_context.get('latest_price', 0):.2f}
- Today's Volume: {market_context.get('volume', 0):,}
- Intraday Trend: {market_context.get('intraday_summary', 'N/A')}

PORTFOLIO STATE:
- Total Budget: ${portfolio_state.get('budget_total', 0):.2f}
- Remaining Budget: ${portfolio_state.get('budget_remaining', 0):.2f}
- Current Position: {portfolio_state.get('current_position', 'None')}
- Unrealized P/L: ${portfolio_state.get('unrealized_pl', 0):.2f}

RISK PARAMETERS:
- Allowed Direction: {risk_params.get('allowed_directions', 'long_only')}
- Max Position Size: {risk_params.get('max_position_pct', 0.25) * 100:.0f}% of budget
- Stop Loss: {risk_params.get('stop_loss_pct', 0.05) * 100:.0f}%

Make your decision."""

    def _parse_json_response(self, response_text: str) -> Dict:
        """Extract JSON from Claude's response, handling code blocks."""
        # Try direct parse
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass

        # Try code block extraction
        match = re.search(r'```(?:json)?\s*(.*?)\s*```', response_text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        # Try finding raw JSON object
        match = re.search(r'(\{.*\})', response_text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        raise ValueError(f"Could not extract JSON from response: {response_text[:200]}")

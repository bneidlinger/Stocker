# sentiment/sentiment_analyzer.py
# Market sentiment analyzer using Claude API (migrated from OpenAI)

import os
import json
import re
import html
import pandas as pd
from typing import Dict, Optional, Any
import webbrowser
import tempfile
import datetime

from ai.claude_client import ClaudeAIClient


class MarketSentimentAnalyzer:
    """
    Analyzes market sentiment using Claude API, processing
    technical indicators, price data, and ML predictions to generate
    sentiment reports with actionable insights.
    """

    def __init__(self, api_key: str = None):
        """
        Initialize the sentiment analyzer with Claude API credentials.

        Args:
            api_key: Anthropic API key. If None, tries to read from environment.
        """
        if api_key is None:
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if api_key is None:
                raise ValueError("Claude API key not provided and not found in environment variables.")

        self.claude = ClaudeAIClient(api_key=api_key)
        self.report_dir = os.path.join(tempfile.gettempdir(), "stocker_reports")
        self._sweep_old_reports()
        print("Market Sentiment Analyzer initialized (Claude API).")

    def _sweep_old_reports(self):
        """Deletes HTML reports left over from previous sessions.

        Reports must outlive their write (the browser opens them from disk), so
        they cannot be deleted at creation time -- clean up on next init instead.
        """
        try:
            os.makedirs(self.report_dir, exist_ok=True)
            for name in os.listdir(self.report_dir):
                if name.endswith(".html"):
                    try:
                        os.remove(os.path.join(self.report_dir, name))
                    except OSError:
                        pass
        except OSError as e:
            print(f"Could not sweep old sentiment reports: {e}")

    def analyze_sentiment(self,
                          symbol: str,
                          price_data: pd.DataFrame,
                          technical_data: Dict,
                          ml_prediction: Dict,
                          horizon_days: int) -> Dict:
        """
        Analyzes market sentiment using Claude.

        Args:
            symbol: Stock ticker symbol
            price_data: DataFrame containing OHLCV data
            technical_data: Dictionary containing technical indicators
            ml_prediction: Dictionary containing ML predictions
            horizon_days: Prediction horizon in days

        Returns:
            Dictionary containing sentiment analysis results
        """
        return self.claude.analyze_sentiment(
            symbol, price_data, technical_data, ml_prediction, horizon_days
        )

    def display_sentiment_report(self, sentiment_data: Dict):
        """
        Generates and displays an HTML report for the sentiment analysis results.
        """
        html_content = self._generate_html_report(sentiment_data)

        os.makedirs(self.report_dir, exist_ok=True)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.html',
                                         dir=self.report_dir) as f:
            f.write(html_content.encode('utf-8'))
            temp_path = f.name

        webbrowser.open('file://' + temp_path)

    def _generate_html_report(self, sentiment_data: Dict) -> str:
        """Generates an HTML report for the sentiment analysis results.

        Every model-derived string is escaped before interpolation -- the
        report is rendered in a real browser, so raw LLM output must never
        reach the HTML unescaped.
        """
        esc = html.escape
        sentiment_colors = {
            "POSITIVE": "#39ff14",
            "NEUTRAL": "#e0fbfc",
            "NEGATIVE": "#ff4d6d",
            "ERROR": "#ff69b4"
        }

        sentiment_raw = str(sentiment_data.get("sentiment", "ERROR"))
        color = sentiment_colors.get(sentiment_raw, sentiment_colors["ERROR"])
        sentiment = esc(sentiment_raw)

        symbol = esc(str(sentiment_data.get('symbol', 'Unknown')))
        analysis_date = esc(str(sentiment_data.get('analysis_date', 'Unknown')))
        horizon_days = esc(str(sentiment_data.get('horizon_days', 'Unknown')))
        confidence = esc(str(sentiment_data.get('confidence', 'Unknown')))
        summary = esc(str(sentiment_data.get('summary', 'No summary available')))
        trade_considerations = esc(str(sentiment_data.get('trade_considerations',
                                                          'No trade considerations provided')))

        price_action = sentiment_data.get('price_action', {}) or {}
        trend = esc(str(price_action.get('trend', 'Unknown')))
        pattern = esc(str(price_action.get('pattern', 'No pattern detected')))
        key_levels = price_action.get('key_levels', {}) or {}
        support = esc(', '.join(str(x) for x in (key_levels.get('support', []) or [])))
        resistance = esc(', '.join(str(x) for x in (key_levels.get('resistance', []) or [])))

        ml_pred = sentiment_data.get('ml_prediction', {}) or {}
        ml_direction = esc(str(ml_pred.get('direction', 'Unknown')))
        ml_interpretation = esc(str(ml_pred.get('interpretation', 'No interpretation available')))
        try:
            ml_probability = float(ml_pred.get('probability') or 0.0)
        except (TypeError, ValueError):
            ml_probability = 0.0

        indicators_html = ""
        for indicator in sentiment_data.get("key_indicators", []) or []:
            indicators_html += f"""
            <tr>
                <td>{esc(str(indicator.get('indicator', 'Unknown')))}</td>
                <td>{esc(str(indicator.get('value', 'N/A')))}</td>
                <td>{esc(str(indicator.get('interpretation', 'No interpretation available')))}</td>
            </tr>
            """

        factors_html = ""
        for factor in sentiment_data.get("key_factors", []) or []:
            factors_html += f"<li>{esc(str(factor))}</li>"

        risks_html = ""
        for risk in sentiment_data.get("risks", []) or []:
            risks_html += f"<li>{esc(str(risk))}</li>"

        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Market Sentiment Report: {symbol}</title>
            <style>
                body {{
                    font-family: 'Courier New', monospace;
                    background-color: #1a1a2e;
                    color: #e0fbfc;
                    margin: 0;
                    padding: 20px;
                    line-height: 1.6;
                }}
                .container {{
                    max-width: 1000px;
                    margin: 0 auto;
                    background-color: #161625;
                    border: 2px solid {color};
                    border-radius: 10px;
                    padding: 20px;
                    box-shadow: 0 0 20px rgba(0, 0, 0, 0.5), 0 0 30px {color}40;
                }}
                header {{
                    text-align: center;
                    margin-bottom: 30px;
                    border-bottom: 1px solid #2a2a4e;
                    padding-bottom: 20px;
                }}
                h1, h2, h3 {{
                    color: {color};
                    text-shadow: 0 0 5px {color}80;
                }}
                .sentiment-badge {{
                    display: inline-block;
                    background-color: {color}30;
                    color: {color};
                    padding: 5px 15px;
                    border: 1px solid {color};
                    border-radius: 20px;
                    font-weight: bold;
                    margin: 10px 0;
                    animation: glow 2s infinite alternate;
                }}
                .grid-container {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 20px;
                    margin-bottom: 20px;
                }}
                .grid-item {{
                    background-color: #2a2a4e;
                    border-radius: 5px;
                    padding: 15px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 15px 0;
                }}
                th, td {{
                    border-bottom: 1px solid #3a3a5e;
                    padding: 12px 8px;
                    text-align: left;
                }}
                th {{
                    background-color: #1a1a2e;
                    color: #ff69b4;
                }}
                tr:hover {{
                    background-color: #3a3a6e;
                }}
                .section {{
                    margin-bottom: 25px;
                    padding-bottom: 15px;
                    border-bottom: 1px solid #2a2a4e;
                }}
                .summary {{
                    font-size: 1.2em;
                    font-weight: bold;
                    margin: 20px 0;
                    padding: 15px;
                    background-color: #2a2a4e;
                    border-left: 5px solid {color};
                    border-radius: 3px;
                }}
                .footer {{
                    text-align: center;
                    font-size: 0.8em;
                    margin-top: 30px;
                    color: #aaaaaa;
                }}
                .led {{
                    display: inline-block;
                    width: 10px;
                    height: 10px;
                    border-radius: 50%;
                    background-color: {color};
                    box-shadow: 0 0 5px {color};
                    margin: 0 5px;
                    animation: blink 2s infinite alternate;
                }}
                .price-box {{
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 10px;
                }}
                .price-item {{
                    text-align: center;
                    padding: 10px;
                    background-color: #1a1a2e;
                    border-radius: 5px;
                    min-width: 80px;
                }}
                .price-label {{
                    font-size: 0.8em;
                    color: #aaaaaa;
                }}
                .price-value {{
                    font-size: 1.2em;
                    font-weight: bold;
                }}
                ul {{
                    list-style-type: none;
                    padding-left: 0;
                }}
                li {{
                    margin-bottom: 10px;
                    padding-left: 20px;
                    position: relative;
                }}
                li:before {{
                    content: ">";
                    position: absolute;
                    left: 0;
                    color: {color};
                }}
                .ml-direction {{
                    font-weight: bold;
                    font-size: 1.1em;
                }}
                .ml-probability {{
                    height: 20px;
                    width: 100%;
                    background-color: #1a1a2e;
                    border-radius: 10px;
                    margin-top: 10px;
                    position: relative;
                    overflow: hidden;
                }}
                .ml-probability-fill {{
                    height: 100%;
                    background-color: {color};
                    width: {ml_probability * 100}%;
                    border-radius: 10px;
                    box-shadow: 0 0 10px {color};
                }}
                @keyframes glow {{
                    from {{ box-shadow: 0 0 5px {color}50, 0 0 10px {color}30; }}
                    to {{ box-shadow: 0 0 10px {color}80, 0 0 20px {color}60; }}
                }}
                @keyframes blink {{
                    0% {{ opacity: 0.3; }}
                    50% {{ opacity: 1; }}
                    100% {{ opacity: 0.3; }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <header>
                    <div style="display: flex; align-items: center; justify-content: center;">
                        <span class="led"></span>
                        <h1>{symbol} Sentiment Analysis</h1>
                        <span class="led"></span>
                    </div>
                    <div class="sentiment-badge">{sentiment} SENTIMENT</div>
                    <p>Analysis Date: {analysis_date} | Prediction Horizon: {horizon_days} days</p>
                    <p>Confidence Level: {confidence}</p>
                </header>

                <div class="section">
                    <h2>Summary</h2>
                    <div class="summary">{summary}</div>
                </div>

                <div class="grid-container">
                    <div class="grid-item">
                        <h3>Price Action</h3>
                        <p><strong>Trend:</strong> {trend}</p>
                        <p><strong>Pattern:</strong> {pattern}</p>
                        <h4>Key Levels</h4>
                        <div class="price-box">
                            <div class="price-item">
                                <div class="price-label">Support</div>
                                <div class="price-value">{support}</div>
                            </div>
                            <div class="price-item">
                                <div class="price-label">Resistance</div>
                                <div class="price-value">{resistance}</div>
                            </div>
                        </div>
                    </div>

                    <div class="grid-item">
                        <h3>ML Prediction</h3>
                        <div class="ml-direction">
                            Direction: {ml_direction}
                        </div>
                        <p>{ml_interpretation}</p>
                        <div class="ml-probability">
                            <div class="ml-probability-fill"></div>
                        </div>
                        <p>Probability: {ml_probability:.2f}</p>
                    </div>
                </div>

                <div class="section">
                    <h3>Key Technical Indicators</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>Indicator</th>
                                <th>Value</th>
                                <th>Interpretation</th>
                            </tr>
                        </thead>
                        <tbody>
                            {indicators_html}
                        </tbody>
                    </table>
                </div>

                <div class="grid-container">
                    <div class="grid-item">
                        <h3>Key Support Factors</h3>
                        <ul>{factors_html}</ul>
                    </div>
                    <div class="grid-item">
                        <h3>Potential Risks</h3>
                        <ul>{risks_html}</ul>
                    </div>
                </div>

                <div class="section">
                    <h3>Trade Considerations</h3>
                    <p>{trade_considerations}</p>
                </div>

                <div class="footer">
                    <p>Generated by Retro Trading Console | Claude Sentiment Engine</p>
                    <div>
                        <span class="led"></span>
                        <span class="led"></span>
                        <span class="led"></span>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        return html

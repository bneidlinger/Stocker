# sentiment/ui_integration.py
# UI integration for the sentiment analyzer

import customtkinter as ctk
import pandas as pd

import os
from typing import Dict
from sentiment.sentiment_analyzer import MarketSentimentAnalyzer


class SentimentModule:
    """
    Manages the UI integration for the sentiment analysis functionality,
    creating a frame with controls and handling the sentiment analysis process.
    """

    def __init__(self, parent, app):
        """
        Initialize the sentiment module UI.

        Args:
            parent: Parent widget
            app: Main application instance
        """
        self.parent = parent
        self.app = app
        self.analyzer = None
        self.api_key_var = ctk.StringVar(value="")

        # Default font settings from main app
        self.font_normal = app.font_normal if hasattr(app, 'font_normal') else ctk.CTkFont(family='Courier New',
                                                                                           size=12)
        self.font_button = app.font_button if hasattr(app, 'font_button') else ctk.CTkFont(family='Courier New',
                                                                                           size=12, weight="bold")

        # Colors - Get them directly from config rather than from app to ensure they're defined
        from config import (COLOR_BACKGROUND, COLOR_FOREGROUND, COLOR_BUTTON, COLOR_BUTTON_HOVER,
                            COLOR_DROPDOWN_FG, COLOR_DROPDOWN_BG, COLOR_ACCENT, COLOR_SECONDARY_BUTTON)

        self.COLOR_BACKGROUND = COLOR_BACKGROUND
        self.COLOR_FOREGROUND = COLOR_FOREGROUND
        self.COLOR_BUTTON = COLOR_BUTTON
        self.COLOR_BUTTON_HOVER = COLOR_BUTTON_HOVER
        self.COLOR_DROPDOWN_FG = COLOR_DROPDOWN_FG
        self.COLOR_DROPDOWN_BG = COLOR_DROPDOWN_BG
        self.COLOR_ACCENT = COLOR_ACCENT
        self.COLOR_SECONDARY_BUTTON = COLOR_SECONDARY_BUTTON

        # Create the main frame with proper background color
        self.create_frame()

        # Try to initialize the analyzer with the API key from environment
        self.try_init_analyzer()

    def create_frame(self):
        """Create the sentiment analysis UI frame."""
        # Main sentiment frame - use transparent fg_color to match parent background
        self.frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)

        # API Key section with proper styling
        api_key_frame = ctk.CTkFrame(self.frame, fg_color=self.COLOR_BACKGROUND)
        api_key_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            api_key_frame,
            text="Claude API Key:",
            font=self.font_normal,
            text_color=self.COLOR_FOREGROUND
        ).pack(side="left", padx=(10, 5))

        api_key_entry = ctk.CTkEntry(
            api_key_frame,
            textvariable=self.api_key_var,
            width=250,
            font=self.font_normal,
            show="*",
            text_color=self.COLOR_DROPDOWN_FG,
            fg_color=self.COLOR_DROPDOWN_BG,
            border_color=self.COLOR_BUTTON,
            border_width=1
        )
        api_key_entry.pack(side="left", padx=(0, 10))

        # Load key from environment if available
        env_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if env_key:
            self.api_key_var.set(env_key)
            api_key_entry.configure(state="disabled")

        # Save API Key button
        self.save_key_button = ctk.CTkButton(
            api_key_frame,
            text="Initialize",
            command=self.save_api_key,
            font=self.font_button,
            text_color=self.COLOR_BACKGROUND,
            fg_color=self.COLOR_BUTTON,
            hover_color=self.COLOR_BUTTON_HOVER,
            width=100
        )
        self.save_key_button.pack(side="left", padx=(0, 10))

        # Status indicator
        self.status_label = ctk.CTkLabel(
            api_key_frame,
            text="Status: Not Initialized",
            font=self.font_normal,
            text_color=self.COLOR_FOREGROUND
        )
        self.status_label.pack(side="left")

        # Sentiment Analysis button
        self.sentiment_button = ctk.CTkButton(
            self.frame,
            text="Generate Sentiment Analysis",
            command=self.run_sentiment_analysis,
            font=self.font_button,
            text_color=self.COLOR_BACKGROUND,
            fg_color=self.COLOR_ACCENT,
            hover_color=self.COLOR_BUTTON_HOVER,
            state="disabled"
        )
        self.sentiment_button.pack(pady=(0, 10))

        # Options Section
        options_frame = ctk.CTkFrame(self.frame, fg_color=self.COLOR_BACKGROUND)
        options_frame.pack(fill="x")

        # Create the horizon selection
        ctk.CTkLabel(
            options_frame,
            text="Horizon (days):",
            font=self.font_normal,
            text_color=self.COLOR_FOREGROUND
        ).pack(side="left", padx=(10, 5))

        # Create the horizon selection dropdown
        self.horizon_var = ctk.StringVar(value="5")
        horizon_values = ["1", "3", "5", "7", "14", "30"]

        horizon_dropdown = ctk.CTkComboBox(
            options_frame,
            values=horizon_values,
            variable=self.horizon_var,
            width=60,
            font=self.font_normal,
            text_color=self.COLOR_DROPDOWN_FG,
            fg_color=self.COLOR_DROPDOWN_BG,
            dropdown_fg_color=self.COLOR_DROPDOWN_BG,
            button_color=self.COLOR_BUTTON,
            button_hover_color=self.COLOR_BUTTON_HOVER,
            border_color=self.COLOR_BUTTON,
            border_width=1
        )
        horizon_dropdown.pack(side="left", padx=(0, 20))

    def try_init_analyzer(self):
        """Try to initialize the analyzer with the API key from environment."""
        try:
            api_key = self.api_key_var.get().strip()
            if api_key:
                self.analyzer = MarketSentimentAnalyzer(api_key=api_key)
                self.status_label.configure(text="Status: Initialized", text_color=self.COLOR_ACCENT)
                self.sentiment_button.configure(state="normal")
                self.save_key_button.configure(text="Reconnect")
                return True
            return False
        except Exception as e:
            self.app.log_message(f"Error initializing sentiment analyzer: {e}", tag="negative")
            self.status_label.configure(text=f"Status: Error", text_color="#ff4d6d")
            return False

    def save_api_key(self):
        """Save the API key and initialize the analyzer."""
        api_key = self.api_key_var.get().strip()
        if not api_key:
            self.app.log_message("Error: Claude API key is required.", tag="negative")
            return

        try:
            self.status_label.configure(text="Status: Initializing...", text_color=self.COLOR_FOREGROUND)
            self.app.update_idletasks()  # Update UI to show status change

            self.analyzer = MarketSentimentAnalyzer(api_key=api_key)
            self.status_label.configure(text="Status: Initialized", text_color=self.COLOR_ACCENT)
            self.sentiment_button.configure(state="normal")
            self.save_key_button.configure(text="Reconnect")

            self.app.log_message("Sentiment analyzer initialized successfully.", tag="positive")
        except Exception as e:
            self.app.log_message(f"Error initializing sentiment analyzer: {e}", tag="negative")
            self.status_label.configure(text=f"Status: Error", text_color="#ff4d6d")

    def run_sentiment_analysis(self):
        """Run sentiment analysis on the current stock data."""
        if not self.analyzer:
            self.app.log_message("Sentiment analyzer not initialized.", tag="negative")
            return

        # Check if data is loaded
        if self.app.current_data is None or self.app.current_data.empty:
            self.app.log_message("No data loaded. Please load data first.", tag="negative")
            return

        # Get the current symbol
        symbol = self.app.current_symbol
        if not symbol:
            self.app.log_message("No symbol selected.", tag="negative")
            return

        # Get the horizon
        try:
            horizon_days = int(self.horizon_var.get())
        except ValueError:
            horizon_days = 5  # Default

        # Prepare technical indicators data (from app's TA calculation)
        technical_data = self._prepare_technical_data()

        # Prepare ML prediction data (from app's ML prediction)
        ml_prediction = self._prepare_ml_prediction(horizon_days)

        # Update UI to show analysis is running
        self.status_label.configure(text="Status: Running Analysis...", text_color=self.COLOR_FOREGROUND)
        self.sentiment_button.configure(state="disabled", text="Analysis in Progress...")
        self.app.set_led_state("ML", "on", flicker=True)  # Use the ML LED for sentiment analysis
        self.app.log_message(f"\n--- Generating Market Sentiment Analysis for {symbol} ---")
        self.app.log_message(f"Prediction Horizon: {horizon_days} days")
        self.app.update_idletasks()  # Update UI

        try:
            # Run the sentiment analysis
            sentiment_data = self.analyzer.analyze_sentiment(
                symbol=symbol,
                price_data=self.app.current_data,
                technical_data=technical_data,
                ml_prediction=ml_prediction,
                horizon_days=horizon_days
            )

            # Log the sentiment result
            sentiment = sentiment_data.get("sentiment", "ERROR")
            confidence = sentiment_data.get("confidence", "UNKNOWN")
            self.app.log_message(f"Sentiment Analysis Complete: {sentiment} ({confidence})")

            # Log summary
            summary = sentiment_data.get("summary", "No summary available")
            self.app.log_message(f"Summary: {summary}")

            # Log key factors (first 2 only to avoid flooding console)
            factors = sentiment_data.get("key_factors", [])
            if factors:
                self.app.log_message("Key factors:")
                for i, factor in enumerate(factors[:2]):
                    self.app.log_message(f"  {i + 1}. {factor}")
                if len(factors) > 2:
                    self.app.log_message(f"  ... and {len(factors) - 2} more (see full report)")

            # Display the HTML report
            self.analyzer.display_sentiment_report(sentiment_data)

            # Update UI to show analysis is complete
            self.status_label.configure(text="Status: Analysis Complete", text_color=self.COLOR_ACCENT)
            self.sentiment_button.configure(state="normal", text="Generate Sentiment Analysis")

        except Exception as e:
            self.app.log_message(f"Error during sentiment analysis: {e}", tag="negative")
            self.status_label.configure(text=f"Status: Error", text_color="#ff4d6d")
            self.sentiment_button.configure(state="normal", text="Generate Sentiment Analysis")
        finally:
            self.app.set_led_state("ML", "off")  # Turn off the LED

    def _prepare_technical_data(self) -> Dict:
        """
        Prepare technical indicators data from the app's state.

        Returns:
            Dictionary containing technical indicators data
        """
        # Use the app's latest TA results if available
        if hasattr(self.app, 'latest_ta_results') and self.app.latest_ta_results:
            ta_results = self.app.latest_ta_results

            # Create a structured dictionary with the available TA data
            technical_data = {
                "rsi": ta_results.get('rsi', None),
                "sma_short": ta_results.get('sma_short', None),
                "sma_long": ta_results.get('sma_long', None),
                "adx": ta_results.get('adx', None),
                "recommendation": ta_results.get('recommendation', "NEUTRAL"),
                "score": ta_results.get('score', 0.0)
            }
        else:
            # Provide a default structure if no TA results available
            technical_data = {
                "rsi": None,
                "sma_short": None,
                "sma_long": None,
                "adx": None,
                "recommendation": "NEUTRAL",
                "score": 0.0
            }

        # Calculate additional indicators if possible
        if not self.app.current_data.empty and hasattr(self.app, 'talib_module') and self.app.talib_module:
            try:
                close = self.app.current_data['close']
                high = self.app.current_data['high']
                low = self.app.current_data['low']

                # Calculate MACD
                macd, macd_signal, macd_hist = self.app.talib_module.MACD(
                    close, fastperiod=12, slowperiod=26, signalperiod=9
                )
                technical_data["macd"] = float(macd.iloc[-1]) if not pd.isna(macd.iloc[-1]) else None
                technical_data["macd_signal"] = float(macd_signal.iloc[-1]) if not pd.isna(
                    macd_signal.iloc[-1]) else None
                technical_data["macd_hist"] = float(macd_hist.iloc[-1]) if not pd.isna(macd_hist.iloc[-1]) else None

                # Calculate Bollinger Bands
                upper, middle, lower = self.app.talib_module.BBANDS(
                    close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0
                )
                technical_data["bb_upper"] = float(upper.iloc[-1]) if not pd.isna(upper.iloc[-1]) else None
                technical_data["bb_middle"] = float(middle.iloc[-1]) if not pd.isna(middle.iloc[-1]) else None
                technical_data["bb_lower"] = float(lower.iloc[-1]) if not pd.isna(lower.iloc[-1]) else None

                # Calculate Stochastic Oscillator
                slowk, slowd = self.app.talib_module.STOCH(
                    high, low, close, fastk_period=14, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0
                )
                technical_data["stoch_k"] = float(slowk.iloc[-1]) if not pd.isna(slowk.iloc[-1]) else None
                technical_data["stoch_d"] = float(slowd.iloc[-1]) if not pd.isna(slowd.iloc[-1]) else None

            except Exception as e:
                self.app.log_message(f"Warning: Error calculating additional indicators: {e}", tag="negative")

        return technical_data

    def _prepare_ml_prediction(self, horizon_days: int) -> Dict:
        """
        Prepare ML prediction data from the app's state.

        Args:
            horizon_days: Prediction horizon in days

        Returns:
            Dictionary containing ML prediction data
        """
        # Default prediction structure
        ml_prediction = {
            "direction": "NEUTRAL",
            "confidence": None,
            "confidence_level": "UNKNOWN",
            "horizon": horizon_days,
            "probabilities": None
        }

        # Use the app's ML prediction if available
        if hasattr(self.app, 'ml_prediction') and self.app.ml_prediction:
            prediction = self.app.ml_prediction

            # Update with actual prediction data
            ml_prediction["direction"] = prediction.get('direction', "NEUTRAL")
            ml_prediction["confidence"] = prediction.get('confidence')
            ml_prediction["confidence_level"] = prediction.get('confidence_level', "UNKNOWN")
            ml_prediction["probabilities"] = prediction.get('probabilities')

            # Use the model's horizon if different from requested
            if 'horizon' in prediction:
                ml_prediction["horizon"] = prediction.get('horizon')

        # Calculate probability based on confidence if available
        if ml_prediction["confidence"] is None and ml_prediction["direction"] != "NEUTRAL":
            if ml_prediction["confidence_level"] == "STRONG":
                ml_prediction["confidence"] = 0.85
            elif ml_prediction["confidence_level"] == "MODERATE":
                ml_prediction["confidence"] = 0.70
            elif ml_prediction["confidence_level"] == "WEAK":
                ml_prediction["confidence"] = 0.60
            else:
                ml_prediction["confidence"] = 0.50

        return ml_prediction
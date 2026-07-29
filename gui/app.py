# gui/app.py
# Main application window class - Refactored

import customtkinter as ctk
from tkinter import font as tkfont, ttk
import tkinter as tk # For TclError handling
import pandas as pd
import numpy as np
import importlib
import datetime
import random
import traceback
import threading
import os
from typing import Dict, List, Tuple, Union, Optional # Typing import
from data.data_source_factory import DataSourceFactory

# Matplotlib imports
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates

# Configuration Imports
from config import (SYMBOLS, DEFAULT_DATA_PERIOD, DEFAULT_DATA_INTERVAL,
                    DEFAULT_CASH, DEFAULT_COMMISSION, DEFAULT_TRADE_SIZE_PERCENT,
                    # Recommendation Params for TA Calc
                    REC_SMA_SHORT, REC_SMA_LONG, REC_RSI_PERIOD, REC_RSI_BUY, REC_RSI_SELL,
                    REC_MACD_FAST, REC_MACD_SLOW, REC_MACD_SIG, # Keep if needed later
                    REC_BBANDS_PERIOD, REC_BBANDS_STDDEV, # Keep if needed later
                    REC_ADX_PERIOD, REC_ADX_THRESHOLD,
                    # Observer Location
                    OBSERVER_LAT, OBSERVER_LON, OBSERVER_ELEV,
                    # Colors & Fonts
                    COLOR_BACKGROUND, COLOR_FOREGROUND, COLOR_BUTTON, COLOR_BUTTON_HOVER,
                    COLOR_DROPDOWN_FG, COLOR_DROPDOWN_BG, COLOR_DROPDOWN_BUTTON, COLOR_DROPDOWN_BUTTON_HOVER,
                    COLOR_TEXTBOX_FG, COLOR_TEXTBOX_BG, FONT_FAMILY_MONO, FONT_SIZE_NORMAL, FONT_SIZE_LARGE,
                    FONT_SIZE_TEXTBOX, FONT_SIZE_LED,
                    COLOR_CHART_BG, COLOR_CHART_LINE, COLOR_CHART_AXES, COLOR_ACCENT,
                    COLOR_POSITIVE, COLOR_NEGATIVE, COLOR_NEUTRAL, COLOR_WEAK_POSITIVE, COLOR_WEAK_NEGATIVE,
                    COLOR_SECONDARY_BUTTON, COLOR_SECONDARY_BUTTON_HOVER,
                    # LED Colors
                    COLOR_LED_PWR_ON, COLOR_LED_CPU_ON, COLOR_LED_DATA_ON, COLOR_LED_COM_ON,
                    # --- Direct Hex Colors for Recommendations ---
                    COLOR_REC_SELL, COLOR_REC_WEAK_SELL, COLOR_REC_HOLD,
                    COLOR_REC_WEAK_BUY, COLOR_REC_BUY, COLOR_REC_DEFAULT,
                    # --- End Direct Hex Colors ---
                    # ML Colors & Config
                    COLOR_LED_ML_ON, COLOR_LED_ML_BORDER, ML_MODEL_DIR, ML_DEFAULT_HORIZON,
                    ML_ENABLE_HYBRID, ML_HYBRID_WEIGHT, ML_TRAIN_TEST_SPLIT,
                    # Auto-Trader Colors
                    COLOR_LED_AUTO_ON, COLOR_LED_AI_ON,
                    COLOR_KILL_SWITCH, COLOR_KILL_SWITCH_HOVER,
                    )

# Local Application Imports
from gui.widgets.vintage_indicators import WornLED
from gui.widgets.dot_matrix import MatrixText # Import MatrixText
from trading.backtester import run_backtest
from trading.ml.service import MlPredictionService
# Import models needed for ML parameter UI
from trading.ml.models import ModelManager
from sentiment.ui_integration import SentimentModule
from gui.auto_trader_tab import AutoTraderTab

# --- Strategy Imports & Definitions ---
# ... (Omitted for Brevity - Keep as before) ...
# Direct imports for non-dependency strategies
from trading.strategies.sma_cross import SmaCross
from trading.strategies.fake_moon_strategy import FakeMoonStrategy
from trading.strategies.ichimoku_strategy import IchimokuStrategy
from trading.strategies.donchian_channel_strategy import DonchianChannelStrategy
from trading.strategies.day_of_week_strategy import DayOfWeekStrategy

# String paths for strategies requiring dynamic loading (TA-Lib, Ephem)
STRATEGY_LOADERS = {
    "SMA Crossover": SmaCross,
    "Ichimoku Cloud": IchimokuStrategy,
    "Donchian Channel": DonchianChannelStrategy,
    "Day of Week Effect": DayOfWeekStrategy,
    "Fake Moon (Day of Month)": FakeMoonStrategy,
    "RSI Oscillator": "trading.strategies.rsi_oscillator.RsiOscillator",
    "Volatility Breakout": "trading.strategies.volatility_breakout.VolatilityBreakout",
    "MACD": "trading.strategies.macd_strategy.MacdStrategy",
    "Bollinger Bands": "trading.strategies.bollinger_bands_strategy.BollingerBandsStrategy",
    "Real Moon (Ephem)": "trading.strategies.real_moon_strategy.RealMoonStrategy"
}

# Strategy Parameter Definitions (Ensure trade_size_percent is always first)
PARAM_CONFIG = {
    "SMA Crossover": [("n1", 10), ("n2", 30)],
    "Ichimoku Cloud": [("tenkan_period", 9), ("kijun_period", 26), ("senkou_b_period", 52), ("chikou_period", 26), ("senkou_displacement", 26)],
    "Donchian Channel": [("n_high", 20), ("n_low", 20)],
    "Day of Week Effect": [("buy_day", 0), ("sell_day", 4)],
    "Fake Moon (Day of Month)": [("buy_day_start", 1), ("buy_day_end", 5), ("sell_day_start", 14), ("sell_day_end", 18)],
    "RSI Oscillator": [("rsi_period", 14), ("upper_bound", 70), ("lower_bound", 30)],
    "Volatility Breakout": [("atr_period", 14), ("ma_period", 20), ("atr_multiplier", 2.0)],
    "MACD": [("fast_period", 12), ("slow_period", 26), ("signal_period", 9)],
    "Bollinger Bands": [("bb_period", 20), ("bb_std_dev", 2.0)],
    "Real Moon (Ephem)": [("days_after_new_moon_buy", 2), ("buy_window_days", 3), ("days_after_full_moon_sell", 2), ("sell_window_days", 3)],
}
# Add default trade size parameter to all strategies
for params in PARAM_CONFIG.values():
     params.insert(0, ("trade_size_percent", DEFAULT_TRADE_SIZE_PERCENT))

# Strategy Descriptions (Keep as before)
STRATEGY_DESCRIPTIONS = {
    "SMA Crossover": "Simple Moving Average Crossover...", # Omitted for brevity
    "Ichimoku Cloud": "Ichimoku Kinko Hyo...",
    "Donchian Channel": "Donchian Channel Breakout...",
    "Day of Week Effect": "Calendar-Based Strategy...",
    "Fake Moon (Day of Month)": "Placeholder Lunar Strategy...",
    "RSI Oscillator": "Relative Strength Index Oscillator...",
    "Volatility Breakout": "Volatility Breakout using ATR...",
    "MACD": "Moving Average Convergence Divergence...",
    "Bollinger Bands": "Bollinger Bands Mean Reversion...",
    "Real Moon (Ephem)": "Lunar Cycle Strategy (Astronomical)...",
}

# Easter Egg Art (Keep as before)
EASTER_EGG_ART = """ ... """ # Omitted for brevity

# --- Constants for Dot Matrix Display ---
MATRIX_COLS = 12
MATRIX_CHAR_WIDTH = 5
MATRIX_SPACING = 1
MATRIX_TOTAL_COLS = MATRIX_COLS * (MATRIX_CHAR_WIDTH + MATRIX_SPACING) - MATRIX_SPACING # Adjusted calculation
MATRIX_ROWS = 7
MATRIX_PIXEL_SIZE = 6
MATRIX_BG = "#050505" # Use config color? COLOR_MATRIX_BG if defined

# --- NEW: Recommendation Color Mapping (Using HEX codes) ---
RECOMMENDATION_HEX_COLORS = {
    'BUY': COLOR_REC_BUY,
    'WEAK BUY': COLOR_REC_WEAK_BUY,
    'HOLD': COLOR_REC_HOLD,
    'WEAK SELL': COLOR_REC_WEAK_SELL,
    'SELL': COLOR_REC_SELL,
    'DEFAULT': COLOR_REC_DEFAULT, # For price display
    'N/A': COLOR_REC_HOLD,
    'ERROR': COLOR_REC_SELL,
    'LOADING...': COLOR_REC_WEAK_SELL, # Or maybe HOLD color?
    'CALC...': COLOR_REC_WEAK_SELL, # Or maybe HOLD color?
    'NO DATA': COLOR_REC_HOLD,
    'NO TA-LIB': COLOR_REC_SELL,
    # Add blank space mapping to background or a very dim color if needed
    ' ': COLOR_REC_HOLD, # Default blank space to HOLD color (or choose another)
}


# ==============================================================================
# Main Application Class
# ==============================================================================
class App(ctk.CTk):
    """ Main application window """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # --- Core Application State ---
        self.current_symbol = ""
        self.current_data = None # Stores the full fetched OHLCV data
        self.plotted_data = None # Reference to data currently shown on chart
        self.latest_price = None
        self._loading_data = False # Flag used by clear_display
        self._shutdown_event = threading.Event() # Interrupts fetcher retry sleeps on close

        # --- TA State ---
        self.talib_module = None # Loaded TA-Lib module
        self.ephem_module = None # Loaded Ephem module
        self.latest_ta_results = None # Stores dict from _calculate_ta_indicators
        # --- FIX: Initialize recommendation state to blank ---
        self.latest_recommendation = " " # String: BUY, SELL, HOLD etc. *** RENAMED & INITIALIZED BLANK ***
        self.latest_technical_score = 0.0 # Float score from TA calc
        self.latest_adx = None # Float ADX value from TA calc

        # --- ML State ---
        self.ml_service = None # Initialized in init_ml_components
        self.ml_model_loaded = False # Flag if a model is loaded for current symbol
        self.ml_prediction = None # Stores the dict result from ml_service.predict
        self.latest_feature_importances = None # Stores dict of feature importances
        # ML UI Variables (initialized in update_ml_controls_frame)
        self.ml_horizon_var = None
        self.ml_model_type_var = None
        self.ml_threshold_var = None
        self.ml_test_split_var = None
        # Add config defaults for ML UI vars
        self.ml_default_horizon = ML_DEFAULT_HORIZON
        self.ml_enable_hybrid = ML_ENABLE_HYBRID
        self.ml_hybrid_weight = ML_HYBRID_WEIGHT
        # Get default threshold from config if defined, else use 1.0
        self.ml_default_threshold_pct = 1.0 # Default 1%
        # if 'ML_DEFAULT_THRESHOLD' in globals():
        #     self.ml_default_threshold_pct = ML_DEFAULT_THRESHOLD * 100.0


        # --- Backtesting State ---
        self.param_entries = {} # Stores CTkStringVars for strategy parameters

        # --- Auto-Trader State ---
        self.auto_trader_tab = None

        # --- UI Update Job IDs ---
        self.activity_led_job = None
        self.matrix_update_job = None
        self.matrix_shows_price = False # Toggles between price/recommendation

        # --- Initialize Core Components ---
        self.data_fetcher = DataSourceFactory.get_data_fetcher()
        self.data_fetcher.stop_event = self._shutdown_event
        self._load_optional_modules() # Load TA-Lib, Ephem
        self._configure_window()
        self._configure_fonts()
        self._create_widgets()
        self.init_ml_components() # Initialize ML service and related UI state
        self._configure_tab_styles()  # Configure tab styles first
        self.init_sentiment_components() # Initialize sentiment components
        self.update_ml_controls_frame() # Create ML control widgets
        self.initialize_leds() # Set initial LED states and start loops
        self._update_feature_importance_button_state() # Ensure button is initially disabled
        self.update_param_widgets(self.strategy_var.get()) # Initial params for default strategy
        self.protocol("WM_DELETE_WINDOW", self.on_closing) # Graceful shutdown
        self._update_core_layouts()  # Update layouts after adding components
        print("Application Initialized.")

    # --------------------------------------------------------------------------
    # Initialization and Configuration Methods
    # --------------------------------------------------------------------------
    # ... (Methods _configure_window, _configure_fonts, _load_optional_modules, _create_widgets,
    #      init_ml_components, update_ml_controls_frame, initialize_leds remain the same
    #      as the previous full version) ...
    def _configure_window(self):
        """Sets up the main window properties."""
        self.title("Retro Trading Console")
        self.geometry("1100x850") # Adjust size as needed
        self.configure(fg_color=COLOR_BACKGROUND)
        # Configure grid layout
        self.grid_columnconfigure(0, weight=3) # Chart area column
        self.grid_columnconfigure(1, weight=1) # Console/Controls column
        self.grid_rowconfigure(0, weight=0) # Header Controls
        self.grid_rowconfigure(1, weight=0) # Chart Controls
        self.grid_rowconfigure(2, weight=0) # Dot Matrix
        self.grid_rowconfigure(3, weight=1) # Main Content (Chart/Console)
        self.grid_rowconfigure(4, weight=0) # Chart Info Label
        self.grid_rowconfigure(5, weight=0) # Backtest Controls
        self.grid_rowconfigure(6, weight=0) # Parameter/ML Controls Frame
        self.grid_rowconfigure(7, weight=0) # LED Frame

    def _configure_fonts(self):
        """Configures fonts used throughout the application."""
        available_fonts = list(tkfont.families())
        # Fallback font if preferred monospace isn't available
        self.mono_font_family = FONT_FAMILY_MONO if FONT_FAMILY_MONO in available_fonts else "Courier"
        print(f"Using font: {self.mono_font_family}")

        self.font_normal = ctk.CTkFont(family=self.mono_font_family, size=FONT_SIZE_NORMAL)
        self.font_large = ctk.CTkFont(family=self.mono_font_family, size=FONT_SIZE_LARGE)
        self.font_button = ctk.CTkFont(family=self.mono_font_family, size=FONT_SIZE_NORMAL, weight="bold")
        self.font_textbox = ctk.CTkFont(family=self.mono_font_family, size=FONT_SIZE_TEXTBOX)
        self.font_led = ctk.CTkFont(family=self.mono_font_family, size=FONT_SIZE_LED)

    def _load_optional_modules(self):
        """Attempts to load optional TA-Lib and Ephem modules."""
        try:
            import talib
            self.talib_module = talib
            print("TA-Lib imported successfully.")
        except ImportError:
            print("Failed to import TA-Lib. Some features might be unavailable.")
            # Log to console as well?
            # self.after(100, lambda: self.log_message("Warning: TA-Lib not found. RSI, MACD, BBands, ADX calculations disabled.", tag="negative"))

        try:
            import ephem
            self.ephem_module = ephem
            print("Ephem imported successfully.")
        except ImportError:
            print("Failed to import Ephem. RealMoonStrategy will be unavailable.")
            # self.after(100, lambda: self.log_message("Warning: Ephem not found. RealMoonStrategy disabled.", tag="negative"))

    def _configure_tab_styles(self):
        """Configure ttk styles for tabs to match the app theme"""
        # Create a ttk style object
        self.ttk_style = ttk.Style()

        # Configure colors with higher contrast for better readability
        tab_bg = COLOR_DROPDOWN_BG
        tab_fg = "#FFFFFF"  # Bright white for better readability
        tab_selected_bg = COLOR_BACKGROUND
        tab_selected_fg = "#39FF14"  # Neon green for better visibility

        # Configure notebook style
        self.ttk_style.configure('Custom.TNotebook',
                                 background=COLOR_BACKGROUND,
                                 borderwidth=0)

        # Configure tab style
        self.ttk_style.configure('Custom.TNotebook.Tab',
                                 background=tab_bg,
                                 foreground=tab_fg,
                                 padding=[10, 2],
                                 borderwidth=1,
                                 font=('Consolas', 12, 'bold'))

        # Configure tab states (selected, active, etc.)
        self.ttk_style.map('Custom.TNotebook.Tab',
                           background=[('selected', tab_selected_bg)],
                           foreground=[('selected', tab_selected_fg)],
                           borderwidth=[('selected', 2)])

    def init_sentiment_components(self):
        """Initialize sentiment analysis components."""
        print("Initializing sentiment analysis components...")

        # Create sentiment tab in the param_ml_container if it exists
        if hasattr(self, 'param_ml_container') and self.param_ml_container.winfo_exists():
            # Configure tab styles if not already done
            if not hasattr(self, 'ttk_style'):
                self._configure_tab_styles()

            # Create new containers for tabs if they don't exist yet
            if not hasattr(self, 'tab_control'):
                # Create the notebook control with styled tabs
                self.tab_control = ttk.Notebook(self.param_ml_container, style='Custom.TNotebook')

                # Create the tabs with proper background color
                self.params_tab = ctk.CTkFrame(self.tab_control, fg_color=COLOR_BACKGROUND)
                self.ml_tab = ctk.CTkFrame(self.tab_control, fg_color=COLOR_BACKGROUND)
                self.sentiment_tab = ctk.CTkFrame(self.tab_control, fg_color=COLOR_BACKGROUND)

                # Add the tabs to the notebook with custom tab IDs
                self.tab_control.add(self.params_tab, text="Parameters")
                self.tab_control.add(self.ml_tab, text="ML")
                self.tab_control.add(self.sentiment_tab, text="Sentiment")

                # Grid the notebook - make it expandable
                self.tab_control.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
                self.param_ml_container.grid_rowconfigure(0, weight=1)

                # Move existing widgets to the appropriate tabs
                if hasattr(self, 'param_frame') and self.param_frame.winfo_exists():
                    # Store the current parameters
                    current_strategy = self.strategy_var.get()
                    param_entries = self.param_entries.copy() if hasattr(self, 'param_entries') else {}

                    self.param_frame.destroy()  # Completely remove old frame
                    self.param_frame = ctk.CTkFrame(self.params_tab, fg_color="transparent")
                    self.param_frame.pack(side="left", fill="x", expand=True, padx=10, pady=5)

                    # Recreate parameter widgets
                    self.param_entries = {}  # Reset parameter entries
                    self.update_param_widgets(current_strategy)

                if hasattr(self, 'ml_controls_frame') and self.ml_controls_frame.winfo_exists():
                    self.ml_controls_frame.destroy()  # Completely remove old frame
                    self.ml_controls_frame = ctk.CTkFrame(self.ml_tab, fg_color="transparent")
                    self.ml_controls_frame.pack(side="left", fill="x", expand=True, padx=10, pady=5)
                    self.update_ml_controls_frame()  # Recreate ML controls

            # Initialize the sentiment module
            self.sentiment_module = SentimentModule(self.sentiment_tab, self)

            # Add Auto-Trade tab
            self.auto_trade_tab = ctk.CTkFrame(self.tab_control, fg_color=COLOR_BACKGROUND)
            self.tab_control.add(self.auto_trade_tab, text="Auto-Trade")
            self.auto_trader_tab = AutoTraderTab(self.auto_trade_tab, self)

            # Force tab control to recalculate its layout
            self.tab_control.update_idletasks()

            # Switch to sentiment tab by default if it's new
            self.tab_control.select(2)  # Select the sentiment tab (index 2)
        else:
            print("Warning: param_ml_container not found, cannot initialize sentiment tab")

    def _update_core_layouts(self):
        """Update core layout components after adding tabs"""
        # Ensure param_ml_container has correct configuration
        if hasattr(self, 'param_ml_container') and self.param_ml_container.winfo_exists():
            # Make sure the container can expand to fill available space
            self.param_ml_container.grid(row=6, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="nsew")
            # Allow rows to expand
            self.param_ml_container.grid_rowconfigure(0, weight=1)
            self.param_ml_container.grid_columnconfigure(0, weight=1)

    def _create_widgets(self):
        """Creates and grids all the main UI widgets."""
        # --- Header / Data Controls Frame (Row 0) ---
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 5), sticky="ew")
        # Symbol Select
        ctk.CTkLabel(self.controls_frame, text="Symbol:", font=self.font_normal, text_color=COLOR_FOREGROUND).pack(side="left", padx=(0, 5))
        self.symbol_var = ctk.StringVar(value=SYMBOLS[0])
        self.symbol_dropdown = ctk.CTkComboBox(
            self.controls_frame, values=SYMBOLS, variable=self.symbol_var, width=100,
            font=self.font_normal, text_color=COLOR_DROPDOWN_FG, fg_color=COLOR_DROPDOWN_BG,
            dropdown_fg_color=COLOR_DROPDOWN_BG, button_color=COLOR_DROPDOWN_BUTTON,
            button_hover_color=COLOR_DROPDOWN_BUTTON_HOVER, border_color=COLOR_BUTTON, border_width=1,
            command=self.on_symbol_change
        )
        self.symbol_dropdown.pack(side="left", padx=(0, 10))
        # Custom Symbol Input
        ctk.CTkLabel(self.controls_frame, text="Custom:", font=self.font_normal, text_color=COLOR_FOREGROUND).pack(side="left", padx=(10, 5))
        self.custom_symbol_entry = ctk.CTkEntry(
            self.controls_frame, width=70, font=self.font_normal,
            text_color=COLOR_DROPDOWN_FG, fg_color=COLOR_DROPDOWN_BG,
            border_color=COLOR_BUTTON, border_width=1
        )
        # Bind Enter key in custom entry to load data
        self.custom_symbol_entry.bind("<Return>", lambda event: self.fetch_and_display_data())
        self.custom_symbol_entry.pack(side="left", padx=(0, 20))
        # Load Data Button
        self.fetch_button = ctk.CTkButton(
            self.controls_frame, text="Load Data", command=self.fetch_and_display_data,
            font=self.font_button, text_color=COLOR_BACKGROUND,
            fg_color=COLOR_BUTTON, hover_color=COLOR_BUTTON_HOVER
        )
        self.fetch_button.pack(side="left", padx=(0, 10))

        # Kill Switch Button (far right of controls frame, always visible)
        self.kill_switch_button = ctk.CTkButton(
            self.controls_frame, text="KILL SWITCH",
            command=self.activate_kill_switch,
            font=self.font_button, text_color="#FFFFFF",
            fg_color=COLOR_KILL_SWITCH, hover_color=COLOR_KILL_SWITCH_HOVER,
            width=120, height=32, state="disabled",
        )
        self.kill_switch_button.pack(side="right", padx=(10, 0))

        # --- Chart Controls Frame (Row 1) ---
        self.chart_controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.chart_controls_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 5), sticky="ew")
        ctk.CTkLabel(self.chart_controls_frame, text="Chart Period:", font=self.font_normal, text_color=COLOR_FOREGROUND).pack(side="left", padx=(0, 10))
        lookback_periods = ["ALL", "YTD", "1Y", "6M", "3M", "1M"]
        self.chart_period_buttons = {} # Store buttons for highlighting
        for period in lookback_periods:
            btn = ctk.CTkButton(
                self.chart_controls_frame, text=period,
                font=self.font_normal, width=40, height=24, text_color=COLOR_FOREGROUND,
                fg_color=COLOR_SECONDARY_BUTTON, hover_color=COLOR_SECONDARY_BUTTON_HOVER
            )
            # Use lambda with default arguments to capture current period and button instance
            btn.configure(command=lambda p=period, b=btn: self._handle_chart_period_click(p, b))
            btn.pack(side="left", padx=(0, 5))
            self.chart_period_buttons[period] = btn
        # Highlight the default 'ALL' button initially
        self._highlight_chart_period_button("ALL")


        # --- Dot Matrix Recommendation Display (Row 2) ---
        self.recommendation_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.recommendation_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=(10, 10), sticky="") # Centered
        self.recommendation_display = MatrixText(
            self.recommendation_frame, rows=MATRIX_ROWS, cols=MATRIX_TOTAL_COLS,
            pixel_size=MATRIX_PIXEL_SIZE, char_spacing=MATRIX_SPACING, bg_color=MATRIX_BG,
            default_on_color=RECOMMENDATION_HEX_COLORS['DEFAULT'] # Pass default HEX color
        )
        self.recommendation_display.get_frame().pack()
        # self.recommendation_display.display_text(" " * MATRIX_COLS) # Initial blank display done by clear() in init flow

        # --- Chart Area (Row 3, Column 0) ---
        self.chart_frame = ctk.CTkFrame(self, fg_color=COLOR_CHART_BG, border_color=COLOR_BUTTON, border_width=1)
        self.chart_frame.grid(row=3, column=0, rowspan=1, padx=(20, 10), pady=5, sticky="nsew")
        self.chart_frame.grid_rowconfigure(0, weight=1)
        self.chart_frame.grid_columnconfigure(0, weight=1)
        # Setup Matplotlib Figure and Axes
        self.fig, self.ax = plt.subplots()
        self.fig.set_facecolor(COLOR_CHART_BG)
        self._style_chart_axes() # Apply axes styling
        # Initial placeholder text
        self.ax.text(0.5, 0.5, 'Select symbol and click Load Data',
                     horizontalalignment='center', verticalalignment='center',
                     transform=self.ax.transAxes, color=COLOR_CHART_AXES,
                     fontsize=self.font_large.cget('size'))
        # Embed chart in Tkinter
        self.chart_canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.chart_canvas_widget = self.chart_canvas.get_tk_widget()
        self.chart_canvas_widget.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.chart_canvas.draw()
        self.chart_canvas.mpl_connect('motion_notify_event', self.on_chart_motion) # Hover effect

        # --- Console Output Textbox (Row 3, Column 1) ---
        self.output_textbox = ctk.CTkTextbox(
            self, font=self.font_textbox, text_color=COLOR_TEXTBOX_FG, fg_color=COLOR_TEXTBOX_BG,
            border_color=COLOR_BUTTON, border_width=1, wrap="word", # Enable word wrap
            activate_scrollbars=True
        )
        self.output_textbox.grid(row=3, column=1, rowspan=1, padx=(10, 20), pady=5, sticky="nsew")
        # Configure tags for colored text
        self.output_textbox.tag_config("positive", foreground=COLOR_POSITIVE)
        self.output_textbox.tag_config("negative", foreground=COLOR_NEGATIVE)
        self.output_textbox.tag_config("neutral", foreground=COLOR_NEUTRAL)
        self.output_textbox.tag_config("weak_positive", foreground=COLOR_WEAK_POSITIVE)
        self.output_textbox.tag_config("weak_negative", foreground=COLOR_WEAK_NEGATIVE)
        # Initial message
        self.log_message("Retro Trading Console Initialized.", clear_first=True)
        self.log_message("Select symbol, load data, then select and run a backtest or train ML.")
        self.output_textbox.configure(state="disabled") # Make read-only initially

        # --- Chart Info Label (Row 4) ---
        self.chart_info_label = ctk.CTkLabel(self, text="", font=self.font_normal, text_color=COLOR_FOREGROUND, anchor="w")
        self.chart_info_label.grid(row=4, column=0, columnspan=2, padx=20, pady=(0, 5), sticky="ew")

        # --- Backtesting Controls Frame (Row 5) ---
        self.backtest_controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.backtest_controls_frame.grid(row=5, column=0, columnspan=2, padx=20, pady=(0, 5), sticky="ew")
        # Strategy Select
        ctk.CTkLabel(self.backtest_controls_frame, text="Strategy:", font=self.font_normal, text_color=COLOR_FOREGROUND).pack(side="left", padx=(0, 10))
        self.strategy_var = ctk.StringVar(value=list(STRATEGY_LOADERS.keys())[0])
        self.strategy_dropdown = ctk.CTkComboBox(
            self.backtest_controls_frame, values=list(STRATEGY_LOADERS.keys()), variable=self.strategy_var,
            font=self.font_normal, text_color=COLOR_DROPDOWN_FG, fg_color=COLOR_DROPDOWN_BG,
            dropdown_fg_color=COLOR_DROPDOWN_BG, button_color=COLOR_DROPDOWN_BUTTON,
            button_hover_color=COLOR_DROPDOWN_BUTTON_HOVER, border_color=COLOR_BUTTON, border_width=1,
            command=self.update_param_widgets # Update params when strategy changes
        )
        self.strategy_dropdown.pack(side="left", padx=(0, 15))
        # Info Button
        self.info_button = ctk.CTkButton(
            self.backtest_controls_frame, text="Info", command=self.show_strategy_info,
            font=self.font_button, text_color=COLOR_FOREGROUND, width=50,
            fg_color=COLOR_SECONDARY_BUTTON, hover_color=COLOR_SECONDARY_BUTTON_HOVER
        )
        self.info_button.pack(side="left", padx=(0,15))
        # Run Backtest Button (Pack to the right)
        self.run_backtest_button = ctk.CTkButton(
            self.backtest_controls_frame, text="Run Backtest", command=self.run_selected_backtest,
            font=self.font_button, text_color=COLOR_BACKGROUND,
            fg_color=COLOR_ACCENT, hover_color=COLOR_BUTTON_HOVER # Use accent color
        )
        self.run_backtest_button.pack(side="right", padx=(15, 0))

        # --- Parameter & ML Controls Frame Container (Row 6) ---
        self.param_ml_container = ctk.CTkFrame(self, fg_color="transparent")
        self.param_ml_container.grid(row=6, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="ew")
        self.param_ml_container.grid_columnconfigure(0, weight=1) # Parameters area stretches
        self.param_ml_container.grid_columnconfigure(1, weight=0) # ML controls area fixed size

        # --- Parameter Frame (Inside Container, Column 0) ---
        self.param_frame = ctk.CTkFrame(self.param_ml_container, fg_color="transparent")
        self.param_frame.grid(row=0, column=0, sticky="w")
        # Initial parameters will be populated by update_param_widgets

        # --- ML Controls Frame (Inside Container, Column 1) ---
        self.ml_controls_frame = ctk.CTkFrame(self.param_ml_container, fg_color="transparent")
        self.ml_controls_frame.grid(row=0, column=1, sticky="e")
        # Widgets populated by update_ml_controls_frame


        # --- LED Frame (Row 7) ---
        self.led_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.led_frame.grid(row=7, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew") # Increased bottom padding
        self.leds = {} # Dictionary to hold LED widgets
        led_configs = [
            ("PWR", COLOR_LED_PWR_ON), ("CPU", COLOR_LED_CPU_ON), ("DATA", COLOR_LED_DATA_ON),
            ("COM", COLOR_LED_COM_ON), ("ERR", COLOR_LED_PWR_ON) # ERR uses PWR color
        ]
        app_bg_color = self.cget("fg_color") # Get actual background color
        for name, on_color in led_configs:
            led_container = ctk.CTkFrame(self.led_frame, fg_color="transparent")
            led_container.pack(side="left", padx=10) # Space out LEDs
            led_label = ctk.CTkLabel(led_container, text=name, font=self.font_led, text_color=COLOR_FOREGROUND)
            led_label.pack(side="top")
            led_indicator = WornLED(
                led_container, color=on_color, size=20,
                explicit_canvas_bg=app_bg_color # Pass background for better look
            )
            led_indicator.pack(side="top", pady=(2,0))
            led_indicator.set_wear_level(0.7) # Set default wear
            self.leds[name.upper()] = led_indicator # Use upper case key
            # Add easter egg binding only to PWR LED
            if name == "PWR":
                led_indicator.bind("<Button-1>", self.show_easter_egg)
                led_label.bind("<Button-1>", self.show_easter_egg) # Bind label too

    def init_ml_components(self):
        """Initialize ML service and add ML LED."""
        print("Initializing ML components...")
        self.ml_service = MlPredictionService(model_dir=ML_MODEL_DIR)
        self.ml_model_loaded = False
        self.ml_prediction = None
        self.latest_feature_importances = None

        # Add the ML LED dynamically if frame exists
        if hasattr(self, 'led_frame') and self.led_frame.winfo_exists():
            app_bg_color = self.cget("fg_color")
            led_container = ctk.CTkFrame(self.led_frame, fg_color="transparent")
            led_container.pack(side="left", padx=10)
            led_label = ctk.CTkLabel(led_container, text="ML", font=self.font_led, text_color=COLOR_FOREGROUND)
            led_label.pack(side="top")
            led_indicator = WornLED(
                led_container, color=COLOR_LED_ML_ON, size=20,
                explicit_canvas_bg=app_bg_color
            )
            led_indicator.pack(side="top", pady=(2, 0))
            led_indicator.set_wear_level(0.7)
            self.leds["ML"] = led_indicator # Add to dict using upper case key

            # Add AUTO and AI LEDs for auto-trader
            for led_name, led_color in [("AUTO", COLOR_LED_AUTO_ON), ("AI", COLOR_LED_AI_ON)]:
                at_container = ctk.CTkFrame(self.led_frame, fg_color="transparent")
                at_container.pack(side="left", padx=10)
                at_label = ctk.CTkLabel(at_container, text=led_name, font=self.font_led, text_color=COLOR_FOREGROUND)
                at_label.pack(side="top")
                at_led = WornLED(at_container, color=led_color, size=20, explicit_canvas_bg=app_bg_color)
                at_led.pack(side="top", pady=(2, 0))
                at_led.set_wear_level(0.7)
                self.leds[led_name] = at_led
        else:
             print("Warning: LED frame not ready for ML LED initialization.")


    def update_ml_controls_frame(self):
        """Creates or updates the widgets within the ML controls frame."""
        # Clear existing widgets first
        if hasattr(self, 'ml_controls_frame'):
            for widget in self.ml_controls_frame.winfo_children():
                widget.destroy()
        else:
             print("Error: ml_controls_frame not found during update.")
             return

        # --- Train Button ---
        self.train_ml_button = ctk.CTkButton(
            self.ml_controls_frame, text="Train ML Model", command=self.train_ml_model,
            font=self.font_button, text_color=COLOR_BACKGROUND, width=130,
            fg_color=COLOR_LED_ML_ON, hover_color=COLOR_SECONDARY_BUTTON_HOVER
        )
        self.train_ml_button.grid(row=0, column=0, padx=(0, 10), pady=2)

        # --- Show Features Button ---
        self.show_features_button = ctk.CTkButton(
            self.ml_controls_frame, text="Show Features", command=self.show_feature_importance_popup,
            font=self.font_button, text_color=COLOR_FOREGROUND, width=120,
            fg_color=COLOR_SECONDARY_BUTTON, hover_color=COLOR_SECONDARY_BUTTON_HOVER,
            state="disabled" # Initially disabled
        )
        self.show_features_button.grid(row=0, column=1, padx=(0, 10), pady=2)

        # --- ML Parameters Row ---
        param_row_frame = ctk.CTkFrame(self.ml_controls_frame, fg_color="transparent")
        param_row_frame.grid(row=1, column=0, columnspan=2, pady=(5, 2), sticky="ew")

        # Horizon
        ctk.CTkLabel(param_row_frame, text="Horizon:", font=self.font_normal, text_color=COLOR_FOREGROUND).pack(side="left", padx=(0, 5))
        self.ml_horizon_var = ctk.StringVar(value=str(self.ml_default_horizon))
        ctk.CTkEntry(
            param_row_frame, textvariable=self.ml_horizon_var, width=40, font=self.font_normal,
            text_color=COLOR_DROPDOWN_FG, fg_color=COLOR_DROPDOWN_BG,
            border_color=COLOR_BUTTON, border_width=1
        ).pack(side="left", padx=(0, 2))
        ctk.CTkLabel(param_row_frame, text="d", font=self.font_normal, text_color=COLOR_FOREGROUND).pack(side="left", padx=(0, 10))

        # Model Type
        ctk.CTkLabel(param_row_frame, text="Model:", font=self.font_normal, text_color=COLOR_FOREGROUND).pack(side="left", padx=(0, 5))
        # Ensure ModelManager class is available to get model types
        try:
            model_types = list(ModelManager.CLASSIFICATION_MODELS.keys())
        except AttributeError:
            model_types = ["random_forest"] # Fallback
            print("Warning: Could not get model types from ModelManager.")
        self.ml_model_type_var = ctk.StringVar(value=model_types[0] if model_types else "")
        ctk.CTkComboBox(
            param_row_frame, values=model_types, variable=self.ml_model_type_var, width=140,
            font=self.font_normal, text_color=COLOR_DROPDOWN_FG, fg_color=COLOR_DROPDOWN_BG,
            dropdown_fg_color=COLOR_DROPDOWN_BG, button_color=COLOR_DROPDOWN_BUTTON,
            button_hover_color=COLOR_DROPDOWN_BUTTON_HOVER, border_color=COLOR_BUTTON, border_width=1
        ).pack(side="left", padx=(0, 10))

        # Threshold
        ctk.CTkLabel(param_row_frame, text="Thr(%):", font=self.font_normal, text_color=COLOR_FOREGROUND).pack(side="left", padx=(0, 5))
        self.ml_threshold_var = ctk.StringVar(value=str(self.ml_default_threshold_pct)) # Use initialized default
        ctk.CTkEntry(
            param_row_frame, textvariable=self.ml_threshold_var, width=40, font=self.font_normal,
            text_color=COLOR_DROPDOWN_FG, fg_color=COLOR_DROPDOWN_BG,
            border_color=COLOR_BUTTON, border_width=1
        ).pack(side="left", padx=(0, 10))

        # Test Split
        ctk.CTkLabel(param_row_frame, text="Test(%):", font=self.font_normal, text_color=COLOR_FOREGROUND).pack(side="left", padx=(0, 5))
        self.ml_test_split_var = ctk.StringVar(value=str(ML_TRAIN_TEST_SPLIT * 100)) # Default from config
        ctk.CTkEntry(
            param_row_frame, textvariable=self.ml_test_split_var, width=40, font=self.font_normal,
            text_color=COLOR_DROPDOWN_FG, fg_color=COLOR_DROPDOWN_BG,
            border_color=COLOR_BUTTON, border_width=1
        ).pack(side="left", padx=(0, 0))


    def initialize_leds(self):
        """Sets initial LED states and starts background loops."""
        print("Initializing LEDs...")
        for name, led_widget in self.leds.items():
            # Ensure widget exists before configuring
            if led_widget and led_widget.winfo_exists():
                if name == "PWR":
                    print("Setting PWR LED ON")
                    led_widget.set_state("on")
                    led_widget.enable_flicker(True)
                else:
                    led_widget.set_state("off")
                    led_widget.enable_flicker(False) # Ensure others don't flicker initially
            else:
                print(f"Warning: LED widget '{name}' not found or destroyed during initialization.")

        # Start background loops if they aren't running
        if self.activity_led_job is None:
            # print("Starting activity LED loop...") # Debug
            self._update_activity_leds()
        if self.matrix_update_job is None:
            # print("Starting matrix display loop...") # Debug
            # Use _start_matrix_loop_if_needed to prevent multiple loops if called again
            self._start_matrix_loop_if_needed()


    # --------------------------------------------------------------------------
    # Core Application Logic Methods
    # --------------------------------------------------------------------------

    def run_in_background(self, fn, on_done=None, on_error=None, busy_widgets=(), led=None):
        """Runs fn() on a daemon thread, marshaling completion back to the Tk thread.

        busy_widgets are disabled for the duration; led is a (name, flicker)
        tuple lit while the work runs. fn must not touch Tk objects -- snapshot
        its inputs on the main thread and do all UI work in on_done/on_error.
        """
        for widget in busy_widgets:
            try:
                widget.configure(state="disabled")
            except tk.TclError:
                pass
        if led:
            self.set_led_state(led[0], "on", flicker=led[1])

        def finish(result, exc):
            if not self.winfo_exists():
                return
            for widget in busy_widgets:
                try:
                    if widget.winfo_exists():
                        widget.configure(state="normal")
                except tk.TclError:
                    pass
            if led:
                self.set_led_state(led[0], "off")
            if exc is not None:
                if on_error is not None:
                    on_error(exc)
                else:
                    self.log_message(f"Background task failed: {exc}", tag="negative")
                    traceback.print_exception(exc)
            elif on_done is not None:
                on_done(result)

        def worker():
            result, error = None, None
            try:
                result = fn()
            except Exception as exc:
                error = exc
            try:
                self.after(0, lambda: finish(result, error))
            except RuntimeError:
                pass  # window destroyed while the worker was running

        threading.Thread(target=worker, daemon=True).start()


    def fetch_and_display_data(self):
        """Kicks off a background fetch + TA + ML pipeline for the selected symbol."""
        custom_symbol = self.custom_symbol_entry.get().strip().upper()
        selected_symbol = custom_symbol if custom_symbol else self.symbol_var.get()
        self.current_symbol = selected_symbol

        if not self.current_symbol:
            self.log_message("Error: No symbol selected or entered.", clear_first=True, tag="negative")
            return

        self._loading_data = True # Flag for placeholder text
        self.clear_display() # Show "Loading data...", clears matrix, restarts loop
        self.log_message(f"--- Loading data for {self.current_symbol} ---", clear_first=True)

        # Reset states for new load
        self.current_data = None
        self.plotted_data = None
        self.latest_price = None
        self.latest_ta_results = None
        self.latest_recommendation = "LOADING..." # Update matrix state
        self.latest_technical_score = 0.0
        self.latest_adx = None
        self.latest_feature_importances = None
        self._update_feature_importance_button_state() # Disable feature button
        self.ml_prediction = None
        self.ml_model_loaded = False
        self._update_matrix_display(force_update=True) # Show "LOADING..."

        # Snapshot worker inputs on the main thread (Tk vars must not be read
        # from the worker)
        symbol = self.current_symbol
        try:
            horizon = int(self.ml_horizon_var.get())
        except (ValueError, TypeError, AttributeError):
            horizon = self.ml_default_horizon
        try:
            threshold = float(self.ml_threshold_var.get()) / 100.0
        except (ValueError, TypeError, AttributeError):
            threshold = 0.01

        self.run_in_background(
            lambda: self._fetch_worker(symbol, horizon, threshold),
            on_done=lambda payload: self._on_fetch_done(symbol, payload),
            on_error=lambda exc: self._on_fetch_error(symbol, exc),
            busy_widgets=(self.fetch_button,),
            led=("CPU", False),
        )


    def _fetch_worker(self, symbol: str, horizon: int, threshold: float) -> Dict:
        """Background part of Load Data: fetch, TA, price, ML. No Tk access --
        UI-bound messages are returned as (text, tag) pairs in 'logs'."""
        logs = []
        data = self.data_fetcher.get_historical_data(
            symbol, period=DEFAULT_DATA_PERIOD, interval=DEFAULT_DATA_INTERVAL)
        if data is None or data.empty:
            return {"data": None, "logs": logs}

        if isinstance(data.index, pd.DatetimeIndex) and data.index.tz is not None:
            data.index = data.index.tz_localize(None)
        logs.append((f"Successfully loaded {len(data)} data points.", None))
        logs.append((f"Data range: {data.index.min().strftime('%Y-%m-%d')} to "
                     f"{data.index.max().strftime('%Y-%m-%d')}", None))

        ta_results, ta_error = self._calculate_ta_indicators(data)
        if ta_results:
            logs.append(("\n--- Technical Analysis ---", None))
            logs.append((f"TA Recommendation: {ta_results['recommendation']} "
                         f"(Score: {ta_results['score']:.1f}, ADX: {ta_results['adx']:.1f})", None))
        else:
            detail = f" ({ta_error})" if ta_error else ""
            logs.append((f"Could not calculate TA indicators{detail}.", "negative"))

        price = self.data_fetcher.get_current_price(symbol)
        if price:
            logs.append((f"Approx. Current Price: {price:.2f}", None))

        ml = self._ml_worker(symbol, data, ta_results, horizon, threshold, logs)

        return {"data": data, "ta": ta_results, "price": price, "ml": ml, "logs": logs}


    def _ml_worker(self, symbol: str, data: pd.DataFrame, ta_results: Optional[Dict],
                   horizon: int, threshold: float, logs: list) -> Dict:
        """ML part of the fetch pipeline (worker thread; no Tk access)."""
        result = {"model_loaded": False, "prediction": None, "importances": None,
                  "hybrid": None, "recommendation": None}
        logs.append(("\n--- Machine Learning ---", None))
        logs.append((f"Attempting to load model for {symbol} (Horizon: {horizon}d)...", None))
        try:
            if not self.ml_service.load_model_for_symbol(symbol, prediction_horizon=horizon):
                logs.append(("No pre-trained model found. Proceeding with TA only.", None))
                return result
            result["model_loaded"] = True
            meta = self.ml_service.get_loaded_model_metadata() or {}
            logs.append((f"Successfully loaded model: {meta.get('model_class_name', 'Unknown')}", None))
            result["importances"] = self.ml_service.get_loaded_feature_importances()

            prediction = self.ml_service.predict(data.copy(), target_threshold=threshold)
            if 'error' in prediction:
                logs.append((f"ML Prediction Error: {prediction['error']}", "negative"))
                return result
            result["prediction"] = prediction
            confidence = prediction.get('confidence')
            confidence_str = f"{confidence:.3f}" if confidence is not None else "N/A"
            logs.append((f"ML Direction: {prediction.get('direction')}", None))
            logs.append((f"ML Confidence: {confidence_str}", None))
            logs.append((f"ML Confidence Level: {prediction.get('confidence_level', 'UNKNOWN')}", None))

            if self.ml_enable_hybrid and ta_results:
                hybrid = self.ml_service.get_hybrid_recommendation(
                    df=data.copy(), technical_score=ta_results['score'],
                    adx_value=ta_results['adx'], target_threshold=threshold)
                result["hybrid"] = hybrid
                result["recommendation"] = str(hybrid.get('recommendation', 'ERROR')).upper()
                logs.append(("\n--- Hybrid Recommendation ---", None))
                logs.append((f"Hybrid Recommendation: {hybrid.get('recommendation')}", None))
                logs.append((f"Hybrid Score: {hybrid.get('hybrid_score', 0.0):.2f}", None))
        except Exception as e:
            logs.append((f"ML step failed: {e}", "negative"))
            print(f"Error during ML step: {e}")
            traceback.print_exc()
        return result


    def _on_fetch_done(self, symbol: str, payload: Dict):
        """Main-thread part of Load Data: state assignment, plotting, logging."""
        self._loading_data = False
        if symbol != self.current_symbol:
            print(f"Discarding stale fetch result for {symbol} (now on {self.current_symbol}).")
            return

        for message, tag in payload.get("logs", []):
            self.log_message(message, tag=tag)

        data = payload.get("data")
        if data is None or data.empty:
            self.log_message(f"Failed to load data or no data available for {symbol}.", tag="negative")
            self.plot_data(None)
            self.latest_recommendation = "NO DATA"
            self._update_matrix_display(force_update=True)
            self._start_matrix_loop_if_needed()
            return

        self.current_data = data
        ta = payload.get("ta")
        self.latest_ta_results = ta
        if ta:
            self.latest_recommendation = ta['recommendation']
            self.latest_technical_score = ta['score']
            self.latest_adx = ta['adx']
        else:
            self.latest_recommendation = "N/A"
        self.latest_price = payload.get("price")

        ml = payload.get("ml") or {}
        self.ml_model_loaded = ml.get("model_loaded", False)
        self.ml_prediction = ml.get("prediction")
        self.latest_feature_importances = ml.get("importances")
        if ml.get("recommendation"):
            self.latest_recommendation = ml["recommendation"]
        self._update_feature_importance_button_state()

        self.plot_data(self.current_data, title_suffix=f" ({DEFAULT_DATA_PERIOD})")
        self.log_message("Chart updated.")
        self._update_matrix_display(force_update=True)
        self._start_matrix_loop_if_needed()


    def _on_fetch_error(self, symbol: str, exc: Exception):
        """Main-thread error handler for the fetch pipeline."""
        self._loading_data = False
        if symbol != self.current_symbol:
            return
        self.log_message(f"An error occurred during data fetch/display: {exc}", tag="negative")
        traceback.print_exception(exc)
        self.plot_data(None)
        self.current_data = None
        self.latest_recommendation = "ERROR"
        self._update_matrix_display(force_update=True)
        self._start_matrix_loop_if_needed()


    def plot_data(self, data_to_plot: pd.DataFrame | None, title_suffix: str = ""):
        """Plots the given data on the main chart canvas."""
        # --- (Implementation from previous fix - app_py_plot_update_fix) ---
        self.ax.clear()
        self.plotted_data = None
        self._style_chart_axes() # Apply base styling

        if data_to_plot is None or data_to_plot.empty:
            self.ax.text(0.5, 0.5, f"No data to plot for {self.current_symbol}",
                         color=COLOR_CHART_AXES, ha='center', va='center',
                         transform=self.ax.transAxes, fontsize=self.font_large.cget('size'))
            self.ax.set_xticks([]); self.ax.set_yticks([]) # Clear ticks for placeholder
        elif 'close' not in data_to_plot.columns:
            self.log_message("Error: 'close' column not found in data. Cannot plot chart.", tag="negative")
            self.ax.text(0.5, 0.5, "Error plotting data", color=COLOR_ACCENT,
                         ha='center', va='center', transform=self.ax.transAxes,
                         fontsize=self.font_large.cget('size'))
            self.ax.set_xticks([]); self.ax.set_yticks([])
        else:
            try:
                # Plotting Logic
                self.ax.plot(data_to_plot.index, data_to_plot['close'], color=COLOR_CHART_LINE, linewidth=1.5)
                self.ax.set_title(f"{self.current_symbol} Price{title_suffix}", color=COLOR_CHART_AXES)
                self.ax.set_ylabel("Price (USD)", color=COLOR_CHART_AXES)
                self.ax.set_xlabel("Date", color=COLOR_CHART_AXES)

                # Formatting
                self.fig.autofmt_xdate()
                date_range = data_to_plot.index.max() - data_to_plot.index.min()
                if date_range.days > 365 * 2: formatter = mdates.DateFormatter('%Y')
                elif date_range.days > 90: formatter = mdates.DateFormatter('%b %Y')
                else: formatter = mdates.DateFormatter('%Y-%m-%d')
                self.ax.xaxis.set_major_formatter(formatter)
                self.ax.tick_params(axis='x', colors=COLOR_CHART_AXES, rotation=30)
                self.ax.tick_params(axis='y', colors=COLOR_CHART_AXES)
                self.ax.grid(True, color=COLOR_DROPDOWN_BG, linestyle='--', linewidth=0.5)
                self.plotted_data = data_to_plot # Store reference after plotting

            except Exception as plot_err:
                 self.log_message(f"Error during plotting: {plot_err}", tag="negative")
                 print(f"Error plotting data: {plot_err}")
                 traceback.print_exc()
                 self.ax.text(0.5, 0.5, "Error during plotting", color=COLOR_ACCENT,
                              ha='center', va='center', transform=self.ax.transAxes,
                              fontsize=self.font_large.cget('size'))
                 self.ax.set_xticks([]); self.ax.set_yticks([])

        # Redraw Canvas
        if hasattr(self, 'chart_canvas'):
            try:
                self.chart_canvas.draw_idle()
            except Exception as e:
                print(f"Error redrawing chart canvas: {e}")


    def _style_chart_axes(self):
        """Helper to apply consistent styling to chart axes."""
        self.ax.set_facecolor(COLOR_CHART_BG)
        self.ax.tick_params(axis='x', colors=COLOR_CHART_AXES)
        self.ax.tick_params(axis='y', colors=COLOR_CHART_AXES)
        self.ax.yaxis.label.set_color(COLOR_CHART_AXES)
        self.ax.xaxis.label.set_color(COLOR_CHART_AXES)
        self.ax.title.set_color(COLOR_CHART_AXES)
        for spine in self.ax.spines.values():
            spine.set_color(COLOR_CHART_AXES)


    def clear_display(self):
        """Clears the chart and info label, showing placeholder text."""
        self.ax.clear()
        self.plotted_data = None
        self._style_chart_axes() # Apply base styling

        placeholder = 'Loading data...' if hasattr(self, '_loading_data') and self._loading_data else 'Select symbol and click Load Data'
        self.ax.text(0.5, 0.5, placeholder,
                     horizontalalignment='center', verticalalignment='center',
                     transform=self.ax.transAxes, color=COLOR_CHART_AXES,
                     fontsize=self.font_large.cget('size'))

        self.ax.set_xlabel("")
        self.ax.set_ylabel("")
        self.ax.set_title("")
        self.ax.set_xticks([])
        self.ax.set_yticks([])

        if hasattr(self, 'chart_canvas'):
            try:
                self.chart_canvas.draw_idle()
            except Exception as e:
                print(f"Error redrawing chart canvas during clear: {e}")
        if hasattr(self, 'chart_info_label'):
             self.chart_info_label.configure(text="")

        # --- FIX: Call clear() on the matrix display ---
        if hasattr(self, 'recommendation_display') and self.recommendation_display.get_frame().winfo_exists():
             if self.matrix_update_job: # Cancel loop first
                  try: self.after_cancel(self.matrix_update_job); self.matrix_update_job = None
                  except tk.TclError: pass
             self.recommendation_display.clear() # Use the clear method
             # Ensure loop restarts after clear display forces update
             self._start_matrix_loop_if_needed()
        # --- END FIX ---


    # --------------------------------------------------------------------------
    # Technical Analysis Logic
    # --------------------------------------------------------------------------

    def _calculate_ta_indicators(self, data: pd.DataFrame) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Calculates standard TA indicators and generates a recommendation score.
        Pure computation -- safe to call from a worker thread (no Tk access).

        Returns:
            (results, error) -- results is a dict with 'recommendation', 'score',
            'adx' etc. or None; error is a short reason string when results is None.
        """
        if data is None or data.empty:
            return None, "no data"
        if self.talib_module is None:
            # Attempt import if needed
            try:
                import talib
                self.talib_module = talib
            except ImportError:
                return None, "TA-Lib not installed"

        required_length = max(REC_SMA_LONG, REC_ADX_PERIOD, REC_RSI_PERIOD)
        if len(data) < required_length:
            return None, f"insufficient data ({len(data)} rows, need {required_length})"

        try:
            required_cols = ['close', 'high', 'low']
            if not all(col in data.columns for col in required_cols):
                 missing_cols_str = ", ".join([c for c in required_cols if c not in data.columns])
                 return None, f"missing columns: {missing_cols_str}"

            close_prices = data['close']
            high_prices = data['high']
            low_prices = data['low']

            # Calculate Indicators
            sma_short = self.talib_module.SMA(close_prices, timeperiod=REC_SMA_SHORT)
            sma_long = self.talib_module.SMA(close_prices, timeperiod=REC_SMA_LONG)
            rsi = self.talib_module.RSI(close_prices, timeperiod=REC_RSI_PERIOD)
            adx = self.talib_module.ADX(high_prices, low_prices, close_prices, timeperiod=REC_ADX_PERIOD)

            # Get latest values safely
            latest_sma_short = sma_short.iloc[-1] if not sma_short.empty else np.nan
            latest_sma_long = sma_long.iloc[-1] if not sma_long.empty else np.nan
            latest_rsi = rsi.iloc[-1] if not rsi.empty else np.nan
            latest_adx = adx.iloc[-1] if not adx.empty else np.nan

            if pd.isna(latest_sma_short) or pd.isna(latest_sma_long) or pd.isna(latest_rsi) or pd.isna(latest_adx):
                return None, "incomplete indicator calculation"

            # Scoring Logic
            score = 0.0; trend_score = 0.0
            if latest_sma_short > latest_sma_long: trend_score += 1.0
            elif latest_sma_short < latest_sma_long: trend_score -= 1.0
            is_trending = latest_adx > REC_ADX_THRESHOLD
            score += trend_score * (1.5 if is_trending else 0.5)
            if latest_rsi > REC_RSI_BUY: score += 1.0
            elif latest_rsi < REC_RSI_SELL: score -= 1.0

            # Determine recommendation string
            recommendation = "HOLD"
            if score >= 2.0: recommendation = "BUY"
            elif score >= 0.5: recommendation = "WEAK BUY"
            elif score <= -2.0: recommendation = "SELL"
            elif score <= -0.5: recommendation = "WEAK SELL"

            results = {
                'recommendation': recommendation, 'score': score, 'adx': latest_adx,
                'rsi': latest_rsi, 'sma_short': latest_sma_short, 'sma_long': latest_sma_long
            }
            return results, None

        except Exception as e:
            print(f"Error calculating TA indicators: {e}"); traceback.print_exc()
            return None, str(e)


    # --------------------------------------------------------------------------
    # Machine Learning Logic Methods
    # --------------------------------------------------------------------------

    def train_ml_model(self):
        """Validates parameters, then trains/evaluates/saves an ML model in the background."""
        custom_symbol = self.custom_symbol_entry.get().strip().upper()
        symbol_used = custom_symbol if custom_symbol else self.symbol_var.get()

        if self.current_data is None or self.current_data.empty:
            self.log_message("Error: No data loaded. Please load data first.", tag="negative"); return

        # Read + validate parameters on the main thread (Tk vars)
        try:
            horizon = int(self.ml_horizon_var.get()); selected_model_type = self.ml_model_type_var.get()
            test_size_pct = float(self.ml_test_split_var.get()); significance_pct = float(self.ml_threshold_var.get())
            if not (0 < test_size_pct < 100): raise ValueError("Test Size % must be between 0 and 100.")
            if significance_pct <= 0: raise ValueError("Significance Threshold % must be positive.")
            if horizon < 1 or horizon > 60: raise ValueError("Horizon must be between 1 and 60 days.")
        except ValueError as ve:
            self.log_message(f"Parameter Error: {ve}", tag="negative")
            print(f"ML Training Parameter Error: {ve}")
            return
        test_size = test_size_pct / 100.0; threshold = significance_pct / 100.0

        self.latest_feature_importances = None; self._update_feature_importance_button_state()
        self.log_message(f"\n--- Starting ML Training for {symbol_used} ---", clear_first=True)
        self.log_message(f"Model: {selected_model_type}, Type: classification, Horizon: {horizon}d, Test Size: {test_size_pct:.1f}%, Threshold: {threshold:.4f}")

        df_snapshot = self.current_data.copy()
        busy = (self.train_ml_button,) if hasattr(self, 'train_ml_button') else ()

        def train_worker():
            return self.ml_service.train_model(
                symbol=symbol_used, df=df_snapshot, model_type=selected_model_type,
                prediction_type='classification', prediction_horizon=horizon,
                test_size=test_size, target_threshold=threshold
            )

        def on_done(results):
            model_info = results.get('model_info', {}); metrics = results.get('metrics', {})
            self.log_message("\n--- Training Complete ---")
            self.log_message(f"Model saved: {os.path.basename(model_info.get('path','N/A'))}")
            self.log_message("\n--- Model Performance (Test Set) ---")
            self.log_message("\n".join([f"{k}: {v:.4f}" for k, v in metrics.items()]))

            self.latest_feature_importances = self.ml_service.get_loaded_feature_importances()
            self._update_feature_importance_button_state()
            if self.latest_feature_importances: self.log_message("Feature importances captured. Use 'Show Features' button.")
            else: self.log_message("Feature importances not available for this model type.")

            self.ml_model_loaded = True
            # Keep the ML LED solid ON after a successful train (run_in_background
            # turned it off when the worker finished)
            self.set_led_state("ML", "on", flicker=False)
            self.plot_data(self.current_data)

        def on_error(exc):
            self.log_message(f"Error training ML model: {type(exc).__name__} - {exc}", tag="negative")
            print("\n--- ML Training Error Traceback ---"); traceback.print_exception(exc); print("--- End Traceback ---\n")
            self.latest_feature_importances = None; self._update_feature_importance_button_state()

        self.run_in_background(train_worker, on_done=on_done, on_error=on_error,
                               busy_widgets=busy, led=("ML", True))


    # --------------------------------------------------------------------------
    # Backtesting Logic Methods
    # --------------------------------------------------------------------------

    def run_selected_backtest(self):
        """Runs the backtest using the selected strategy, data, and GUI parameters."""
        # --- (Implementation from previous context - app_py_ta_log_fix) ---
        selected_strategy_name = self.strategy_var.get()
        strategy_loader = STRATEGY_LOADERS.get(selected_strategy_name)
        custom_symbol = self.custom_symbol_entry.get().strip().upper()
        symbol_used = custom_symbol if custom_symbol else self.symbol_var.get()

        if strategy_loader is None:
            self.log_message(f"Error: Strategy loader not found for {selected_strategy_name}.", tag="negative"); return
        if self.current_data is None or self.current_data.empty:
            self.log_message(f"Error: No data loaded for {symbol_used} to run backtest.", tag="negative"); return

        # Collect parameters
        strategy_params = {}; default_params = {name: default for name, default in PARAM_CONFIG.get(selected_strategy_name, [])}
        param_log_list = []
        for param_name, param_var in self.param_entries.items():
            value = None; default_val = default_params.get(param_name)
            try:
                value_str = param_var.get()
                if isinstance(default_val, float): value = float(value_str)
                elif isinstance(default_val, int): value = int(value_str)
                else: value = value_str
            except (ValueError, TypeError):
                value = default_val; self.log_message(f"Warning: Invalid value for '{param_name}'. Using default '{value}'.")
            except Exception as e:
                value = default_val; self.log_message(f"Error processing param '{param_name}': {e}. Using default.")

            if param_name == 'trade_size_percent':
                try:
                    size_percent = float(value)
                    if 0 < size_percent <= 100: strategy_params[param_name] = size_percent / 100.0
                    else: raise ValueError("Percentage out of range")
                except (ValueError, TypeError):
                    default_fraction = DEFAULT_TRADE_SIZE_PERCENT / 100.0
                    strategy_params[param_name] = default_fraction
                    self.log_message(f"Warning: Invalid trade size % ({value}). Using default {default_fraction:.1%}")
            else: strategy_params[param_name] = value
            param_log_list.append(f"{param_name}={strategy_params.get(param_name, value)}")

        self.log_message(f"\n--- Running Backtest: {selected_strategy_name} on {symbol_used} ---", clear_first=True)
        self.log_message(f"Params: {', '.join(param_log_list)}")

        data_snapshot = self.current_data.copy()

        def backtest_worker():
            strategy_class = self._load_strategy_class(strategy_loader)
            return run_backtest(
                strategy_class=strategy_class, data=data_snapshot,
                cash=DEFAULT_CASH, commission=DEFAULT_COMMISSION, **strategy_params
            )

        def on_done(result):
            stats, _bt_results = result
            if stats is not None:
                self.log_message("--- Backtest Results ---"); self._log_backtest_stats(stats)
            else:
                self.log_message("Backtest failed to produce results.", tag="negative")

        def on_error(exc):
            if isinstance(exc, ImportError):
                self.log_message(f"ImportError: {exc}.", tag="negative")
            else:
                self.log_message(f"Backtesting Error: {type(exc).__name__} - {exc}", tag="negative")
                print("\n--- Backtesting Error Traceback ---"); traceback.print_exception(exc); print("--- End Traceback ---\n")

        self.run_in_background(backtest_worker, on_done=on_done, on_error=on_error,
                               busy_widgets=(self.run_backtest_button,), led=("CPU", True))


    def _load_strategy_class(self, strategy_loader):
        """Resolves a STRATEGY_LOADERS entry to a strategy class, importing and
        injecting optional modules (TA-Lib, Ephem) for string-path loaders."""
        if not isinstance(strategy_loader, str):
            return strategy_loader

        module_path, class_name = strategy_loader.rsplit('.', 1)
        needs_talib = any(s in strategy_loader for s in ["rsi_oscillator", "volatility_breakout", "macd_strategy", "bollinger_bands_strategy"])
        needs_ephem = "real_moon_strategy" in strategy_loader
        if (needs_talib and self.talib_module is None) or (needs_ephem and self.ephem_module is None):
            self._load_optional_modules()
        if needs_talib and self.talib_module is None: raise ImportError("TA-Lib is required but failed to load.")
        if needs_ephem and self.ephem_module is None: raise ImportError("Ephem is required but failed to load.")

        strategy_module = importlib.import_module(module_path)
        if needs_talib: setattr(strategy_module, 'talib', self.talib_module)
        if needs_ephem: setattr(strategy_module, 'ephem', self.ephem_module)
        strategy_class = getattr(strategy_module, class_name)

        if class_name == "RealMoonStrategy":
            if not OBSERVER_LAT or not OBSERVER_LON: raise ValueError("Observer Lat/Lon not set for RealMoonStrategy")
            strategy_class.OBSERVER_LAT = OBSERVER_LAT
            strategy_class.OBSERVER_LON = OBSERVER_LON
            strategy_class.OBSERVER_ELEV = OBSERVER_ELEV
        return strategy_class


    def _log_backtest_stats(self, stats: pd.Series):
        """Formats and logs backtesting statistics to the console."""
        # --- (Implementation from previous context - app_py_ta_log_fix) ---
        if stats is None or stats.empty: return
        self.output_textbox.configure(state="normal")
        try:
            stats_to_display = stats.drop(index=['_strategy', '_equity_curve', '_trades'], errors='ignore')
            max_key_len = max(len(str(idx)) for idx in stats_to_display.index) if not stats_to_display.empty else 25
            key_width = max(25, max_key_len)
            for idx, value in stats_to_display.items():
                tag = None; value_str = ""; line = ""; idx_str = str(idx)
                if isinstance(value, pd.Timedelta):
                    value_str = str(value).split('.')[0] if not pd.isna(value) else "NaT"
                    line = f"{idx_str:<{key_width}}: {value_str}\n"; tags_to_apply = ()
                else:
                    try:
                        is_numeric = isinstance(value, (int, float, np.number)); numeric_value = float(value) if is_numeric else 0
                        percent_keys = ["Return", "CAGR", "Alpha", "Volatility", "Drawdown", "Trade [%]", "Expectancy [%]", "Win Rate", "Exposure Time"]
                        is_percent = any(pk in idx_str for pk in percent_keys)
                        positive_good_keys = ["Return", "Equity Final", "Profit Factor", "Ratio", "Alpha", "CAGR", "Expectancy", "SQN", "Best Trade", "Avg. Trade", "Win Rate"]
                        is_positive_good = any(pgk in idx_str for pgk in positive_good_keys)
                        if is_numeric:
                            if "Drawdown" in idx_str or "Worst Trade" in idx_str: tag = "negative" if numeric_value < 0 else None
                            elif is_positive_good: tag = "positive" if numeric_value > 0 else ("negative" if numeric_value < 0 else None)
                            elif "Profit Factor" in idx_str: tag = "positive" if numeric_value > 1 else ("negative" if numeric_value < 1 else None)
                        if is_percent: value_str = f"{value:>{14}.2%}"
                        elif "Equity" in idx_str or "Commissions" in idx_str: value_str = f"{value:>{15},.2f}"
                        elif "Ratio" in idx_str or "Beta" in idx_str or "SQN" in idx_str or "Factor" in idx_str: value_str = f"{value:>{15}.2f}"
                        elif isinstance(value, pd.Timestamp): value_str = f"{value.strftime('%Y-%m-%d'):>15}"
                        elif isinstance(value, (int)): value_str = f"{value:>15,}"
                        elif isinstance(value, (float, np.number)): value_str = f"{value:>15.2f}"
                        else: value_str = f"{str(value):>15}"
                    except Exception as fmt_e: print(f"Fmt Err: {fmt_e}"); value_str = "[FMT_ERR]"
                    line = f"{idx_str:<{key_width}}: {value_str:>15}\n"; tags_to_apply = (tag,) if tag else ()
                self.output_textbox.insert("end", line, tags_to_apply)
            trades = stats.get('_trades')
            if trades is not None and not trades.empty:
                self.output_textbox.insert("end", "\n--- Trades --- \n")
                trades_display = trades[['Size', 'EntryTime', 'ExitTime', 'EntryPrice', 'ExitPrice', 'PnL', 'ReturnPct']].copy()
                trades_display.rename(columns={'EntryTime': 'Entry', 'ExitTime': 'Exit', 'ReturnPct': 'Return %'}, inplace=True)
                trades_display['PnL'] = trades_display['PnL'].map('{:,.2f}'.format); trades_display['Return %'] = trades_display['Return %'].map('{:.2%}'.format)
                trades_display['EntryPrice'] = trades_display['EntryPrice'].map('{:.2f}'.format); trades_display['ExitPrice'] = trades_display['ExitPrice'].map('{:.2f}'.format)
                trades_display['Entry'] = pd.to_datetime(trades_display['Entry']).dt.strftime('%Y-%m-%d'); trades_display['Exit'] = pd.to_datetime(trades_display['Exit']).dt.strftime('%Y-%m-%d')
                pd.set_option('display.width', 1000); trades_str = trades_display.to_string(index=False, justify='right'); self.output_textbox.insert("end", trades_str + "\n"); pd.reset_option('display.width')
            else: self.output_textbox.insert("end", "\n--- No Trades Executed --- \n")
        except Exception as log_e: print(f"Log Err: {log_e}"); self.output_textbox.insert("end", f"\nErr display stats: {log_e}\n")
        finally: self.output_textbox.configure(state="disabled"); self.output_textbox.see("end")


    # --------------------------------------------------------------------------
    # UI Update and Event Handler Methods
    # --------------------------------------------------------------------------

    def update_param_widgets(self, strategy_name: str):
        """Clears and repopulates the strategy parameter entry widgets."""
        # --- (Implementation from previous context - app_py_ta_log_fix) ---
        for widget in self.param_frame.winfo_children(): widget.destroy()
        self.param_entries.clear(); params = PARAM_CONFIG.get(strategy_name, [])
        if not params:
            ctk.CTkLabel(self.param_frame, text="No parameters for this strategy.", font=self.font_normal, text_color=COLOR_FOREGROUND).pack(anchor="w"); return
        for param_name, default_value in params:
            entry_frame = ctk.CTkFrame(self.param_frame, fg_color="transparent"); entry_frame.pack(side="left", padx=10, pady=2)
            ctk.CTkLabel(entry_frame, text=f"{param_name}:", font=self.font_normal, text_color=COLOR_FOREGROUND).pack(side="left", padx=(0, 5))
            param_var = ctk.StringVar(value=str(default_value))
            ctk.CTkEntry(entry_frame, textvariable=param_var, width=60, font=self.font_normal, text_color=COLOR_DROPDOWN_FG, fg_color=COLOR_DROPDOWN_BG, border_color=COLOR_BUTTON, border_width=1).pack(side="left")
            self.param_entries[param_name] = param_var


    def on_symbol_change(self, selected_symbol: str = None):
        """Handles symbol change from dropdown or custom entry."""
        # --- (Implementation from previous fix - app_py_ta_log_fix, removed reload check) ---
        custom_symbol = self.custom_symbol_entry.get().strip().upper()
        symbol_to_use = custom_symbol if custom_symbol else self.symbol_var.get()
        if custom_symbol and custom_symbol in SYMBOLS: self.symbol_var.set(custom_symbol)
        # Allow reloading same symbol
        self.current_symbol = symbol_to_use
        self.log_message(f"Symbol changed to: {self.current_symbol}. Click 'Load Data'.", clear_first=True)
        self.clear_display() # This now calls .clear() on matrix and restarts loop
        self.current_data = None; self.plotted_data = None; self.latest_price = None
        self.latest_ta_results = None; self.latest_recommendation = " "; self.latest_technical_score = 0.0; self.latest_adx = None # Init rec to blank
        self.ml_model_loaded = False; self.ml_prediction = None; self.latest_feature_importances = None
        self._update_feature_importance_button_state()
        self.set_led_state("CPU", "off"); self.set_led_state("ERR", "off"); self.set_led_state("ML", "off") # Turn ML off on symbol change
        self._highlight_chart_period_button("ALL")


    def _handle_chart_period_click(self, period: str, button_widget: ctk.CTkButton):
        """Calls update function and handles button highlighting."""
        # --- (Implementation from previous context - app_py_ta_log_fix) ---
        self.update_chart_lookback(period)
        self._highlight_chart_period_button(period, button_widget.master)


    def _highlight_chart_period_button(self, active_period: str, parent_frame=None):
         """Highlights the active chart period button."""
         # --- (Implementation from previous context - app_py_ta_log_fix) ---
         container = parent_frame or self.chart_controls_frame
         if not container or not hasattr(container, 'winfo_children'): return
         # Use the stored dictionary if available
         if hasattr(self, 'chart_period_buttons'):
             for period, button in self.chart_period_buttons.items():
                 if button and button.winfo_exists():
                     if period == active_period:
                         button.configure(fg_color=COLOR_ACCENT, text_color=COLOR_BACKGROUND)
                     else:
                         button.configure(fg_color=COLOR_SECONDARY_BUTTON, text_color=COLOR_FOREGROUND)
         else: # Fallback if dictionary wasn't created
             for widget in container.winfo_children():
                  if isinstance(widget, ctk.CTkButton) and hasattr(widget, 'cget'):
                       button_text = widget.cget("text")
                       if button_text == active_period: widget.configure(fg_color=COLOR_ACCENT, text_color=COLOR_BACKGROUND)
                       else: widget.configure(fg_color=COLOR_SECONDARY_BUTTON, text_color=COLOR_FOREGROUND)


    def update_chart_lookback(self, period: str):
        """Filters the currently loaded data and updates the chart view."""
        # --- (Implementation from previous context - app_py_ta_log_fix) ---
        if self.current_data is None or self.current_data.empty: self.log_message("No data loaded to filter."); return
        self.log_message(f"Updating chart view to: {period}"); filtered_data = None; now_dt = datetime.datetime.now()
        try:
            full_data = self.current_data; end_date = full_data.index.max()
            if period == "ALL": filtered_data = full_data
            elif period == "YTD": start_of_year = pd.Timestamp(year=now_dt.year, month=1, day=1); filtered_data = full_data[full_data.index >= start_of_year]
            else:
                offset_map = {"1Y": pd.Timedelta(days=365), "6M": pd.Timedelta(days=183), "3M": pd.Timedelta(days=91), "1M": pd.Timedelta(days=30)}
                offset = offset_map.get(period)
                if offset: start_date = end_date - offset; filtered_data = full_data[full_data.index >= start_date]
                else: self.log_message(f"Unknown period: {period}"); filtered_data = full_data
            if filtered_data is None or filtered_data.empty:
                self.log_message(f"No data available for period: {period}"); self.plot_data(None, title_suffix=f" (No data for {period})")
            else: self.plot_data(filtered_data, title_suffix=f" ({period})")
        except Exception as e:
            self.log_message(f"Error filtering data for period {period}: {e}", tag="negative"); traceback.print_exc(); self.plot_data(self.current_data)


    def on_chart_motion(self, event):
        """Handles mouse hover events on the chart to display price info."""
        # --- (Implementation from previous fix - app_py_plot_update_fix) ---
        if event.inaxes != self.ax or event.xdata is None or self.plotted_data is None or self.plotted_data.empty:
             if hasattr(self, 'chart_info_label'): self.chart_info_label.configure(text=""); return
        try:
            dt_naive = mdates.num2date(event.xdata).replace(tzinfo=None)
            nearest_index = self.plotted_data.index.get_indexer([dt_naive], method='nearest')[0]
            actual_date = self.plotted_data.index[nearest_index]
            row_data = self.plotted_data.iloc[nearest_index]
            open_price = row_data.get('open', float('nan')); high_price = row_data.get('high', float('nan'))
            low_price = row_data.get('low', float('nan')); close_price = row_data.get('close', float('nan'))
            volume = row_data.get('volume', 0)
            date_str = actual_date.strftime('%Y-%m-%d')
            info_text = f"Date: {date_str}, O: {open_price:.2f}, H: {high_price:.2f}, L: {low_price:.2f}, C: {close_price:.2f}, Vol: {volume:,.0f}"
            self.chart_info_label.configure(text=info_text)
        except Exception as e:
            if hasattr(self, 'chart_info_label'): self.chart_info_label.configure(text="")


    def show_strategy_info(self):
        """Displays strategy description in a popup window."""
        # --- (Implementation from previous context - app_py_ta_log_fix) ---
        selected_strategy_name = self.strategy_var.get()
        description = STRATEGY_DESCRIPTIONS.get(selected_strategy_name, "No description available.")
        info_window = ctk.CTkToplevel(self); info_window.title(f"{selected_strategy_name} - Info"); info_window.geometry("450x350")
        info_window.configure(fg_color=COLOR_BACKGROUND); info_window.transient(self); info_window.grab_set()
        info_frame = ctk.CTkFrame(info_window, fg_color="transparent"); info_frame.pack(padx=15, pady=15, fill="both", expand=True)
        ctk.CTkLabel(info_frame, text=selected_strategy_name, font=self.font_large, text_color=COLOR_FOREGROUND).pack(pady=(0, 10))
        desc_textbox = ctk.CTkTextbox(info_frame, font=self.font_normal, text_color=COLOR_TEXTBOX_FG, fg_color=COLOR_TEXTBOX_BG, border_width=1, border_color=COLOR_BUTTON, wrap="word")
        desc_textbox.pack(fill="both", expand=True); desc_textbox.insert("1.0", description); desc_textbox.configure(state="disabled")
        ctk.CTkButton(info_frame, text="Close", command=info_window.destroy, font=self.font_button, text_color=COLOR_BACKGROUND, fg_color=COLOR_BUTTON, hover_color=COLOR_BUTTON_HOVER).pack(pady=(10, 0))


    def show_feature_importance_popup(self):
        """Displays feature importances in a popup window with a chart."""
        # --- MODIFIED: Remove redundant get_loaded_feature_importances call ---
        print("DEBUG: show_feature_importance_popup called") # Debug print
        if not self.ml_model_loaded or self.ml_service is None:
            self.log_message("No ML model loaded. Train or load a model first.", tag="negative")
            return

        # Rely on the state variable set during training/loading
        # self.latest_feature_importances = self.ml_service.get_loaded_feature_importances() # REMOVED

        print(f"DEBUG: Importance data available: {bool(self.latest_feature_importances)}") # Debug print
        if not self.latest_feature_importances:
            self.log_message("Feature importance data not available for the loaded model.", tag="negative")
            # Optionally try fetching again as a fallback?
            # self.latest_feature_importances = self.ml_service.get_loaded_feature_importances()
            # if not self.latest_feature_importances:
            #      return # Still nothing, exit
            return # Exit if not available

        if not isinstance(self.latest_feature_importances, dict) or not self.latest_feature_importances:
             self.log_message("Feature importance data is invalid.", tag="negative")
             return

        try:
             sorted_features = sorted(
                 self.latest_feature_importances.items(),
                 key=lambda item: abs(item[1]), reverse=True
             )
        except Exception as e:
             self.log_message(f"Error sorting feature importances: {e}", tag="negative")
             return

        top_n = 20; top_features = sorted_features[:top_n]; feature_names = [item[0] for item in top_features]; importance_scores = [abs(item[1]) for item in top_features] # Use absolute for plotting magnitude
        metadata = self.ml_service.get_loaded_model_metadata(); symbol = metadata.get('symbol', self.current_symbol) if metadata else self.current_symbol
        model_name = metadata.get('model_class_name', 'Unknown Model') if metadata else 'Unknown Model'
        popup = ctk.CTkToplevel(self); popup.geometry("700x650"); popup.title(f"Feature Importance - {symbol} ({model_name})")
        popup.configure(fg_color=COLOR_BACKGROUND); popup.transient(self); popup.grab_set()
        popup.grid_columnconfigure(0, weight=1); popup.grid_rowconfigure(0, weight=0); popup.grid_rowconfigure(1, weight=1); popup.grid_rowconfigure(2, weight=0)
        info_frame = ctk.CTkFrame(popup, fg_color="transparent"); info_frame.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="ew")
        ctk.CTkLabel(info_frame, text="Feature Importance indicates relative contribution. Chart shows top features by absolute score.", font=self.font_normal, text_color=COLOR_FOREGROUND, wraplength=650, justify="left").pack(anchor="w")
        chart_frame = ctk.CTkFrame(popup, fg_color=COLOR_CHART_BG); chart_frame.grid(row=1, column=0, padx=15, pady=5, sticky="nsew")
        chart_frame.grid_rowconfigure(0, weight=1); chart_frame.grid_columnconfigure(0, weight=1)
        # Use a plain Figure (not plt.subplots) so pyplot never tracks it -- popup
        # figures were previously never closed and leaked
        fig_feat = Figure(figsize=(6, 5)); ax_feat = fig_feat.add_subplot(111)
        fig_feat.set_facecolor(COLOR_CHART_BG); ax_feat.set_facecolor(COLOR_CHART_BG)
        y_pos = np.arange(len(feature_names)); ax_feat.barh(y_pos, importance_scores[::-1], align='center', color=COLOR_ACCENT)
        ax_feat.set_yticks(y_pos); ax_feat.set_yticklabels(feature_names[::-1]); ax_feat.invert_yaxis()
        ax_feat.set_xlabel('Importance Score (Absolute)', color=COLOR_CHART_AXES); ax_feat.set_title('Top Feature Importances', color=COLOR_CHART_AXES)
        ax_feat.tick_params(axis='x', colors=COLOR_CHART_AXES); ax_feat.tick_params(axis='y', colors=COLOR_CHART_AXES)
        for spine in ax_feat.spines.values(): spine.set_color(COLOR_CHART_AXES)
        ax_feat.grid(axis='x', color=COLOR_DROPDOWN_BG, linestyle='--', linewidth=0.5); fig_feat.tight_layout()
        canvas_feat = FigureCanvasTkAgg(fig_feat, master=chart_frame); canvas_feat_widget = canvas_feat.get_tk_widget()
        canvas_feat_widget.pack(fill="both", expand=True, padx=5, pady=5); canvas_feat.draw()
        ctk.CTkButton(popup, text="Close", command=popup.destroy, font=self.font_button, text_color=COLOR_BACKGROUND, fg_color=COLOR_BUTTON, hover_color=COLOR_BUTTON_HOVER).grid(row=2, column=0, pady=(5, 15))


    def show_easter_egg(self, event=None):
        """Displays the easter egg art."""
        # --- (Implementation from previous context - app_py_ta_log_fix) ---
        print("DEBUG: show_easter_egg triggered"); egg_window = ctk.CTkToplevel(self); egg_window.title("WOW"); egg_window.geometry("600x400")
        egg_window.configure(fg_color=COLOR_BACKGROUND); egg_window.transient(self); egg_window.grab_set()
        egg_frame = ctk.CTkFrame(egg_window, fg_color="transparent"); egg_frame.pack(padx=10, pady=10, fill="both", expand=True)
        art_textbox = ctk.CTkTextbox(egg_frame, font=self.font_normal, text_color=COLOR_ACCENT, fg_color=COLOR_TEXTBOX_BG, border_width=1, border_color=COLOR_BUTTON, wrap="none")
        art_textbox.pack(fill="both", expand=True, padx=5, pady=5); art_textbox.insert("1.0", EASTER_EGG_ART); art_textbox.configure(state="disabled")
        ctk.CTkButton(egg_frame, text="Much Close", command=egg_window.destroy, font=self.font_button, text_color=COLOR_BACKGROUND, fg_color=COLOR_BUTTON, hover_color=COLOR_BUTTON_HOVER).pack(pady=(10, 0))


    # --------------------------------------------------------------------------
    # Utility and Helper Methods
    # --------------------------------------------------------------------------

    def log_message(self, message: str, clear_first: bool = False, tag: str | None = None):
        """Logs a message to the output textbox, optionally clearing first."""
        # --- (Implementation from previous context - app_py_ta_log_fix) ---
        is_error_warning = "error" in message.lower() or "warning" in message.lower() or "failed" in message.lower()
        if is_error_warning and "ML Prediction Error:" not in message:
            self.set_led_state("ERR", "on", flicker=True)
            if self.winfo_exists():
                self.after(1500, lambda name="ERR": self.set_led_state(name, "off"))
        if hasattr(self, 'output_textbox') and self.output_textbox.winfo_exists():
            try:
                self.output_textbox.configure(state="normal")
                if clear_first: self.output_textbox.delete("1.0", "end")
                tags_to_apply = (tag,) if tag else (); self.output_textbox.insert("end", f"{message}\n", tags_to_apply)
                self.output_textbox.see("end"); self.output_textbox.configure(state="disabled")
            except tk.TclError as e: print(f"Error updating output_textbox: {e}")
        else: print(f"Log message skipped, output_textbox not available: {message}")


    def set_led_state(self, name: str, state: str, flicker: bool | None = None):
        """Sets the state ('on'/'off') and flicker status of a specific LED."""
        # --- (Implementation from previous context - app_py_ta_log_fix) ---
        name_upper = name.upper()
        if name_upper in self.leds:
            led_widget = self.leds[name_upper]
            if led_widget and led_widget.winfo_exists(): # Check if widget exists
                led_widget.set_state(state)
                should_flicker = (state == "on") if flicker is None else (flicker and state == "on")
                led_widget.enable_flicker(should_flicker)


    def _update_activity_leds(self):
        """Randomly flickers DATA and COM LEDs."""
        # --- (Implementation from previous context - app_py_ta_log_fix) ---
        if not self.winfo_exists(): return
        # Check if LED exists before getting state
        data_led = self.leds.get("DATA")
        if data_led and data_led.winfo_exists() and random.random() < 0.2: # Check exists
             self.set_led_state("DATA", "off" if data_led.get_state() == "on" else "on")
        com_led = self.leds.get("COM")
        if com_led and com_led.winfo_exists() and random.random() < 0.15: # Check exists
             self.set_led_state("COM", "off" if com_led.get_state() == "on" else "on")

        delay = random.randint(150, 550)
        if self.winfo_exists(): self.activity_led_job = self.after(delay, self._update_activity_leds)
        else: self.activity_led_job = None


    def _update_matrix_display(self, force_update=False):
        """Updates the dot matrix display, optionally forcing immediate redraw."""
        # Add debug print
        # print(f"MATRIX DEBUG: _update_matrix_display called. force={force_update}, job={self.matrix_update_job}, rec='{self.latest_recommendation}'")
        if not self.winfo_exists(): return

        # Cancel existing loop only if forcing update
        if force_update and self.matrix_update_job:
             try:
                 self.after_cancel(self.matrix_update_job)
                 # print("MATRIX DEBUG: Loop cancelled by force_update") # Debug
             except tk.TclError: pass
             self.matrix_update_job = None # Ensure job ID is cleared

        # Use the state variable that is initialized in __init__
        display_text = self.latest_recommendation # This holds TA or Hybrid result
        rec_key = display_text.strip().upper()
        # --- Use HEX COLOR map ---
        hex_color = RECOMMENDATION_HEX_COLORS.get(rec_key, RECOMMENDATION_HEX_COLORS['HOLD'])

        # Determine if showing price or recommendation
        should_show_price = False
        if not force_update:
             # Toggle only if not forced
             self.matrix_shows_price = not self.matrix_shows_price
             should_show_price = self.matrix_shows_price
             # print(f"MATRIX DEBUG: Toggled matrix_shows_price to {self.matrix_shows_price}") # Debug

        # Prepare display text
        if should_show_price and self.latest_price is not None:
             price_str = f"{self.latest_price:.2f}"
             display_text_final = price_str.rjust(MATRIX_COLS)
             hex_color = RECOMMENDATION_HEX_COLORS['DEFAULT'] # Price uses default color
             # print(f"MATRIX DEBUG: Displaying Price: '{display_text_final}'") # Debug
        else:
             # Use recommendation text (already in display_text)
             display_text_final = display_text.center(MATRIX_COLS)
             # print(f"MATRIX DEBUG: Displaying Rec: '{display_text_final}' Color: {hex_color}") # Debug
             # hex_color is already set based on recommendation

        # Update the display widget
        if hasattr(self, 'recommendation_display') and self.recommendation_display.get_frame().winfo_exists():
            display_text_final = display_text_final[:MATRIX_COLS] # Truncate
            # Pass HEX color code
            self.recommendation_display.display_text(display_text_final, color=hex_color)

        # --- MODIFIED: Always reschedule loop if not forced update ---
        if not force_update:
             delay = 3500
             if self.winfo_exists():
                  # print(f"MATRIX DEBUG: Scheduling next matrix update in {delay}ms...") # Debug
                  # Clear previous job ID before setting new one to prevent duplicates if called rapidly
                  if self.matrix_update_job:
                       try: self.after_cancel(self.matrix_update_job)
                       except tk.TclError: pass
                  self.matrix_update_job = self.after(delay, self._update_matrix_display)
             # else: print("MATRIX DEBUG: Window closed, not rescheduling matrix.") # Debug


    def _start_matrix_loop_if_needed(self):
        """Starts the matrix update loop if it's not already scheduled."""
        # Add debug print
        # print(f"MATRIX DEBUG: _start_matrix_loop_if_needed called. matrix_update_job={self.matrix_update_job}")
        # Check if window exists before scheduling
        if self.matrix_update_job is None and self.winfo_exists():
            # print("MATRIX DEBUG: Restarting matrix update loop...") # Debug
            # Schedule the *next* update, which will then continue the loop
            delay = 3500 # Standard delay
            self.matrix_update_job = self.after(delay, self._update_matrix_display)
        # elif self.matrix_update_job is not None:
            # print("MATRIX DEBUG: Loop already running, not restarting.") # Debug


    def _update_feature_importance_button_state(self):
        """Enables or disables the feature importance button."""
        # --- (Implementation from previous context - app_py_ta_log_fix) ---
        if hasattr(self, 'show_features_button') and self.show_features_button.winfo_exists():
            state = "normal" if self.ml_model_loaded and self.latest_feature_importances else "disabled"
            try: self.show_features_button.configure(state=state)
            except tk.TclError as e: print(f"Error updating feature button state: {e}")


    def _get_feature_explanation(self, feature_name: str) -> str:
        """Provides a simple explanation for common feature name patterns."""
        # --- (Implementation from previous context - app_py_ta_log_fix) ---
        name = feature_name.lower()
        if name.startswith("return_"): return f"{name.split('_')[-1]} return %"
        if name.startswith("log_return"): return "Logarithmic return"
        if name.startswith("sma_"): return f"{name.split('_')[-1]}-period Simple Moving Avg"
        if name.startswith("ema_"): return f"{name.split('_')[-1]}-period Exponential Moving Avg"
        if name == "hl_range": return "High-Low Range %"; # ... (add rest of explanations) ...
        if name == "oc_range": return "Open-Close Range %"
        if name == "log_volume": return "Log of Volume"
        if name == "volume_change": return "Volume % Change"
        if name == "relative_volume": return "Volume vs Rolling Avg"
        if name == "bb_upper": return "Bollinger Band Upper"
        if name == "bb_lower": return "Bollinger Band Lower"
        if name == "bb_width": return "Bollinger Band Width %"
        if name == "bb_pos": return "Position within Bollinger Bands (0-1)"
        if name.startswith("rsi_"): return f"{name.split('_')[-1]}-period RSI"
        if name == "macd": return "MACD Line"
        if name == "macd_signal": return "MACD Signal Line"
        if name == "macd_hist": return "MACD Histogram"
        if name == "day_of_week": return "Day of Week (0=Mon)"
        if name == "day_of_month": return "Day of Month"
        if name == "month": return "Month of Year"
        if name == "year": return "Year"
        if name == "quarter": return "Quarter"
        if name.startswith("is_month_"): return f"Is {name.split('_')[-1]} of Month? (1=Yes)"
        if name.startswith("is_quarter_"): return f"Is {name.split('_')[-1]} of Quarter? (1=Yes)"
        if name.startswith("is_year_"): return f"Is {name.split('_')[-1]} of Year? (1=Yes)"
        return feature_name


    # --------------------------------------------------------------------------
    # Application Exit Method
    # --------------------------------------------------------------------------

    def activate_kill_switch(self):
        """Emergency stop: halt auto-trader and optionally liquidate positions."""
        if not self.auto_trader_tab or not self.auto_trader_tab.auto_trader:
            return
        if not self.auto_trader_tab.auto_trader.is_running:
            return

        # Confirmation dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("KILL SWITCH")
        dialog.geometry("400x150")
        dialog.configure(fg_color=COLOR_BACKGROUND)
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Stop all trading and liquidate positions?",
                     font=self.font_button, text_color=COLOR_FOREGROUND).pack(pady=(20, 15))

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack()

        def stop_and_liquidate():
            dialog.destroy()
            self.auto_trader_tab.stop_trading(liquidate=True)
            self.recommendation_display.display_text("EMERGENCY STOP", color=COLOR_KILL_SWITCH)
            self.log_message("KILL SWITCH: Trading stopped, positions liquidated.", tag="negative")

        def stop_only():
            dialog.destroy()
            self.auto_trader_tab.stop_trading(liquidate=False)
            self.log_message("KILL SWITCH: Trading stopped, positions kept.", tag="negative")

        ctk.CTkButton(btn_frame, text="Stop & Liquidate", command=stop_and_liquidate,
                      font=self.font_button, text_color="#FFFFFF",
                      fg_color=COLOR_KILL_SWITCH, hover_color=COLOR_KILL_SWITCH_HOVER,
                      width=140).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Stop Only", command=stop_only,
                      font=self.font_button, text_color=COLOR_BACKGROUND,
                      fg_color=COLOR_BUTTON, hover_color=COLOR_BUTTON_HOVER,
                      width=100).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Cancel", command=dialog.destroy,
                      font=self.font_button, text_color=COLOR_FOREGROUND,
                      fg_color=COLOR_DROPDOWN_BG, hover_color=COLOR_BACKGROUND,
                      width=80).pack(side="left", padx=5)

    def on_closing(self):
        """Handles graceful shutdown procedures."""
        print("Closing application gracefully...")
        # Interrupt any fetcher retry sleeps on worker threads
        self._shutdown_event.set()
        # Stop auto-trader if running
        if self.auto_trader_tab and self.auto_trader_tab.auto_trader and self.auto_trader_tab.auto_trader.is_running:
            print("Stopping auto-trader...")
            self.auto_trader_tab.auto_trader.stop(liquidate=False)
        # Stop background loops
        if self.activity_led_job:
            try: self.after_cancel(self.activity_led_job)
            except tk.TclError: pass
            # --- CORRECTED SYNTAX ---
            self.activity_led_job = None
        if self.matrix_update_job:
            try: self.after_cancel(self.matrix_update_job)
            except tk.TclError: pass
            # --- CORRECTED SYNTAX ---
            self.matrix_update_job = None

        # Stop individual LED flickers
        for led_widget in self.leds.values():
            # Check widget exists before calling methods
            if led_widget and led_widget.winfo_exists():
                led_widget.enable_flicker(False) # This also cancels internal job

        # Close Matplotlib figure
        try:
            # Check if fig exists before trying to close
            if hasattr(self, 'fig') and self.fig is not None:
                plt.close(self.fig)
                print("Matplotlib figure closed.")
                self.fig = None # Clear reference
        except Exception as e:
            print(f"Error closing matplotlib figure: {e}")

        # Allow UI to update before destroying
        self.update_idletasks()
        print("Destroying application window...")
        self.destroy()
        print("Application window destroyed.")
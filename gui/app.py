# gui/app.py
# Main application window class - USING WornLED widgets & DotMatrix display
# Added random flashing for DATA/COM LEDs
# Added alternating Matrix display (Price/Rec) with color coding
# Moved Matrix Display to top center (Row 2)
# Changed initial matrix display to blank

import customtkinter as ctk
from tkinter import font as tkfont, ttk
import tkinter as tk # For TclError handling
from config import (SYMBOLS, DEFAULT_DATA_PERIOD, DEFAULT_DATA_INTERVAL,
                   DEFAULT_CASH, DEFAULT_COMMISSION, DEFAULT_TRADE_SIZE_PERCENT,
                   # Recommendation Params
                   REC_SMA_SHORT, REC_SMA_LONG, REC_RSI_PERIOD, REC_RSI_BUY, REC_RSI_SELL,
                   REC_MACD_FAST, REC_MACD_SLOW, REC_MACD_SIG,
                   REC_BBANDS_PERIOD, REC_BBANDS_STDDEV,
                   REC_ADX_PERIOD, REC_ADX_THRESHOLD,
                   # Observer Location
                   OBSERVER_LAT, OBSERVER_LON, OBSERVER_ELEV,
                   # Colors - Import main background color
                   COLOR_BACKGROUND, COLOR_FOREGROUND, COLOR_BUTTON, COLOR_BUTTON_HOVER,
                   COLOR_DROPDOWN_FG, COLOR_DROPDOWN_BG, COLOR_DROPDOWN_BUTTON, COLOR_DROPDOWN_BUTTON_HOVER,
                   COLOR_TEXTBOX_FG, COLOR_TEXTBOX_BG, FONT_FAMILY_MONO, FONT_SIZE_NORMAL, FONT_SIZE_LARGE,
                   FONT_SIZE_TEXTBOX, FONT_SIZE_LED, # FONT_SIZE_RECOMMENDATION removed
                   COLOR_CHART_BG, COLOR_CHART_LINE, COLOR_CHART_AXES, COLOR_ACCENT,
                   COLOR_POSITIVE, COLOR_NEGATIVE, COLOR_NEUTRAL, COLOR_WEAK_POSITIVE, COLOR_WEAK_NEGATIVE,
                   COLOR_SECONDARY_BUTTON, COLOR_SECONDARY_BUTTON_HOVER,
                   # LED Colors (Using ON colors for WornLED)
                   COLOR_LED_PWR_ON, COLOR_LED_CPU_ON, COLOR_LED_DATA_ON, COLOR_LED_COM_ON,
                   # Recommendation Colors
                   COLOR_REC_SELL, COLOR_REC_WEAK_SELL, COLOR_REC_HOLD,
                   COLOR_REC_WEAK_BUY, COLOR_REC_BUY, COLOR_REC_DEFAULT
                   )
from data.data_fetcher import DataFetcher
# --- Import the indicator widgets ---
from gui.widgets.vintage_indicators import WornLED
from gui.widgets.dot_matrix import MatrixText # Import the new MatrixText

import pandas as pd
import importlib
import datetime
import random
import traceback

# Matplotlib imports
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates

# Backtesting imports
from trading.backtester import run_backtest
# --- Strategy Imports ---
from trading.strategies.sma_cross import SmaCross
from trading.strategies.fake_moon_strategy import FakeMoonStrategy
from trading.strategies.ichimoku_strategy import IchimokuStrategy
from trading.strategies.donchian_channel_strategy import DonchianChannelStrategy
from trading.strategies.day_of_week_strategy import DayOfWeekStrategy

# Define strategies, using strings for classes that need dynamic loading
STRATEGY_LOADERS = { # (Remains the same)
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

# --- Strategy Parameter Definitions ---
PARAM_CONFIG = { # (Remains the same)
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
for params in PARAM_CONFIG.values():
     params.insert(0, ("trade_size_percent", DEFAULT_TRADE_SIZE_PERCENT))

# --- Strategy Descriptions ---
STRATEGY_DESCRIPTIONS = { # (Remains the same)
    "SMA Crossover": "Simple Moving Average Crossover.\nBuys when a short-term SMA (e.g., 10-day) crosses above a long-term SMA (e.g., 30-day).\nSells (closes long) when the short SMA crosses below the long SMA.\nA basic trend-following strategy.",
    "Ichimoku Cloud": "Ichimoku Kinko Hyo.\nA comprehensive trend-following indicator.\nExample Logic: Buys when Price > Kumo Cloud, Tenkan > Kijun, Price > Price 26 periods ago.\nSells on reverse conditions.\n(Calculated using pandas).",
    "Donchian Channel": "Donchian Channel Breakout.\nBuys when price closes above the highest high of the last N periods (e.g., 20).\nSells (closes long) when price closes below the lowest low of the last M periods (e.g., 20).\nA pure price-action trend-following strategy.",
    "Day of Week Effect": "Calendar-Based Strategy.\nTests simple market timing hypotheses.\nExample Logic: Buys at the close of the specified 'buy day' (e.g., Monday=0) and sells at the close of the 'sell day' (e.g., Friday=4).",
    "Fake Moon (Day of Month)": "Placeholder Lunar Strategy.\nTrades based on the day of the month as a proxy for moon phases.\nExample: Buys early in the month (days 1-5), sells mid-month (days 14-18).\n(Disclaimer: No proven financial basis).",
    "RSI Oscillator": "Relative Strength Index Oscillator.\nA mean-reversion strategy.\nBuys when RSI crosses below an oversold threshold (e.g., 30).\nSells (closes long) when RSI crosses above an overbought threshold (e.g., 70).\n(Requires TA-Lib).",
    "Volatility Breakout": "Volatility Breakout using ATR.\nBuys when price closes significantly above a moving average, based on Average True Range (ATR).\nSells (closes long) when price closes below the moving average.\nAttempts to capture strong directional moves.\n(Requires TA-Lib).",
    "MACD": "Moving Average Convergence Divergence.\nA trend-following momentum indicator.\nBuys when the MACD line crosses above the Signal line.\nSells (closes long) when the MACD line crosses below the Signal line.\n(Requires TA-Lib).",
    "Bollinger Bands": "Bollinger Bands Mean Reversion.\nBuys when price touches or crosses below the lower band.\nSells (closes long) when price touches or crosses above the upper band.\nAssumes price will revert to the mean (middle band).\n(Requires TA-Lib).",
    "Real Moon (Ephem)": "Lunar Cycle Strategy (Astronomical).\nTrades based on calculated moon phases using the 'ephem' library.\nUses observer location from config.py.\nExample: Buys a few days after the New Moon, Sells a few days after the Full Moon.\n(Requires Ephem library).",
}

# Define EASTER_EGG_ART constant
EASTER_EGG_ART = """
       wow                            such profit
             _______________________                     much gain
            /\\                     /\\                   /
           /  \\ TO THE MOON!      /  \\                 /
          /____\\_________________/    \\    ▀█▀ █▀█ ▄▀█ █▄░█ █▄▀
          \\    / _______________ \\    /    ░█░ █▀▄ █▀█ █░▀█ █░█
   HODL    \\  / /             \\ \\  /
            \\/ /   O      O    \\ \\/    stonks
             \\/    -------     \\/             very retro
              \\      ∪       /          /
               \\___________ /          /
                   ||   ||           /
                   ||   ||__________/
                   ^^   ^^
"""

# --- Constants for Dot Matrix Display ---
MATRIX_COLS = 12
MATRIX_CHAR_WIDTH = 5
MATRIX_SPACING = 1
MATRIX_TOTAL_COLS = MATRIX_COLS * (MATRIX_CHAR_WIDTH + MATRIX_SPACING)
MATRIX_ROWS = 7
MATRIX_PIXEL_SIZE = 6
MATRIX_BG = "#050505"

class App(ctk.CTk):
    """ Main application window """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.talib_module = None
        self.ephem_module = None
        self.plotted_data = None
        self.current_symbol = ""
        self.param_entries = {}
        self.activity_led_job = None
        self.matrix_update_job = None
        self.matrix_shows_price = False
        self.latest_recommendation = " " * MATRIX_COLS # Initialize with spaces
        self.latest_price = None

        self.title("Retro Trading Console")
        self.geometry("1100x850")
        self.configure(fg_color=COLOR_BACKGROUND)
        self.grid_columnconfigure(0, weight=3); self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0); self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0); self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=0); self.grid_rowconfigure(5, weight=0)
        self.grid_rowconfigure(6, weight=0); self.grid_rowconfigure(7, weight=0)

        available_fonts = list(tkfont.families())
        if FONT_FAMILY_MONO not in available_fonts: self.mono_font_family = "Courier"
        else: self.mono_font_family = FONT_FAMILY_MONO
        self.font_normal = ctk.CTkFont(family=self.mono_font_family, size=FONT_SIZE_NORMAL)
        self.font_large = ctk.CTkFont(family=self.mono_font_family, size=FONT_SIZE_LARGE)
        self.font_button = ctk.CTkFont(family=self.mono_font_family, size=FONT_SIZE_NORMAL, weight="bold")
        self.font_textbox = ctk.CTkFont(family=self.mono_font_family, size=FONT_SIZE_TEXTBOX)
        self.font_led = ctk.CTkFont(family=self.mono_font_family, size=FONT_SIZE_LED)

        self.data_fetcher = DataFetcher()
        self.current_data = None

        # --- Header / Data Controls Frame (Row 0) ---
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 5), sticky="ew")
        self.symbol_label = ctk.CTkLabel(self.controls_frame, text="Symbol:", font=self.font_normal, text_color=COLOR_FOREGROUND); self.symbol_label.pack(side="left", padx=(0, 10))
        self.symbol_var = ctk.StringVar(value=SYMBOLS[0])
        self.symbol_dropdown = ctk.CTkComboBox( self.controls_frame, values=SYMBOLS, variable=self.symbol_var, font=self.font_normal, text_color=COLOR_DROPDOWN_FG, fg_color=COLOR_DROPDOWN_BG, dropdown_fg_color=COLOR_DROPDOWN_BG, button_color=COLOR_DROPDOWN_BUTTON, button_hover_color=COLOR_DROPDOWN_BUTTON_HOVER, border_color=COLOR_BUTTON, border_width=1, command=self.on_symbol_change ); self.symbol_dropdown.pack(side="left", padx=(0, 10))
        self.custom_symbol_label = ctk.CTkLabel(self.controls_frame, text="Custom:", font=self.font_normal, text_color=COLOR_FOREGROUND); self.custom_symbol_label.pack(side="left", padx=(10, 5))
        self.custom_symbol_entry = ctk.CTkEntry( self.controls_frame, width=70, font=self.font_normal, text_color=COLOR_DROPDOWN_FG, fg_color=COLOR_DROPDOWN_BG, border_color=COLOR_BUTTON, border_width=1 ); self.custom_symbol_entry.pack(side="left", padx=(0, 20))
        self.fetch_button = ctk.CTkButton( self.controls_frame, text="Load Data", command=self.fetch_and_display_data, font=self.font_button, text_color=COLOR_BACKGROUND, fg_color=COLOR_BUTTON, hover_color=COLOR_BUTTON_HOVER ); self.fetch_button.pack(side="left", padx=(0, 30))

        # --- Chart Controls Frame (Row 1) ---
        self.chart_controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.chart_controls_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 5), sticky="ew")
        self.chart_period_label = ctk.CTkLabel(self.chart_controls_frame, text="Chart Period:", font=self.font_normal, text_color=COLOR_FOREGROUND); self.chart_period_label.pack(side="left", padx=(0, 10))
        lookback_periods = ["ALL", "YTD", "1Y", "6M", "3M", "1M"]
        for period in lookback_periods:
            btn = ctk.CTkButton( self.chart_controls_frame, text=period, command=lambda p=period: self.update_chart_lookback(p), font=self.font_normal, width=40, height=24, text_color=COLOR_FOREGROUND, fg_color=COLOR_SECONDARY_BUTTON, hover_color=COLOR_SECONDARY_BUTTON_HOVER ); btn.pack(side="left", padx=(0, 5))

        # --- Dot Matrix Recommendation Display (Row 2) ---
        self.recommendation_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.recommendation_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=(10, 10), sticky="")
        self.recommendation_display = MatrixText(self.recommendation_frame, rows=MATRIX_ROWS, cols=MATRIX_TOTAL_COLS, pixel_size=MATRIX_PIXEL_SIZE, char_spacing=MATRIX_SPACING, bg_color=MATRIX_BG)
        self.recommendation_display.get_frame().pack()
        # --- Initialize with blank spaces ---
        self.recommendation_display.display_text(" " * MATRIX_COLS)

        # --- Chart Area (Row 3) ---
        self.chart_frame = ctk.CTkFrame(self, fg_color=COLOR_CHART_BG, border_color=COLOR_BUTTON, border_width=1)
        self.chart_frame.grid(row=3, column=0, columnspan=1, padx=(20, 10), pady=5, sticky="nsew")
        self.chart_frame.grid_rowconfigure(0, weight=1); self.chart_frame.grid_columnconfigure(0, weight=1)
        self.fig, self.ax = plt.subplots(); self.fig.set_facecolor(COLOR_CHART_BG); self.ax.set_facecolor(COLOR_CHART_BG)
        self.ax.tick_params(axis='x', colors=COLOR_CHART_AXES); self.ax.tick_params(axis='y', colors=COLOR_CHART_AXES)
        self.ax.yaxis.label.set_color(COLOR_CHART_AXES); self.ax.xaxis.label.set_color(COLOR_CHART_AXES); self.ax.title.set_color(COLOR_CHART_AXES)
        self.ax.spines['bottom'].set_color(COLOR_CHART_AXES); self.ax.spines['top'].set_color(COLOR_CHART_AXES); self.ax.spines['right'].set_color(COLOR_CHART_AXES); self.ax.spines['left'].set_color(COLOR_CHART_AXES)
        self.ax.text(0.5, 0.5, 'Select symbol and click Load Data', horizontalalignment='center', verticalalignment='center', transform=self.ax.transAxes, color=COLOR_CHART_AXES, fontsize=self.font_large.cget('size'))
        self.chart_canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.chart_canvas_widget = self.chart_canvas.get_tk_widget(); self.chart_canvas_widget.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.chart_canvas.draw(); self.chart_canvas.mpl_connect('motion_notify_event', self.on_chart_motion)

        # --- Display Area (Console Output) (Row 3) ---
        self.output_textbox = ctk.CTkTextbox( self, font=self.font_textbox, text_color=COLOR_TEXTBOX_FG, fg_color=COLOR_TEXTBOX_BG, border_color=COLOR_BUTTON, border_width=1, activate_scrollbars=True )
        self.output_textbox.grid(row=3, column=1, columnspan=1, padx=(10, 20), pady=5, sticky="nsew")
        self.output_textbox.insert("end", "Retro Trading Console Initialized.\nSelect symbol, load data, then select and run a backtest.\n"); self.output_textbox.tag_config("positive", foreground=COLOR_POSITIVE); self.output_textbox.tag_config("negative", foreground=COLOR_NEGATIVE); self.output_textbox.configure(state="disabled")

        # --- Chart Info Label (Row 4) ---
        self.chart_info_label = ctk.CTkLabel(self, text="", font=self.font_normal, text_color=COLOR_FOREGROUND, anchor="w");
        self.chart_info_label.grid(row=4, column=0, columnspan=2, padx=20, pady=(0, 5), sticky="ew")

        # --- Backtesting Controls Frame (Row 5) ---
        self.backtest_controls_frame = ctk.CTkFrame(self, fg_color="transparent");
        self.backtest_controls_frame.grid(row=5, column=0, columnspan=2, padx=20, pady=(0, 5), sticky="ew")
        self.strategy_label = ctk.CTkLabel(self.backtest_controls_frame, text="Strategy:", font=self.font_normal, text_color=COLOR_FOREGROUND); self.strategy_label.pack(side="left", padx=(0, 10))
        self.strategy_var = ctk.StringVar(value=list(STRATEGY_LOADERS.keys())[0])
        self.strategy_dropdown = ctk.CTkComboBox( self.backtest_controls_frame, values=list(STRATEGY_LOADERS.keys()), variable=self.strategy_var, font=self.font_normal, text_color=COLOR_DROPDOWN_FG, fg_color=COLOR_DROPDOWN_BG, dropdown_fg_color=COLOR_DROPDOWN_BG, button_color=COLOR_DROPDOWN_BUTTON, button_hover_color=COLOR_DROPDOWN_BUTTON_HOVER, border_color=COLOR_BUTTON, border_width=1, command=self.update_param_widgets ); self.strategy_dropdown.pack(side="left", padx=(0, 15))
        self.info_button = ctk.CTkButton( self.backtest_controls_frame, text="Info", command=self.show_strategy_info, font=self.font_button, text_color=COLOR_FOREGROUND, fg_color=COLOR_SECONDARY_BUTTON, hover_color=COLOR_SECONDARY_BUTTON_HOVER, width=50 ); self.info_button.pack(side="left", padx=(0,15))
        self.run_backtest_button = ctk.CTkButton( self.backtest_controls_frame, text="Run Backtest", command=self.run_selected_backtest, font=self.font_button, text_color=COLOR_BACKGROUND, fg_color=COLOR_ACCENT, hover_color=COLOR_BUTTON_HOVER ); self.run_backtest_button.pack(side="right", padx=(15, 0))

        # --- Parameter Frame (Row 6) ---
        self.param_frame = ctk.CTkFrame(self, fg_color="transparent");
        self.param_frame.grid(row=6, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="ew")
        self.update_param_widgets(self.strategy_var.get())

        # --- LED Frame (Row 7) ---
        self.led_frame = ctk.CTkFrame(self, fg_color="transparent");
        self.led_frame.grid(row=7, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="ew")
        self.leds = {}
        led_configs = [ ("PWR", COLOR_LED_PWR_ON), ("CPU", COLOR_LED_CPU_ON), ("DATA", COLOR_LED_DATA_ON), ("COM", COLOR_LED_COM_ON), ("ERR", COLOR_LED_PWR_ON) ]
        app_bg_color = COLOR_BACKGROUND
        for name, on_color in led_configs:
             led_container = ctk.CTkFrame(self.led_frame, fg_color="transparent"); led_container.pack(side="left", padx=10)
             led_label = ctk.CTkLabel(led_container, text=name, font=self.font_led, text_color=COLOR_FOREGROUND); led_label.pack(side="top")
             led_indicator = WornLED( led_container, color=on_color, size=20, explicit_canvas_bg=app_bg_color ); led_indicator.pack(side="top", pady=(2,0))
             led_indicator.set_wear_level(0.7); self.leds[name] = led_indicator
             if name == "PWR": led_indicator.bind("<Button-1>", self.show_easter_egg); led_label.bind("<Button-1>", self.show_easter_egg)

        # --- Initialize LED States and start loops ---
        self.initialize_leds()

        # --- Graceful Shutdown ---
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    # --- Methods ---
    def initialize_leds(self):
        for name, led_widget in self.leds.items():
            if led_widget.winfo_exists():
                if name == "PWR": led_widget.set_state("on"); led_widget.enable_flicker(True)
                else: led_widget.set_state("off"); led_widget.enable_flicker(False)
        self._update_activity_leds()
        self._update_matrix_display()

    def _update_activity_leds(self):
        if not self.winfo_exists(): return
        if random.random() < 0.2:
             data_led = self.leds.get("DATA")
             if data_led and data_led.winfo_exists():
                  current_state = data_led.get_state(); new_state = "off" if current_state == "on" else "on"
                  self.set_led_state("DATA", new_state, flicker=(new_state == "on"))
        if random.random() < 0.15:
             com_led = self.leds.get("COM")
             if com_led and com_led.winfo_exists():
                  current_state = com_led.get_state(); new_state = "off" if current_state == "on" else "on"
                  self.set_led_state("COM", new_state, flicker=(new_state == "on"))
        delay = random.randint(150, 550)
        if self.winfo_exists(): self.activity_led_job = self.after(delay, self._update_activity_leds)
        else: self.activity_led_job = None

    def _update_matrix_display(self):
        if not self.winfo_exists(): return
        display_text = ""
        display_color = COLOR_REC_DEFAULT
        self.matrix_shows_price = not self.matrix_shows_price
        if self.matrix_shows_price and self.latest_price is not None:
            price_str = f"{self.latest_price:.2f}"
            display_text = price_str.rjust(MATRIX_COLS)
            display_color = COLOR_REC_DEFAULT
        else:
            rec_text = self.latest_recommendation
            display_text = rec_text.center(MATRIX_COLS)
            if "WEAK SELL" in rec_text: display_color = COLOR_REC_WEAK_SELL
            elif "SELL" in rec_text: display_color = COLOR_REC_SELL
            elif "WEAK BUY" in rec_text: display_color = COLOR_REC_WEAK_BUY
            elif "BUY" in rec_text: display_color = COLOR_REC_BUY
            elif "HOLD" in rec_text: display_color = COLOR_REC_HOLD
            elif "N/A" in rec_text or "-" in rec_text: display_color = COLOR_REC_HOLD
            elif "ERROR" in rec_text or "NO" in rec_text: display_color = COLOR_REC_SELL
            elif "CALC" in rec_text: display_color = COLOR_REC_WEAK_SELL
            else: display_color = COLOR_REC_DEFAULT
        if hasattr(self, 'recommendation_display') and self.recommendation_display.get_frame().winfo_exists():
             display_text = display_text[:MATRIX_COLS]
             self.recommendation_display.display_text(display_text, color=display_color)
        delay = 3500
        if self.winfo_exists(): self.matrix_update_job = self.after(delay, self._update_matrix_display)
        else: self.matrix_update_job = None

    def set_led_state(self, name: str, state: str, flicker: bool | None = None):
        if name in self.leds:
            led_widget = self.leds[name]
            if led_widget.winfo_exists():
                led_widget.set_state(state)
                if flicker is None: led_widget.enable_flicker(state == "on")
                else: led_widget.enable_flicker(flicker and state == "on")
            else: print(f"Warning: Attempted to set state for destroyed LED: {name}")
        else: print(f"Warning: Attempted to set state for unknown LED: {name}")

    def update_param_widgets(self, strategy_name: str):
         for widget in self.param_frame.winfo_children(): widget.destroy()
         self.param_entries.clear(); params = PARAM_CONFIG.get(strategy_name, [])
         if not params:
              no_param_label = ctk.CTkLabel(self.param_frame, text="No parameters for this strategy.", font=self.font_normal, text_color=COLOR_FOREGROUND); no_param_label.pack(anchor="w"); return
         for param_name, default_value in params:
              entry_frame = ctk.CTkFrame(self.param_frame, fg_color="transparent"); entry_frame.pack(side="left", padx=10, pady=2)
              label = ctk.CTkLabel(entry_frame, text=f"{param_name}:", font=self.font_normal, text_color=COLOR_FOREGROUND); label.pack(side="left", padx=(0, 5))
              param_var = ctk.StringVar(value=str(default_value))
              entry = ctk.CTkEntry( entry_frame, textvariable=param_var, width=60, font=self.font_normal, text_color=COLOR_DROPDOWN_FG, fg_color=COLOR_DROPDOWN_BG, border_color=COLOR_BUTTON, border_width=1 ); entry.pack(side="left")
              self.param_entries[param_name] = param_var

    def on_closing(self):
        print("Closing application gracefully...")
        try: plt.close(self.fig); print("Matplotlib figure closed.")
        except Exception as e: print(f"Error closing matplotlib figure: {e}")
        print("Stopping LED flickering...")
        if self.activity_led_job:
            try: self.after_cancel(self.activity_led_job)
            except tk.TclError as e: print(f"Ignoring TclError during activity_led_job cancel: {e}")
            self.activity_led_job = None
        if self.matrix_update_job:
            try: self.after_cancel(self.matrix_update_job)
            except tk.TclError as e: print(f"Ignoring TclError during matrix_update_job cancel: {e}")
            self.matrix_update_job = None
        for name, led_widget in self.leds.items():
            if led_widget.winfo_exists():
                led_widget.enable_flicker(False)
                if led_widget.flicker_job:
                    try: led_widget.after_cancel(led_widget.flicker_job)
                    except tk.TclError as e: print(f"Ignoring TclError during after_cancel for {name}: {e}")
                    led_widget.flicker_job = None
        self.update_idletasks(); print("Destroying application window..."); self.destroy(); print("Application window destroyed.")

    def log_message(self, message: str, clear_first: bool = False, tag: str | None = None):
        is_error_warning = "error" in message.lower() or "warning" in message.lower()
        if is_error_warning:
            self.set_led_state("ERR", "on", flicker=True)
            if self.winfo_exists(): self.after(1500, lambda name="ERR": self.set_led_state(name, "off"))
        if hasattr(self, 'output_textbox') and self.output_textbox.winfo_exists():
            try:
                self.output_textbox.configure(state="normal")
                if clear_first: self.output_textbox.delete("1.0", "end")
                tags_to_apply = (tag,) if tag else (); self.output_textbox.insert("end", f"{message}\n", tags_to_apply);
                self.output_textbox.see("end"); self.output_textbox.configure(state="disabled")
            except tk.TclError as e: print(f"Error updating output_textbox: {e}")
        else: print(f"Log message skipped, output_textbox does not exist: {message}")

    # --- MODIFIED: clear_display updates matrix state ---
    def clear_display(self):
        self.ax.clear(); self.ax.set_facecolor(COLOR_CHART_BG)
        self.ax.tick_params(axis='x', colors=COLOR_CHART_AXES); self.ax.tick_params(axis='y', colors=COLOR_CHART_AXES)
        self.ax.yaxis.label.set_color(COLOR_CHART_AXES); self.ax.xaxis.label.set_color(COLOR_CHART_AXES); self.ax.title.set_color(COLOR_CHART_AXES)
        self.ax.spines['bottom'].set_color(COLOR_CHART_AXES); self.ax.spines['top'].set_color(COLOR_CHART_AXES); self.ax.spines['right'].set_color(COLOR_CHART_AXES); self.ax.spines['left'].set_color(COLOR_CHART_AXES)
        placeholder = 'Loading data...' if hasattr(self, '_loading_data') and self._loading_data else 'Select symbol and click Load Data'
        self.ax.text(0.5, 0.5, placeholder, horizontalalignment='center', verticalalignment='center', transform=self.ax.transAxes, color=COLOR_CHART_AXES, fontsize=self.font_large.cget('size'))
        self.chart_canvas.draw(); self.chart_info_label.configure(text="")
        # Update latest recommendation to trigger blank display in loop
        self.latest_recommendation = " " * MATRIX_COLS
        # Update matrix display immediately if possible
        if hasattr(self, 'recommendation_display') and self.recommendation_display.get_frame().winfo_exists():
             self.recommendation_display.display_text(self.latest_recommendation)
        self.plotted_data = None

    # --- MODIFIED: on_symbol_change updates matrix state ---
    def on_symbol_change(self, selected_symbol: str):
        self.custom_symbol_entry.delete(0, 'end'); self.clear_display() # clear_display now handles matrix placeholder
        self.log_message(f"Symbol changed to: {selected_symbol}. Click 'Load Data'.", clear_first=True)
        self.current_data = None; self.plotted_data = None; self.latest_price = None
        # Update recommendation state so matrix shows placeholder
        self.latest_recommendation = " " * MATRIX_COLS
        # Trigger immediate matrix update if possible
        if hasattr(self, 'recommendation_display') and self.recommendation_display.get_frame().winfo_exists():
            self.recommendation_display.display_text(self.latest_recommendation)
        self.update_param_widgets(self.strategy_var.get())
        self.set_led_state("CPU", "off"); self.set_led_state("ERR", "off")

    def plot_data(self, data_to_plot: pd.DataFrame | None, title_suffix: str = ""):
        self.ax.clear(); self.plotted_data = None
        if data_to_plot is None or data_to_plot.empty: self.ax.text(0.5, 0.5, f"No data to plot for {self.current_symbol}", color=COLOR_CHART_AXES, ha='center', va='center', transform=self.ax.transAxes)
        elif 'close' not in data_to_plot.columns: self.log_message("Error: 'close' column not found in data. Cannot plot chart."); self.ax.text(0.5, 0.5, "Error plotting data", color=COLOR_ACCENT, ha='center', va='center', transform=self.ax.transAxes)
        else:
            self.ax.plot(data_to_plot.index, data_to_plot['close'], color=COLOR_CHART_LINE, linewidth=1.5)
            self.ax.set_title(f"{self.current_symbol} Price{title_suffix}", color=COLOR_CHART_AXES)
            self.ax.set_ylabel("Price (USD)", color=COLOR_CHART_AXES); self.ax.set_xlabel("Date", color=COLOR_CHART_AXES)
            self.fig.autofmt_xdate(); self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            self.ax.tick_params(axis='x', colors=COLOR_CHART_AXES, rotation=45); self.ax.tick_params(axis='y', colors=COLOR_CHART_AXES)
            self.ax.grid(True, color=COLOR_DROPDOWN_BG, linestyle='--', linewidth=0.5); self.plotted_data = data_to_plot
        self.ax.set_facecolor(COLOR_CHART_BG)
        self.ax.spines['bottom'].set_color(COLOR_CHART_AXES); self.ax.spines['top'].set_color(COLOR_CHART_AXES); self.ax.spines['right'].set_color(COLOR_CHART_AXES); self.ax.spines['left'].set_color(COLOR_CHART_AXES)
        self.chart_canvas.draw()

    # --- MODIFIED: fetch_and_display_data updates matrix state ---
    def fetch_and_display_data(self):
        custom_symbol = self.custom_symbol_entry.get().strip().upper(); selected_symbol = custom_symbol if custom_symbol else self.symbol_var.get()
        self.current_symbol = selected_symbol
        if not selected_symbol: self.log_message("Error: No symbol selected or entered.", clear_first=True); return
        self._loading_data = True; self.clear_display(); self.log_message(f"--- Loading data for {selected_symbol} ---", clear_first=True)
        self.set_led_state("CPU", "on", flicker=False); self.update_idletasks()
        self.latest_price = None; self.latest_recommendation = "LOADING..."
        try:
            self.current_data = self.data_fetcher.get_historical_data( selected_symbol, period=DEFAULT_DATA_PERIOD, interval=DEFAULT_DATA_INTERVAL )
            if self.current_data is not None and not self.current_data.empty:
                self.log_message(f"Successfully loaded {len(self.current_data)} data points.")
                self.log_message(f"Data range: {self.current_data.index.min().strftime('%Y-%m-%d')} to {self.current_data.index.max().strftime('%Y-%m-%d')}")
                self.plot_data(self.current_data, title_suffix=f" ({DEFAULT_DATA_PERIOD})"); self.log_message("Chart updated.")
                current_price = self.data_fetcher.get_current_price(selected_symbol)
                self.latest_price = current_price
                self.log_message(f"\n--- Approx. Current Price ---")
                if current_price: self.log_message(f"{selected_symbol}: {current_price:.2f}")
                else: self.log_message(f"Could not retrieve current price for {selected_symbol}.")
                self.generate_recommendation() # Updates self.latest_recommendation
            else:
                self.log_message(f"Failed to load data or no data available for {selected_symbol}.")
                self.plot_data(None); self.current_data = None; self.latest_recommendation = "N/A"
        except Exception as e:
            self.log_message(f"An error occurred during data fetch/display: {e}")
            self.plot_data(None); self.current_data = None; self.latest_recommendation = "ERROR"
        finally:
            self._loading_data = False; self.set_led_state("CPU", "off")
            if self.matrix_update_job:
                 try: self.after_cancel(self.matrix_update_job)
                 except tk.TclError: pass
            if self.winfo_exists(): self._update_matrix_display()

    def update_chart_lookback(self, period: str):
        if self.current_data is None or self.current_data.empty: self.log_message("No data loaded to filter."); return
        self.log_message(f"Updating chart view to: {period}"); filtered_data = None; now = datetime.datetime.now().date()
        try:
            if period == "ALL":
                filtered_data = self.current_data
            elif period == "YTD":
                start_of_year = datetime.date(now.year, 1, 1)
                if isinstance(self.current_data.index, pd.DatetimeIndex):
                    filtered_data = self.current_data[self.current_data.index.date >= start_of_year]
                else:
                    filtered_data = self.current_data
            else:
                offset_map = {"1Y": "365d", "6M": "183d", "3M": "91d", "1M": "30d"}; offset = offset_map.get(period)
                if offset:
                    end_date = self.current_data.index.max(); start_date = end_date - pd.Timedelta(offset); filtered_data = self.current_data[self.current_data.index >= start_date]
                else:
                    self.log_message(f"Unknown period: {period}"); filtered_data = self.current_data

            if filtered_data is None or filtered_data.empty:
                self.log_message(f"No data available for the selected period: {period}"); self.plot_data(None, title_suffix=f" (No data for {period})")
            else:
                self.plot_data(filtered_data, title_suffix=f" ({period})")
        except Exception as e:
            self.log_message(f"Error filtering data for period {period}: {e}"); self.plot_data(self.current_data)

    def on_chart_motion(self, event):
        if event.inaxes != self.ax or event.xdata is None or self.plotted_data is None or self.plotted_data.empty: self.chart_info_label.configure(text=""); return
        try:
            dt = mdates.num2date(event.xdata).replace(tzinfo=None); nearest_index = self.plotted_data.index.get_indexer([dt], method='nearest')[0]
            actual_date = self.plotted_data.index[nearest_index]; close_price = self.plotted_data['close'].iloc[nearest_index]
            date_str = actual_date.strftime('%Y-%m-%d'); info_text = f"Date: {date_str}, Price: {close_price:.2f}"; self.chart_info_label.configure(text=info_text)
        except Exception as e: self.chart_info_label.configure(text="")

    def show_strategy_info(self):
        selected_strategy_name = self.strategy_var.get(); description = STRATEGY_DESCRIPTIONS.get(selected_strategy_name, "No description available for this strategy.")
        info_window = ctk.CTkToplevel(self); info_window.title(f"{selected_strategy_name} - Info"); info_window.geometry("450x350"); info_window.configure(fg_color=COLOR_BACKGROUND); info_window.transient(self); info_window.grab_set()
        info_frame = ctk.CTkFrame(info_window, fg_color="transparent"); info_frame.pack(padx=15, pady=15, fill="both", expand=True)
        title_label = ctk.CTkLabel(info_frame, text=selected_strategy_name, font=self.font_large, text_color=COLOR_FOREGROUND); title_label.pack(pady=(0, 10))
        desc_textbox = ctk.CTkTextbox( info_frame, font=self.font_normal, text_color=COLOR_TEXTBOX_FG, fg_color=COLOR_TEXTBOX_BG, border_width=1, border_color=COLOR_BUTTON, wrap="word" ); desc_textbox.pack(fill="both", expand=True); desc_textbox.insert("1.0", description); desc_textbox.configure(state="disabled")
        close_button = ctk.CTkButton( info_frame, text="Close", command=info_window.destroy, font=self.font_button, text_color=COLOR_BACKGROUND, fg_color=COLOR_BUTTON, hover_color=COLOR_BUTTON_HOVER ); close_button.pack(pady=(10, 0))

    def generate_recommendation(self):
         """Generates a simple Buy/Sell/Hold recommendation based on indicators, controlling CPU LED and updating internal state."""
         self.log_message("Generating recommendation..."); print("DEBUG: Generating recommendation...")
         self.set_led_state("CPU", "on", flicker=True); self.update_idletasks()
         recommendation = "ERROR"
         try:
             if self.current_data is None or self.current_data.empty: recommendation = "N/A"; return
             if self.talib_module is None:
                  try: self.talib_module = importlib.import_module("talib"); print("TA-Lib imported.")
                  except ImportError: self.log_message("TA-Lib not found."); print("ERROR: TA-Lib not found for recommendation."); recommendation = "NO TA-LIB"; return
             required_length = max(REC_SMA_LONG, REC_MACD_SLOW + REC_MACD_SIG, REC_BBANDS_PERIOD, REC_ADX_PERIOD, REC_RSI_PERIOD)
             if len(self.current_data) < required_length: recommendation = "NO DATA"; return
             close_prices = self.current_data['close']; high_prices = self.current_data['high']; low_prices = self.current_data['low']
             sma_short = self.talib_module.SMA(close_prices, timeperiod=REC_SMA_SHORT); sma_long = self.talib_module.SMA(close_prices, timeperiod=REC_SMA_LONG)
             rsi = self.talib_module.RSI(close_prices, timeperiod=REC_RSI_PERIOD); macd, macdsignal, macdhist = self.talib_module.MACD(close_prices, fastperiod=REC_MACD_FAST, slowperiod=REC_MACD_SLOW, signalperiod=REC_MACD_SIG)
             upper, middle, lower = self.talib_module.BBANDS(close_prices, timeperiod=REC_BBANDS_PERIOD, nbdevup=REC_BBANDS_STDDEV, nbdevdn=REC_BBANDS_STDDEV, matype=0)
             adx = self.talib_module.ADX(high_prices, low_prices, close_prices, timeperiod=REC_ADX_PERIOD)
             latest_close = close_prices.iloc[-1]; latest_sma_short = sma_short.iloc[-1]; latest_sma_long = sma_long.iloc[-1]; latest_rsi = rsi.iloc[-1]
             latest_macd = macd.iloc[-1]; latest_macdsignal = macdsignal.iloc[-1]; latest_middleband = middle.iloc[-1]; latest_adx = adx.iloc[-1]
             if pd.isna(latest_sma_short) or pd.isna(latest_sma_long) or pd.isna(latest_rsi) or pd.isna(latest_macd) or pd.isna(latest_macdsignal) or pd.isna(latest_middleband) or pd.isna(latest_adx): recommendation = "CALC..."; return
             score = 0; trend_score = 0
             if latest_close > latest_sma_long: trend_score += 0.5
             if latest_sma_short > latest_sma_long: trend_score += 0.5
             elif latest_sma_short < latest_sma_long: trend_score -= 0.5
             if latest_macd > latest_macdsignal: trend_score += 1.0
             else: trend_score -= 1.0
             if latest_close > latest_middleband: trend_score += 0.5
             else: trend_score -= 0.5
             is_trending = latest_adx > REC_ADX_THRESHOLD
             if is_trending: score += trend_score * 1.5
             else: score += trend_score * 0.5
             if latest_rsi > REC_RSI_BUY: score += 1.0
             elif latest_rsi < REC_RSI_SELL: score -= 1.0
             if score >= 2.5: recommendation = "BUY"
             elif score >= 0.5: recommendation = "WEAK BUY"
             elif score <= -2.5: recommendation = "SELL"
             elif score <= -0.5: recommendation = "WEAK SELL"
             else: recommendation = "HOLD"
             log_text = f"Recommendation generated: {recommendation} (Score: {score:.1f}, ADX: {latest_adx:.1f})"; self.log_message(log_text); print(log_text)
         except Exception as e: error_msg = f"Error generating recommendation: {e}"; self.log_message(error_msg); print(error_msg); recommendation = "ERROR"
         finally:
             self.latest_recommendation = recommendation.upper()
             if self.matrix_update_job:
                  try: self.after_cancel(self.matrix_update_job)
                  except tk.TclError: pass
             if self.winfo_exists(): self._update_matrix_display()
             self.set_led_state("CPU", "off")

    def show_easter_egg(self, event=None):
        print("DEBUG: show_easter_egg triggered"); egg_window = ctk.CTkToplevel(self); egg_window.title("WOW"); egg_window.geometry("600x400"); egg_window.configure(fg_color=COLOR_BACKGROUND); egg_window.transient(self); egg_window.grab_set()
        egg_frame = ctk.CTkFrame(egg_window, fg_color="transparent"); egg_frame.pack(padx=10, pady=10, fill="both", expand=True)
        art_textbox = ctk.CTkTextbox( egg_frame, font=self.font_normal, text_color=COLOR_ACCENT, fg_color=COLOR_TEXTBOX_BG, border_width=1, border_color=COLOR_BUTTON, wrap="none" ); art_textbox.pack(fill="both", expand=True, padx=5, pady=5); art_textbox.insert("1.0", EASTER_EGG_ART); art_textbox.configure(state="disabled")
        close_button = ctk.CTkButton( egg_frame, text="Much Close", command=egg_window.destroy, font=self.font_button, text_color=COLOR_BACKGROUND, fg_color=COLOR_BUTTON, hover_color=COLOR_BUTTON_HOVER ); close_button.pack(pady=(10, 0))

    def run_selected_backtest(self):
        """Runs the backtest using the selected strategy, data, and GUI parameters, controlling LEDs."""
        selected_strategy_name = self.strategy_var.get(); strategy_loader = STRATEGY_LOADERS.get(selected_strategy_name)
        custom_symbol = self.custom_symbol_entry.get().strip().upper(); symbol_used = custom_symbol if custom_symbol else self.symbol_var.get()
        if strategy_loader is None: self.log_message(f"Error: Strategy loader not found."); return
        if self.current_data is None or self.current_data.empty: self.log_message(f"Error: No data loaded for {symbol_used}."); return
        strategy_params = {}; default_params = {name: default for name, default in PARAM_CONFIG.get(selected_strategy_name, [])}; param_log_list = []

        for param_name, param_var in self.param_entries.items():
            try:
                value_str = param_var.get(); value = float(value_str)
                if value.is_integer(): value = int(value)
            except ValueError: value = default_params.get(param_name); print(f"Warning: Non-numeric param '{param_name}'. Using default '{value}'.")
            except Exception as e: print(f"Error processing parameter '{param_name}': {e}. Using default."); value = default_params.get(param_name)

            if param_name == 'trade_size_percent':
                 if isinstance(value, (int, float)) and 0 < value <= 100: strategy_params[param_name] = value / 100.0
                 else: default_fraction = DEFAULT_TRADE_SIZE_PERCENT / 100.0 if DEFAULT_TRADE_SIZE_PERCENT > 1 else DEFAULT_TRADE_SIZE_PERCENT; strategy_params[param_name] = default_fraction; print(f"Warning: Invalid trade size % ({value}). Using default {default_fraction:.1%}")
            else: strategy_params[param_name] = value
            param_log_list.append(f"{param_name}={value}")

        self.log_message(f"\n--- Running Backtest: {selected_strategy_name} on {symbol_used} ---", clear_first=True)
        param_log_str = ", ".join([f"{k}={v:.3f}" if k == 'trade_size_percent' else f"{k}={v}" for k,v in strategy_params.items()]); self.log_message(f"Params: {param_log_str}")
        self.set_led_state("CPU", "on", flicker=True); self.update_idletasks()
        selected_strategy_class = None; stats = None; bt_results = None
        try:
            if isinstance(strategy_loader, str):
                module_path, class_name = strategy_loader.rsplit('.', 1)
                needs_talib = any(s in strategy_loader for s in ["rsi_oscillator", "volatility_breakout", "macd_strategy", "bollinger_bands_strategy"])
                _talib_local = self.talib_module
                if needs_talib and _talib_local is None:
                     try: _talib_local = importlib.import_module("talib"); self.talib_module = _talib_local; print("TA-Lib imported.")
                     except ImportError: self.log_message("ImportError: Failed to import 'talib'."); raise
                needs_ephem = "real_moon_strategy" in strategy_loader
                _ephem_local = self.ephem_module
                if needs_ephem and _ephem_local is None:
                     try: _ephem_local = importlib.import_module("ephem"); self.ephem_module = _ephem_local; print("Ephem imported.")
                     except ImportError: self.log_message("ImportError: Failed to import 'ephem'."); raise
                strategy_module = importlib.import_module(module_path)
                if needs_talib: setattr(strategy_module, 'talib', _talib_local)
                if needs_ephem: setattr(strategy_module, 'ephem', _ephem_local)
                selected_strategy_class = getattr(strategy_module, class_name)
                if class_name == "RealMoonStrategy": selected_strategy_class.OBSERVER_LAT = OBSERVER_LAT; selected_strategy_class.OBSERVER_LON = OBSERVER_LON; selected_strategy_class.OBSERVER_ELEV = OBSERVER_ELEV
            else: selected_strategy_class = strategy_loader
            if selected_strategy_class is None: raise ValueError("Could not load strategy class.")
            stats, bt_results = run_backtest( strategy_class=selected_strategy_class, data=self.current_data, cash=DEFAULT_CASH, commission=DEFAULT_COMMISSION, **strategy_params )
            if stats is not None:
                self.log_message("--- Backtest Results ---")
                stats_to_display = stats.drop(index=['_strategy', '_equity_curve', '_trades'], errors='ignore')
                max_key_len = max(len(idx) for idx in stats_to_display.index) if not stats_to_display.empty else 25; key_width = max(25, max_key_len)
                self.output_textbox.configure(state="normal")
                for idx, value in stats_to_display.items():
                    tag = None; value_str = ""; line = ""
                    if isinstance(value, pd.Timedelta):
                         if pd.isna(value): value_str = "NaT"
                         else: value_str = str(value).split('.')[0]
                         line = f"{idx:<{key_width}}: {value_str}\n"; tag = None; tags_to_apply = (); self.output_textbox.insert("end", line, tags_to_apply); continue
                    try:
                        is_numeric = isinstance(value, (int, float)); numeric_value = float(value) if is_numeric else 0
                        percent_keys = ["Return", "CAGR", "Alpha", "Volatility", "Drawdown", "Trade [%]", "Expectancy [%]", "Win Rate", "Exposure Time"]
                        is_percent = any(pk in idx for pk in percent_keys)
                        positive_good_keys = ["Return", "Equity Final", "Profit Factor", "Ratio", "Alpha", "CAGR", "Expectancy", "SQN", "Best Trade", "Avg. Trade", "Win Rate"]
                        is_positive_good = any(pgk in idx for pgk in positive_good_keys)
                        if is_numeric:
                             if "Drawdown" in idx or "Worst Trade" in idx: tag = "negative" if numeric_value < 0 else None
                             elif is_positive_good: tag = "positive" if numeric_value > 0 else ("negative" if numeric_value < 0 else None)
                             elif "Profit Factor" in idx: tag = "positive" if numeric_value > 1 else ("negative" if numeric_value < 1 else None)
                        if is_percent: value_str = f"{value:>{14}.2f}%"
                        elif "Equity" in idx or "Commissions" in idx: value_str = f"{value:>{15},.2f}"
                        elif "Ratio" in idx or "Beta" in idx or "SQN" in idx or "Factor" in idx: value_str = f"{value:>{15}.2f}"
                        elif isinstance(value, pd.Timestamp): value_str = f"{value.strftime('%Y-%m-%d'):>15}"
                        elif isinstance(value, (int, float)): value_str = f"{value:>15}"
                        else: value_str = f"{str(value):>15}"
                    except Exception as fmt_e: print(f"Error formatting stat '{idx}' (Value: {value}, Type: {type(value)}): {fmt_e}"); value_str = "[FMT_ERR]"; line = f"{idx:<{key_width}}: {value_str}\n"
                    if not line: line = f"{idx:<{key_width}}: {value_str:>15}\n"
                    tags_to_apply = (tag,) if tag else (); self.output_textbox.insert("end", line, tags_to_apply)
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
                self.output_textbox.configure(state="disabled"); self.output_textbox.see("end")
            else: self.log_message("Backtest failed to produce results. Check console for errors.")
        except ImportError as e:
             self.log_message(f"ImportError: {e}. Required library might be missing for {selected_strategy_name}.")
             if 'talib' in str(e).lower(): self.log_message("Please ensure TA-Lib is correctly installed (C library + Python wrapper).")
             elif 'ephem' in str(e).lower(): self.log_message("Please ensure Ephem is installed: pip install ephem")
        except Exception as e:
            self.log_message(f"An error occurred during backtesting: {type(e).__name__} - {e}")
            print("\n--- Backtesting Error Traceback ---"); traceback.print_exc(); print("--- End Traceback ---\n")
        finally:
            # --- This block ensures CPU LED turns off even if errors occur ---
            self.set_led_state("CPU", "off")


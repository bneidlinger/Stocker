# config.py
# Configuration settings for the application

import os

# List of stock symbols to track/analyze
# AMZN, NVDA, META, PLTR + AAPL, TSLA
SYMBOLS = ["AMZN", "NVDA", "META", "PLTR", "AAPL", "TSLA"]

# Default time period for fetching historical data (e.g., "1y", "5y", "max")
DEFAULT_DATA_PERIOD = "5y" # Fetch a longer period initially

# Default interval for data (e.g., "1d", "1wk", "1h")
DEFAULT_DATA_INTERVAL = "1d"

# --- Backtesting Defaults ---
DEFAULT_CASH = 10000
DEFAULT_COMMISSION = 0.001 # 0.1% commission per trade
DEFAULT_TRADE_SIZE_PERCENT = 95 # Default trade size as percentage (e.g., 95 for 95%)

# --- Recommendation Engine Parameters ---
REC_SMA_SHORT = 20
REC_SMA_LONG = 50
REC_RSI_PERIOD = 14
REC_RSI_BUY = 55 # RSI threshold suggesting potential buy strength
REC_RSI_SELL = 45 # RSI threshold suggesting potential sell weakness
REC_MACD_FAST = 12
REC_MACD_SLOW = 26
REC_MACD_SIG = 9
REC_BBANDS_PERIOD = 20
REC_BBANDS_STDDEV = 2.0
REC_ADX_PERIOD = 14
REC_ADX_THRESHOLD = 25

# --- Claude Configuration (replaces OpenAI) ---
CLAUDE_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = "claude-sonnet-4-20250514"
SENTIMENT_ENABLED = True

# --- Alpaca Configuration ---
ALPACA_API_KEY = os.environ.get("ALPACA_API_KEY", "")
ALPACA_API_SECRET = os.environ.get("ALPACA_API_SECRET", "")
ALPACA_BASE_URL_PAPER = "https://paper-api.alpaca.markets"
ALPACA_BASE_URL_LIVE = "https://api.alpaca.markets"
ALPACA_PAPER_TRADING = True

# --- Auto-Trader Defaults ---
AUTO_TRADER_DEFAULT_BUDGET = 100.0
AUTO_TRADER_CYCLE_MINUTES = 60
AUTO_TRADER_MAX_POSITION_PCT = 0.25
AUTO_TRADER_STOP_LOSS_PCT = 0.05

# --- Discord Configuration ---
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")

# --- ML Configuration ---
ML_MODEL_DIR = 'data/models'
ML_DEFAULT_MODEL = 'random_forest'
ML_DEFAULT_HORIZON = 5
ML_TRAIN_TEST_SPLIT = 0.2
ML_ENABLE_HYBRID = True       # Enable hybrid ML + Technical Analysis recommendations
ML_HYBRID_WEIGHT = 0.5        # Default weight for ML vs TA (0.0 = all TA, 1.0 = all ML)

# --- Location for Astronomical Calculations (Ephem) ---
# Used for RealMoonStrategy - Coordinates for Apple Valley, MN
OBSERVER_LAT = '44.73' # Latitude
OBSERVER_LON = '-93.22' # Longitude
OBSERVER_ELEV = 280 # Elevation in meters (approx)

# --- Theme Colors (Miami Vice / Retro Fallout Inspired) ---
# Using hex codes for more control
COLOR_BACKGROUND = "#1a1a2e" # Dark blue/purple
COLOR_FOREGROUND = "#e0fbfc" # Light cyan/near white
COLOR_BUTTON = "#ff69b4"     # Neon Pink
COLOR_BUTTON_HOVER = "#ff85c1" # Lighter Pink
COLOR_DROPDOWN_FG = "#e0fbfc"
COLOR_DROPDOWN_BG = "#2a2a4e" # Slightly lighter dark blue
COLOR_DROPDOWN_BUTTON = "#ff69b4"
COLOR_DROPDOWN_BUTTON_HOVER = "#ff85c1"
COLOR_TEXTBOX_FG = "#e0fbfc"
COLOR_TEXTBOX_BG = "#161625" # Even darker for console feel
COLOR_ACCENT = "#39ff14" # Neon Green (optional accent)
COLOR_CHART_BG = "#161625" # Match textbox background
COLOR_CHART_LINE = "#ff69b4" # Pink line
COLOR_CHART_AXES = "#e0fbfc" # Cyan axes/ticks

# Added colors for positive/negative results
COLOR_POSITIVE = "#39ff14" # Neon Green (BUY)
COLOR_NEGATIVE = "#ff4d6d" # Neon Red/Pink variation (SELL)
COLOR_NEUTRAL = COLOR_FOREGROUND # Default color for HOLD
COLOR_WEAK_POSITIVE = "#00f5d4" # Teal/Cyan (Weak Buy)
COLOR_WEAK_NEGATIVE = "#f77f00" # Orange (Weak Sell)

# Secondary Button Colors (for Chart Period, Info)
COLOR_SECONDARY_BUTTON = "#007f7f" # Dark Cyan/Teal
COLOR_SECONDARY_BUTTON_HOVER = "#00aaaa" # Lighter Cyan/Teal

# --- LED Colors ---
# Slightly less saturated ON colors, distinct OFF colors
COLOR_LED_BORDER_OFF = "#10101a" # Used in app.py WornLED fix
COLOR_LED_PWR_ON = "#E6455E" # Slightly less intense Red/Pink
COLOR_LED_CPU_ON = "#2FC41F" # Slightly less intense Green
COLOR_LED_DATA_ON = "#E1E100" # Slightly less intense Yellow
COLOR_LED_COM_ON = "#00C2C2" # Slightly less intense Cyan
# ERR LED uses PWR colors

# --- Recommendation Matrix Colors ---
COLOR_REC_SELL = "#FF4136"       # Red
COLOR_REC_WEAK_SELL = "#FF851B"  # Orange
COLOR_REC_HOLD = "#AAAAAA"       # Gray
COLOR_REC_WEAK_BUY = "#AFFFAD"   # Light Green
COLOR_REC_BUY = "#2ECC40"        # Green
COLOR_REC_DEFAULT = "#00FF00"    # Default matrix green

# --- ML LED Colors ---
COLOR_LED_ML_ON = "#7D26CD"      # Purple for ML activity
COLOR_LED_ML_BORDER = "#10101a"  # Same border as other LEDs

# --- Auto-Trader LED Colors ---
COLOR_LED_AUTO_ON = "#FF6EC7"    # Hot pink for auto-trader activity
COLOR_LED_AI_ON = "#00BFFF"      # Deep sky blue for AI decisions

# --- Kill Switch Colors ---
COLOR_KILL_SWITCH = "#FF0000"        # Pure red
COLOR_KILL_SWITCH_HOVER = "#CC0000"  # Darker red

# --- ML Visualization Colors ---
COLOR_ML_FEATURE_BAR = "#7D26CD"  # Purple for feature importance bars
COLOR_ML_PREDICTION_UP = "#2ECC40"  # Green for up predictions
COLOR_ML_PREDICTION_DOWN = "#FF4136"  # Red for down predictions
COLOR_ML_CONFIDENCE_HIGH = "#39ff14"  # Neon Green for high confidence
COLOR_ML_CONFIDENCE_MED = "#FFDC00"   # Yellow for medium confidence
COLOR_ML_CONFIDENCE_LOW = "#FF851B"   # Orange for low confidence

# --- Fonts ---
# Using a common monospace font for the console feel
FONT_FAMILY_MONO = "Consolas" # Or "Courier New" or others available
FONT_SIZE_NORMAL = 12
FONT_SIZE_LARGE = 16
FONT_SIZE_TEXTBOX = 14 # Added specific font size for the output textbox
FONT_SIZE_LED = 10 # Smaller font for LED labels
# FONT_SIZE_RECOMMENDATION = 18 # No longer needed for label
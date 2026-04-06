# RetroTrader 2000: Stock Trading Interface

*"Listen up, M-M-Morty! I've built the most badass trading interface in the multiverse! It's got neon colors, vintage LEDs, and enough predictive algorithms to make the Galactic Federation's economists wet themselves!"*

![RetroTrader Screenshot](assets/screenshot.png)

## What the $@#% is this thing?

RetroTrader 2000 is a feature-rich desktop application for stock market analysis, combining retro aesthetics with cutting-edge machine learning capabilities. This application combines retro-futuristic Miami Vice / Fallout-inspired styling with serious financial analysis tools.

Built with Python and CustomTkinter, RetroTrader delivers:

- Real-time market data visualization 
- Technical analysis indicators
- Backtesting for multiple trading strategies
- Machine learning-powered predictions
- Hybrid recommendation system

## Features (or "Why This Blows All Other Trading Apps Out of the Water, Morty!")

### Core Features

- **Data Fetching**: Live data using yfinance API
- **Interactive Charts**: Responsive OHLCV charting with period selection
- **Technical Analysis**: RSI, MACD, Bollinger Bands, ADX and more
- **Strategy Backtesting**: 10+ trading strategies including:
  - SMA/EMA Crossover
  - RSI Oscillator
  - Volatility Breakout
  - Bollinger Bands
  - Ichimoku Cloud
  - ...and even an actual *burp* moon phase strategy

### Machine Learning Capabilities

*"My ML doesn't just throw darts at the market, M-Morty! It's got more features than a Gazorpian beauty pageant and more predictive power than a Testicle Monster's time crystal!"*

#### Feature Engineering

RetroTrader's ML uses a comprehensive feature set for predictive analysis:

- **Price Features**: Returns, high-low ranges, volume metrics
- **Technical Indicators**: Moving averages, RSI, MACD, Bollinger Bands
- **Time Features**: Seasonality, day-of-week effects, month-of-year patterns

#### Models & Training

The system supports multiple classification models:
- **Random Forest** (default)
- **Gradient Boosting**
- **Logistic Regression**

Key ML parameters are user-configurable:
- Prediction horizon (days)
- Classification threshold
- Train/test split 
- Model selection

#### Prediction System

The ML pipeline processes historical data in these phases:

1. **Feature Engineering**: Transforms raw OHLCV data into 40+ predictive features
2. **Target Generation**: Creates forward-looking directional targets (UP/DOWN/NEUTRAL)
3. **Model Training**: Fits models with class balancing to handle market asymmetry
4. **Evaluation**: Measures accuracy, precision, recall, and F1-score
5. **Prediction**: Generates directional forecasts with confidence scores
6. **Hybrid Recommendations**: Combines ML signals with technical analysis

#### Feature Importance

Visualize which factors most influence predictions:
- Top 20 features by importance
- Absolute contribution scores
- Interactive chart display

## Installation ("Three Steps, Morty! Three $%&#@ Steps!")

```bash
# Clone the repository
git clone https://github.com/yourusername/retrotrader.git

# Install requirements
pip install -r requirements.txt

# Run the application
python main.py
```

## Dependencies

- Python 3.8+
- CustomTkinter
- yfinance
- pandas
- numpy
- matplotlib
- scikit-learn
- backtesting.py
- TA-Lib (optional, enhances TA capabilities)
- ephem (optional, for moon-based strategies)

## Advanced Usage

### Configuring ML Parameters

The ML system is highly configurable:

```python
# In config.py:
ML_DEFAULT_HORIZON = 5           # Default prediction period (days)
ML_TRAIN_TEST_SPLIT = 0.2        # Default train/test split ratio
ML_ENABLE_HYBRID = True          # Enable hybrid ML+TA recommendations
ML_HYBRID_WEIGHT = 0.5           # Weight for ML vs TA (0.0 = all TA, 1.0 = all ML)
```

### Creating Custom Strategies

Add your own strategies by:
1. Creating a class inheriting from `backtesting.Strategy`
2. Implementing `init()` and `next()` methods
3. Adding to `STRATEGY_LOADERS` dictionary

*"Don't mess with the GUI code unless you know what you're doing, M-Morty! One wrong move and the whole interface implodes like a Meeseeks box in a black hole!"*

---

## Disclaimer

*"Disclaimer, Morty! This isn't financial advice! Y-y-you think I'd risk interdimensional prison for giving financial advice without a Series 7? Use this at your own risk, or d-d-don't use it at all! I don't care! I'm not your broker!"*

This application is for educational and research purposes only. Past performance does not guarantee future results. The creator(s) of RetroTrader 2000 are not responsible for any financial losses incurred while using this application.

## License

MIT License - *"That means you can do whatever you want with it, Morty! Just don't come crying to me when your algorithm shorts the wrong dimension's currency!"*
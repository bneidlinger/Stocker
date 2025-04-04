# Retro Trading Console: User Guide

## Introduction

Welcome to the Retro Trading Console, a vintage-inspired backtesting platform for stock trading strategies. This user guide will walk you through the application interface, explain how to interpret the results, and help you get the most out of your backtesting experience.

![Retro Trading Console Main Interface](./screenshots/main_app.png)

## Getting Started

### Running the Application

1. Ensure you've installed all dependencies (see `requirements.txt` and the TA-Lib Installation Guide)
2. Launch the application by running:
   ```bash
   python main.py
   ```
3. The application will open with the default dark retro theme inspired by Miami Vice and Fallout

### Interface Overview

The interface is divided into several sections:

1. **Top Controls**: Symbol selection and data loading
2. **Chart Period Controls**: Timeframe selection for the displayed chart
3. **Matrix Display**: Shows current price or trading recommendation
4. **Chart Area**: Displays price history with interactive hover information
5. **Console Output**: Shows data loading information, backtest results, and trades
6. **Backtest Controls**: Strategy selection and parameter configuration
7. **Status Indicators**: Vintage LED indicators showing application status

## Step-by-Step Usage Guide

### 1. Loading Stock Data

1. Select a symbol from the dropdown menu, or enter a custom symbol in the "Custom" field
2. Click the "Load Data" button
3. The application will fetch historical data from Yahoo Finance
4. Once loaded, you'll see:
   - A price chart for the selected symbol
   - Console output showing the data range
   - Current price information (if available)
   - An automated trading recommendation on the matrix display

### 2. Adjusting the Chart View

Use the chart period buttons to adjust the visible timeframe:
- **ALL**: Shows all available data
- **YTD**: Shows data from the start of the current year
- **1Y**: Shows the last year of data
- **6M**: Shows the last 6 months
- **3M**: Shows the last 3 months  
- **1M**: Shows the last month

Hover your mouse over the chart to see date and price information at any point.

### 3. Running a Backtest

1. Select a trading strategy from the "Strategy" dropdown
2. Click the "Info" button to see a detailed explanation of the selected strategy
3. Adjust the strategy parameters as needed (each strategy has different parameters)
4. Click the "Run Backtest" button
5. The console output will display the backtest results, including:
   - Performance metrics (Return, Volatility, Sharpe Ratio, etc.)
   - A list of trades executed by the strategy

### 4. Interpreting the Backtesting Results

The console output displays key performance metrics:

- **Return [%]**: Total percentage return of the strategy
- **Exposure [%]**: Percentage of time invested in the market
- **Equity Final [$]**: Final account value
- **Equity Peak [$]**: Maximum account value reached
- **Return (Ann.) [%]**: Annualized return percentage
- **Volatility (Ann.) [%]**: Annualized volatility
- **Sharpe Ratio**: Risk-adjusted return (higher is better)
- **Sortino Ratio**: Similar to Sharpe but only considers downside risk
- **Max. Drawdown [%]**: Largest percentage drop from peak to trough
- **Avg. Drawdown [%]**: Average of all drawdowns
- **Max. Drawdown Duration**: Longest time to recover from a drawdown
- **Avg. Drawdown Duration**: Average time to recover from drawdowns
- **# Trades**: Total number of trades executed
- **Win Rate [%]**: Percentage of winning trades
- **Best Trade [%]**: Highest return from a single trade
- **Worst Trade [%]**: Worst loss from a single trade
- **Avg. Trade [%]**: Average return per trade
- **Max. Trade Duration**: Longest time a position was held
- **Avg. Trade Duration**: Average time positions were held
- **Profit Factor**: Gross profit divided by gross loss
- **Expectancy [%]**: Average trade return x Win rate - Average loss x Loss rate
- **SQN**: System Quality Number (measures strategy robustness)

The trade list shows detailed information about each individual trade:
- **Size**: Position size
- **Entry**: Entry date
- **Exit**: Exit date  
- **EntryPrice**: Price at entry
- **ExitPrice**: Price at exit
- **PnL**: Profit or loss in dollars
- **Return %**: Percentage return for the trade

### 5. Understanding the Matrix Display

The dot matrix display alternates between showing:
1. The current price of the selected symbol
2. The trading recommendation ("BUY", "SELL", "HOLD", etc.)

Recommendations are color-coded:
- **Green**: Strong buy signal
- **Light Green**: Weak buy signal
- **Gray**: Hold/neutral signal
- **Orange**: Weak sell signal
- **Red**: Strong sell signal

### 6. Indicator LED Meanings

The status LEDs at the bottom of the interface provide system status:
- **PWR** (Red): Power indicator, always on (click for an Easter egg!)
- **CPU** (Green): Processor activity during calculations
- **DATA** (Yellow): Data transfer activity
- **COM** (Cyan): Communication activity
- **ERR** (Red): Error indicator, lights up when errors occur

## Advanced Usage Tips

### Optimizing Strategy Parameters

To find the optimal parameters for a strategy:
1. Run multiple backtests with different parameter values
2. Compare the results, focusing on:
   - Risk-adjusted returns (Sharpe/Sortino ratios)
   - Maximum drawdown
   - Win rate
   - Profit factor
3. Be cautious of over-optimization that may not perform well with future data

### Adding Custom Symbols

You can analyze any symbol supported by Yahoo Finance:
1. Enter the ticker symbol in the "Custom" field
2. For international stocks, use the appropriate suffix:
   - London Stock Exchange: `.L` (e.g., `VOD.L`)
   - Tokyo Stock Exchange: `.T` (e.g., `7203.T`)
   - Frankfurt Stock Exchange: `.F` (e.g., `VOW.F`)

### Understanding Strategy Limitations

Each strategy performs differently under various market conditions:
- **Trend-following strategies** (SMA Cross, MACD, Ichimoku) work best in strong trending markets
- **Mean-reversion strategies** (RSI, Bollinger Bands) work best in range-bound markets
- **Calendar strategies** (Day of Week, Moon phases) test market anomalies and may have limited practical value

### Extending the Time Period

For more robust backtesting:
1. Modify the `DEFAULT_DATA_PERIOD` in `config.py` (e.g., change "5y" to "10y" or "max")
2. Restart the application
3. Load data for your symbol

## Troubleshooting

### Data Loading Issues

- **No data available**: Verify the symbol exists and is correctly entered
- **Limited data**: Some newer stocks have limited historical data
- **Missing prices**: Check for corporate actions (splits, mergers) that might affect the data

### Backtest Execution Problems

- **TA-Lib errors**: Ensure TA-Lib is correctly installed (see TA-Lib Installation Guide)
- **Parameters not taking effect**: Make sure to press Enter after changing parameter values
- **Error messages**: Check the console output and ERR LED for specific error details

### Display Issues

- **Missing vintage LED indicators**: This could indicate a problem with the Tkinter canvas implementation
- **Dot matrix display not updating**: The display alternates between price and recommendation; wait a few seconds for it to switch

## Feature Highlights 

### Vintage UI Elements

The application features custom-built vintage UI elements:
- **WornLED**: Simulated worn LED indicators with flickering effects
- **MatrixText**: Dot matrix display with customizable text and colors
- **Retro color scheme**: Miami Vice / Fallout inspired color palette

For more information about these custom UI elements, check out [Rick's Vintage Lights repository](https://github.com/bneidlinger/Rick-s_Vintage_Lights) that demonstrates similar retro indicators.

### Automated Trading Recommendations

The application includes a proprietary recommendation engine that:
1. Analyzes multiple technical indicators (SMAs, RSI, MACD, Bollinger Bands, ADX)
2. Calculates a composite score based on indicator values and relationships
3. Generates a color-coded recommendation (BUY, WEAK BUY, HOLD, WEAK SELL, SELL)
4. Displays the recommendation on the dot matrix display

## Conclusion

The Retro Trading Console combines powerful backtesting capabilities with a unique vintage aesthetic. By following this guide, you should be able to:
- Load and visualize historical stock data
- Configure and run strategy backtests
- Interpret performance metrics
- Understand trading recommendations

Remember that backtested performance does not guarantee future results. Use this tool as one component of a comprehensive trading strategy development process.

Happy trading and enjoy the retro experience!

# trading/backtester.py
# Handles running backtests using the backtesting.py library
# MODIFIED: Reinstate workaround using bt._results._trades

from backtesting import Backtest
import pandas as pd

# Dictionary mapping column names expected by backtesting.py to potential lowercase versions
COLUMN_MAPPING = {
    'Open': 'open',
    'High': 'high',
    'Low': 'low',
    'Close': 'close',
    'Volume': 'volume'
}


# Accept **strategy_params again
def run_backtest(strategy_class, data: pd.DataFrame, cash: int = 10000, commission: float = 0.001, **strategy_params):
    """
    Runs a backtest for a given strategy and data.
    Strategy-specific parameters are passed via **strategy_params to bt.run().

    Args:
        strategy_class: The strategy class (inheriting from backtesting.Strategy).
        data (pd.DataFrame): DataFrame with historical OHLCV data (lowercase columns).
        cash (int): Initial cash for the backtest.
        commission (float): Commission rate per trade (e.g., 0.001 for 0.1%).
        **strategy_params: Keyword arguments (parameters) to pass to the strategy for this run.

    Returns:
        tuple: (stats, backtest_object)
               stats (pd.Series): Backtesting statistics including '_trades'.
               backtest_object (Backtest): The Backtest instance for potential plotting.
               Returns (None, None) if backtest fails.
    """
    if data is None or data.empty:
        print("Error: Cannot run backtest with empty data.")
        return None, None
    required_lowercase = list(COLUMN_MAPPING.values())
    if not all(col in data.columns for col in required_lowercase):
        print(
            f"Error: Data missing required columns for backtesting. Need: {required_lowercase}, Found: {data.columns.tolist()}")
        return None, None
    backtest_data = data.copy()
    rename_dict = {v: k for k, v in COLUMN_MAPPING.items()}
    backtest_data.rename(columns=rename_dict, inplace=True)
    required_uppercase = list(COLUMN_MAPPING.keys())
    if not all(col in backtest_data.columns for col in required_uppercase):
        print(f"Error: Column renaming failed. Need: {required_uppercase}, Found: {backtest_data.columns.tolist()}")
        return None, None

    print(f"\n--- Running Backtest ---")
    print(f"Strategy: {strategy_class.__name__}")
    print(f"Initial Cash: {cash:,.2f}")
    print(f"Commission: {commission:.4f}")
    # Print strategy parameters being used
    print(f"Parameters: {strategy_params}")

    try:
        # Initialize Backtest WITHOUT passing strategy_params to constructor
        bt = Backtest(backtest_data, strategy_class, cash=cash, commission=commission)

        # Run backtest WITH strategy_params BUT WITHOUT return_trades argument
        stats = bt.run(**strategy_params)

        # WORKAROUND REINSTATED: Manually add the trades DataFrame to the stats Series
        # Accessing internal _results._trades attribute, necessary due to run() conflict
        try:
            # Attempt to access trades via the internal attribute (note underscore on _trades)
            stats['_trades'] = bt._results._trades
            print("Successfully retrieved trades via bt._results._trades")
        except AttributeError:
            print("Warning: Could not access bt._results._trades. Trade list might be missing.")
            # Ensure the '_trades' key exists even if empty
            stats['_trades'] = pd.DataFrame()

        print("--- Backtest Complete ---")
        return stats, bt
    except Exception as e:
        print(f"Error during backtest execution: {e}")
        # import traceback # Uncomment for full traceback
        # traceback.print_exc()
        return None, None
# trading/ml/features.py
# Feature engineering for ML stock prediction

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional


class FeatureEngineer:
    """Class responsible for generating features from price data for ML models."""

    def __init__(self):
        """Initialize the feature engineer."""
        pass

    @staticmethod
    def add_price_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        Add basic price-derived features to the dataframe.

        Args:
            df: DataFrame with at least OHLCV data

        Returns:
            DataFrame with additional features
        """
        if df is None or df.empty:
            return df

        # Create a copy to avoid modifying the original
        result = df.copy()

        # Ensure we have the necessary columns
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        missing_cols = [col for col in required_cols if col not in result.columns]
        if missing_cols:
            print(f"Warning: Missing columns {missing_cols} for feature engineering")
            # Try to work with what we have

        # Calculate returns if 'close' is available
        if 'close' in result.columns:
            # Daily return
            result['return_1d'] = result['close'].pct_change()

            # Logarithmic return
            result['log_return'] = np.log(result['close']).diff()

            # N-day returns (5, 10, 20)
            for n in [5, 10, 20]:
                if len(result) > n:
                    result[f'return_{n}d'] = result['close'].pct_change(n)

        # High-Low range
        if all(col in result.columns for col in ['high', 'low']):
            result['hl_range'] = (result['high'] - result['low']) / result['low']

        # Open-Close range
        if all(col in result.columns for col in ['open', 'close']):
            result['oc_range'] = (result['close'] - result['open']) / result['open']

        # Volume features if available
        if 'volume' in result.columns:
            # Log volume
            result['log_volume'] = np.log(result['volume'] + 1)  # +1 to handle zeros

            # Volume change
            result['volume_change'] = result['volume'].pct_change()

            # Relative volume (compared to 20-day average)
            if len(result) > 20:
                result['relative_volume'] = result['volume'] / result['volume'].rolling(20).mean()
        
        # Add capital gains column (zero values for compatibility with previously trained models)
        result['capital gains'] = 0.0
        
        # Use additional Alpha Vantage specific features if available
        if 'implied_dividend_adjustment' in df.columns:
            result['implied_dividend_adjustment'] = df['implied_dividend_adjustment']

        return result

    @staticmethod
    def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        Add technical indicators as features to the dataframe.
        Uses pandas built-in functions to avoid TA-Lib dependency at this step.

        Args:
            df: DataFrame with at least 'close' price data

        Returns:
            DataFrame with technical indicators added
        """
        if df is None or df.empty or 'close' not in df.columns:
            return df

        result = df.copy()
        close = result['close']

        # Simple Moving Averages (SMA)
        for period in [5, 10, 20, 50, 200]:
            if len(result) > period:
                result[f'sma_{period}'] = close.rolling(window=period).mean()

                # Distance from SMA (%)
                result[f'close_to_sma_{period}'] = (close / result[f'sma_{period}'] - 1) * 100

        # Exponential Moving Averages (EMA)
        for period in [5, 10, 20, 50, 200]:
            if len(result) > period:
                result[f'ema_{period}'] = close.ewm(span=period, adjust=False).mean()

                # Distance from EMA (%)
                result[f'close_to_ema_{period}'] = (close / result[f'ema_{period}'] - 1) * 100

        # Bollinger Bands (20, 2)
        if len(result) > 20:
            ma = close.rolling(window=20).mean()
            std = close.rolling(window=20).std()
            result['bb_upper'] = ma + (std * 2)
            result['bb_lower'] = ma - (std * 2)
            result['bb_width'] = (result['bb_upper'] - result['bb_lower']) / ma
            # Position within BB (0 = lower band, 1 = upper band)
            result['bb_pos'] = (close - result['bb_lower']) / (result['bb_upper'] - result['bb_lower'])

        # RSI (using Simple Method with pandas)
        if len(result) > 14:
            delta = close.diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(window=14).mean()
            avg_loss = loss.rolling(window=14).mean()
            rs = avg_gain / avg_loss
            result['rsi_14'] = 100 - (100 / (1 + rs))

        # MACD (12, 26, 9)
        if len(result) > 26:
            ema12 = close.ewm(span=12, adjust=False).mean()
            ema26 = close.ewm(span=26, adjust=False).mean()
            result['macd'] = ema12 - ema26
            result['macd_signal'] = result['macd'].ewm(span=9, adjust=False).mean()
            result['macd_hist'] = result['macd'] - result['macd_signal']

        return result

    @staticmethod
    def add_date_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        Add date-related features for time series modeling.

        Args:
            df: DataFrame with DatetimeIndex

        Returns:
            DataFrame with additional date features
        """
        if df is None or df.empty:
            return df

        result = df.copy()

        # Extract date components
        result['day_of_week'] = result.index.dayofweek
        result['day_of_month'] = result.index.day
        result['month'] = result.index.month
        result['year'] = result.index.year
        result['quarter'] = result.index.quarter

        # Is month start/end
        result['is_month_start'] = result.index.is_month_start.astype(int)
        result['is_month_end'] = result.index.is_month_end.astype(int)

        # Is quarter start/end
        result['is_quarter_start'] = result.index.is_quarter_start.astype(int)
        result['is_quarter_end'] = result.index.is_quarter_end.astype(int)

        # Is year start/end
        result['is_year_start'] = result.index.is_year_start.astype(int)
        result['is_year_end'] = result.index.is_year_end.astype(int)

        return result

    @staticmethod
    def engineer_features(df: pd.DataFrame, with_date_features: bool = True, min_required_samples: int = 100, 
                          economic_data: Optional[Dict[str, pd.DataFrame]] = None) -> pd.DataFrame:
        """
        Complete feature engineering process.

        Args:
            df: DataFrame with at least OHLCV data
            with_date_features: Whether to include date-based features
            min_required_samples: Minimum number of samples required after processing
            economic_data: Optional dictionary of economic indicators to add to features

        Returns:
            DataFrame with all engineered features
        """
        if df is None or df.empty:
            return df

        print("Preparing data: Engineering features...")

        # Check if we have enough data
        if len(df) < 50:  # Absolute minimum for reasonable feature engineering
            print(f"Warning: Dataset is very small ({len(df)} samples). Features may be unreliable.")
        
        # Chain all feature engineering steps
        result = FeatureEngineer.add_price_features(df)
        result = FeatureEngineer.add_technical_indicators(result)

        # Add date features if requested and index is DatetimeIndex
        if with_date_features and isinstance(result.index, pd.DatetimeIndex):
            result = FeatureEngineer.add_date_features(result)

        # --- Handle NaN values ---
        # 1. Forward fill NaN values created by lagging features
        result = result.ffill()
        
        # 2. For any remaining NaNs (e.g., at the beginning), use backward fill with limit
        result = result.bfill(limit=5)
        
        # 3. Any still remaining NaNs (rare edge cases), fill with column medians
        for col in result.columns:
            if result[col].isna().any():
                median_value = result[col].median()
                if pd.isna(median_value):  # If median is also NaN, use 0
                    result[col].fillna(0, inplace=True)
                else:
                    result[col].fillna(median_value, inplace=True)
                    
        # Add economic indicators if provided
        if economic_data and isinstance(result.index, pd.DatetimeIndex):
            print("Adding economic indicators to features...")
            
            # Process each economic indicator
            for indicator_name, indicator_df in economic_data.items():
                if indicator_df is None or indicator_df.empty:
                    continue
                    
                try:
                    # Ensure index is datetime
                    if not isinstance(indicator_df.index, pd.DatetimeIndex):
                        print(f"Warning: Economic indicator {indicator_name} doesn't have DatetimeIndex. Skipping.")
                        continue
                    
                    # Get the latest value for each date in our price data
                    for col in indicator_df.columns:
                        if col in ['date']:  # Skip index/metadata columns
                            continue
                            
                        # Create a resampled version aligned to price data
                        feature_name = f"economic_{indicator_name.lower()}_{col.lower()}"
                        
                        # Resample to daily frequency, forward filling values
                        # This ensures we have a value for each trading day
                        daily_series = indicator_df[col].resample('D').ffill()
                        
                        # Merge with our price data by aligning on dates
                        for date in result.index:
                            date_str = date.strftime('%Y-%m-%d')
                            # Find the latest available economic data point at or before this date
                            available_dates = daily_series.index[daily_series.index <= date]
                            if not available_dates.empty:
                                latest_date = available_dates[-1]
                                result.loc[date, feature_name] = daily_series.loc[latest_date]
                            else:
                                # No data available before this date
                                result.loc[date, feature_name] = np.nan
                        
                        # Fill any NaN values
                        if result[feature_name].isna().any():
                            # Use forward fill first
                            result[feature_name] = result[feature_name].ffill()
                            # Then use backward fill for initial NaNs
                            result[feature_name] = result[feature_name].bfill()
                            # Any remaining NaNs, use median or 0
                            median_value = result[feature_name].median()
                            if pd.isna(median_value):
                                result[feature_name].fillna(0, inplace=True)
                            else:
                                result[feature_name].fillna(median_value, inplace=True)
                                
                    print(f"Added {indicator_name} features")
                        
                except Exception as e:
                    print(f"Error adding economic indicator {indicator_name}: {e}")
        
        # Drop any remaining full NaN rows if absolutely necessary
        if result.isna().any().any():
            print("Warning: Some NaN values remained after filling methods.")
            result = result.dropna()
        
        # Final check if we have enough data after processing
        if len(result) < min_required_samples:
            print(f"Warning: After processing, only {len(result)} samples remain, " 
                  f"which is below the recommended minimum of {min_required_samples}.")
        
        return result

    @staticmethod
    def get_target_variable(df: pd.DataFrame, horizon: int = 5, threshold: float = 0.01) -> pd.DataFrame:
        """
        Create target variable for ML classification or regression.

        Args:
            df: DataFrame with 'close' price data
            horizon: Prediction horizon in days
            threshold: Price change threshold for classification (e.g., 0.01 for 1%)

        Returns:
            DataFrame with target variables added
        """
        if df is None or df.empty or 'close' not in df.columns:
            return df

        result = df.copy()

        # Future returns at specified horizon
        # Ensure we shift correctly; shift(-horizon) looks into the future
        result[f'future_return_{horizon}d'] = result['close'].pct_change(periods=horizon).shift(-horizon)

        # Classification target: 1 for up, 0 for sideways, -1 for down
        # Uses threshold to determine if change is significant
        result[f'target_direction_{horizon}d'] = 0  # Default to neutral (0)

        # Find indices where future return exceeds positive threshold
        up_indices = result[f'future_return_{horizon}d'] > threshold
        result.loc[up_indices, f'target_direction_{horizon}d'] = 1

        # Find indices where future return is below negative threshold
        down_indices = result[f'future_return_{horizon}d'] < -threshold
        result.loc[down_indices, f'target_direction_{horizon}d'] = -1

        # Binary classification: 1 for up, 0 for down/neutral (ignoring threshold for this simple binary)
        # result[f'target_binary_{horizon}d'] = (result[f'future_return_{horizon}d'] > 0).astype(int)
        # Let's keep the focus on the 3-class target for now.

        # Drop the future return column as it introduces lookahead bias if kept during training on features
        # result = result.drop(columns=[f'future_return_{horizon}d'])
        # --> Correction: Don't drop it here. It's needed for regression and excluded during feature prep anyway.

        return result

    @staticmethod
    def prepare_ml_data(df: pd.DataFrame, target_col: str, test_size: float = 0.2,
                        exclude_cols: Optional[List[str]] = None) -> Tuple[
        np.ndarray, np.ndarray, np.ndarray, np.ndarray, List[str]]:
        """
        Prepare data for ML modeling, splitting into train/test sets.

        Args:
            df: DataFrame with features and target
            target_col: Target column name
            test_size: Proportion of data to use for testing
            exclude_cols: List of columns to exclude from features

        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        # Validate inputs
        if df is None or df.empty or target_col not in df.columns:
            raise ValueError(f"Invalid dataframe or target column '{target_col}' not found")

        # Remove NaN values from dataset
        clean_df = df.dropna()
        if len(clean_df) == 0:
            raise ValueError("No data left after removing NaN values")

        # Exclude columns
        if exclude_cols is None:
            exclude_cols = []
        exclude_cols.append(target_col)  # Always exclude the target

        # Add all future target columns to exclude list (any that start with 'future_' or 'target_')
        exclude_cols.extend([col for col in clean_df.columns if col.startswith(('future_', 'target_'))])

        # Prepare feature matrix
        feature_cols = [col for col in clean_df.columns if col not in exclude_cols]
        X = clean_df[feature_cols].values
        y = clean_df[target_col].values

        # Time-series train/test split (no random shuffle, use last portion for test)
        split_idx = int(len(X) * (1 - test_size))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]

        return X_train, X_test, y_train, y_test, feature_cols
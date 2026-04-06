# trading/ml/service.py
# Service layer for ML predictions

import os
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Assuming FeatureEngineer and ModelManager are correctly imported
from trading.ml.features import FeatureEngineer
from trading.ml.models import ModelManager
# Import config if needed for default threshold, or define it here
# from config import ML_DEFAULT_THRESHOLD # Example if you add it to config

class MlPredictionService:
    """
    Service layer for managing ML model training, loading, prediction,
    and generating hybrid recommendations for stock analysis.
    """

    # Direction labels for classification results
    DIRECTION_LABELS = {
        1: "UP",
        0: "NEUTRAL",
        -1: "DOWN"
    }

    # Confidence level thresholds
    CONFIDENCE_THRESHOLDS = {
        "STRONG": 0.80,
        "MODERATE": 0.65,
        "WEAK": 0.55
    }

    def __init__(self, model_dir: str = 'data/models'):
        """
        Initialize the ML prediction service.

        Args:
            model_dir: Directory where models are stored and loaded from.
        """
        print("ML Prediction Service Initialized.") # Log initialization
        self.model_manager = ModelManager(model_dir=model_dir)
        self.feature_engineer = FeatureEngineer()
        # self.current_symbol = None # State like current symbol is better managed by the calling UI (App)
        self.loaded_model_info = None # Stores metadata about the currently loaded model

    def prepare_data(self, df: pd.DataFrame, prediction_horizon: int = 5,
                     target_threshold: float = 0.01, 
                     economic_data: Optional[Dict[str, pd.DataFrame]] = None) -> Optional[pd.DataFrame]:
        """
        Prepare data for ML by engineering features and adding target variables.

        Args:
            df: DataFrame with OHLCV data (lowercase columns expected).
            prediction_horizon: Horizon for target variable calculation in days.
            target_threshold: Threshold for classifying UP/DOWN vs NEUTRAL.
            economic_data: Optional economic indicators to include in feature engineering.

        Returns:
            DataFrame with engineered features and target variables, or None if error.
        """
        if df is None or df.empty:
            print("Error: Cannot prepare data, input DataFrame is empty.")
            return None

        # print(f"Preparing data: Engineering features...") # Verbose logging
        # Engineer features (assuming engineer_features handles NaN/dropna)
        features_df = self.feature_engineer.engineer_features(
            df, 
            with_date_features=True,
            min_required_samples=50,  
            economic_data=economic_data
        )
        
        if features_df is None or features_df.empty:
             print("Error: Feature engineering resulted in empty DataFrame.")
             return None
        # print(f"Features engineered. Shape: {features_df.shape}") # Verbose logging


        # Add target variable (needed for training, useful context for prediction)
        # print(f"Adding target variables (Horizon: {prediction_horizon}d, Threshold: {target_threshold:.4f})...") # Verbose logging
        if len(features_df) > prediction_horizon:
            # Pass the threshold to the target variable function
            features_df = self.feature_engineer.get_target_variable(
                features_df, horizon=prediction_horizon, threshold=target_threshold)
            # print(f"Target variables added. Shape: {features_df.shape}") # Verbose logging
            # Check if target columns were actually added
            target_col_name = f'target_direction_{prediction_horizon}d'
            if target_col_name not in features_df.columns:
                 print(f"Warning: Target column '{target_col_name}' not found after get_target_variable.")
                 # It might be okay if just predicting, but crucial for training.
        else:
            print(f"Warning: Not enough data ({len(features_df)}) to calculate target for horizon {prediction_horizon}.")
            # Cannot add target, proceed with features only (might fail training later)

        return features_df

    def train_model(self, symbol: str, df: pd.DataFrame, model_type: str = 'random_forest',
                    prediction_type: str = 'classification', prediction_horizon: int = 5,
                    test_size: float = 0.2, target_threshold: float = 0.01,
                    economic_data: Optional[Dict[str, pd.DataFrame]] = None) -> Dict:
        """
        Train an ML model, evaluate it, and save it.

        Args:
            symbol: Stock symbol.
            df: DataFrame with OHLCV data.
            model_type: Type of model to train (key from ModelManager.CLASSIFICATION_MODELS/REGRESSION_MODELS).
            prediction_type: 'classification' or 'regression'.
            prediction_horizon: Horizon for predictions in days.
            test_size: Portion of data to use for testing (e.g., 0.2 for 20%).
            target_threshold: Threshold for classifying UP/DOWN vs NEUTRAL (used in data prep).
            economic_data: Optional dictionary of economic indicators to include in feature engineering.

        Returns:
            Dictionary containing 'model_info', 'train_results', and 'metrics'.

        Raises:
            ValueError: If data preparation fails, target column is missing, or prediction_type is invalid.
            Exception: If errors occur during data splitting, training, evaluation, or saving.
        """
        # print(f"\n--- Starting ML Training for {symbol} ---") # Logging handled by App
        # print(f"Model: {model_type}, Type: {prediction_type}, Horizon: {prediction_horizon}d, Test Size: {test_size:.1%}, Threshold: {target_threshold:.4f}")

        # 1. Prepare Data (including target variable)
        prepared_data = self.prepare_data(
            df, 
            prediction_horizon=prediction_horizon, 
            target_threshold=target_threshold,
            economic_data=economic_data
        )
        if prepared_data is None or prepared_data.empty:
            # Logged in prepare_data
            raise ValueError(f"Failed to prepare data for {symbol}")

        # 2. Define Target Column
        if prediction_type == 'classification':
            target_col = f'target_direction_{prediction_horizon}d'
        elif prediction_type == 'regression':
            target_col = f'future_return_{prediction_horizon}d'
        else:
             raise ValueError(f"Invalid prediction_type: {prediction_type}")

        # Make sure the target column exists after data prep (crucial for training)
        if target_col not in prepared_data.columns:
            raise ValueError(f"Target column '{target_col}' not found in prepared data. Insufficient data for horizon?")

        # 3. Split Data into Train/Test
        # print("Splitting data into training and testing sets...") # Logging handled by App
        try:
            X_train, X_test, y_train, y_test, feature_cols = self.feature_engineer.prepare_ml_data(
                prepared_data, target_col=target_col, test_size=test_size)
            # print(f"Data split: Train shape {X_train.shape}, Test shape {X_test.shape}") # Logging handled by App
            # print(f"Using {len(feature_cols)} features: {feature_cols}") # Logging handled by App
        except Exception as e:
             print(f"Error during data splitting: {e}")
             raise # Re-raise

        # 4. Train Model & Evaluate
        train_results = {}
        metrics = {}
        model_path = None
        try:
            if prediction_type == 'classification':
                print(f"Training classification model: {model_type}") # Log action
                train_results = self.model_manager.train_classification_model(
                    X_train, y_train, model_type=model_type, feature_cols=feature_cols)
                print("Evaluating classification model...") # Log action
                metrics = self.model_manager.evaluate_classification(X_test, y_test)
                print(f"Evaluation Metrics: {metrics}") # Log result
            # --- Add Regression Training/Evaluation Here ---
            # elif prediction_type == 'regression':
            #     print(f"Training regression model: {model_type}")
            #     train_results = self.model_manager.train_regression_model(X_train, y_train, model_type=model_type, feature_cols=feature_cols)
            #     print("Evaluating regression model...")
            #     metrics = self.model_manager.evaluate_regression(X_test, y_test)
            #     print(f"Evaluation Metrics: {metrics}")
            else:
                 raise ValueError(f"Training not implemented for prediction_type: {prediction_type}")

            # 5. Save Model
            print(f"Saving model to: {self.model_manager.model_dir}") # Log action
            model_path = self.model_manager.save_model(symbol, horizon=prediction_horizon)
            print(f"Model saved successfully.") # Log result

        except Exception as e:
            print(f"An error occurred during model training, evaluation, or saving: {e}")
            # Reset current model in manager on error to prevent inconsistent state
            self.model_manager.current_model = None
            self.model_manager.feature_columns = None
            raise # Re-raise the exception

        # 6. Update Service State (Store metadata about the successfully trained model)
        # This info will be used by predict() if this model remains loaded.
        self.loaded_model_info = {
            'symbol': symbol,
            'model_class_name': type(self.model_manager.current_model).__name__,
            'model_config_name': model_type, # Store the key used ('random_forest')
            'prediction_type': prediction_type, # Store 'classification' or 'regression'
            'horizon': prediction_horizon,
            'path': model_path,
            'metrics': metrics, # Store evaluation metrics from this training run
            'feature_columns': self.model_manager.feature_columns, # Store feature names used
            'timestamp': datetime.now().strftime('%Y%m%d_%H%M%S') # Add training time
        }
        # print("--- ML Training Complete ---") # Logging handled by App

        # 7. Combine Results for Return to Caller (App)
        results = {
            'model_info': self.loaded_model_info, # Metadata just created
            'train_results': train_results, # Contains model object, raw importances etc. from manager
            'metrics': metrics # Pass metrics back explicitly
        }

        return results

    def load_model_for_symbol(self, symbol: str, prediction_horizon: int = 5, model_type: str = 'classification') -> bool:
        """
        Load the latest pre-trained model for a symbol, horizon, and type.
        Updates the service's internal state (`self.loaded_model_info`).

        Args:
            symbol: Stock symbol.
            prediction_horizon: Prediction horizon in days.
            model_type: 'classification' or 'regression'. Determines model filename pattern.

        Returns:
            True if a model was successfully loaded, False otherwise.
        """
        # print(f"Attempting to load latest '{model_type}' model for {symbol} (Horizon: {prediction_horizon}d)...") # Logging handled by App
        self.loaded_model_info = None # Clear previous info before attempting load

        # Use the model manager to find and load the latest model file
        # NOTE: Assumes ModelManager.load_latest_model is updated to accept/use model_type for filtering filenames
        model_data = self.model_manager.load_latest_model(symbol, horizon=prediction_horizon, model_type=model_type)

        if model_data is None:
            # print(f"No suitable pre-trained model found.") # Logging handled by App
            return False

        # Store metadata about the loaded model in the service's state
        self.loaded_model_info = {
            'symbol': symbol,
            # Get class name from the actual loaded model object in the manager
            'model_class_name': type(self.model_manager.current_model).__name__,
             # Get model type ('classification'/'regression') from manager state after load
            'prediction_type': self.model_manager.current_model_type,
            # Get horizon from the loaded model data if available, otherwise use requested horizon
            'horizon': model_data.get('horizon', prediction_horizon),
            # Get path from the loaded model data (added by load_latest_model/load_model)
            'path': model_data.get('filepath'),
            'metrics': None, # Metrics aren't stored with the model file
             # Get feature columns from the manager state after load
            'feature_columns': self.model_manager.feature_columns,
            # Get timestamp from the loaded model data
            'timestamp': model_data.get('timestamp')
        }
        # print(f"Successfully loaded model: {self.loaded_model_info.get('model_class_name')}") # Logging handled by App
        return True

    # --- predict method with target_threshold fix ---
    def predict(self, df: pd.DataFrame, target_threshold: float = 0.01, 
               economic_data: Optional[Dict[str, pd.DataFrame]] = None) -> Dict:
        """
        Make predictions using the currently loaded model.
        Requires a model to be loaded first via load_model_for_symbol or train_model.

        Args:
            df: DataFrame with OHLCV data (must contain necessary history for feature eng).
            target_threshold (float): The significance threshold used for preparing data
                                      (ensures consistency, though not directly used in prediction logic itself).
            economic_data: Optional economic indicators to include in feature engineering.

        Returns:
            Dictionary with prediction results (direction, confidence, etc.).

        Raises:
            ValueError: If no model is loaded, data is invalid, or features are missing.
        """
        if self.loaded_model_info is None or self.model_manager.current_model is None:
            raise ValueError("No model has been loaded or trained. Call load_model_for_symbol or train_model first.")
        if df is None or df.empty:
            raise ValueError("No data provided for prediction.")

        current_symbol_for_log = self.loaded_model_info.get('symbol', 'Unknown')
        # print(f"\n--- Generating ML Prediction for {current_symbol_for_log} ---") # Logging handled by App
        # print(f"Using model: {self.loaded_model_info.get('model_class_name')}, Horizon: {self.loaded_model_info.get('horizon')}d") # Logging handled by App

        # 1. Prepare Features for the *entire* dataframe needed for context
        prepared_data = self.prepare_data(
            df,
            prediction_horizon=self.loaded_model_info.get('horizon', 5),
            target_threshold=target_threshold, # Pass the threshold
            economic_data=economic_data
            )
        if prepared_data is None or prepared_data.empty:
            raise ValueError("Failed to prepare data for prediction (feature engineering failed).")

        # 2. Get the *last* row of features needed for prediction
        required_features = self.loaded_model_info.get('feature_columns')
        if not required_features:
             raise ValueError("Model was loaded without feature column information. Cannot make predictions.")

        # Check if all required features exist in the prepared data and add missing ones with zeros
        missing_features = [f for f in required_features if f not in prepared_data.columns]
        if missing_features:
            print(f"Warning: Adding missing features with zero values: {missing_features}")
            # Add missing features with zeros
            for feature in missing_features:
                prepared_data[feature] = 0.0

        # Select the last row and only the required feature columns
        try:
            last_feature_vector = prepared_data[required_features].iloc[-1:] # Keep as DataFrame row initially
            X_predict = last_feature_vector.values # Convert to numpy array for prediction
        except IndexError:
            raise ValueError("Could not select the last row of features. Prepared data might be empty after processing.")
        except KeyError as e:
            # Defensive fallback if we still have missing features
            print(f"Error selecting required features for prediction: {e}")
            raise ValueError(f"Prepared data still missing required features for the loaded model: {e}. Available columns: {prepared_data.columns.tolist()}")


        # 3. Make Prediction based on loaded model type
        prediction_type = self.loaded_model_info.get('prediction_type', 'classification')
        prediction_result = {}

        try:
            if prediction_type == 'classification':
                pred_class, pred_proba = self.model_manager.predict_classification(X_predict)
                prediction = int(pred_class[0]) # Get the single prediction
                prediction_label = self.DIRECTION_LABELS.get(prediction, "UNKNOWN")

                # Get confidence from probabilities
                confidence = None
                confidence_label = "UNKNOWN"
                probabilities_list = None
                if pred_proba is not None and len(pred_proba) > 0:
                    probabilities = pred_proba[0] # Probabilities for the single prediction
                    probabilities_list = probabilities.tolist() # Convert to list for storage/display
                    confidence = float(np.max(probabilities)) # Highest probability as confidence

                    # Determine confidence level string
                    if confidence >= self.CONFIDENCE_THRESHOLDS["STRONG"]: confidence_label = "STRONG"
                    elif confidence >= self.CONFIDENCE_THRESHOLDS["MODERATE"]: confidence_label = "MODERATE"
                    elif confidence >= self.CONFIDENCE_THRESHOLDS["WEAK"]: confidence_label = "WEAK"
                    else: confidence_label = "UNCERTAIN"
                else:
                     # Handle cases where probabilities aren't available
                     confidence_label = "N/A" # Indicate not applicable


                prediction_result = {
                    'prediction': prediction, # -1, 0, or 1
                    'direction': prediction_label, # 'UP', 'NEUTRAL', 'DOWN'
                    'confidence': confidence, # Float (highest probability) or None
                    'confidence_level': confidence_label, # 'STRONG', 'MODERATE', etc.
                    'probabilities': probabilities_list, # List of probabilities per class or None
                    # Safely get date and format
                    'date': prepared_data.index[-1].strftime('%Y-%m-%d') if isinstance(prepared_data.index[-1], pd.Timestamp) else str(prepared_data.index[-1]),
                    'horizon': self.loaded_model_info.get('horizon', 5)
                }
                # print(f"ML Prediction: {prediction_label}, Confidence: {confidence:.3f if confidence is not None else 'N/A'} ({confidence_label})") # Logging handled by App

            # --- Add Regression Prediction Here ---
            # elif prediction_type == 'regression':
            #     predicted_value = self.model_manager.predict_regression(X_predict)
            #     # ... process regression output ...
            #     prediction_result = { ... }
            else:
                 raise ValueError(f"Prediction not implemented for model type: {prediction_type}")

        except Exception as e:
             print(f"Error during ML prediction execution: {e}")
             # Return an error structure or re-raise
             prediction_result = { 'error': str(e) } # Indicate error in result

        return prediction_result


    def get_loaded_feature_importances(self) -> Optional[Dict[str, float]]:
         """Gets feature importances from the currently loaded model via ModelManager."""
         if not self.model_manager or self.model_manager.current_model is None:
             # print("Debug: No model manager or current model in service.") # Optional debug
             return None
         # print("Debug: Calling model_manager.get_current_feature_importances()") # Optional debug
         return self.model_manager.get_current_feature_importances()

    def get_loaded_model_metadata(self) -> Optional[Dict]:
        """Returns metadata about the currently loaded model."""
        # Returns the dictionary stored during load or train
        return self.loaded_model_info

    def get_hybrid_recommendation(self, df: pd.DataFrame, technical_score: float,
                                  adx_value: Optional[float] = None,
                                  target_threshold: float = 0.01,
                                  economic_data: Optional[Dict[str, pd.DataFrame]] = None) -> Dict: # Added parameters
        """
        Generate a hybrid recommendation combining ML predictions with technical indicators.
        Assumes an ML model has been loaded and a prediction can be made.

        Args:
            df: DataFrame with OHLCV data (for ML prediction).
            technical_score: Pre-calculated technical analysis score (e.g., -3 to 3).
            adx_value: Optional ADX value for trend strength adjustment.
            target_threshold: Threshold used for preparing data for the predict call.

        Returns:
            Dictionary with hybrid recommendation details.
        """
        # print("\n--- Generating Hybrid Recommendation ---") # Logging handled by App
        ml_prediction = None
        hybrid_recommendation = "ERROR" # Default in case of issues
        hybrid_score = 0.0
        ml_weight = 0.0
        tech_weight = 1.0 # Default to all technical if ML fails
        ml_score = 0.0
        trend_strength = "WEAK" # Default

        # 1. Get ML Prediction
        try:
            # Use the predict method which uses the currently loaded model
            # Pass the threshold and economic data for consistent data prep
            ml_prediction = self.predict(
                df, 
                target_threshold=target_threshold,
                economic_data=economic_data
            )
            if 'error' in ml_prediction:
                 raise ValueError(f"ML Prediction failed: {ml_prediction['error']}")

        except Exception as e:
            print(f"Error getting ML prediction for hybrid: {e}")
            ml_prediction = None # Ensure it's None if prediction fails

        # 2. Calculate Hybrid Score (if ML prediction succeeded)
        if ml_prediction:
            try:
                # ML directional signal (-1, 0, 1)
                ml_signal = ml_prediction.get('prediction', 0)
                ml_score = ml_signal * 3.0 # Scale ML signal

                # ML confidence weight (0.4 to 0.7 based on confidence level)
                confidence_level = ml_prediction.get('confidence_level', 'UNCERTAIN')
                if confidence_level == 'STRONG': ml_weight = 0.70
                elif confidence_level == 'MODERATE': ml_weight = 0.60
                elif confidence_level == 'WEAK': ml_weight = 0.50
                else: ml_weight = 0.40 # UNCERTAIN or N/A

                # Adjust ML weight based on ADX (trend strength) if available
                trend_adjustment = 1.0
                if adx_value is not None:
                    if adx_value > 30: trend_adjustment = 1.15; trend_strength = "STRONG"
                    elif adx_value > 20: trend_adjustment = 1.05; trend_strength = "MODERATE"
                    else: trend_adjustment = 0.90; trend_strength = "WEAK" # Keep WEAK as default otherwise
                    ml_weight *= trend_adjustment
                    # Cap weight between reasonable bounds (e.g., 0.3 to 0.8)
                    ml_weight = max(0.3, min(0.8, ml_weight))

                # Calculate technical weight
                tech_weight = 1.0 - ml_weight

                # Calculate final hybrid score
                hybrid_score = (ml_score * ml_weight) + (technical_score * tech_weight)

                # Generate recommendation string based on hybrid score
                if hybrid_score >= 2.0: hybrid_recommendation = "BUY"
                elif hybrid_score >= 0.5: hybrid_recommendation = "WEAK BUY"
                elif hybrid_score <= -2.0: hybrid_recommendation = "SELL"
                elif hybrid_score <= -0.5: hybrid_recommendation = "WEAK SELL"
                else: hybrid_recommendation = "HOLD"

                # print(f"Hybrid Score: {hybrid_score:.2f} (ML: {ml_score:.1f} * {ml_weight:.2f}, TA: {technical_score:.1f} * {tech_weight:.2f}) -> {hybrid_recommendation}") # Logging handled by App

            except Exception as e:
                 print(f"Error calculating hybrid score: {e}")
                 # Fallback to technical score if hybrid calculation fails
                 hybrid_recommendation = "ERROR" # Indicate calculation error
                 hybrid_score = technical_score # Report TA score as the score
                 ml_weight = 0.0
                 tech_weight = 1.0
                 if adx_value is not None: # Still determine trend strength if possible
                      if adx_value > 30: trend_strength = "STRONG"
                      elif adx_value > 20: trend_strength = "MODERATE"

        else:
            # ML Prediction failed, use only technical score
            # print("ML Prediction failed, using Technical Recommendation only.") # Logging handled by App
            hybrid_score = technical_score # Use TA score
            if technical_score >= 2.0: hybrid_recommendation = "BUY"
            elif technical_score >= 0.5: hybrid_recommendation = "WEAK BUY"
            elif technical_score <= -2.0: hybrid_recommendation = "SELL"
            elif technical_score <= -0.5: hybrid_recommendation = "WEAK SELL"
            else: hybrid_recommendation = "HOLD"
            ml_weight = 0.0
            tech_weight = 1.0
            if adx_value is not None: # Still determine trend strength
                 if adx_value > 30: trend_strength = "STRONG"
                 elif adx_value > 20: trend_strength = "MODERATE"


        # 3. Build the result dictionary
        result = {
            'recommendation': hybrid_recommendation,
            'hybrid_score': hybrid_score,
            'ml_prediction': ml_prediction, # Include the raw ML prediction dict (or None)
            'ml_score': ml_score if ml_prediction and 'error' not in ml_prediction else None, # Use calculated ml_score
            'ml_weight': ml_weight,
            'technical_score': technical_score,
            'technical_weight': tech_weight,
            'trend_strength': trend_strength,
            'horizon': ml_prediction.get('horizon', 5) if ml_prediction and 'error' not in ml_prediction else 5 # Use ML horizon or default
        }

        return result


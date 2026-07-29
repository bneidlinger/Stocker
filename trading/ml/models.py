# trading/ml/models.py

import numpy as np
import joblib
import os
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple, Union, Optional

# scikit-learn imports (ensure these are present)
from sklearn.base import clone
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


class ModelManager:
    """Class to manage ML models for stock price prediction."""

    # Dictionary of available classification models
    CLASSIFICATION_MODELS = {
        'random_forest': RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced'), # Added class_weight
        'gradient_boosting': GradientBoostingClassifier(random_state=42),
        'logistic_regression': LogisticRegression(random_state=42, max_iter=1000, class_weight='balanced'),
    }

    # Dictionary of available regression models
    REGRESSION_MODELS = {
        'linear_regression': LinearRegression(),
        'gradient_boosting_regressor': GradientBoostingRegressor(random_state=42)
    }

    def __init__(self, model_dir: str = 'data/models'):
        """
        Initialize the model manager.

        Args:
            model_dir: Directory to store trained models
        """
        self.model_dir = model_dir
        self.scaler = StandardScaler()
        self.current_model = None
        self.current_model_type = None # 'classification' or 'regression'
        self.feature_columns = None # List of feature names used by the model

        # Create model directory if it doesn't exist
        os.makedirs(model_dir, exist_ok=True)

    def train_classification_model(self, X_train: np.ndarray, y_train: np.ndarray,
                                     model_type: str = 'random_forest',
                                     feature_cols: Optional[List[str]] = None) -> Dict:
        """
        Train a classification model for stock price direction prediction.

        Args:
            X_train: Training feature matrix
            y_train: Training target vector
            model_type: Type of model to train (key from CLASSIFICATION_MODELS)
            feature_cols: List of feature column names (for feature importance)

        Returns:
            Dictionary with training results, including the model object and feature importances if available.
        """
        if model_type not in self.CLASSIFICATION_MODELS:
            raise ValueError(
                f"Unknown model type '{model_type}'. Available models: {list(self.CLASSIFICATION_MODELS.keys())}")

        # --- Feature Scaling ---
        # Fresh scaler per training run, fitted ONLY on the training data
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        print(f"Scaler fitted with {self.scaler.n_features_in_} features.")

        # --- Model Initialization ---
        # clone() the registry entry: the class-level instances are templates
        # and must never be fitted directly (fitting them would share state
        # across training runs and ModelManager instances)
        model = clone(self.CLASSIFICATION_MODELS[model_type])
        print(f"Training classification model: {type(model).__name__}")

        # --- Model Training ---
        try:
            model.fit(X_train_scaled, y_train)
        except Exception as e:
            print(f"Error during model fitting: {e}")
            raise # Re-raise the exception after logging

        # --- Store Current Model Info ---
        self.current_model = model
        self.current_model_type = 'classification'
        # Store feature columns IF they were provided AND match the scaler
        if feature_cols and len(feature_cols) == self.scaler.n_features_in_:
             self.feature_columns = feature_cols
             print(f"Stored {len(self.feature_columns)} feature columns.")
        elif feature_cols:
             print(f"Warning: Provided feature columns ({len(feature_cols)}) don't match scaler features ({self.scaler.n_features_in_}). Not storing column names.")
             self.feature_columns = None # Reset if mismatch
        else:
             self.feature_columns = None # No names provided
             print("No feature column names provided during training.")


        # --- Get Feature Importances (if available) ---
        # This is now handled by get_current_feature_importances after training/loading
        feature_importances_dict = self.get_current_feature_importances()
        if feature_importances_dict:
             print(f"Successfully retrieved feature importances after training.")
        else:
             print(f"Could not retrieve feature importances after training for {type(model).__name__}.")


        return {
            'model': model, # Return the trained model object
            'model_type': model_type,
            'scaler_features': self.scaler.n_features_in_, # Info about scaler
            'feature_importances': feature_importances_dict, # Include importances if found
            'training_samples': len(X_train)
        }

    def predict_classification(self, X: np.ndarray) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """
        Make predictions with the current classification model.
        Ensures data is scaled using the FITTED scaler.

        Args:
            X: Feature matrix to predict (unscaled)

        Returns:
            Tuple of (predicted_classes, prediction_probabilities)
            Probabilities might be None if the model doesn't support predict_proba.
        """
        if self.current_model is None or self.current_model_type != 'classification':
            raise ValueError("No classification model has been trained or loaded yet.")
        if not hasattr(self.scaler, 'n_features_in_') or self.scaler.n_features_in_ is None:
             raise ValueError("Scaler has not been fitted. Train a model first.")

        # --- Validate Input Shape ---
        if X.shape[1] != self.scaler.n_features_in_:
             raise ValueError(f"Input feature count ({X.shape[1]}) does not match scaler/model feature count ({self.scaler.n_features_in_}).")

        # --- Scale Features ---
        # Use transform, NOT fit_transform, on new data
        X_scaled = self.scaler.transform(X)

        # --- Get Predictions ---
        try:
            predictions = self.current_model.predict(X_scaled)
        except Exception as e:
            print(f"Error during prediction: {e}")
            raise

        # --- Get Probabilities (if available) ---
        probabilities = None
        if hasattr(self.current_model, 'predict_proba'):
            try:
                probabilities = self.current_model.predict_proba(X_scaled)
            except Exception as e:
                print(f"Warning: Could not get probabilities from model {type(self.current_model).__name__}: {e}")
                probabilities = None # Ensure it's None on error
        else:
            print(f"Model type {type(self.current_model).__name__} does not support predict_proba.")


        return predictions, probabilities

    def evaluate_classification(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict:
        """
        Evaluate the current classification model on test data.

        Args:
            X_test: Test feature matrix (unscaled)
            y_test: Test target vector

        Returns:
            Dictionary with evaluation metrics
        """
        if self.current_model is None or self.current_model_type != 'classification':
            raise ValueError("No classification model has been trained or loaded for evaluation.")

        # Get predictions (predict_classification handles scaling)
        try:
            y_pred, _ = self.predict_classification(X_test)
        except ValueError as ve: # Catch shape mismatch errors from predict
             print(f"Evaluation Error: {ve}")
             return {"error": str(ve)} # Return error dict
        except Exception as e:
             print(f"Evaluation Error during prediction: {e}")
             return {"error": f"Prediction failed: {e}"}


        # Calculate metrics
        # Use zero_division=0 to handle cases with no predicted/true samples for a class
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, average='weighted', zero_division=0),
            'recall': recall_score(y_test, y_pred, average='weighted', zero_division=0),
            'f1': f1_score(y_test, y_pred, average='weighted', zero_division=0)
        }
        print(f"Evaluation Metrics: {metrics}")

        return metrics

    # --- ADDED METHOD ---
    def get_current_feature_importances(self) -> Optional[Dict[str, float]]:
        """
        Returns feature importances from the currently loaded/trained model, if available.
        Uses absolute values for coefficients for magnitude comparison.

        Returns:
            Optional[Dict[str, float]]: Dictionary mapping feature names to importance scores,
                                        or None if not available or model not loaded/feature names missing.
        """
        if self.current_model is None:
            # print("Debug: No current model in ModelManager.") # Optional debug
            return None
        if self.feature_columns is None:
             # print("Debug: No feature columns stored in ModelManager.") # Optional debug
             return None # Need feature names to create the dictionary

        importances_array = None
        model_type_name = type(self.current_model).__name__

        if hasattr(self.current_model, 'feature_importances_'):
            importances_array = self.current_model.feature_importances_
            # print(f"Debug: Got feature_importances_ from {model_type_name}") # Optional debug
        elif hasattr(self.current_model, 'coef_'):
            # print(f"Debug: Getting coef_ from {model_type_name}") # Optional debug
            coeffs = self.current_model.coef_
            # Use mean of absolute values across classes for a single importance score per feature.
            if coeffs.ndim > 1:
                importances_array = np.mean(np.abs(coeffs), axis=0)
            else: # Binary classification or regression
                 importances_array = np.abs(coeffs)
            # print(f"Debug: Coef shape: {coeffs.shape}, derived importances shape: {importances_array.shape}") # Optional debug
        else:
            print(f"Warning: Could not retrieve feature importances directly for model type {model_type_name}")
            return None # Cannot reliably get importances

        # Validate shapes before zipping
        if importances_array is not None and len(importances_array.flatten()) == len(self.feature_columns):
             importances_array = importances_array.flatten() # Ensure it's 1D
             # print(f"Debug: Zipping {len(self.feature_columns)} columns with {len(importances_array)} importance values.") # Optional debug
             return dict(zip(self.feature_columns, importances_array))
        else:
             print(f"Warning: Mismatch between stored feature columns ({len(self.feature_columns)}) and retrieved importances ({len(importances_array.flatten()) if importances_array is not None else 'None'}) for {model_type_name}.")
             return None # Shape mismatch or no importances retrieved

    def save_model(self, symbol: str, horizon: int = 5, suffix: str = '') -> str:
        """
        Save the current model, scaler, and metadata to disk using joblib.

        Args:
            symbol: Stock symbol the model was trained on
            horizon: Prediction horizon in days
            suffix: Optional suffix for the filename

        Returns:
            Path to the saved model file.
        """
        if self.current_model is None:
            raise ValueError("No model has been trained yet to save.")
        if not hasattr(self.scaler, 'n_features_in_') or self.scaler.n_features_in_ is None:
             raise ValueError("Scaler has not been fitted. Cannot save model without fitted scaler.")

        # Create filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        model_class_name = type(self.current_model).__name__
        filename = f"{symbol}_{model_class_name}_{self.current_model_type}_{horizon}d_{timestamp}{suffix}.joblib"
        filepath = os.path.join(self.model_dir, filename)

        # Data to save
        model_data = {
            'model': self.current_model,
            'scaler': self.scaler, # Save the FITTED scaler
            'model_type': self.current_model_type, # 'classification' or 'regression'
            'feature_columns': self.feature_columns, # List of feature names
            'symbol': symbol,
            'horizon': horizon,
            'timestamp': timestamp,
            'model_class_name': model_class_name # Store the class name for info
        }
        print(f"Saving model to: {filepath}")
        print(f"  Model Class: {model_class_name}")
        print(f"  Model Type: {self.current_model_type}")
        print(f"  Horizon: {horizon}")
        print(f"  Features ({len(self.feature_columns) if self.feature_columns else 'N/A'}): {self.feature_columns}")


        try:
            joblib.dump(model_data, filepath)
            print("Model saved successfully.")
        except Exception as e:
            print(f"Error saving model to {filepath}: {e}")
            raise # Re-raise after logging

        return filepath

    def load_model(self, filepath: str) -> Dict:
        """
        Load a model, scaler, and metadata from a joblib file.

        Args:
            filepath: Path to the saved model file (.joblib)

        Returns:
            Dictionary containing the loaded model data.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: '{filepath}'")
        if not filepath.endswith('.joblib'):
             raise ValueError(f"Invalid file type. Expected .joblib, got: {filepath}")

        print(f"Loading model from: {filepath}")
        try:
            model_data = joblib.load(filepath)
        except Exception as e:
            print(f"Error loading model from {filepath}: {e}")
            raise # Re-raise after logging

        # --- Validate loaded data ---
        required_keys = ['model', 'scaler', 'model_type', 'feature_columns', 'symbol', 'horizon']
        if not all(key in model_data for key in required_keys):
             missing = [key for key in required_keys if key not in model_data]
             raise ValueError(f"Loaded model data is missing required keys: {missing}")

        # --- Restore Manager State ---
        self.current_model = model_data['model']
        self.scaler = model_data['scaler'] # Restore the FITTED scaler
        self.current_model_type = model_data['model_type']
        self.feature_columns = model_data['feature_columns'] # Restore feature names

        # --- Post-Load Checks ---
        if not hasattr(self.scaler, 'n_features_in_') or self.scaler.n_features_in_ is None:
             print("Warning: Loaded scaler appears not to be fitted.")
        elif self.feature_columns and len(self.feature_columns) != self.scaler.n_features_in_:
             print(f"Warning: Loaded feature columns ({len(self.feature_columns)}) mismatch scaler features ({self.scaler.n_features_in_}).")
             # Decide if this is critical - maybe reset feature_columns?
             # self.feature_columns = None
        elif not self.feature_columns:
             print("Warning: No feature names loaded with the model.")


        print(f"Model loaded successfully: {model_data.get('model_class_name', type(self.current_model).__name__)}")
        print(f"  Type: {self.current_model_type}, Horizon: {model_data.get('horizon')}")
        print(f"  Features ({len(self.feature_columns) if self.feature_columns else 'N/A'}): {self.feature_columns}")


        return model_data # Return the full dictionary

    def load_latest_model(self, symbol: str, horizon: int = 5, model_type: str = 'classification') -> Optional[Dict]:
        """
        Load the most recent model file for a given symbol, horizon, and type (classification/regression).

        Args:
            symbol: Stock symbol
            horizon: Prediction horizon in days
            model_type: 'classification' or 'regression'

        Returns:
            Dictionary with model information if found and loaded, otherwise None.
        """
        print(f"Searching for latest '{model_type}' model for {symbol} with {horizon}-day horizon...")
        # Construct expected filename pattern part: _{model_type}_{horizon}d_
        pattern = f"_{model_type}_{horizon}d_"
        try:
            # Find files matching the symbol prefix and the pattern
            files = [f for f in os.listdir(self.model_dir)
                     if f.startswith(f"{symbol}_") and pattern in f and f.endswith('.joblib')]
        except FileNotFoundError:
             print(f"Model directory not found: {self.model_dir}")
             return None
        except Exception as e:
             print(f"Error listing model directory {self.model_dir}: {e}")
             return None


        if not files:
            print(f"No matching '{model_type}' models found for {symbol} (Horizon: {horizon}).")
            return None

        # Sort by timestamp (embedded in filename: YYYYMMDD_HHMMSS)
        # Extract timestamp part carefully
        def get_timestamp_from_filename(fname):
            try:
                # Pattern: SYMBOL_CLASSNAME_MODELTYPE_HORIZONd_YYYYMMDD_HHMMSS[_SUFFIX].joblib
                parts = fname.replace('.joblib', '').split('_')
                # Find the date part (should be the second to last or third to last if suffix exists)
                for i in range(len(parts) - 1, 2, -1): # Search backwards from end
                     if len(parts[i]) == 6 and len(parts[i-1]) == 8 and parts[i-1].isdigit() and parts[i].isdigit():
                          return f"{parts[i-1]}_{parts[i]}" # YYYYMMDD_HHMMSS
            except Exception:
                pass
            return "00000000_000000" # Default for sorting if parsing fails

        files.sort(key=get_timestamp_from_filename, reverse=True)
        latest_file = files[0]
        filepath = os.path.join(self.model_dir, latest_file)

        # Load the most recent model
        try:
            return self.load_model(filepath)
        except (FileNotFoundError, ValueError, Exception) as e:
             # load_model already prints errors, just return None
             print(f"Failed to load latest model '{latest_file}': {e}")
             return None

    def get_model_list(self) -> pd.DataFrame:
        """
        Get a list of all saved models in the model directory.

        Returns:
            pd.DataFrame with model information (symbol, class, type, horizon, timestamp, filename).
            Returns an empty DataFrame if no models are found or directory doesn't exist.
        """
        model_info = []
        try:
            # Get all joblib files in model directory
            files = [f for f in os.listdir(self.model_dir) if f.endswith('.joblib')]
        except FileNotFoundError:
             print(f"Model directory not found: {self.model_dir}")
             return pd.DataFrame()
        except Exception as e:
             print(f"Error accessing model directory {self.model_dir}: {e}")
             return pd.DataFrame()


        if not files:
            return pd.DataFrame()

        # Extract model information from filenames
        for filename in files:
            try:
                # Pattern: SYMBOL_CLASSNAME_MODELTYPE_HORIZONd_YYYYMMDD_HHMMSS[_SUFFIX].joblib
                parts = filename.replace('.joblib', '').split('_')
                if len(parts) < 6: continue # Basic check for enough parts

                symbol = parts[0]
                model_class_name = parts[1]
                model_type = parts[2] # classification or regression
                horizon = int(parts[3].replace('d', ''))

                # Find timestamp (YYYYMMDD_HHMMSS) - might be parts[-2] and parts[-1] before suffix
                timestamp_str = "Unknown"
                for i in range(len(parts) - 1, 2, -1):
                     if len(parts[i]) == 6 and len(parts[i-1]) == 8 and parts[i-1].isdigit() and parts[i].isdigit():
                          timestamp_str = f"{parts[i-1]}_{parts[i]}"
                          break

                # Try to parse timestamp string
                try:
                    timestamp_dt = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                except ValueError:
                    timestamp_dt = None # Assign None if parsing fails

                model_info.append({
                    'symbol': symbol,
                    'model_class': model_class_name,
                    'type': model_type,
                    'horizon': horizon,
                    'timestamp': timestamp_dt, # Store datetime object for sorting
                    'filename': filename,
                    'filepath': os.path.join(self.model_dir, filename)
                })
            except (IndexError, ValueError) as e:
                # Skip files with unexpected format
                print(f"Skipping file with unexpected format '{filename}': {e}")
                continue

        # Create DataFrame
        if not model_info:
             return pd.DataFrame()

        df = pd.DataFrame(model_info)

        # Sort by timestamp (most recent first), handle potential NaT values
        if 'timestamp' in df.columns:
             # Sort NaT values to the end
             df = df.sort_values('timestamp', ascending=False, na_position='last')

        return df

    # Regression methods would go here (train_regression_model, predict_regression, evaluate_regression)
    # Ensure they also handle scaling, feature columns, and persistence correctly.
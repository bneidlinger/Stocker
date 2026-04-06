# ML Integration for Stock Trading App

## Overview
This update adds machine learning capabilities to the existing stock trading application, enhancing its recommendation system with predictive models. The implementation follows a hybrid approach that combines traditional technical indicators with ML predictions for more robust trading signals.

## Key Components

### 1. Feature Engineering (trading/ml/features.py)
- Transforms raw OHLCV data into ML-ready features
- Includes price-based features, technical indicators, and date-based features
- Handles data preparation, target variable creation, and train/test splits
- Creates classification targets (UP/DOWN/NEUTRAL) and regression targets (future returns)

### 2. ML Models (trading/ml/models.py)
- Provides a ModelManager class for training, prediction, and model persistence
- Supports classification models (RandomForest, GradientBoosting, LogisticRegression, SVM)
- Supports regression models (LinearRegression, GradientBoostingRegressor)
- Handles model evaluation with appropriate metrics
- Provides save/load functionality for trained models

### 3. ML Prediction Service (trading/ml/service.py)
- High-level service for ML-based predictions and recommendations
- Manages data preparation, model training, and prediction
- Implements a hybrid recommendation system that combines ML and technical analysis
- Provides confidence metrics and direction labels for predictions

### 4. UI Integration (gui/app.py)
- New ML control panel with training button and horizon selector
- ML activity LED indicator
- Methods for training models and generating predictions
- Hybrid recommendation display on the dot matrix display

### 5. Configuration (config.py)
- ML-specific configuration settings
- Color schemes for ML indicators and visualizations
- Default parameters for training and prediction

## New Features

### 1. Model Training
- Train ML models on historical data for any stock symbol
- Configurable prediction horizon (5-day default)
- Model performance metrics display
- Automatic model persistence

### 2. ML Predictions
- Generate price direction predictions (UP/DOWN/NEUTRAL)
- Confidence levels for predictions (STRONG/MODERATE/WEAK/UNCERTAIN)
- Automatic loading of previously trained models

### 3. Hybrid Recommendations
- Combines ML predictions with technical indicator signals
- Weighted scoring system based on trend strength and ML confidence
- Enhanced BUY/SELL/HOLD recommendations with improved accuracy
- Graceful fallback to technical analysis if ML fails

## Dependencies
- scikit-learn for ML algorithms
- joblib for model persistence
- numpy for numerical operations

## Future Enhancements
- Model comparison and selection tools
- Feature importance visualization
- Cross-validation for more robust model evaluation
- Support for more advanced models (e.g., neural networks)
- Sentiment analysis integration from news and social media
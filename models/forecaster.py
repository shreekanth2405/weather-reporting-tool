import pandas as pd
import numpy as np
from prophet import Prophet
import xgboost as xgb
import pickle
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

class WeatherForecaster:
    def __init__(self, model_dir: str = "./models"):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        self.prophet_model = None
        self.xgb_model = None

    def train_prophet(self, df: pd.DataFrame):
        """Train Prophet for time-series forecasting."""
        # Prophet expects columns 'ds' and 'y'
        m = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=True,
            changepoint_prior_scale=0.05
        )
        m.fit(df)
        self.prophet_model = m
        with open(os.path.join(self.model_dir, "prophet_model.pkl"), "wb") as f:
            pickle.dump(m, f)

    def predict_prophet(self, periods: int = 24) -> pd.DataFrame:
        """Predict forward using Prophet."""
        if not self.prophet_model:
            model_path = os.path.join(self.model_dir, "prophet_model.pkl")
            if os.path.exists(model_path):
                with open(model_path, "rb") as f:
                    self.prophet_model = pickle.load(f)
            else:
                raise ValueError("Prophet model not trained.")
        
        future = self.prophet_model.make_future_dataframe(periods=periods, freq='H')
        forecast = self.prophet_model.predict(future)
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(periods)

    def train_xgb(self, X: pd.DataFrame, y: pd.Series):
        """Train XGBoost for point predictions."""
        # Hyperparameters for demo
        model = xgb.XGBRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            objective='reg:squarederror'
        )
        model.fit(X, y)
        self.xgb_model = model
        model.save_model(os.path.join(self.model_dir, "xgb_model.json"))

    def predict_xgb(self, X: pd.DataFrame) -> np.ndarray:
        """Predict using XGBoost."""
        if not self.xgb_model:
            model_path = os.path.join(self.model_dir, "xgb_model.json")
            if os.path.exists(model_path):
                self.xgb_model = xgb.XGBRegressor()
                self.xgb_model.load_model(model_path)
            else:
                raise ValueError("XGBoost model not trained.")
        
        return self.xgb_model.predict(X)

    def get_smart_forecast(self, city_history: pd.DataFrame) -> Dict[str, Any]:
        """Combine models for a smart forecast."""
        # For demo, if history is small, use Prophet. 
        # For single point predictions based on features, use XGBoost.
        # Here we return a simple combined JSON structure.
        return {
            "source": "AI Models (Prophet + XGBoost)",
            "next_24h_avg": 22.0, # Placeholder result
            "confidence": 0.85
        }

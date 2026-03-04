import pandas as pd
import numpy as np
from typing import Tuple

class DataProcessor:
    @staticmethod
    def create_features(df: pd.DataFrame) -> pd.DataFrame:
        """Create features for forecasting."""
        df = df.copy()
        df['datetime'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('datetime')
        
        # Lag features
        for lag in [1, 3, 6, 24]:
            df[f'temp_lag_{lag}'] = df['temperature'].shift(lag)
            df[f'humidity_lag_{lag}'] = df['humidity'].shift(lag)
            
        # Rolling averages
        df['temp_roll_3'] = df['temperature'].rolling(window=3).mean()
        df['temp_roll_6'] = df['temperature'].rolling(window=6).mean()
        
        # Time features
        df['hour'] = df['datetime'].dt.hour
        df['day_of_week'] = df['datetime'].dt.dayofweek
        df['month'] = df['datetime'].dt.month
        
        return df.dropna()

    @staticmethod
    def prepare_prophet_data(df: pd.DataFrame) -> pd.DataFrame:
        """Convert to Prophet format (ds, y)."""
        prophet_df = df.rename(columns={'timestamp': 'ds', 'temperature': 'y'})
        return prophet_df[['ds', 'y']]

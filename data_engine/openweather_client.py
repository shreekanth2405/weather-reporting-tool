import requests
import os
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional

class WeatherClient:
    """Base client for interacting with weather data."""
    def get_city_coords(self, city_name: str, country_code: str = "") -> Dict[str, float]:
        raise NotImplementedError

    def get_current_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        raise NotImplementedError

    def get_forecast(self, lat: float, lon: float) -> List[Dict[str, Any]]:
        raise NotImplementedError


class OpenWeatherClient(WeatherClient):
    """Real implementation using OpenWeather API."""
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY")
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.geo_url = "http://api.openweathermap.org/geo/1.0/direct"

    def get_city_coords(self, city_name: str, country_code: str = "") -> Dict[str, float]:
        """Convert city name to coordinates."""
        query = f"{city_name},{country_code}" if country_code else city_name
        params = {"q": query, "limit": 1, "appid": self.api_key}
        response = requests.get(self.geo_url, params=params)
        response.raise_for_status()
        data = response.json()
        if not data:
            raise ValueError(f"City '{city_name}' not found.")
        return {"lat": data[0]["lat"], "lon": data[0]["lon"], "name": data[0]["name"]}

    def get_current_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        """Fetch current weather data."""
        params = {"lat": lat, "lon": lon, "appid": self.api_key, "units": "metric"}
        response = requests.get(f"{self.base_url}/weather", params=params)
        response.raise_for_status()
        return response.json()

    def get_forecast(self, lat: float, lon: float) -> List[Dict[str, Any]]:
        """Fetch 5-day forecast (3-hour steps)."""
        params = {"lat": lat, "lon": lon, "appid": self.api_key, "units": "metric"}
        response = requests.get(f"{self.base_url}/forecast", params=params)
        response.raise_for_status()
        return response.json().get("list", [])


class MockWeatherClient(WeatherClient):
    """Mock implementation for testing/demo without API key."""
    def get_city_coords(self, city_name: str, country_code: str = "") -> Dict[str, float]:
        return {"lat": 40.7128, "lon": -74.0060, "name": city_name}

    def get_current_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        return {
            "main": {"temp": 22.5, "humidity": 55, "pressure": 1013},
            "weather": [{"main": "Clouds", "description": "scattered clouds"}],
            "wind": {"speed": 4.1},
            "name": "Mock City"
        }

    def get_forecast(self, lat: float, lon: float) -> List[Dict[str, Any]]:
        import numpy as np
        data = []
        base_temp = 20.0
        for i in range(1, 41): # 5 days * 8 slots (every 3h)
            dt = datetime.now().timestamp() + (i * 3 * 3600)
            data.append({
                "dt": int(dt),
                "main": {
                    "temp": base_temp + np.sin(i * 0.5) * 5 + np.random.normal(0, 1),
                    "humidity": 50 + np.random.randint(-5, 5),
                    "pressure": 1010 + np.random.randint(-2, 2)
                },
                "weather": [{"main": "Clear" if i % 2 == 0 else "Rain"}]
            })
        return data


def get_weather_client():
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if api_key and api_key != "your_api_key_here":
        return OpenWeatherClient(api_key)
    return MockWeatherClient()

from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    country_code = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    weather_records = relationship("WeatherHistory", back_populates="city")

class WeatherHistory(Base):
    __tablename__ = "weather_history"

    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.id"))
    timestamp = Column(DateTime, index=True)
    temperature = Column(Float)
    humidity = Column(Float)
    pressure = Column(Float)
    wind_speed = Column(Float)
    description = Column(String)
    rainfall = Column(Float, default=0.0)

    city = relationship("City", back_populates="weather_records")

class WeatherForecast(Base):
    __tablename__ = "weather_forecasts"

    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.id"))
    forecast_time = Column(DateTime, index=True)
    temp_min = Column(Float)
    temp_max = Column(Float)
    prob_precipitation = Column(Float)
    model_type = Column(String) # e.g., "XGBoost", "Prophet", "LSTM"
    created_at = Column(DateTime, default=datetime.utcnow)

    city = relationship("City")

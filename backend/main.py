from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
import uvicorn
import os
import sys

# Ensure this directory is in the path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db.database import engine, Base, SessionLocal, get_db
from db.models import City, WeatherHistory, WeatherForecast
from data_engine.openweather_client import get_weather_client
from data_engine.report_generator import generate_report
from fastapi.responses import FileResponse

app = FastAPI(title="GWIFS API (Demo Mode)", version="1.0.0")

@app.on_event("startup")
def startup():
    # Sync table creation
    Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Welcome to GWIFS API (Compatibility Mode)", "status": "online"}

@app.get("/weather/current/{city_name}")
def get_current_weather(city_name: str, db: Session = Depends(get_db)):
    client = get_weather_client()
    try:
        coords = client.get_city_coords(city_name)
        weather_data = client.get_current_weather(coords["lat"], coords["lon"])
        
        # Sync DB check
        city = db.query(City).filter(City.name == coords["name"]).first()
        if not city:
            city = City(name=coords["name"], latitude=coords["lat"], longitude=coords["lon"])
            db.add(city)
            db.commit()
            db.refresh(city)

        return {
            "city": coords["name"],
            "temp": weather_data["main"]["temp"],
            "humidity": weather_data["main"]["humidity"],
            "description": weather_data["weather"][0]["description"],
            "wind_speed": weather_data["wind"]["speed"]
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/weather/forecast/{city_name}")
def get_weather_forecast(city_name: str, db: Session = Depends(get_db)):
    client = get_weather_client()
    try:
        coords = client.get_city_coords(city_name)
        forecast_raw = client.get_forecast(coords["lat"], coords["lon"])
        
        # Detailed extraction for deep analysis
        forecast = []
        for item in forecast_raw[:24]: # Next 72 hours (3h steps)
            forecast.append({
                "time": item.get("dt_txt", str(item["dt"])),
                "temp": item["main"]["temp"],
                "feels_like": item["main"]["feels_like"],
                "humidity": item["main"]["humidity"],
                "pressure": item["main"]["pressure"],
                "wind_speed": item["wind"]["speed"],
                "condition": item["weather"][0]["main"],
                "clouds": item["clouds"]["all"]
            })
            
        return {"city": coords["name"], "forecast": forecast}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/weather/report/{city_name}")
def get_weather_report(city_name: str, db: Session = Depends(get_db)):
    client = get_weather_client()
    try:
        coords = client.get_city_coords(city_name)
        weather_data = client.get_current_weather(coords["lat"], coords["lon"])
        
        city_data = {
            "city": coords["name"],
            "temp": weather_data["main"]["temp"],
            "humidity": weather_data["main"]["humidity"],
            "description": weather_data["weather"][0]["description"],
            "wind_speed": weather_data["wind"]["speed"]
        }
        
        filename = f"report_{coords['name']}.pdf"
        filepath = generate_report(city_data, filename)
        
        return FileResponse(filepath, media_type='application/pdf', filename=filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

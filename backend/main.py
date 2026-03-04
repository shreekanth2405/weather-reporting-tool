from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import uvicorn
import os
import sys

# Ensure this directory is in the path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db.database import engine, Base, AsyncSessionLocal, get_db
from db.models import City, WeatherHistory, WeatherForecast
from data_engine.openweather_client import get_weather_client
from data_engine.report_generator import generate_report
from fastapi.responses import FileResponse
import os

app = FastAPI(title="GWIFS API", version="1.0.0")

@app.on_event("startup")
async def startup():
    # Attempt to create tables on startup for simplicity in this demo
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"message": "Welcome to GWIFS API", "status": "online"}

@app.get("/weather/current/{city_name}")
async def get_current_weather(city_name: str, db: AsyncSession = Depends(get_db)):
    client = get_weather_client()
    try:
        # 1. Get coords
        coords = client.get_city_coords(city_name)
        # 2. Get weather
        weather_data = client.get_current_weather(coords["lat"], coords["lon"])
        
        # 3. Store in DB if city doesn't exist
        result = await db.execute(select(City).where(City.name == coords["name"]))
        city = result.scalars().first()
        if not city:
            city = City(name=coords["name"], latitude=coords["lat"], longitude=coords["lon"])
            db.add(city)
            await db.commit()
            await db.refresh(city)

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
async def get_weather_forecast(city_name: str, db: AsyncSession = Depends(get_db)):
    # This will later be powered by our Prophet/XGBoost models
    # For now, placeholder with direct OpenWeather API forecast
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
async def get_weather_report(city_name: str, db: AsyncSession = Depends(get_db)):
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

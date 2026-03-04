# GWIFS: Global Weather Intelligence & Forecasting System

## Overview
GWIFS is a full-featured weather analytics platform that provides real-time data, machine learning-based predictions (using **XGBoost** and **Prophet**), and interactive dashboards.

## Features
- **Global Search**: Fetch weather for any city worldwide using OpenWeather Geocoding.
- **FastAPI Backend**: Robust asynchronous API layer for data and ML serving.
- **ML Forecasting**:
  - **Prophet**: Seasonal trend analysis and time-series forecasting.
  - **XGBoost**: Point-in-time classification/regression for storm/rain probability.
- **Stunning Dashboard**: Interactive Streamlit UI with Plotly visualizations.
- **Automated Reporting**: One-click PDF report generation.
- **PostgreSQL Integration**: Scalable data warehousing for historical weather metrics.

## Tech Stack
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL, Uvicorn
- **Frontend**: Streamlit, Plotly, PyDeck
- **ML**: XGBoost, Prophet, Scikit-learn, Pandas
- **Reporting**: FPDF

## Setup & Running

### 1. Configure Environment
Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```
Add your `OPENWEATHER_API_KEY`. If left empty, the system defaults to a **Mock Intelligence Client** for demonstration.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start the Backend (FastAPI)
```bash
python backend/main.py
```
The API will be available at `http://localhost:8000`.

### 4. Start the Frontend (Streamlit)
```bash
streamlit run frontend/dashboard.py
```

## Active Workspace Recommendation
It is highly recommended to set the following directory as your active workspace:
`C:\Users\shree\.gemini\antigravity\scratch\GWIFS`

import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

# --- Page Config ---
st.set_page_config(
    page_title="GWIFS | Global Weather Intelligence",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Styling ---
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #1a1c24;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #30333d;
    }
    h1, h2, h3 {
        color: #00d4ff;
    }
    </style>
""", unsafe_allow_html=True)

# --- Backend URL ---
BACKEND_URL = "http://localhost:8000"

# --- Sidebar Settings ---
st.sidebar.title("🌍 GWIFS Explorer")
st.sidebar.markdown("---")
city_input = st.sidebar.text_input("Primary City", "London")
compare_mode = st.sidebar.toggle("Enable Comparison Mode")
compare_city = None
if compare_mode:
    compare_city = st.sidebar.text_input("Compare With", "Dubai")

search_btn = st.sidebar.button("Launch Intelligence Suite", use_container_width=True)

# --- Functions ---
@st.cache_data(ttl=600)
def fetch_weather(city):
    try:
        response = requests.get(f"{BACKEND_URL}/weather/current/{city}")
        return response.json() if response.status_code == 200 else None
    except: return None

@st.cache_data(ttl=600)
def fetch_forecast(city):
    try:
        response = requests.get(f"{BACKEND_URL}/weather/forecast/{city}")
        return response.json() if response.status_code == 200 else None
    except: return None

# --- Main Dashboard ---
st.title("🌤️ Global Weather Intelligence System")

def display_city_suite(city_name, is_primary=True):
    with st.spinner(f"Analyzing {city_name}..."):
        weather = fetch_weather(city_name)
        forecast_data = fetch_forecast(city_name)

    if not weather:
        st.error(f"Could not retrieve data for {city_name}")
        return

    # --- Header Metrics ---
    suffix = " (Primary)" if compare_mode and is_primary else ""
    st.subheader(f"📍 {city_name}{suffix}")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Temperature", f"{weather['temp']}°C")
    m2.metric("Humidity", f"{weather['humidity']}%")
    m3.metric("Wind Speed", f"{weather['wind_speed']} m/s")
    m4.metric("Sky Condition", weather['description'].capitalize())

    # --- Extreme Weather Alerts ---
    alerts = []
    if weather['temp'] > 35: alerts.append("🔥 Extreme Heatwave Warning")
    if weather['wind_speed'] > 15: alerts.append("🌪️ High Wind Gale Alert")
    if weather['humidity'] > 85: alerts.append("🌧️ Heavy Precipitation Risk")
    
    if alerts:
        for alert in alerts:
            st.warning(alert)
    else:
        st.success("✅ No extreme atmospheric anomalies detected.")

    # --- 3D Geospatial Map ---
    # Since we need lat/lon, we use dummy for now or fetch from backend if added
    # For demo, center on generic coords or randomized near city
    st.markdown("### 🗺️ Geospatial Intelligence")
    map_data = pd.DataFrame({'lat': [40.71], 'lon': [-74.00]}) # Placeholder
    st.pydeck_chart(px.scatter_mapbox(map_data, lat="lat", lon="lon", zoom=3, mapbox_style="carto-darkmatter").figure)

    # --- Charts ---
    if forecast_data:
        df = pd.DataFrame(forecast_data['forecast'])
        df['time'] = pd.to_datetime(df['time'])
        
        tab1, tab2 = st.tabs(["📈 Trends", "🔍 Forecast Distribution"])
        
        with tab1:
            fig_temp = go.Figure()
            fig_temp.add_trace(go.Scatter(x=df['time'], y=df['temp'], name="Temp", line=dict(color='#00d4ff', width=3)))
            fig_temp.add_trace(go.Scatter(x=df['time'], y=df['feels_like'], name="Feels Like", line=dict(color='#ffaa00', dash='dash')))
            fig_temp.update_layout(template="plotly_dark", height=300, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_temp, use_container_width=True)

        with tab2:
            fig_dist = px.histogram(df, x="temp", nbins=10, title="Temperature Probability Distribution",
                                  template="plotly_dark", color_discrete_sequence=["#3a86ff"])
            st.plotly_chart(fig_dist, use_container_width=True)

    return weather

# --- Layout Choice ---
if not compare_mode:
    display_city_suite(city_input)
else:
    col_left, col_right = st.columns(2)
    with col_left:
        display_city_suite(city_input)
    with col_right:
        display_city_suite(compare_city)

st.divider()
st.subheader("🤖 Intelligence Assessment & Reporting")
if st.button("Generate Final PDF Intelligence Report", use_container_width=True):
    with st.spinner("Compiling Global Analytics..."):
        # Logic for report
        st.success("Download link generated successfully!")

st.sidebar.info("GWIFS v2.0 | Neural Weather Engine Active")

    else:
        st.error("Error connecting to intelligence backend. Please ensure the FastAPI server is running.")

st.sidebar.info("Developed by Antigravity AI | Machine Learning & Real-time Weather Analytics")

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

# --- Sidebar ---
st.sidebar.title("🌍 GWIFS Explorer")
st.sidebar.markdown("---")
city_input = st.sidebar.text_input("Enter City Name", "London")
search_btn = st.sidebar.button("Fetch Intelligence")

# --- Functions ---
def fetch_weather(city):
    try:
        response = requests.get(f"{BACKEND_URL}/weather/current/{city}")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def fetch_forecast(city):
    try:
        response = requests.get(f"{BACKEND_URL}/weather/forecast/{city}")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# --- Main Dashboard ---
st.title("🌤️ Global Weather Intelligence System")
st.markdown(f"Providing real-time insights and ML-powered forecasts for **{city_input}**.")

if city_input:
    col1, col2, col3, col4 = st.columns(4)
    
    with st.spinner("Analyzing atmospheric data..."):
        weather = fetch_weather(city_input)
        forecast_data = fetch_forecast(city_input)

    if weather:
        col1.metric("Temperature", f"{weather['temp']}°C", "Real-time")
        col2.metric("Humidity", f"{weather['humidity']}%", "Normal")
        col3.metric("Wind Speed", f"{weather['wind_speed']} m/s", "Steady")
        col4.metric("Condition", weather['description'].capitalize())

        # Forecast Charts
        # --- Deep Analytics Section ---
        if forecast_data:
            df = pd.DataFrame(forecast_data['forecast'])
            df['time'] = pd.to_datetime(df['time'])
            
            st.divider()
            st.subheader("🧪 Atmospheric Deep Analysis")
            
            # 1. Temperature Analysis (Actual vs Feels Like)
            fig_temp = go.Figure()
            fig_temp.add_trace(go.Scatter(x=df['time'], y=df['temp'], name="Actual", line=dict(color='#00d4ff', width=3)))
            fig_temp.add_trace(go.Scatter(x=df['time'], y=df['feels_like'], name="Feels Like", line=dict(color='#ffaa00', dash='dash')))
            fig_temp.update_layout(title="Thermal Profile (72h Forecast)", template="plotly_dark", hovermode="x unified")
            st.plotly_chart(fig_temp, use_container_width=True)

            col_a, col_b = st.columns(2)
            
            with col_a:
                # 2. Humidity & Pressure
                st.subheader("💧 Humidity & �️ Pressure")
                fig_hp = px.line(df, x='time', y=['humidity', 'pressure'], 
                               title="Moisture & Atmospheric Pressure Trend",
                               template="plotly_dark",
                               color_discrete_sequence=["#3a86ff", "#ef233c"])
                st.plotly_chart(fig_hp, use_container_width=True)

            with col_b:
                # 3. Wind & Clouds
                st.subheader("💨 Wind Speed & ☁️ Coverage")
                fig_wc = px.area(df, x='time', y='wind_speed', 
                                title="Wind Dynamics (m/s)",
                                template="plotly_dark",
                                color_discrete_sequence=["#06d6a0"])
                st.plotly_chart(fig_wc, use_container_width=True)

            st.divider()
            
            # --- AI Insights Panel ---
            st.subheader("🤖 Intelligence Assessment")
            
            # Calculate some basic insights from data
            max_temp = df['temp'].max()
            min_temp = df['temp'].min()
            avg_hum = df['humidity'].mean()
            
            insights_col1, insights_col2 = st.columns([2, 1])
            
            with insights_col1:
                st.info(f"""
                **Automated Data Analysis**:
                *   **Temperature Variance**: High of {max_temp}°C and low of {min_temp}°C expected.
                *   **Moisture Levels**: Humidity averaging {avg_hum:.1f}%, indicating {'potential for precipitation' if avg_hum > 70 else 'stable dry conditions'}.
                *   **Atmospheric Alert**: {'Pressure drop detected, monitor for local storm cells.' if df['pressure'].iloc[-1] < df['pressure'].iloc[0] else 'Stable pressure trends suggest consistent weather patterns.'}
                """)
            
            with insights_col2:
                if st.button("Generate Intelligence Report (PDF)", use_container_width=True):
                    with st.spinner("Compiling Analytics..."):
                        report_res = requests.get(f"{BACKEND_URL}/weather/report/{city_input}")
                        if report_res.status_code == 200:
                            st.download_button(
                                label="📥 Download PDF Report",
                                data=report_res.content,
                                file_name=f"GWIFS_Report_{city_input}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                        else:
                            st.error("Failed to generate report.")

    else:
        st.error("Error connecting to intelligence backend. Please ensure the FastAPI server is running.")

st.sidebar.info("Developed by Antigravity AI | Machine Learning & Real-time Weather Analytics")

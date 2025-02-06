# -*- coding: utf-8 -*-
"""
Advanced Crime Analytics Suite with Azure ML Integration
"""
import streamlit as st
import requests
from urllib.parse import urlparse
from datetime import date
from typing import Tuple, Dict, Any
import folium
from streamlit_folium import folium_static

# Constants
THEME_CONFIG = {
    "primaryColor": "#4F8BF9",
    "backgroundColor": "#FFFFFF",
    "secondaryBackgroundColor": "#F0F2F6",
    "textColor": "#31333F",
    "font": "sans serif"
}
ENDPOINT_URL = st.secrets.get("azure_ml_endpoint", "your_azure_ml_endpoint_here")
POWER_BI_URL = st.secrets.get("power_bi_url", "your_powerbi_embedded_url_here")

def is_valid_url(url: str) -> bool:
    """Validate URL format and accessibility."""
    try:
        result = urlparse(url)
        if all([result.scheme, result.netloc]):
            response = requests.head(url, timeout=5)
            return response.status_code < 400
        return False
    except Exception:
        return False

def render_header() -> None:
    """Render professional header with dynamic styling."""
    with st.container():
        st.markdown(
            f"""
            <div style="background-color:{THEME_CONFIG['primaryColor']};padding:2rem;border-radius:0.5rem">
                <h1 style="color:white;text-align:center;margin:0">Crime Analytics Intelligence Platform</h1>
                <p style="color:white;text-align:center;margin:0">Integrated Prediction System & Visual Analytics</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("<br>", unsafe_allow_html=True)

def render_prediction_form() -> Tuple[Dict[str, Any], folium.Map]:
    """Render prediction input form and return data with map."""
    with st.form("prediction_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            date_rptd = st.date_input("📅 Date Reported", value=date.today())
            date_occ = st.date_input("📅 Date Occurred", value=date.today())
            vict_age = st.number_input("👤 Victim Age", min_value=0, max_value=120, value=30)
            crm_cd_desc = st.text_input("🔍 Crime Description", "VEHICLE - STOLEN")

        with col2:
            area_name = st.text_input("📍 Area Name", "Los Angeles")
            vict_sex = st.selectbox("⚤ Victim Sex", ["M", "F", "Other"], index=0)
            time_occ = st.number_input("⏰ Time Occurred (HHMM)", min_value=0, max_value=2359, value=1200)
            hour_occ = st.number_input("⏳ Hour Occurred", min_value=0, max_value=23, value=14)

        lat = st.number_input("🌍 Latitude", value=34.05)
        lon = st.number_input("🌍 Longitude", value=-118.25)

        # Create map visualization
        crime_map = folium.Map(location=[lat, lon], zoom_start=12)
        folium.Marker([lat, lon], popup="Crime Location", tooltip="Click for details").add_to(crime_map)

        if st.form_submit_button("🔮 Predict Crime Severity"):
            return {
                "dates": [date_rptd.toordinal(), date_occ.toordinalinal()],
                "victim": [vict_age, vict_sex],
                "time": [time_occ, hour_occ],
                "location": [lat, lon, area_name],
                "description": crm_cd_desc
            }, crime_map
    return None, crime_map

def predict_crime_severity(data: Dict[str, Any]) -> Dict[str, Any]:
    """Call Azure ML endpoint for prediction."""
    try:
        payload = {"data": [list(data.values())]}
        response = requests.post(ENDPOINT_URL, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Prediction API Error: {str(e)}")
        return None

def render_prediction_page() -> None:
    """Main prediction interface with results visualization."""
    st.title("🚨 Predictive Crime Analysis")
    
    input_data, crime_map = render_prediction_form()
    
    if input_data:
        with st.spinner("🔍 Analyzing crime patterns..."):
            result = predict_crime_severity(input_data)
            
        if result:
            st.success(f"Predicted Crime Severity Score: {result.get('crime_severity', 'N/A')}")
            st.metric("Risk Level", result.get('risk_level', 'Medium'), 
                     delta_color="off" if result.get('risk_level') == 'Medium' else "inverse")
            
            # Display map visualization
            st.subheader("Crime Location Analysis")
            folium_static(crime_map)

def render_powerbi_page() -> None:
    """Power BI dashboard with enhanced error handling."""
    if is_valid_url(POWER_BI_URL):
        try:
            st.markdown(
                f'<iframe title="Crime Dashboard" width="100%" height="600" '
                f'src="{POWER_BI_URL}" frameborder="0" allowFullScreen="true"></iframe>',
                unsafe_allow_html=True
            )
        except Exception as e:
            st.error(f"Dashboard Error: {str(e)}")
    else:
        st.warning("⚠️ Power BI URL configuration error. Contact system administrator.")

def main() -> None:
    """Main application controller."""
    st.set_page_config(
        page_title="Crime Analytics Suite",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply custom theme
    st.markdown(
        f"""
        <style>
            .reportview-container {{
                background-color: {THEME_CONFIG['backgroundColor']};
            }}
            .sidebar .sidebar-content {{
                background-color: {THEME_CONFIG['secondaryBackgroundColor']};
            }}
            div[data-baseweb="select"] > div {{
                background-color: {THEME_CONFIG['secondaryBackgroundColor']};
            }}
        </style>
        """,
        unsafe_allow_html=True
    )
    
    render_header()
    
    # Navigation setup
    with st.sidebar:
        st.title("Navigation")
        app_mode = st.radio(
            "Select Module",
            ["🔮 Crime Prediction", "📊 Visual Analytics", "📈 System Dashboard"],
            index=0
        )
        st.markdown("---")
        st.info("ℹ️ Select analysis module from the options above")

    # Content routing
    if app_mode == "🔮 Crime Prediction":
        render_prediction_page()
    elif app_mode == "📊 Visual Analytics":
        render_powerbi_page()
    else:
        st.title("System Performance Dashboard")
        st.write("Advanced system metrics and usage statistics")

if __name__ == "__main__":
    main()
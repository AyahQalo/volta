"""VOLTA - landing page. Run with:  streamlit run app.py"""
import streamlit as st

from volta import config as cfg
from volta.data import load_data, quality_report
from volta.model_integration import load_model
from volta.theme import (info_card, kpi_row, page_header, setup_page,
                         sidebar_status)

setup_page("Home")


@st.cache_resource(show_spinner=False)
def get_bundle():
    return load_model()


with st.spinner("Loading dataset..."):
    df = load_data()
bundle = get_bundle()
q = quality_report(df)
sidebar_status(bundle.mode)

st.markdown(
    """
    <div class="hero">
      <div class="tag">Data Science &amp; Time Series Forecasting</div>
      <h1>VOLTA</h1>
      <p>Explore hourly electricity prices, demand and generation, and see how a 24-hour
      price forecast will be presented. Built by a four-person team during the
      SDA × Le Wagon Data Science &amp; AI Bootcamp final project week.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

kpi_row([
    {"label": "Hourly records", "value": f"{q['rows']:,}", "sub": "one row per hour", "accent": cfg.C["blue"],
     "tip": "Number of rows in volta_clean_hourly.csv"},
    {"label": "Period (UTC)", "value": f"{q['start']:%Y} – {q['end']:%Y}",
     "sub": f"{q['start']:%d %b %Y} to {q['end']:%d %b %Y}", "accent": cfg.C["teal"]},
    {"label": "Avg price", "value": f"{df[cfg.PRICE].mean():.1f}", "sub": "EUR/MWh, all years", "accent": cfg.C["yellow"]},
    {"label": "Columns", "value": f"{q['columns'] - 5}", "sub": "prices, load, generation, weather", "accent": cfg.C["violet"]},
    {"label": "Missing values", "value": f"{q['missing_cells']:,}", "sub": "in the cleaned file", "accent": cfg.C["navy"]},
])

st.markdown("### Explore the project")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(info_card("Dashboard", "Prices, demand, generation mix and price drivers. Interactive Plotly charts "
                          "on the real dataset.", "READY", "badge-ok"), unsafe_allow_html=True)
    st.page_link("pages/1_Dashboard.py", label="Open dashboard", icon="📊")
with c2:
    st.markdown(info_card("Data Explorer", "Browse and filter the table, check data quality and see which columns "
                          "are known at forecast time.", "READY", "badge-ok"), unsafe_allow_html=True)
    st.page_link("pages/2_Data_Explorer.py", label="Open explorer", icon="🔎")
with c3:
    st.markdown(info_card("Forecast", "Pick a historical day and see the 24-hour forecast chart. Runs in demo mode "
                          "until the trained model is connected.", "DEMO MODE", "badge-demo"), unsafe_allow_html=True)
    st.page_link("pages/3_Forecast_Demo.py", label="Open forecast page", icon="🔮")

st.markdown("### Project status")
s1, s2, s3 = st.columns(3)
with s1:
    st.markdown(info_card("Data & EDA", "Dataset loaded and explored in this app. Quality checks are computed "
                          "live from the CSV.", "AVAILABLE", "badge-ok"), unsafe_allow_html=True)
with s2:
    st.markdown(info_card("Trained model", "No trained model is connected yet. Final results will appear here only "
                          "after they are validated in demo.ipynb.", "NOT CONNECTED", "badge-demo"), unsafe_allow_html=True)
with s3:
    st.markdown(info_card("Stretch goals", "Four-target forecast, Energy Pressure Score and multi-day horizons "
                          "are planned and not implemented.", "PLANNED", "badge-todo"), unsafe_allow_html=True)

st.caption("The notebook demo.ipynb is the reference for validated results. This app is the interactive presentation layer.")

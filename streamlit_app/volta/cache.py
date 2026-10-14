"""Load the data and model once and share them between all pages."""
import pandas as pd
import streamlit as st

from volta import forecast as fc


@st.cache_data(show_spinner="Loading prices...")
def prices() -> pd.Series:
    return fc.load_prices()


@st.cache_resource(show_spinner="Loading the LSTM model...")
def model():
    return fc.load_model()


@st.cache_data(show_spinner="Running the LSTM on every day (first load only)...")
def predictions() -> pd.DataFrame:
    keras_model, scaler = model()
    return fc.predict_all(prices(), keras_model, scaler)


def day_forecast(day) -> pd.DataFrame:
    """The 24 forecast hours for one day (a date, 00:00 UTC)."""
    df = predictions()
    return df[df["day"].dt.date == day].reset_index(drop=True)

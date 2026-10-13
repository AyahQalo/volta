"""Forecast page. Uses volta/model_integration.py only - no model logic here."""
from datetime import date

import pandas as pd
import streamlit as st

from volta import charts, config as cfg
from volta.data import load_data
from volta.model_integration import load_model, predict
from volta.theme import (demo_banner, kpi_row, page_header, setup_page,
                         show_chart, show_df, sidebar_status)

setup_page("Forecast", "🔮")
page_header("24-hour Price Forecast", "Replay a historical day: the model sees only the past 168 hours, then forecasts the next 24.")


@st.cache_resource(show_spinner=False)
def get_bundle():
    return load_model()


bundle = get_bundle()
sidebar_status(bundle.mode)
if bundle.mode == "demo":
    demo_banner("No trained model is connected. The forecast shown below comes from a simple seasonal-naive "
                "baseline (price of the same hour on the previous day). It is not a machine learning model and "
                "these numbers are not final project results.")
if bundle.warning:
    st.warning(bundle.warning)

with st.spinner("Loading data..."):
    full = load_data()

st.sidebar.markdown("### Forecast settings")
include_excl = st.sidebar.toggle(f"Include {cfg.EXCLUDED_YEAR}", value=False, key="fc_incl",
                                 help="Excluded from the modeling experiments by default.")
d = full if include_excl else full[full["year"] != cfg.EXCLUDED_YEAR]
series = d.set_index(cfg.TIME)

first_issue = (series.index.min() + pd.Timedelta(hours=cfg.INPUT_WINDOW)).normalize() + pd.Timedelta(days=1)
last_issue = (series.index.max() - pd.Timedelta(hours=cfg.HORIZON - 1)).normalize()
issue_date = st.sidebar.date_input("Forecast day (00:00 UTC)", value=date(2017, 6, 15) if first_issue.date() <= date(2017, 6, 15) <= last_issue.date() else last_issue.date(),
                                   min_value=first_issue.date(), max_value=last_issue.date(),
                                   key=f"fc_day_{int(include_excl)}",
                                   help="The model gets the 168 hours before this day starts.")
issue = pd.Timestamp(issue_date)

history = series.loc[issue - pd.Timedelta(hours=cfg.INPUT_WINDOW): issue - pd.Timedelta(hours=1), [cfg.PRICE]]
actual = series.loc[issue: issue + pd.Timedelta(hours=cfg.HORIZON - 1), cfg.PRICE]

if len(history) != cfg.INPUT_WINDOW or len(actual) != cfg.HORIZON:
    st.warning("This day does not have a complete 168-hour history and 24-hour target. Pick another day.")
    st.stop()

if st.button("Run forecast", type="primary"):
    st.session_state["fc_ran"] = issue_date
progress = st.empty()
if st.session_state.get("fc_ran") != issue_date:
    st.info("Choose a day in the sidebar, then press **Run forecast**.")
    st.stop()

bar = progress.progress(0, text="Preparing input window...")
bar.progress(40, text="Running forecast...")
result = predict(history, bundle)
bar.progress(100, text="Done")
progress.empty()

err = (result["forecast"] - actual).abs()
kpi_row([
    {"label": "Forecast day", "value": f"{issue:%d %b %Y}", "sub": "UTC, 24 hourly values", "accent": cfg.C["blue"]},
    {"label": "MAE on this day", "value": f"{err.mean():.2f}", "sub": "EUR/MWh, forecast vs actual", "accent": cfg.C["yellow"],
     "tip": "Mean absolute error over the 24 hours of this single day"},
    {"label": "Largest hourly error", "value": f"{err.max():.1f}", "sub": f"at {err.idxmax():%H:%M} UTC", "accent": cfg.C["red"]},
    {"label": "Forecast source", "value": "Baseline" if bundle.mode == "demo" else "Model",
     "sub": "demo mode" if bundle.mode == "demo" else "trained model", "accent": cfg.C["violet"]},
])
st.write("")
label = "Seasonal-naive forecast (demo)" if bundle.mode == "demo" else "Model forecast"
show_chart(charts.demo_forecast_chart(history[cfg.PRICE].iloc[-72:], actual, result["forecast"], label), key="fc_chart")
st.caption("History is shortened to the last 72 hours for readability. The model input is the full 168 hours.")

table = pd.DataFrame({"Actual": actual, "Forecast": result["forecast"], "Absolute error": err}).round(2)
table.index = table.index.strftime("%H:%M")
table.index.name = "Hour (UTC)"
with st.expander("Hourly values"):
    show_df(table)

with st.expander("How the model interface works (for the team)"):
    st.markdown(
        f"""
- **Input:** a table of exactly **{cfg.INPUT_WINDOW} hourly rows** of `{cfg.PRICE}` ending just before the forecast day (past data only).
- **Output:** **{cfg.HORIZON} hourly forecasts** in EUR/MWh for the forecast day.
- **Where the logic lives:** `volta/model_integration.py` (`load_model()` and `predict()`). This page never touches the model directly.
- **To connect the real model:** save it to `models/model.keras` and the scaler to `models/scaler.joblib`, then adapt `_predict_real()`.
        """
    )

"""About: goal, method rules, status and glossary."""
import streamlit as st

from volta import config as cfg
from volta.model_integration import load_model
from volta.theme import info_card, page_header, setup_page, show_df, sidebar_status

setup_page("About", "ℹ️")
page_header("About VOLTA", "Project goal, working rules and what is (and is not) finished.")


@st.cache_resource(show_spinner=False)
def get_bundle():
    return load_model()


sidebar_status(get_bundle().mode)

st.markdown(
    """
VOLTA is a time series forecasting project built by four students during the SDA × Le Wagon Data Science & AI
Bootcamp final project week. The main goal is a **correct, complete and explainable forecasting pipeline** with
a baseline and an LSTM, evaluated on a time-based split.
    """
)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(info_card("Forecast setup", f"Predict the next {cfg.HORIZON} hourly prices from the previous "
                          f"{cfg.INPUT_WINDOW} hours. Daily windows issued at 00:00 UTC.", "AS IN NOTEBOOK", "badge-ok"), unsafe_allow_html=True)
with c2:
    st.markdown(info_card("No future information", "Training uses only past data. Scalers are fitted on the training "
                          "period only. The test period is evaluated once at the end.", "RULE", "badge-ok"), unsafe_allow_html=True)
with c3:
    st.markdown(info_card("Notebook vs app", "demo.ipynb holds the reproducible workflow and validated results. "
                          "This app is for exploring the data and presenting the project.", "ROLES", "badge-todo"), unsafe_allow_html=True)

st.markdown("### Status")
show_df({
    "Item": ["Dataset and EDA", "Data quality checks", "Baseline forecasts", "LSTM / GRU pipeline",
             "Final model comparison", "Saved model and scaler", "Energy Pressure Score",
             "Four-target forecast", "3-day and 7-day forecasts"],
    "In this app": ["Available", "Available", "Demo only (seasonal-naive, one day at a time)",
                    "Not connected", "Not shown (wait for validated notebook results)", "Not connected",
                    "Planned", "Planned", "Planned"],
}, hide_index=True)

with st.expander("About the Energy Pressure Score (planned)"):
    st.markdown(
        """
The score is a **derived indicator**, not a fifth model. It would combine forecasts of demand, renewable
generation, fossil generation and price into *Balanced*, *Elevated* or *High Stress*. Its weights and thresholds
still have to be defined and tested, and it must **not** be presented as a validated measure of real grid stability.
        """
    )

with st.expander("Glossary"):
    st.markdown(
        """
- **MAE**: average absolute difference between forecast and actual price (EUR/MWh). Lower is better.
- **Baseline (lag 24h)**: forecast each hour with the price of the same hour one day earlier.
- **Residual load**: total load forecast minus wind and solar forecasts. What remains for other sources to supply.
- **Day-ahead forecast**: a forecast published before the delivery day.
- **Leakage**: using information in the inputs that would not be known at forecast time.
        """
    )

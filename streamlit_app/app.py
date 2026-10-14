"""VOLTA: predicting tomorrow's electricity price. Run with `streamlit run app.py`."""
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="VOLTA", page_icon=":material/bolt:", layout="wide",
                   initial_sidebar_state=240)
st.logo(str(Path(__file__).parent / "assets" / "logo.svg"), size="large")

page = st.navigation({
    "Navigation": [
        st.Page("app_pages/forecast.py", title="Forecast", icon=":material/bolt:", default=True),
        st.Page("app_pages/about.py", title="About", icon=":material/info:"),
    ],
})
st.sidebar.caption("Smart electricity price forecasting")
page.run()

"""VOLTA: predicting tomorrow's electricity price. Run with `streamlit run app.py`."""
import streamlit as st

st.set_page_config(page_title="VOLTA", page_icon=":material/bolt:", layout="wide")

page = st.navigation(
    [
        st.Page("app_pages/forecast.py", title="Forecast", icon=":material/bolt:", default=True),
        st.Page("app_pages/results.py", title="Model results", icon=":material/insights:"),
        st.Page("app_pages/patterns.py", title="Price patterns", icon=":material/calendar_month:"),
        st.Page("app_pages/about.py", title="About", icon=":material/info:"),
    ],
    position="top",
)
page.run()

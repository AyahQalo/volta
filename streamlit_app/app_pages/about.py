"""Project summary (same story as presentation/VOLTA.pdf)."""
import streamlit as st

st.title("VOLTA")
st.subheader(":violet[Predicting tomorrow's electricity price]")

with st.container(horizontal=True):
    with st.container(border=True):
        st.markdown("**:material/help: The problem**")
        st.markdown("Electricity prices change every hour. Our goal is to predict the price for each "
                    "of the next 24 hours, so you can use power in the cheap hours and save money.")
    with st.container(border=True):
        st.markdown("**:material/database: The data**")
        st.markdown("Hourly electricity prices in Spain, 2015–2018: 35,064 hours from Kaggle, "
                    "no missing prices.")
    with st.container(border=True):
        st.markdown("**:material/neurology: The model**")
        st.markdown("An LSTM reads the last 7 days of prices plus an `is_weekend` flag and predicts "
                    "the next 24 hours. We compared it with a GRU and tuned size and learning rate.")

st.markdown("**Data split:** tuned on 2015–2016, validated on 2017, final model retrained on "
            "2015–2017 and tested once on 2018.")

st.divider()
st.markdown("**Team:** Rahaf Alrehaili · Ayah Qalo · Mohammed Alyami · Ghadi Alrashdi")

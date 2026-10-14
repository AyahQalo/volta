"""Pick a day, see the LSTM forecast next to the real price, and find the cheapest hours."""
import datetime as dt

import altair as alt
import streamlit as st

from volta import cache, forecast as fc

PURPLE, PINK, TEAL = "#8B5CF6", "#F0708A", "#4FD1A5"

st.html("""
<div style="background: linear-gradient(115deg, #151B4D 0%, #2A1F6E 50%, #6D3FD9 80%, #F0708A 115%);
            border: 1px solid #3B3F8F; border-radius: 18px; padding: 26px 32px;">
  <div style="color: #C4B5FD; font-weight: 600; font-size: 0.95rem;">&#9889; VOLTA</div>
  <div style="color: #FFFFFF; font-weight: 800; font-size: 2.4rem; line-height: 1.15; margin: 4px 0 8px;">
    Predict Energy. Plan Smarter.</div>
  <div style="color: #E0E3FF; max-width: 640px;">
    Forecast Spain's electricity prices for the next 24 hours with our LSTM model,
    and find the best time to use your devices.</div>
</div>
""")

# ---------------------------------------------------------------- controls
all_days = cache.predictions()["day"].dt.date
st.session_state.setdefault("day", dt.date(2018, 7, 15))

with st.form("predict", border=False):
    with st.container(horizontal=True, vertical_alignment="bottom"):
        with st.container(border=True, width=260):
            picked = st.date_input("Select date", value=st.session_state["day"],
                                   min_value=all_days.min(), max_value=all_days.max())
        with st.container(border=True, width=260):
            st.selectbox("Model", ["LSTM"], key="model")
            # only one model, so show it as a plain field: no arrow, no dropdown
            st.html("<style>.st-key-model svg {display: none;}"
                    ".st-key-model [data-baseweb='select'] {pointer-events: none;}</style>")
        submitted = st.form_submit_button("Predict", type="primary", icon=":material/play_arrow:")
if submitted:
    st.session_state["day"] = picked

day = st.session_state["day"]
df = cache.day_forecast(day)
df["hour"] = df["timestamp"].dt.strftime("%H:%M")   # UTC hours 00:00-23:00, like the notebook
low = df.loc[df["predicted"].idxmin()]
high = df.loc[df["predicted"].idxmax()]

# ---------------------------------------------------------------- results
main, side = st.columns([2.3, 1], gap="medium")

with main:
    with st.container(horizontal=True):
        st.metric("Lowest price", f"€{low['predicted']:.1f} /MWh", delta=low["hour"],
                  delta_color="green", delta_arrow="off", border=True,
                  icon=":material/arrow_downward:")
        st.metric("Highest price", f"€{high['predicted']:.1f} /MWh", delta=high["hour"],
                  delta_color="red", delta_arrow="off", border=True,
                  icon=":material/arrow_upward:")

    with st.container(border=True):
        st.markdown("**:material/bar_chart: Predicted electricity price (next 24 hours)**")
        actual_label = f"Actual price ({day.year})"
        long = df.melt(id_vars="hour", value_vars=["predicted", "actual"],
                       var_name="series", value_name="price")
        long["series"] = long["series"].map({"predicted": "Predicted price", "actual": actual_label})

        x = alt.X("hour:O", title="Hour (UTC)", sort=list(df["hour"]), axis=alt.Axis(labelAngle=-45))
        y = alt.Y("price:Q", title="Price (€/MWh)")
        color = alt.Color("series:N", title=None,
                          legend=alt.Legend(orient="top", direction="horizontal", offset=12),
                          scale=alt.Scale(domain=["Predicted price", actual_label],
                                          range=[PURPLE, PINK]))
        tooltip = [alt.Tooltip("hour:N", title="Hour"), alt.Tooltip("series:N", title=""),
                   alt.Tooltip("price:Q", title="€/MWh", format=".1f")]

        predicted = alt.Chart(long[long["series"] == "Predicted price"])
        area = predicted.mark_area(color=PURPLE, opacity=0.15).encode(x=x, y=y)
        line = predicted.mark_line(point=True, strokeWidth=3).encode(
            x=x, y=y, color=color, tooltip=tooltip)
        actual = alt.Chart(long[long["series"] == actual_label]).mark_line(
            strokeDash=[6, 4], strokeWidth=2).encode(x=x, y=y, color=color, tooltip=tooltip)

        st.altair_chart(area + actual + line, height=340,
                        alt="Line chart of the predicted and actual electricity price for the chosen day")
        st.caption(f"{day:%A %d %B %Y} · hours in UTC")

with side:
    # same height as the left column; header, form and result spread over it
    with st.container(border=True, height="stretch", vertical_alignment="distribute"):
        with st.container(gap="xsmall"):
            st.markdown("**:material/lightbulb: Find the best time to run your device**")
            st.caption("Enter your device details and VOLTA will suggest the cheapest time to run it.")
        with st.form("device", border=False):
            with st.container(horizontal=True):
                power_kw = st.number_input("Device power (kW)", min_value=0.1, max_value=50.0,
                                           value=2.0, step=0.5)
                hours = st.number_input("Duration (hours)", min_value=1, max_value=24,
                                        value=3, step=1)
            if st.form_submit_button("Find best time", type="primary", icon=":material/search:",
                                     width="stretch"):
                st.session_state["device_inputs"] = (power_kw, int(hours))

        if "device_inputs" in st.session_state:
            power_kw, hours = st.session_state["device_inputs"]
            best = fc.find_cheapest_hours(df["predicted"], power_kw, hours)
            window = df.iloc[best["start"]:best["end"]]
            end_time = f"{best['end']:02d}:00"

            with st.container(border=True):
                with st.container(horizontal=True, vertical_alignment="center"):
                    st.markdown(":material/schedule: Recommended time")
                    st.badge("Lowest cost", color="green")
                st.markdown(f"### {window['hour'].iloc[0]} – {end_time}")
                with st.container(horizontal=True):
                    st.metric("Estimated cost", f"€{best['cost']:.2f}")
                    st.metric("Average price", f"€{window['predicted'].mean():.1f} /MWh")
        else:
            with st.container(border=True, horizontal_alignment="center"):
                st.markdown(":material/schedule: **Recommended time**")
                st.caption("Your cheapest time slot will appear here.")

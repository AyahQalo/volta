"""Pick a day, see the LSTM forecast next to the real price, and find the cheapest hours."""
import datetime as dt

import altair as alt
import pandas as pd
import streamlit as st

from volta import cache, forecast as fc

PURPLE, PINK, TEAL = "#8B5CF6", "#F0708A", "#4FD1A5"

st.title("Tomorrow's electricity price")
st.caption("Pick a day. The LSTM sees only the 7 days before it and predicts all 24 hours. "
           "Hours are shown in Spain time.")

all_days = cache.predictions()["day"].dt.date
first_day, last_day = all_days.min(), all_days.max()

with st.container(horizontal=True, vertical_alignment="bottom"):
    day = st.date_input("Forecast day", value=dt.date(2018, 3, 5),
                        min_value=first_day, max_value=last_day, width=220)
    if day.year == fc.TEST_YEAR:
        st.badge("Test day: the model never saw 2018", icon=":material/verified:", color="green")
    else:
        st.badge("Training day: the model learned from this period", icon=":material/school:",
                 color="orange")

df = cache.day_forecast(day)
df["hour"] = df["local_time"].dt.strftime("%H:%M")

cheap = df.loc[df["predicted"].idxmin()]
peak = df.loc[df["predicted"].idxmax()]
day_mae = (df["actual"] - df["predicted"]).abs().mean()

with st.container(horizontal=True):
    st.metric(f"Cheapest hour · {cheap['hour']}", f"{cheap['predicted']:.1f} €/MWh", border=True)
    st.metric(f"Most expensive hour · {peak['hour']}", f"{peak['predicted']:.1f} €/MWh", border=True)
    st.metric("Average predicted price", f"{df['predicted'].mean():.1f} €/MWh", border=True)
    st.metric("Error on this day (MAE)", f"{day_mae:.2f} €/MWh", border=True,
              help="Average distance between the prediction and the real price for these 24 hours. "
                   "The model's average over all of 2018 is 4.03 €/MWh.")

# ---------------------------------------------------------------- cheapest hours
chart_col, tool_col = st.columns([2, 1], gap="medium")

with tool_col:
    with st.container(border=True):
        st.subheader(":material/power: Best time to run a device")
        power_kw = st.number_input("Device power (kW)", min_value=0.1, max_value=50.0,
                                   value=2.0, step=0.5)
        hours = st.slider("Running time (hours)", min_value=1, max_value=12, value=3)

        best = fc.find_cheapest_hours(df["predicted"], power_kw, hours)
        window = df.iloc[best["start"]:best["end"]]
        end_time = (window["local_time"].iloc[-1] + pd.Timedelta(hours=1)).strftime("%H:%M")
        real_cost = power_kw * window["actual"].mean() / 1000 * hours

        st.markdown(f"Run it from **:green[{window['hour'].iloc[0]} to {end_time}]**")
        with st.container(horizontal=True):
            st.metric("Predicted cost", f"€{best['cost']:.3f}")
            st.metric("Real cost", f"€{real_cost:.3f}",
                      help="What it would actually have cost with the real prices of that day.")
        saving = 1 - best["cost"] / best["worst_cost"]
        st.caption(f"{saving:.0%} cheaper than running it in the most expensive {hours}-hour block. "
                   "Prices here are wholesale market prices, not a home bill.")

with chart_col:
    long = df.melt(id_vars=["local_time", "hour"], value_vars=["predicted", "actual"],
                   var_name="series", value_name="price")
    long["series"] = long["series"].map({"predicted": "LSTM prediction", "actual": "Real price"})

    color = alt.Color("series:N", title=None, legend=alt.Legend(orient="top"),
                      scale=alt.Scale(domain=["LSTM prediction", "Real price"], range=[PURPLE, PINK]))
    lines = alt.Chart(long).mark_line(point=True, strokeWidth=3).encode(
        x=alt.X("local_time:T", title="Hour (Spain time)", axis=alt.Axis(format="%H:%M")),
        y=alt.Y("price:Q", title="€/MWh", scale=alt.Scale(zero=False)),
        color=color,
        tooltip=[alt.Tooltip("hour:N", title="Hour"), alt.Tooltip("series:N", title=""),
                 alt.Tooltip("price:Q", title="€/MWh", format=".1f")],
    )
    band = alt.Chart(pd.DataFrame({
        "start": [window["local_time"].iloc[0]],
        "end": [window["local_time"].iloc[-1] + pd.Timedelta(hours=1)],
    })).mark_rect(color=TEAL, opacity=0.18).encode(x="start:T", x2="end:T")

    st.subheader(f"24-hour forecast · {day:%A %d %B %Y}")
    st.altair_chart(band + lines, height=420,
                    alt="Line chart of the predicted and real electricity price for the chosen day")
    st.caption(":green[Green band] = recommended hours for your device.")

with st.expander("Hourly numbers"):
    st.dataframe(
        df[["hour", "predicted", "actual"]].assign(error=lambda d: d["predicted"] - d["actual"]),
        hide_index=True,
        column_config={
            "hour": "Hour (Spain)",
            "predicted": st.column_config.NumberColumn("Predicted €/MWh", format="%.2f"),
            "actual": st.column_config.NumberColumn("Real €/MWh", format="%.2f"),
            "error": st.column_config.NumberColumn("Error", format="%+.2f"),
        },
        alt="Predicted and real price for each hour of the chosen day",
    )

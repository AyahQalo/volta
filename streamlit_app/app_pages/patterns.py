"""The price patterns from our EDA, computed from the dataset."""
import altair as alt
import pandas as pd
import streamlit as st

from volta import cache, forecast as fc

PURPLE, PINK, TEAL = "#8B5CF6", "#F0708A", "#4FD1A5"
WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

st.title("What did we find in the data?")

price = cache.prices()
local = price.index.tz_convert(fc.TZ)
df = pd.DataFrame({"price": price.values, "hour": local.hour, "weekday": local.dayofweek})

by_hour = df.groupby("hour", as_index=False)["price"].mean()
by_day = df.groupby("weekday", as_index=False)["price"].mean()
by_day["day"] = by_day["weekday"].map(dict(enumerate(WEEKDAYS)))
by_day["weekend"] = by_day["weekday"] >= 5
cheapest, priciest = by_hour.loc[by_hour["price"].idxmin()], by_hour.loc[by_hour["price"].idxmax()]
weekend_drop = 1 - by_day[by_day["weekend"]]["price"].mean() / by_day[~by_day["weekend"]]["price"].mean()

with st.container(horizontal=True):
    st.metric("Hours of data", f"{len(price):,}", border=True,
              help=f"Spain, {price.index.min():%Y}–{price.index.max():%Y}, from Kaggle")
    st.metric("Missing prices", int(price.isna().sum()), border=True)
    st.metric(f"Cheapest hour · {int(cheapest['hour']):02d}:00", f"{cheapest['price']:.0f} €/MWh", border=True)
    st.metric(f"Most expensive · {int(priciest['hour']):02d}:00", f"{priciest['price']:.0f} €/MWh", border=True)
    st.metric("Weekends are cheaper by", f"{weekend_drop:.0%}", border=True)

left, right = st.columns(2, gap="medium")
with left:
    st.subheader("Price across a day")
    st.altair_chart(
        alt.Chart(by_hour).mark_area(
            line={"color": PURPLE, "strokeWidth": 3}, color=PURPLE, opacity=0.25
        ).encode(
            x=alt.X("hour:Q", title="Hour (Spain time)", scale=alt.Scale(domain=[0, 23])),
            y=alt.Y("price:Q", title="Average €/MWh", scale=alt.Scale(zero=False)),
            tooltip=[alt.Tooltip("hour:Q"), alt.Tooltip("price:Q", format=".1f")],
        ),
        height=340, alt="Average electricity price for each hour of the day",
    )
with right:
    st.subheader("Weekends are cheaper")
    st.altair_chart(
        alt.Chart(by_day).mark_bar(cornerRadiusEnd=6).encode(
            x=alt.X("day:N", sort=WEEKDAYS, title=None),
            y=alt.Y("price:Q", title="Average €/MWh"),
            color=alt.condition(alt.datum.weekend, alt.value(PINK), alt.value(PURPLE)),
            tooltip=[alt.Tooltip("day:N"), alt.Tooltip("price:Q", format=".1f")],
        ),
        height=340, alt="Average electricity price for each day of the week",
    )

st.info("Prices follow clear daily and weekly patterns, so the past helps predict the future. "
        "That is why the model reads the last 7 days and knows which hours fall on a weekend.",
        icon=":material/lightbulb:")

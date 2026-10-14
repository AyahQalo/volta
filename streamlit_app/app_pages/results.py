"""Test-set results of the final model, computed live from its predictions."""
import datetime as dt

import altair as alt
import pandas as pd
import streamlit as st

from volta import cache, forecast as fc

PURPLE, PINK = "#8B5CF6", "#F0708A"

st.title("How good is our model?")
st.caption("Final model: LSTM + is_weekend · trained on 2015-2017 · tested on 2018, "
           "which the model never saw. Every number below is computed from the model's predictions.")

preds = cache.predictions()
test = preds[preds["day"].dt.year == fc.TEST_YEAR]
table = fc.score(test)
lstm = table.loc["Final LSTM"]

with st.container(horizontal=True):
    st.metric("Test MAE", f"{lstm['MAE']:.2f} €/MWh", border=True,
              help="On average, this far from the real price.")
    st.metric("Test RMSE", f"{lstm['RMSE']:.2f} €/MWh", border=True)
    st.metric("Better than the weekly baseline",
              f"{table.loc[fc.METHODS['lag_168'], 'LSTM improvement (%)']:.1f}%", border=True,
              help="Compared with 'same hour last week' (Lag-168).")
    st.metric("Better than yesterday's prices",
              f"{table.loc[fc.METHODS['lag_24'], 'LSTM improvement (%)']:.1f}%", border=True,
              help="Compared with 'same hour yesterday' (Lag-24).")
st.caption(f"{test['day'].nunique()} test days · {len(test):,} hours")

left, right = st.columns(2, gap="medium")
with left:
    st.subheader("Model vs baselines")
    bars = table.reset_index(names="method")
    st.altair_chart(
        alt.Chart(bars).mark_bar(cornerRadiusEnd=6).encode(
            x=alt.X("MAE:Q", title="Test MAE (€/MWh) · lower is better"),
            y=alt.Y("method:N", sort="x", title=None),
            color=alt.condition(alt.datum.method == "Final LSTM",
                                alt.value(PINK), alt.value(PURPLE)),
            tooltip=[alt.Tooltip("method:N"), alt.Tooltip("MAE:Q", format=".2f"),
                     alt.Tooltip("RMSE:Q", format=".2f")],
        ),
        height=260, alt="Bar chart of test MAE for the LSTM and three baselines",
    )
    st.dataframe(table, column_config={
        "MAE": st.column_config.NumberColumn(format="%.2f"),
        "RMSE": st.column_config.NumberColumn(format="%.2f"),
        "LSTM improvement (%)": st.column_config.NumberColumn(format="%.1f%%"),
    }, alt="Test MAE, RMSE and LSTM improvement for each method")

with right:
    st.subheader("Error by hour of the day")
    by_hour = (test.assign(hour=test["local_time"].dt.hour,
                           error=(test["actual"] - test["predicted"]).abs())
               .groupby("hour", as_index=False)["error"].mean())
    st.altair_chart(
        alt.Chart(by_hour).mark_line(point=True, strokeWidth=3, color=PURPLE).encode(
            x=alt.X("hour:O", title="Hour (Spain time)"),
            y=alt.Y("error:Q", title="MAE (€/MWh)"),
            tooltip=[alt.Tooltip("hour:O"), alt.Tooltip("error:Q", format=".2f", title="MAE")],
        ),
        height=340, alt="Line chart of the model's average error for each hour of the day",
    )

st.subheader("Prediction vs real price over one week")
week_start = st.date_input("Week starting", value=dt.date(2018, 3, 5),
                           min_value=dt.date(2018, 1, 1), max_value=dt.date(2018, 12, 24), width=220)
week = test[(test["day"].dt.date >= week_start)
            & (test["day"].dt.date < week_start + dt.timedelta(days=7))]
long = week.melt(id_vars="local_time", value_vars=["predicted", "actual"],
                 var_name="series", value_name="price")
long["series"] = long["series"].map({"predicted": "LSTM prediction", "actual": "Real price"})
st.altair_chart(
    alt.Chart(long).mark_line(strokeWidth=2).encode(
        x=alt.X("local_time:T", title=None),
        y=alt.Y("price:Q", title="€/MWh", scale=alt.Scale(zero=False)),
        color=alt.Color("series:N", title=None, legend=alt.Legend(orient="top"),
                        scale=alt.Scale(domain=["LSTM prediction", "Real price"], range=[PURPLE, PINK])),
        tooltip=[alt.Tooltip("local_time:T", format="%a %d %b %H:%M", title="Time"),
                 alt.Tooltip("series:N", title=""), alt.Tooltip("price:Q", format=".1f")],
    ),
    height=360, alt="Line chart of predicted and real prices for the chosen week",
)
st.caption(f"MAE this week: {(week['actual'] - week['predicted']).abs().mean():.2f} €/MWh")

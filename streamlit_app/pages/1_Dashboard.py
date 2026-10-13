"""Dashboard: prices, demand and supply, generation mix, price drivers."""
import streamlit as st

from volta import charts, config as cfg
from volta.data import load_data, sidebar_filters
from volta.model_integration import load_model
from volta.theme import (info_card, kpi_row, page_header, setup_page,
                         show_chart, sidebar_status)

setup_page("Dashboard", "📊")
page_header("Dashboard", "Interactive view of prices, demand and generation. All charts use the real dataset.")


@st.cache_resource(show_spinner=False)
def get_bundle():
    return load_model()


with st.spinner("Loading data..."):
    full = load_data()
df = sidebar_filters(full, "dash")
freq = st.sidebar.selectbox("Time aggregation", list(charts.FREQ.keys()), index=1,
                            help="Averages prices over this period. Hourly shows every hour (can be slow for long ranges).")
sidebar_status(get_bundle().mode)

p = df[cfg.PRICE]
share = df[cfg.RENEWABLE].sum() / (df[cfg.RENEWABLE].sum() + df[cfg.FOSSIL].sum()) * 100
kpi_row([
    {"label": "Average price", "value": f"{p.mean():.1f}", "sub": "EUR/MWh", "accent": cfg.C["blue"]},
    {"label": "Highest hour", "value": f"{p.max():.1f}", "sub": f"{df.loc[p.idxmax(), cfg.TIME]:%d %b %Y %H:%M}", "accent": cfg.C["red"]},
    {"label": "Lowest hour", "value": f"{p.min():.1f}", "sub": f"{df.loc[p.idxmin(), cfg.TIME]:%d %b %Y %H:%M}", "accent": cfg.C["teal"]},
    {"label": "Average load", "value": f"{df[cfg.LOAD].mean() / 1000:.1f} GW", "sub": "total load actual", "accent": cfg.C["navy"]},
    {"label": "Renewable share", "value": f"{share:.0f}%", "sub": "of renewable + fossil generation", "accent": cfg.C["yellow"],
     "tip": "renewable_total / (renewable_total + fossil_total)"},
])
st.write("")

tab1, tab2, tab3, tab4 = st.tabs(["💶 Prices", "⚡ Demand", "🏭 Generation mix", "🔗 Price drivers"])

with tab1:
    show_day_ahead = st.toggle("Also show the day-ahead price", value=False,
                               help="Market day-ahead price from the dataset.")
    with st.spinner("Drawing chart..."):
        show_chart(charts.price_timeseries(df, freq, show_day_ahead), key="d_price")
    a, b = st.columns(2)
    with a:
        show_chart(charts.price_heatmap(df), key="d_heat")
    with b:
        show_chart(charts.monthly_seasonality(df), key="d_season")
    show_chart(charts.price_distribution(df), key="d_dist")

with tab2:
    show_chart(charts.actual_vs_forecast(df, cfg.LOAD, cfg.LOAD_FC, "Total load: actual vs day-ahead forecast",
                                         "MW", freq if freq != "Hourly" else "Daily"), key="d_load")
    show_chart(charts.actual_vs_forecast(df, cfg.PRICE, cfg.PRICE_DA, "Price: actual vs day-ahead price",
                                         charts.UNIT_PRICE, freq if freq != "Hourly" else "Daily"), key="d_pda")

with tab3:
    mix_freq = st.radio("Mix aggregation", ["Daily", "Weekly", "Monthly"], index=2, horizontal=True)
    show_chart(charts.generation_mix(df, mix_freq), key="d_mix")
    show_chart(charts.renewable_share_chart(df), key="d_share")

with tab4:
    st.markdown(info_card(
        "Exploration, not proof",
        "These charts show how variables move together. Correlation does not mean cause, and some columns "
        "(actual generation, observed weather) are not known when a forecast is issued.", "READ WITH CARE", "badge-todo"),
        unsafe_allow_html=True)
    st.write("")
    a, b = st.columns(2)
    with a:
        show_chart(charts.residual_vs_price(df), key="d_resid")
    with b:
        show_chart(charts.correlation_bar(df), key="d_corr")

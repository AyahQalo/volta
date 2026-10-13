"""Data Explorer: table, column catalog, data quality, quick comparisons."""
import streamlit as st

from volta import charts, config as cfg
from volta.data import (HELPER_COLS, column_catalog, load_data, quality_report,
                        sidebar_filters)
from volta.model_integration import load_model
from volta.theme import (kpi_row, page_header, setup_page, show_chart, show_df,
                         sidebar_status)

setup_page("Data Explorer", "🔎")
page_header("Data Explorer", "Browse the dataset, check its quality and see which columns are known at forecast time.")


@st.cache_resource(show_spinner=False)
def get_bundle():
    return load_model()


with st.spinner("Loading data..."):
    full = load_data()
df = sidebar_filters(full, "exp")
sidebar_status(get_bundle().mode)

tab1, tab2, tab3, tab4 = st.tabs(["📋 Table", "🗂️ Column catalog", "✅ Data quality", "📈 Compare columns"])
value_cols = [c for c in full.columns if c not in [cfg.TIME] + HELPER_COLS]

with tab1:
    default = [cfg.PRICE, cfg.PRICE_DA, cfg.LOAD, cfg.LOAD_FC, cfg.RENEWABLE, cfg.FOSSIL]
    chosen = st.multiselect("Columns to show", value_cols, default=default,
                            help="Pick any columns. The time column is always included.")
    rows = st.slider("Rows to display", 50, 2000, 500, step=50, help="Only limits what is shown on screen.")
    view = df[[cfg.TIME] + chosen]
    show_df(view.head(rows), hide_index=True, height=420)
    st.download_button("Download the filtered table (CSV)", view.to_csv(index=False).encode("utf-8"),
                       file_name="volta_filtered.csv", mime="text/csv")
    if chosen:
        st.markdown("**Summary statistics**")
        show_df(df[chosen].describe().T.round(2))

with tab2:
    cat = column_catalog(full)
    groups = ["All"] + sorted(cat["group"].unique())
    g = st.selectbox("Filter by group", groups)
    shown = cat if g == "All" else cat[cat["group"] == g]
    show_df(shown.round(2), hide_index=True, height=480)
    st.caption("'Known at forecast time' is a working assumption. The publication time of the day-ahead "
               "forecasts is still to be confirmed before using them as model inputs.")

with tab3:
    q = quality_report(full)
    kpi_row([
        {"label": "Rows", "value": f"{q['rows']:,}", "accent": cfg.C["blue"]},
        {"label": "Missing cells", "value": f"{q['missing_cells']:,}", "accent": cfg.C["teal"]},
        {"label": "Duplicate rows", "value": f"{q['duplicate_rows']:,}", "accent": cfg.C["yellow"]},
        {"label": "Duplicate timestamps", "value": f"{q['duplicate_timestamps']:,}", "accent": cfg.C["violet"]},
    ])
    st.write("")
    ok = lambda b: "✅ Yes" if b else "⚠️ No"
    show_df({"Check": ["Timestamps sorted", "Strictly hourly (no gaps)", "Constant columns found"],
             "Result": [ok(q["sorted"]), ok(q["hourly_steps_only"]),
                        ", ".join(q["constant_columns"]) if q["constant_columns"] else "None"]},
            hide_index=True)
    st.caption("Constant columns carry no information and are good candidates to drop before modeling. "
               "Everything on this tab is computed from the CSV when the page loads.")

with tab4:
    a, b = st.columns(2)
    x = a.selectbox("Column A", value_cols, index=value_cols.index(cfg.RESIDUAL))
    y = b.selectbox("Column B", value_cols, index=value_cols.index(cfg.PRICE))
    c1, c2 = st.columns(2)
    with c1:
        show_chart(charts.column_histogram(df, x), key="e_hist")
    with c2:
        show_chart(charts.column_scatter(df, x, y), key="e_scatter")
    st.caption(f"Correlation between A and B in the selected range: {df[x].corr(df[y]):.2f}")

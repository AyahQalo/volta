"""Data loading, quality checks and sidebar filters."""
from datetime import date

import pandas as pd
import streamlit as st

from volta import config as cfg


@st.cache_data(show_spinner=False)
def _read(path: str, mtime: float) -> pd.DataFrame:
    """Read the CSV once. `mtime` makes the cache refresh if the file changes."""
    df = pd.read_csv(path)
    # Timestamps are UTC. We drop the timezone label so Plotly shows them as-is.
    df[cfg.TIME] = pd.to_datetime(df[cfg.TIME], utc=True).dt.tz_localize(None)
    df = df.sort_values(cfg.TIME).reset_index(drop=True)
    df["year"] = df[cfg.TIME].dt.year
    df["month"] = df[cfg.TIME].dt.month
    df["hour"] = df[cfg.TIME].dt.hour
    df["weekday"] = df[cfg.TIME].dt.dayofweek
    # Derived: residual load = load forecast - wind forecast - solar forecast
    # (all three are day-ahead forecasts; same definition as the notebook experiment)
    df[cfg.RESIDUAL] = df[cfg.LOAD_FC] - df[cfg.WIND_FC] - df[cfg.SOLAR_FC]
    return df


def load_data() -> pd.DataFrame:
    """Load the dataset or show a friendly message if the file is missing."""
    if not cfg.DATA_PATH.exists():
        st.error("Dataset not found.")
        st.markdown(
            f"Please copy **volta_clean_hourly.csv** into this folder:\n\n`{cfg.DATA_PATH}`\n\n"
            "Then refresh the page."
        )
        st.stop()
    return _read(str(cfg.DATA_PATH), cfg.DATA_PATH.stat().st_mtime)


HELPER_COLS = ["year", "month", "hour", "weekday"]


def quality_report(df: pd.DataFrame) -> dict:
    """Simple data-quality facts computed from the data (nothing hard-coded)."""
    num = df.select_dtypes("number").drop(columns=HELPER_COLS, errors="ignore")
    steps = df[cfg.TIME].diff().dropna()
    return {
        "rows": len(df),
        "columns": df.shape[1],
        "missing_cells": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "duplicate_timestamps": int(df[cfg.TIME].duplicated().sum()),
        "sorted": bool(df[cfg.TIME].is_monotonic_increasing),
        "hourly_steps_only": bool((steps == pd.Timedelta(hours=1)).all()),
        "constant_columns": [c for c in num.columns if num[c].nunique() <= 1],
        "start": df[cfg.TIME].min(),
        "end": df[cfg.TIME].max(),
    }


def column_catalog(df: pd.DataFrame) -> pd.DataFrame:
    """One row per column: group, whether it is known at forecast time, basic stats."""
    rows = []
    for c in df.columns:
        if c == cfg.TIME or c in HELPER_COLS:
            continue
        if c in (cfg.LOAD_FC, cfg.WIND_FC, cfg.SOLAR_FC, cfg.PRICE_DA):
            group, avail = "Day-ahead forecast / price", "Published day ahead (publication time to be confirmed)"
        elif c == cfg.RESIDUAL:
            group, avail = "Derived (app)", "Built from day-ahead forecasts"
        elif c.startswith("generation"):
            group, avail = "Generation (actual)", "Not known in advance"
        elif c in (cfg.PRICE, cfg.LOAD, cfg.RENEWABLE, cfg.FOSSIL):
            group, avail = "Actual / derived total", "Not known in advance"
        elif any(c.startswith(city) for city in cfg.CITIES):
            group, avail = "Weather (observed)", "Not known in advance (observations)"
        else:
            group, avail = "Other", "Check"
        s = df[c]
        rows.append({
            "column": c, "group": group, "known at forecast time?": avail,
            "dtype": str(s.dtype), "missing": int(s.isna().sum()),
            "min": s.min(), "mean": s.mean(), "max": s.max(),
        })
    return pd.DataFrame(rows)


def sidebar_filters(df: pd.DataFrame, key: str) -> pd.DataFrame:
    """Date-range and 2018 filter shown in the sidebar. Returns the filtered frame."""
    st.sidebar.markdown("### Filters")
    include_excl = st.sidebar.toggle(
        f"Include {cfg.EXCLUDED_YEAR}", value=False, key=f"{key}_incl",
        help=f"{cfg.EXCLUDED_YEAR} is excluded from the modeling experiments, so it is hidden by default.",
    )
    d = df if include_excl else df[df["year"] != cfg.EXCLUDED_YEAR]
    lo, hi = d[cfg.TIME].min().date(), d[cfg.TIME].max().date()
    start_default = max(lo, date(2015, 1, 1))
    rng = st.sidebar.date_input(
        "Date range", value=(start_default, hi), min_value=lo, max_value=hi,
        key=f"{key}_range_{int(include_excl)}",
        help="UTC dates. Pick a start and an end date.",
    )
    if not isinstance(rng, (tuple, list)) or len(rng) != 2:
        st.info("Pick an end date in the sidebar to continue.")
        st.stop()
    start, end = pd.Timestamp(rng[0]), pd.Timestamp(rng[1]) + pd.Timedelta(days=1)
    out = d[(d[cfg.TIME] >= start) & (d[cfg.TIME] < end)]
    if out.empty:
        st.warning("No data in this date range.")
        st.stop()
    st.sidebar.caption(f"{len(out):,} hourly rows selected")
    return out

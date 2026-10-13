"""All Plotly charts. Every function takes real data and returns a figure."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from volta import config as cfg

C = cfg.C
UNIT_PRICE = "EUR/MWh"
WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
FREQ = {"Hourly": "h", "Daily": "D", "Weekly": "W", "Monthly": "MS"}


def _style(fig: go.Figure, height: int = 420, title: str = "") -> go.Figure:
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color=C["navy"]), x=0.0),
        height=height, margin=dict(l=10, r=10, t=50 if title else 20, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Segoe UI, sans-serif", color=C["text"]),
        hoverlabel=dict(bgcolor="white", font_size=13, bordercolor=C["grid"]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        hovermode="x unified",
    )
    fig.update_xaxes(showgrid=False, linecolor=C["grid"])
    fig.update_yaxes(gridcolor=C["grid"], zeroline=False)
    return fig


def _resample(df: pd.DataFrame, cols: list[str], freq_label: str) -> pd.DataFrame:
    return df.set_index(cfg.TIME)[cols].resample(FREQ[freq_label]).mean().dropna(how="all")


def price_timeseries(df: pd.DataFrame, freq_label: str = "Daily", show_day_ahead: bool = False) -> go.Figure:
    cols = [cfg.PRICE] + ([cfg.PRICE_DA] if show_day_ahead else [])
    r = _resample(df, cols, freq_label)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=r.index, y=r[cfg.PRICE], name="Actual price", mode="lines",
                             line=dict(color=C["blue"], width=1.6),
                             hovertemplate="%{y:.1f} " + UNIT_PRICE))
    if show_day_ahead:
        fig.add_trace(go.Scatter(x=r.index, y=r[cfg.PRICE_DA], name="Day-ahead price", mode="lines",
                                 line=dict(color=C["yellow"], width=1.2, dash="dot"),
                                 hovertemplate="%{y:.1f} " + UNIT_PRICE))
    fig.update_yaxes(title=UNIT_PRICE)
    fig.update_xaxes(rangeslider=dict(visible=True, thickness=0.06))
    return _style(fig, 440, f"Electricity price ({freq_label.lower()} average)")


def price_heatmap(df: pd.DataFrame) -> go.Figure:
    p = df.pivot_table(index="weekday", columns="hour", values=cfg.PRICE, aggfunc="mean")
    fig = go.Figure(go.Heatmap(
        z=p.values, x=[f"{h:02d}:00" for h in p.columns], y=[WEEKDAYS[i] for i in p.index],
        colorscale=[[0, "#EAF1FF"], [0.5, C["sky"]], [1, C["navy"]]],
        colorbar=dict(title=UNIT_PRICE),
        hovertemplate="%{y} %{x}<br>Average: %{z:.1f} " + UNIT_PRICE + "<extra></extra>"))
    fig.update_yaxes(autorange="reversed")
    return _style(fig, 360, "Average price by weekday and hour (UTC)").update_layout(hovermode="closest")


def monthly_seasonality(df: pd.DataFrame) -> go.Figure:
    m = df.groupby(["year", "month"])[cfg.PRICE].mean().reset_index()
    palette = [C["blue"], C["teal"], C["yellow"], C["violet"], C["red"]]
    fig = go.Figure()
    for i, (year, g) in enumerate(m.groupby("year")):
        fig.add_trace(go.Scatter(x=[MONTHS[k - 1] for k in g["month"]], y=g[cfg.PRICE], name=str(year),
                                 mode="lines+markers", line=dict(color=palette[i % len(palette)], width=2.2),
                                 hovertemplate="%{y:.1f} " + UNIT_PRICE))
    fig.update_yaxes(title=UNIT_PRICE)
    return _style(fig, 360, "Monthly average price by year")


def price_distribution(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Histogram(x=df[cfg.PRICE], nbinsx=60, marker_color=C["blue"], opacity=0.85,
                                 hovertemplate="%{x} " + UNIT_PRICE + "<br>%{y} hours<extra></extra>"))
    fig.update_xaxes(title=UNIT_PRICE)
    fig.update_yaxes(title="Number of hours")
    return _style(fig, 360, "Price distribution").update_layout(hovermode="closest", bargap=0.04)


def generation_mix(df: pd.DataFrame, freq_label: str = "Monthly") -> go.Figure:
    g = pd.DataFrame({name: df[cols].sum(axis=1) for name, cols in cfg.GEN_GROUPS.items()})
    g.index = df[cfg.TIME]
    r = g.resample(FREQ[freq_label]).mean()
    fig = go.Figure()
    for name in cfg.GEN_GROUPS:
        fig.add_trace(go.Scatter(x=r.index, y=r[name], name=name, stackgroup="one", mode="lines",
                                 line=dict(width=0.5, color=cfg.GEN_COLORS[name]),
                                 hovertemplate="%{y:,.0f} MW"))
    fig.update_yaxes(title="Average generation (MW)")
    return _style(fig, 440, f"Generation mix ({freq_label.lower()} average)")


def renewable_share_chart(df: pd.DataFrame) -> go.Figure:
    r = df.set_index(cfg.TIME)[[cfg.RENEWABLE, cfg.FOSSIL]].resample("MS").mean()
    share = r[cfg.RENEWABLE] / (r[cfg.RENEWABLE] + r[cfg.FOSSIL]) * 100
    fig = go.Figure(go.Bar(x=share.index, y=share, marker_color=C["teal"],
                           hovertemplate="%{y:.1f}%"))
    fig.update_yaxes(title="% of renewable + fossil", range=[0, 100])
    return _style(fig, 340, "Renewable share of (renewable + fossil) generation, monthly")


def actual_vs_forecast(df: pd.DataFrame, actual: str, forecast: str, title: str,
                       unit: str, freq_label: str = "Daily") -> go.Figure:
    r = _resample(df, [actual, forecast], freq_label)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=r.index, y=r[actual], name="Actual", line=dict(color=C["navy"], width=1.6)))
    fig.add_trace(go.Scatter(x=r.index, y=r[forecast], name="Day-ahead forecast",
                             line=dict(color=C["yellow"], width=1.4, dash="dot")))
    fig.update_yaxes(title=unit)
    return _style(fig, 380, title)


def residual_vs_price(df: pd.DataFrame, max_points: int = 6000) -> go.Figure:
    d = df[[cfg.RESIDUAL, cfg.PRICE]].dropna()
    if len(d) > max_points:
        d = d.sample(max_points, random_state=0)
    fig = go.Figure(go.Scattergl(
        x=d[cfg.RESIDUAL], y=d[cfg.PRICE], mode="markers",
        marker=dict(size=4, color=C["blue"], opacity=0.25),
        hovertemplate="Residual load: %{x:,.0f} MW<br>Price: %{y:.1f} " + UNIT_PRICE + "<extra></extra>"))
    fig.update_xaxes(title="Residual load forecast (MW) = load - wind - solar")
    fig.update_yaxes(title=UNIT_PRICE)
    return _style(fig, 400, "Price vs residual load forecast").update_layout(hovermode="closest")


def correlation_bar(df: pd.DataFrame, target: str = cfg.PRICE, top: int = 15) -> go.Figure:
    num = df.select_dtypes("number").drop(columns=["year", "month", "hour", "weekday"], errors="ignore")
    corr = num.corr()[target].drop(target).dropna()
    corr = corr.reindex(corr.abs().sort_values(ascending=False).index).head(top).iloc[::-1]
    fig = go.Figure(go.Bar(x=corr.values, y=corr.index, orientation="h",
                           marker_color=[C["teal"] if v >= 0 else C["red"] for v in corr.values],
                           hovertemplate="%{y}<br>correlation: %{x:.2f}<extra></extra>"))
    fig.update_xaxes(title="Pearson correlation with price", range=[-1, 1])
    return _style(fig, 460, f"Top {top} correlations with price").update_layout(hovermode="closest")


def column_histogram(df: pd.DataFrame, col: str) -> go.Figure:
    fig = go.Figure(go.Histogram(x=df[col], nbinsx=60, marker_color=C["violet"], opacity=0.85))
    fig.update_yaxes(title="Rows")
    return _style(fig, 340, f"Distribution of {col}").update_layout(hovermode="closest", bargap=0.04)


def column_scatter(df: pd.DataFrame, x: str, y: str, max_points: int = 6000) -> go.Figure:
    d = df[[x, y]].dropna()
    if len(d) > max_points:
        d = d.sample(max_points, random_state=0)
    fig = go.Figure(go.Scattergl(x=d[x], y=d[y], mode="markers",
                                 marker=dict(size=4, color=C["blue"], opacity=0.3)))
    fig.update_xaxes(title=x)
    fig.update_yaxes(title=y)
    return _style(fig, 400, f"{y} vs {x}").update_layout(hovermode="closest")


def demo_forecast_chart(history: pd.Series, actual: pd.Series, forecast: pd.Series,
                        forecast_label: str) -> go.Figure:
    """Last days of history, then the next 24 h: actual vs forecast."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=history.index, y=history.values, name="History (model input)",
                             line=dict(color=C["slate"], width=1.5)))
    fig.add_trace(go.Scatter(x=actual.index, y=actual.values, name="Actual (next 24 h)",
                             line=dict(color=C["navy"], width=2.4)))
    fig.add_trace(go.Scatter(x=forecast.index, y=forecast.values, name=forecast_label,
                             line=dict(color=C["yellow"], width=2.4, dash="dash")))
    fig.add_vline(x=forecast.index[0], line_width=1, line_dash="dot", line_color=C["slate"])
    fig.update_yaxes(title=UNIT_PRICE)
    return _style(fig, 430, "Forecast day vs actual prices")

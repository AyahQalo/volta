"""Look and feel: CSS, KPI cards, headers and small UI helpers."""
import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.stApp { font-family: 'Inter', 'Segoe UI', system-ui, sans-serif; }
.block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1280px; }
header[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }
h1, h2, h3 { color: #0F2A4A; letter-spacing: -0.01em; }

@keyframes fadeUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

/* Brand above the sidebar navigation */
[data-testid="stSidebarNav"]::before {
    content: "\\26A1  VOLTA"; display: block; font-size: 1.5rem; font-weight: 800;
    color: #FFFFFF; padding: 1.2rem 1rem 0.4rem 1rem; letter-spacing: 0.04em;
}

/* Hero */
.hero { background: linear-gradient(135deg, #0F2A4A 0%, #1B4B82 60%, #2F6FED 100%);
        border-radius: 20px; padding: 44px 46px; margin-bottom: 1.4rem; animation: fadeUp .6s ease both; }
.hero h1 { color: #FFFFFF !important; font-size: 2.7rem; font-weight: 800; margin: 0 0 .3rem 0; }
.hero .tag { color: #F5B301; font-weight: 700; letter-spacing: .12em; font-size: .8rem; text-transform: uppercase; }
.hero p { color: #D6E2F3; max-width: 760px; font-size: 1.05rem; line-height: 1.6; margin: .6rem 0 0 0; }

/* Page header */
.ph { margin-bottom: 1.1rem; animation: fadeUp .45s ease both; }
.ph h1 { font-size: 2rem; font-weight: 800; margin: 0; }
.ph p { color: #6B7A90; margin: .25rem 0 0 0; }

/* KPI cards */
.kpi { position: relative; overflow: hidden; background: #FFFFFF; border: 1px solid #E5EAF2;
       border-radius: 16px; padding: 18px 20px 16px 22px; box-shadow: 0 1px 2px rgba(15,42,74,.04);
       transition: transform .2s ease, box-shadow .2s ease; animation: fadeUp .5s ease both; height: 100%; }
.kpi:hover { transform: translateY(-3px); box-shadow: 0 12px 26px rgba(15,42,74,.10); }
.kpi::before { content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 5px; background: var(--accent, #2F6FED); }
.kpi .label { font-size: .74rem; text-transform: uppercase; letter-spacing: .07em; color: #6B7A90; font-weight: 700; }
.kpi .value { font-size: 1.85rem; font-weight: 800; color: #0F2A4A; line-height: 1.25; margin-top: 4px; }
.kpi .sub { font-size: .8rem; color: #6B7A90; margin-top: 2px; }

/* Generic cards */
.card { background: #FFFFFF; border: 1px solid #E5EAF2; border-radius: 16px; padding: 20px 22px;
        transition: transform .2s ease, box-shadow .2s ease; animation: fadeUp .5s ease both; height: 100%; }
.card:hover { transform: translateY(-3px); box-shadow: 0 12px 26px rgba(15,42,74,.10); }
.card h4 { margin: 0 0 .35rem 0; color: #0F2A4A; font-weight: 700; }
.card p { margin: 0; color: #4A5A70; font-size: .93rem; line-height: 1.55; }

/* Status badges */
.badge { display: inline-block; padding: 3px 11px; border-radius: 999px; font-size: .72rem; font-weight: 700; letter-spacing: .04em; }
.badge-ok   { background: #DDF5EE; color: #0B6B58; }
.badge-demo { background: #FFF4CC; color: #8A6500; border: 1px solid #F5B301; }
.badge-todo { background: #EAEFF6; color: #4A5A70; }

/* Demo banner */
.demo-banner { background: #FFF8E1; border: 1px solid #F5B301; border-left: 6px solid #F5B301;
               border-radius: 12px; padding: 14px 18px; color: #6B4E00; margin-bottom: 1rem; animation: fadeUp .4s ease both; }
.demo-banner b { color: #8A6500; }

/* Tabs and buttons: subtle hover */
button[data-baseweb="tab"] { font-weight: 600; }
.stButton > button, .stDownloadButton > button { border-radius: 10px; transition: transform .15s ease, box-shadow .15s ease; }
.stButton > button:hover, .stDownloadButton > button:hover { transform: translateY(-1px); box-shadow: 0 6px 14px rgba(15,42,74,.12); }
</style>
"""


def setup_page(title: str, icon: str = "⚡") -> None:
    """Call first in every page."""
    st.set_page_config(page_title=f"{title} · VOLTA", page_icon=icon, layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "") -> None:
    sub = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(f'<div class="ph"><h1>{title}</h1>{sub}</div>', unsafe_allow_html=True)


def kpi_card(label: str, value: str, sub: str = "", accent: str = "#2F6FED", tip: str = "") -> str:
    tip_attr = f' title="{tip}"' if tip else ""
    return (f'<div class="kpi" style="--accent:{accent}"{tip_attr}>'
            f'<div class="label">{label}</div><div class="value">{value}</div>'
            f'<div class="sub">{sub}</div></div>')


def kpi_row(cards: list[dict]) -> None:
    """cards = [{"label":..., "value":..., "sub":..., "accent":..., "tip":...}, ...]"""
    cols = st.columns(len(cards))
    for col, card in zip(cols, cards):
        col.markdown(kpi_card(**card), unsafe_allow_html=True)


def info_card(title: str, body: str, badge: str = "", badge_cls: str = "badge-todo") -> str:
    b = f'<span class="badge {badge_cls}">{badge}</span><br><br>' if badge else ""
    return f'<div class="card">{b}<h4>{title}</h4><p>{body}</p></div>'


def demo_banner(text: str) -> None:
    st.markdown(f'<div class="demo-banner"><b>DEMO MODE.</b> {text}</div>', unsafe_allow_html=True)


def sidebar_status(mode: str) -> None:
    """Small status line at the bottom of the sidebar."""
    label = "Demo mode · no trained model" if mode == "demo" else "Trained model connected"
    st.sidebar.markdown("---")
    st.sidebar.caption(f"Model status: **{label}**")
    st.sidebar.caption("All timestamps are in UTC.")


def _wide() -> dict:
    return {"width": "stretch"}


def show_chart(fig, key: str | None = None) -> None:
    """Show a Plotly chart full width (works on old and new Streamlit versions)."""
    try:
        st.plotly_chart(fig, key=key, config={"displaylogo": False}, **_wide())
    except TypeError:
        st.plotly_chart(fig, key=key, config={"displaylogo": False}, use_container_width=True)


def show_df(df, **kwargs) -> None:
    """Show a dataframe full width (works on old and new Streamlit versions)."""
    try:
        st.dataframe(df, width="stretch", **kwargs)
    except TypeError:
        st.dataframe(df, use_container_width=True, **kwargs)

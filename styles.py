"""styles.py – all CSS injected once at startup."""
from __future__ import annotations
import streamlit as st

PRIMARY    = "#0A1628"
ACCENT     = "#1D6BF3"
SUCCESS    = "#059669"
WARNING    = "#E5890A"
DANGER     = "#E03535"
PAGE_BG    = "#F2F5FA"
CARD_BG    = "#FFFFFF"
TEXT_MAIN  = "#0F172A"
TEXT_MUTED = "#64748B"
BORDER     = "#E2E8F0"
SIDEBAR_BG = "#0A1628"


def inject() -> None:
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&family=DM+Serif+Display&display=swap');

*, *::before, *::after {{ box-sizing: border-box; }}

html, body, [class*="css"] {{
    font-family: 'DM Sans', sans-serif;
    background: {PAGE_BG};
    color: {TEXT_MAIN};
}}

/* ── TOP BAR ── */
header[data-testid="stHeader"] {{
    background: {PRIMARY};
    height: 2.6rem;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}}
[data-testid="stDecoration"] {{ display: none !important; }}

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {{
    background: linear-gradient(160deg, #0A1628 0%, #0f2248 60%, #0d1c3d 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
    min-width: 248px !important;
    max-width: 272px !important;
}}
section[data-testid="stSidebar"] * {{ color: #B8C5D6 !important; }}
section[data-testid="stSidebar"] label {{
    color: #6B82A0 !important;
    font-size: 0.65rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.12em !important;
}}
section[data-testid="stSidebar"] [data-baseweb="select"] > div {{
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 9px !important;
    transition: border-color .2s;
}}
section[data-testid="stSidebar"] [data-baseweb="select"] > div:focus-within {{
    border-color: {ACCENT} !important;
}}
section[data-testid="stSidebar"] [data-baseweb="select"] span {{
    color: #D4DFF0 !important;
    font-size: 0.78rem !important;
}}
section[data-testid="stSidebar"] [data-baseweb="tag"] {{
    background: rgba(29,107,243,0.3) !important;
    border: 1px solid rgba(29,107,243,0.5) !important;
    border-radius: 5px !important;
}}
section[data-testid="stSidebar"] [data-baseweb="tag"] span {{ color: #9EC5FF !important; }}
section[data-testid="stSidebar"] [data-testid="stFileUploader"] section {{
    background: rgba(255,255,255,0.04) !important;
    border: 1.5px dashed rgba(255,255,255,0.15) !important;
    border-radius: 10px !important;
}}

/* ── MAIN LAYOUT ── */
.main .block-container {{ padding: 1.2rem 2.2rem 2rem 2.2rem; max-width: 100%; }}

/* ── KPI CARDS ── */
.kpi-grid {{ display:grid; grid-template-columns:repeat(6,1fr); gap:14px; margin-bottom:1rem; }}
.kpi-card {{
    background: {CARD_BG};
    border-radius: 14px;
    border: 1px solid {BORDER};
    box-shadow: 0 2px 8px rgba(10,22,40,0.06);
    padding: 1.1rem 1.2rem 1rem;
    position: relative;
    overflow: hidden;
    transition: box-shadow .2s, transform .2s;
}}
.kpi-card::before {{
    content:'';
    position:absolute;
    top:0; left:0; right:0;
    height: 3px;
    background: var(--accent-color, {ACCENT});
    border-radius: 14px 14px 0 0;
}}
.kpi-card:hover {{
    box-shadow: 0 8px 28px rgba(10,22,40,0.13);
    transform: translateY(-2px);
}}
.kpi-icon {{ font-size:1.4rem; opacity:.18; position:absolute; top:.9rem; right:1rem; }}
.kpi-label {{
    font-size: 0.63rem;
    font-weight: 700;
    color: {TEXT_MUTED};
    text-transform: uppercase;
    letter-spacing: 0.11em;
    margin-bottom: 0.5rem;
}}
.kpi-value {{
    font-family: 'DM Mono', monospace;
    font-size: 2.05rem;
    font-weight: 500;
    line-height: 1;
    margin-bottom: 0.2rem;
}}
.kpi-sub {{ font-size: 0.65rem; color: {TEXT_MUTED}; }}
.kpi-trend {{ font-size:0.65rem; font-weight:600; }}
.kpi-trend.up {{ color:{DANGER}; }}
.kpi-trend.neutral {{ color:{TEXT_MUTED}; }}

/* ── CHART CARD ── */
.chart-card {{
    background: {CARD_BG};
    border-radius: 14px;
    border: 1px solid {BORDER};
    box-shadow: 0 2px 8px rgba(10,22,40,0.05);
    padding: 1.1rem 1.3rem 0.4rem;
    height: 100%;
}}
.chart-title {{
    font-size: 0.72rem;
    font-weight: 700;
    color: {TEXT_MUTED};
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: .7rem;
}}

/* ── SECTION LABEL ── */
.section-label {{
    font-size: 0.63rem;
    font-weight: 700;
    color: {TEXT_MUTED};
    text-transform: uppercase;
    letter-spacing: 0.14em;
    margin: 1.4rem 0 0.7rem;
    display: flex;
    align-items: center;
    gap: 6px;
}}
.section-label::after {{
    content: '';
    flex: 1;
    height: 1px;
    background: {BORDER};
}}

/* ── BADGES ── */
.badge {{
    display: inline-flex;
    align-items: center;
    padding: 2px 9px;
    border-radius: 6px;
    font-size: 0.67rem;
    font-weight: 700;
    letter-spacing: 0.02em;
    white-space: nowrap;
    line-height: 1.6;
}}
.badge-critical {{ background:#FEE2E2; color:#7F1D1D; }}
.badge-high     {{ background:#FDECEA; color:#B91C1C; }}
.badge-medium   {{ background:#FEF9C3; color:#78350F; }}
.badge-low      {{ background:#DCFCE7; color:#14532D; }}
.badge-open     {{ background:#DBEAFE; color:#1D4ED8; }}
.badge-progress {{ background:#FEF3C7; color:#92400E; }}
.badge-blocked  {{ background:#FEE2E2; color:#B91C1C; }}
.badge-closed   {{ background:#D1FAE5; color:#065F46; }}
.badge-yes      {{ background:#FEE2E2; color:#7F1D1D; }}
.badge-no       {{ background:#F1F5F9; color:#475569; }}

/* ── TOPIC TABLE ── */
.topic-table-wrap {{
    background: {CARD_BG};
    border-radius: 14px;
    border: 1px solid {BORDER};
    box-shadow: 0 2px 8px rgba(10,22,40,0.05);
    overflow: hidden;
    margin-bottom: 1rem;
}}
table.qm-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.78rem;
}}
table.qm-table thead tr {{ background: {PRIMARY}; }}
table.qm-table thead th {{
    color: rgba(255,255,255,0.6);
    font-size: 0.6rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    padding: 10px 13px;
    text-align: left;
    white-space: nowrap;
    border: none;
}}
table.qm-table tbody tr {{
    border-bottom: 1px solid {BORDER};
    transition: background .12s;
}}
table.qm-table tbody tr:last-child {{ border-bottom: none; }}
table.qm-table tbody tr:hover {{ background: #EFF6FF; }}
table.qm-table tbody tr:nth-child(even) {{ background: #FAFBFD; }}
table.qm-table tbody tr:nth-child(even):hover {{ background: #EFF6FF; }}
table.qm-table td {{
    padding: 9px 13px;
    color: {TEXT_MAIN};
    vertical-align: middle;
}}
.td-id {{
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    color: {TEXT_MUTED};
    font-weight: 500;
}}
.td-days {{
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    font-weight: 600;
}}
.td-days.red   {{ color:{DANGER}; }}
.td-days.amber {{ color:{WARNING}; }}
.td-days.green {{ color:{SUCCESS}; }}

/* ── PAGE HEADER ── */
.page-header {{
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 0.2rem 0 1.1rem;
    border-bottom: 1px solid {BORDER};
    margin-bottom: 1.1rem;
}}
.page-header-bar {{
    width: 4px; height: 46px;
    background: linear-gradient(180deg, {ACCENT} 0%, {PRIMARY} 100%);
    border-radius: 2px;
    flex-shrink: 0;
}}
.page-header-title {{
    font-family: 'DM Serif Display', serif;
    font-size: 1.45rem;
    color: {PRIMARY};
    line-height: 1.1;
    letter-spacing: -0.01em;
}}
.page-header-sub {{
    font-size: 0.71rem;
    color: {TEXT_MUTED};
    margin-top: 3px;
}}

/* ── BUTTONS ── */
div.stButton > button {{
    background: {ACCENT};
    color: #fff;
    border: none;
    border-radius: 9px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    font-size: 0.8rem;
    padding: 0.46rem 1.1rem;
    transition: background .18s, transform .1s, box-shadow .18s;
    box-shadow: 0 1px 4px rgba(29,107,243,0.25);
}}
div.stButton > button:hover {{
    background: #155BDE;
    transform: translateY(-1px);
    box-shadow: 0 4px 14px rgba(29,107,243,0.35);
}}
div[data-testid="stDownloadButton"] > button {{
    background: {PRIMARY};
    color: #fff;
    border: none;
    border-radius: 9px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    font-size: 0.8rem;
    padding: 0.46rem 1.3rem;
}}

/* ── TABS ── */
div[data-testid="stTabs"] {{
    background: {CARD_BG};
    border-radius: 10px;
    border: 1px solid {BORDER};
    padding: 0 0.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 4px rgba(10,22,40,0.04);
}}
div[data-testid="stTabs"] button {{
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    font-size: 0.82rem;
    color: {TEXT_MUTED};
    padding: 0.7rem 1.1rem;
    border-bottom: 2px solid transparent;
    border-radius: 0;
    transition: color .15s;
}}
div[data-testid="stTabs"] button[aria-selected="true"] {{
    color: {ACCENT};
    border-bottom: 2px solid {ACCENT};
}}

/* ── FORM ── */
.form-card {{
    background: {CARD_BG};
    border-radius: 14px;
    border: 2px solid {ACCENT};
    box-shadow: 0 6px 28px rgba(29,107,243,0.12);
    padding: 1.6rem 1.8rem;
    margin-bottom: 1.4rem;
}}

/* ── AI PANEL ── */
.ai-panel {{
    background: linear-gradient(135deg, #EFF6FF 0%, #F0FDF4 100%);
    border-radius: 14px;
    border: 1px solid #BFDBFE;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
}}
.ai-panel::before {{
    content: '✦';
    position: absolute;
    top: 1rem; right: 1.2rem;
    font-size: 1.6rem;
    opacity: .15;
    color: {ACCENT};
}}
.ai-panel-title {{
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: {ACCENT};
    margin-bottom: .5rem;
}}

/* ── ALERT / EXPANDER ── */
div[data-testid="stAlert"] {{ border-radius: 10px; }}
div[data-testid="stExpander"] {{
    background: {CARD_BG};
    border: 1px solid {BORDER} !important;
    border-left: none !important;
    border-right: none !important;
    border-top: none !important;
    border-radius: 0 !important;
    margin-bottom: 0 !important;
}}
div[data-testid="stExpander"] summary {{
    padding: 0 !important; font-size: 0; height: 0; overflow: hidden;
}}

/* ── MISC ── */
hr {{ border: none; border-top: 1px solid {BORDER}; margin: 1rem 0; }}
div[data-testid="stSelectbox"] > div,
div[data-testid="stTextInput"] > div > input {{
    border-radius: 9px;
    border-color: {BORDER};
    font-family: 'DM Sans', sans-serif;
}}
.img-thumb {{
    border-radius: 8px;
    border: 2px solid {BORDER};
    object-fit: cover;
    transition: border-color .2s, transform .2s;
}}
.img-thumb:hover {{ border-color: {ACCENT}; transform: scale(1.02); }}

/* ── RISK HEATMAP ── */
.heat-cell {{
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'DM Mono', monospace;
    font-size: 1.1rem;
    font-weight: 600;
    min-height: 52px;
    transition: transform .15s;
    cursor: default;
}}
.heat-cell:hover {{ transform: scale(1.05); }}
</style>
""", unsafe_allow_html=True)

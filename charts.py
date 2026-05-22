"""charts.py – all Plotly figure factories, pure functions."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from data import (
    STAT_ORDER, STAT_COLOR, SEV_ORDER, AGING_ORDER, AGING_COLORS,
    CAT_EMOJI, CATEGORIES,
)

_FONT = "DM Sans"
_TEXT_MUTED = "#64748B"
_TEXT_MAIN  = "#0F172A"
_BG = "white"
_GRID = "#F1F5F9"


def _base(title: str, h: int = 300) -> dict:
    return dict(
        title=dict(text=title, font=dict(size=11, color=_TEXT_MAIN, family=_FONT), x=0, y=.98),
        plot_bgcolor=_BG, paper_bgcolor=_BG,
        font=dict(family=_FONT, color=_TEXT_MUTED, size=11),
        margin=dict(t=36, b=8, l=6, r=6),
        height=h,
    )


def category_status_bar(df: pd.DataFrame) -> go.Figure:
    grp = df.groupby(["Category", "Status"]).size().reset_index(name="n")
    fig = px.bar(
        grp, x="Category", y="n", color="Status",
        color_discrete_map=STAT_COLOR,
        category_orders={"Status": STAT_ORDER},
        text_auto=True,
        labels={"n": "Topics", "Category": ""},
        barmode="stack",
    )
    fig.update_layout(
        **_base("Topics by Category & Status"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font=dict(size=9)),
        legend_title="",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor=_GRID, zeroline=False),
    )
    fig.update_traces(textfont_size=9, marker_line_width=0)
    return fig


def status_donut(df: pd.DataFrame, h: int = 290) -> go.Figure:
    sc = df["Status"].value_counts().reset_index()
    sc.columns = ["Status", "n"]
    fig = px.pie(
        sc, names="Status", values="n", hole=0.58,
        color="Status", color_discrete_map=STAT_COLOR,
    )
    fig.update_layout(
        **_base("Status Overview", h=h),
        showlegend=True,
        legend=dict(orientation="v", font=dict(size=9), x=1, y=0.5),
    )
    fig.update_traces(
        textposition="inside", textinfo="percent",
        marker=dict(line=dict(color="white", width=2)),
    )
    return fig


def aging_bar(df: pd.DataFrame, orientation: str = "h", h: int = 290) -> go.Figure:
    aging = df["Aging Bucket"].value_counts().reindex(AGING_ORDER).fillna(0)
    if orientation == "h":
        fig = go.Figure(go.Bar(
            y=aging.index, x=aging.values, orientation="h",
            marker_color=AGING_COLORS[:len(aging)],
            text=aging.values.astype(int), textposition="outside",
        ))
        fig.update_layout(
            **_base("Aging Distribution", h=h),
            showlegend=False,
            xaxis=dict(showgrid=True, gridcolor=_GRID, zeroline=False),
            yaxis=dict(showgrid=False, autorange="reversed"),
        )
    else:
        fig = go.Figure(go.Bar(
            x=aging.index, y=aging.values,
            marker_color=AGING_COLORS[:len(aging)],
            text=aging.values.astype(int), textposition="outside",
        ))
        fig.update_layout(
            **_base("Aging Distribution", h=h),
            showlegend=False,
            xaxis=dict(showgrid=False, tickfont=dict(size=8)),
            yaxis=dict(showgrid=True, gridcolor=_GRID),
        )
    return fig


def severity_bar(df: pd.DataFrame) -> go.Figure:
    sev_counts = df["Severity"].value_counts().reindex(SEV_ORDER).dropna()
    fig = go.Figure(go.Bar(
        x=sev_counts.index, y=sev_counts.values,
        marker_color=["#7F1D1D", "#DC2626", "#D97706", "#059669"],
        text=sev_counts.values, textposition="outside",
    ))
    fig.update_layout(
        **_base("Topics by Severity"),
        showlegend=False,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor=_GRID),
    )
    return fig


def customer_impact_donut(df: pd.DataFrame) -> go.Figure:
    ci = df["Cust. Impact"].value_counts()
    fig = px.pie(
        values=ci.values, names=ci.index, hole=0.5,
        color_discrete_sequence=["#DC2626", "#059669"],
    )
    fig.update_layout(**_base("Customer Impact"), showlegend=True)
    fig.update_traces(marker=dict(line=dict(color="white", width=2)))
    return fig


def pic_workload_bar(df: pd.DataFrame) -> go.Figure:
    """Who owns the most open issues."""
    open_df = df[df["Status"].isin(["Open", "In Progress", "Blocked"])]
    wl = open_df["PIC NED"].replace("", "Unassigned").value_counts().head(10)
    fig = go.Figure(go.Bar(
        y=wl.index, x=wl.values, orientation="h",
        marker_color="#1D6BF3",
        text=wl.values, textposition="outside",
    ))
    fig.update_layout(
        **_base("Open Topics by Owner (PIC NED)", h=320),
        showlegend=False,
        xaxis=dict(showgrid=True, gridcolor=_GRID, zeroline=False),
        yaxis=dict(showgrid=False, autorange="reversed"),
    )
    return fig


def risk_heatmap_data(df: pd.DataFrame) -> pd.DataFrame:
    """Returns pivot: Severity (rows) × Status (cols) with counts."""
    sevs = ["Critical", "High", "Medium", "Low"]
    stats = ["Blocked", "Open", "In Progress", "Closed"]
    pivot = (
        df.groupby(["Severity", "Status"])
        .size()
        .reset_index(name="n")
        .pivot(index="Severity", columns="Status", values="n")
        .reindex(index=sevs, columns=stats)
        .fillna(0)
        .astype(int)
    )
    return pivot


def opening_trend(df: pd.DataFrame) -> go.Figure:
    """Issues opened per month."""
    tmp = df.copy()
    tmp["Month"] = pd.to_datetime(tmp["Opening Date"], errors="coerce").dt.to_period("M")
    counts = tmp.groupby("Month").size().tail(12)
    if counts.empty:
        return go.Figure()
    fig = go.Figure(go.Scatter(
        x=[str(m) for m in counts.index],
        y=counts.values,
        mode="lines+markers",
        line=dict(color="#1D6BF3", width=2.5),
        marker=dict(size=6, color="#1D6BF3"),
        fill="tozeroy",
        fillcolor="rgba(29,107,243,0.08)",
    ))
    fig.update_layout(
        **_base("Issues Opened per Month (last 12)", h=230),
        xaxis=dict(showgrid=False, tickangle=-30, tickfont=dict(size=9)),
        yaxis=dict(showgrid=True, gridcolor=_GRID, zeroline=False),
    )
    return fig

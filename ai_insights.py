"""ai_insights.py – Claude-powered analysis of the QM dataset."""
from __future__ import annotations

import json
import streamlit as st
import pandas as pd

from data import safe_str


def _call_claude(prompt: str, max_tokens: int = 600) -> str:
    """Call Anthropic API; return text or error string."""
    try:
        import anthropic
        client = anthropic.Anthropic()
        msg = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text
    except Exception as e:
        return f"⚠ AI unavailable: {e}"


def _df_summary(df: pd.DataFrame) -> str:
    """Compact summary for the prompt."""
    rows = []
    for _, r in df.iterrows():
        rows.append(
            f"ID={int(r['ID'])} | {r['Category']} | {r['Severity']} | {r['Status']} | "
            f"Days={int(r['Days Open'])} | Taskforce={r['Taskforce']} | "
            f"PIC={safe_str(r.get('PIC NED',''),'?')} | "
            f"Problem: {safe_str(r.get('Problem Description',''),'')[:80]}"
        )
    return "\n".join(rows)


@st.cache_data(ttl=120, show_spinner=False)
def get_executive_summary(df_json: str) -> str:
    df = pd.read_json(df_json)
    summary = _df_summary(df)
    prompt = f"""You are a Quality Management expert at NGK Europe, an automotive parts manufacturer.
Analyse this list of open quality issues and write a crisp executive summary (5-7 bullet points, max 200 words).
Focus on: top risks, overdue items, resource bottlenecks, recommended priorities.
Format each bullet as "• [risk level emoji] <insight>".

Issues:
{summary}

Output ONLY the bullets, no preamble."""
    return _call_claude(prompt, max_tokens=400)


@st.cache_data(ttl=300, show_spinner=False)
def get_rca_suggestion(problem: str, category: str, severity: str) -> str:
    prompt = f"""You are a senior quality engineer. Given this quality issue, suggest the 3 most likely root causes using the Ishikawa/5-Why framework. Be concise (max 120 words).

Category: {category}
Severity: {severity}
Problem: {problem}

Format: numbered list 1. 2. 3. – each max 1 sentence."""
    return _call_claude(prompt, max_tokens=200)


@st.cache_data(ttl=300, show_spinner=False)
def get_action_recommendations(problem: str, rca: str, current_actions: str) -> str:
    prompt = f"""You are a quality management consultant. Suggest 3 concrete next-step corrective actions (max 150 words total).

Problem: {problem}
Root cause: {rca}
Actions taken so far: {current_actions}

Format: numbered list. Be specific and actionable."""
    return _call_claude(prompt, max_tokens=250)


def render_ai_executive_panel(df: pd.DataFrame) -> None:
    """Render the AI executive summary card."""
    st.markdown("""
    <div class="ai-panel">
      <div class="ai-panel-title">✦ AI Executive Summary</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Refresh Analysis", key="ai_refresh", use_container_width=True):
            st.cache_data.clear()

    with col1:
        if len(df) == 0:
            st.info("No data to analyse.")
            return
        with st.spinner("Analysing quality data…"):
            result = get_executive_summary(df.to_json())
        st.markdown(result)


def render_ai_topic_assistant(row: pd.Series, scope: str) -> None:
    """Inline AI assistant for a single topic."""
    tid = int(row["ID"])
    with st.expander("✦ Ask AI for insights on this topic", expanded=False):
        tab1, tab2 = st.tabs(["🔍 RCA Suggestions", "✅ Action Recommendations"])
        with tab1:
            if st.button("Analyse Root Causes", key=f"ai_rca_{scope}_{tid}"):
                with st.spinner("Thinking…"):
                    suggestion = get_rca_suggestion(
                        safe_str(row.get("Problem Description", ""), fallback=""),
                        str(row.get("Category", "")),
                        str(row.get("Severity", "")),
                    )
                st.markdown(suggestion)
        with tab2:
            if st.button("Suggest Next Actions", key=f"ai_act_{scope}_{tid}"):
                with st.spinner("Thinking…"):
                    suggestion = get_action_recommendations(
                        safe_str(row.get("Problem Description", ""), fallback=""),
                        safe_str(row.get("Root Cause Analysis", ""), fallback=""),
                        safe_str(row.get("Corrective Actions", ""), fallback=""),
                    )
                st.markdown(suggestion)

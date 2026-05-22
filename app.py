"""app.py – NGK Europe QM Dashboard · optimised edition."""
from __future__ import annotations

import base64
from datetime import date
from typing import Optional

import pandas as pd
import streamlit as st

# ── Local modules ──────────────────────────────────────────────
from auth import require_auth, render_auth_header, can_edit
import data as D
import styles
import charts as C
from ai_insights import render_ai_executive_panel, render_ai_topic_assistant

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NGK Europe · QM Dashboard",
    page_icon="🔵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# SESSION STATE HELPERS
# ─────────────────────────────────────────────────────────────
def _init() -> None:
    defaults = {
        "df": None,
        "_loaded_file": None,
        "topic_images": {},
        "show_add_form": None,
        "edit_topic_id": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def _ensure_data(uploaded=None) -> None:
    file_key = getattr(uploaded, "name", None)
    if st.session_state["df"] is None or st.session_state["_loaded_file"] != file_key:
        if uploaded is not None:
            df = D.load_from_excel(uploaded)
        else:
            df = D.load_sample()
        st.session_state["df"] = df
        st.session_state["_loaded_file"] = file_key


def get_df() -> pd.DataFrame:
    return st.session_state["df"]


def save_df(df: pd.DataFrame) -> None:
    st.session_state["df"] = df.sort_values("ID").reset_index(drop=True)


# ─────────────────────────────────────────────────────────────
# IMAGE ATTACHMENTS
# ─────────────────────────────────────────────────────────────
def get_attachments(tid: int) -> list[dict]:
    return st.session_state["topic_images"].get(tid, [])


def add_attachments(tid: int, files) -> None:
    existing = st.session_state["topic_images"].get(tid, [])
    names = {f["name"] for f in existing}
    for f in files:
        if f.name not in names:
            existing.append({"name": f.name, "data": f.read(), "type": f.type})
    st.session_state["topic_images"][tid] = existing


def remove_attachment(tid: int, name: str) -> None:
    st.session_state["topic_images"][tid] = [
        i for i in st.session_state["topic_images"].get(tid, [])
        if i["name"] != name
    ]


# ─────────────────────────────────────────────────────────────
# HTML HELPERS
# ─────────────────────────────────────────────────────────────
_SEV_CLS = {"Critical": "critical", "High": "high", "Medium": "medium", "Low": "low"}
_STAT_CLS = {"Open": "open", "In Progress": "progress", "Blocked": "blocked", "Closed": "closed"}

def badge(cls: str, text: str) -> str:
    return f'<span class="badge badge-{cls}">{text}</span>'

def sev_badge(v: str) -> str:
    return badge(_SEV_CLS.get(v, "no"), v)

def stat_badge(v: str) -> str:
    return badge(_STAT_CLS.get(v, "no"), v)


# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
def render_sidebar() -> tuple[pd.DataFrame, pd.DataFrame]:
    df_raw = get_df()

    with st.sidebar:
        st.markdown("""
        <div style="padding:1.1rem 0 .7rem;">
          <div style="font-size:.95rem;font-weight:800;color:#FFFFFF;letter-spacing:.08em;font-family:'DM Sans',sans-serif;">NGK EUROPE</div>
          <div style="font-size:.58rem;color:#3E5271;text-transform:uppercase;letter-spacing:.16em;margin-top:3px;">Quality Management</div>
        </div>
        <div style="border-top:1px solid rgba(255,255,255,0.07);margin:.2rem 0 .9rem;"></div>
        """, unsafe_allow_html=True)

        # ── Data source ──
        st.markdown('<div style="font-size:.6rem;font-weight:700;color:#3E5271;text-transform:uppercase;letter-spacing:.14em;margin-bottom:.4rem;">📁 Data Source</div>', unsafe_allow_html=True)
        uploaded = st.file_uploader("Excel Database", type=["xlsx"], label_visibility="collapsed",
                                     help="Upload Topic Database (.xlsx)")
        if uploaded:
            _ensure_data(uploaded)

        st.markdown('<div style="border-top:1px solid rgba(255,255,255,0.06);margin:.9rem 0;"></div>', unsafe_allow_html=True)

        # ── Filters ──
        cat_opts  = sorted(df_raw["Category"].dropna().unique())
        pic_opts  = sorted(df_raw["PIC NED"].replace("", pd.NA).dropna().unique())
        days_max  = max(int(df_raw["Days Open"].max()), 500) if len(df_raw) else 500

        def _head(label: str) -> None:
            st.markdown(f'<div style="font-size:.6rem;font-weight:700;color:#3E5271;text-transform:uppercase;letter-spacing:.14em;margin:.55rem 0 .25rem;">{label}</div>', unsafe_allow_html=True)

        _head("Category")
        sel_cat = st.multiselect("Category", cat_opts, default=cat_opts, label_visibility="collapsed")
        _head("Status")
        sel_stat = st.multiselect("Status", D.STAT_ORDER, default=D.STAT_ORDER, label_visibility="collapsed")
        _head("Taskforce")
        sel_tf = st.multiselect("Taskforce", ["YES", "No"], default=["YES", "No"], label_visibility="collapsed")
        _head("PIC NED")
        sel_pic = st.multiselect("PIC NED", pic_opts, default=pic_opts, label_visibility="collapsed")
        _head("Max. Days Open")
        sel_days = st.slider("Days Open", 0, days_max, days_max, label_visibility="collapsed")

        st.markdown('<div style="border-top:1px solid rgba(255,255,255,0.06);margin:.9rem 0 .4rem;"></div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:.62rem;color:#2C3D55;">📅 {date.today().strftime("%d %b %Y")}</div>', unsafe_allow_html=True)

    df_filtered = D.apply_filters(df_raw, sel_cat, sel_stat, sel_tf, sel_pic, sel_days)
    return df_raw, df_filtered


# ─────────────────────────────────────────────────────────────
# PAGE HEADER
# ─────────────────────────────────────────────────────────────
def render_header(n_shown: int, n_total: int) -> None:
    st.markdown(f"""
    <div class="page-header">
      <div class="page-header-bar"></div>
      <div>
        <div class="page-header-title">Quality Management · Topic Database</div>
        <div class="page-header-sub">NGK Europe &nbsp;·&nbsp; {date.today().strftime('%d %B %Y')} &nbsp;·&nbsp;
          <strong>{n_shown}</strong> of {n_total} topics shown
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# KPI ROW  (6 cards)
# ─────────────────────────────────────────────────────────────
def render_kpi_row(df: pd.DataFrame, df_raw: pd.DataFrame) -> None:
    counts  = df["Status"].value_counts()
    blocked = counts.get("Blocked", 0)
    critical = (df["Severity"] == "Critical").sum()

    kpis = [
        ("Total Topics",  len(df),                       styles.PRIMARY,  f"of {len(df_raw)} total",   "📋",  None),
        ("Open",          counts.get("Open", 0),          styles.ACCENT,   "active issues",             "🔵",  None),
        ("In Progress",   counts.get("In Progress", 0),   styles.WARNING,  "in work",                   "🔄",  None),
        ("Blocked",       blocked,                        styles.DANGER,   "needs immediate action",    "🚫",  "up" if blocked else "neutral"),
        ("Closed",        counts.get("Closed", 0),        styles.SUCCESS,  "resolved",                  "✅",  None),
        ("Critical",      critical,                       "#7C3AED",       "highest severity",          "⚡",  "up" if critical else "neutral"),
    ]
    accent_colors = [v[2] for v in kpis]
    cols = st.columns(6)
    for col, (label, value, color, sub, icon, trend_cls), accent in zip(cols, kpis, accent_colors):
        trend_html = ""
        if trend_cls == "up" and value > 0:
            trend_html = f'<div class="kpi-trend up">▲ Needs attention</div>'
        col.markdown(f"""
        <div class="kpi-card" style="--accent-color:{accent};">
          <div class="kpi-icon">{icon}</div>
          <div class="kpi-label">{label}</div>
          <div class="kpi-value" style="color:{color};">{value}</div>
          <div class="kpi-sub">{sub}</div>
          {trend_html}
        </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# RISK HEATMAP
# ─────────────────────────────────────────────────────────────
def render_risk_heatmap(df: pd.DataFrame) -> None:
    pivot = C.risk_heatmap_data(df)
    st.markdown('<div class="section-label">🔥 Risk Heatmap — Severity × Status</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)

    _RISK = {
        ("Critical", "Blocked"): ("#7F1D1D", "#FEE2E2"),
        ("Critical", "Open"):    ("#B91C1C", "#FEE2E2"),
        ("Critical", "In Progress"): ("#D97706", "#FEF3C7"),
        ("High",     "Blocked"): ("#B91C1C", "#FEE2E2"),
        ("High",     "Open"):    ("#D97706", "#FEF3C7"),
    }
    _DEFAULT = ("#475569", "#F8FAFC")

    cols = st.columns([1.4] + [1] * len(pivot.columns))
    with cols[0]:
        st.markdown("")
        for sev in pivot.index:
            st.markdown(f"<div style='height:52px;display:flex;align-items:center;font-weight:700;font-size:.78rem;color:#334155;'>{sev}</div>", unsafe_allow_html=True)

    for ci, status in enumerate(pivot.columns):
        with cols[ci + 1]:
            st.markdown(f"<div style='font-size:.65rem;font-weight:700;text-align:center;color:#64748B;text-transform:uppercase;letter-spacing:.09em;margin-bottom:.3rem;'>{status}</div>", unsafe_allow_html=True)
            for sev in pivot.index:
                val = int(pivot.loc[sev, status])
                txt_col, bg_col = _RISK.get((sev, status), _DEFAULT)
                opacity = "1" if val > 0 else "0.35"
                st.markdown(
                    f'<div class="heat-cell" style="background:{bg_col};color:{txt_col};opacity:{opacity};">'
                    f'{val if val > 0 else "·"}</div>',
                    unsafe_allow_html=True,
                )
    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# ADD / EDIT FORM
# ─────────────────────────────────────────────────────────────
def _topic_form(mode: str, existing: Optional[pd.Series] = None, scope: str = "ov") -> None:
    is_edit = mode == "edit"
    title   = f"✏️ Edit Topic #{int(existing['ID'])}" if is_edit else "➕ New Topic"
    st.markdown(f'<div class="form-card"><div style="font-size:1rem;font-weight:700;color:{styles.PRIMARY};margin-bottom:1rem;">{title}</div></div>', unsafe_allow_html=True)

    def _v(f, d=""):
        if is_edit and existing is not None:
            v = existing.get(f, d)
            return "" if (pd.isna(v) or str(v) == "nan") else str(v)
        return d

    def _vi(f, opts):
        v = _v(f, opts[0])
        return opts.index(v) if v in opts else 0

    with st.form(key=f"topic_form_{mode}_{scope}_{_v('ID','new')}"):
        st.markdown("#### 🏷 Identification")
        c1, c2, c3 = st.columns(3)
        with c1: tg  = st.text_input("Topic Group *",  value=_v("Topic Group"))
        with c2: sub = st.text_input("Sub-Topic *",     value=_v("Sub-Topic"))
        with c3: cat = st.selectbox("Category *",       D.CATEGORIES, index=_vi("Category", D.CATEGORIES))
        c4, c5, c6 = st.columns(3)
        with c4: sev = st.selectbox("Severity *",       D.SEVERITIES, index=_vi("Severity", D.SEVERITIES))
        with c5: sta = st.selectbox("Status *",         D.STATUSES,   index=_vi("Status",   D.STATUSES))
        with c6: tf  = st.selectbox("Taskforce",        D.TASKFORCES, index=_vi("Taskforce",D.TASKFORCES))

        st.markdown("#### 👤 Responsible")
        p1, p2, ci_col = st.columns(3)
        with p1:     ned = st.text_input("PIC NED",         value=_v("PIC NED"))
        with p2:     hq  = st.text_input("PIC HQ",          value=_v("PIC HQ"))
        with ci_col: ci  = st.selectbox("Customer Impact",  D.CUST_IMPACT, index=_vi("Cust. Impact", D.CUST_IMPACT))

        st.markdown("#### 📅 Dates")
        d1, d2, d3 = st.columns(3)
        with d1: od = st.date_input("Opening Date *",        value=D.to_date_or_none(_v("Opening Date")) or date.today())
        with d2: cd = st.date_input("Close Date (optional)", value=D.to_date_or_none(_v("Close Date")))
        with d3: ms = st.text_input("Milestones / Dates",    value=_v("Milestones / Dates", ""))

        st.markdown("#### 📝 Details")
        pd_ = st.text_area("Problem Description *",      value=_v("Problem Description"),    height=80)
        r1, r2 = st.columns(2)
        with r1: rca = st.text_area("Root Cause Analysis",   value=_v("Root Cause Analysis"),   height=80)
        with r2: ca  = st.text_area("Corrective Actions",    value=_v("Corrective Actions"),    height=80)
        q1, q2 = st.columns(2)
        with q1: prv = st.text_area("Prevention of Recurrence", value=_v("Prevention of recurrence"), height=70)
        with q2: ns  = st.text_area("Next Steps",               value=_v("Next Steps"),               height=70)

        st.markdown("---")
        sc, cc, _ = st.columns([1, 1, 4])
        with sc: submitted = st.form_submit_button("💾 Save" if is_edit else "✅ Create", use_container_width=True, type="primary")
        with cc: cancelled = st.form_submit_button("✕ Cancel", use_container_width=True)

    if cancelled:
        st.session_state["show_add_form"] = None
        st.session_state["edit_topic_id"] = None
        st.rerun()

    if submitted:
        errs = []
        if not tg.strip():  errs.append("Topic Group is required.")
        if not sub.strip(): errs.append("Sub-Topic is required.")
        if not pd_.strip(): errs.append("Problem Description is required.")
        if errs:
            for e in errs: st.error(e)
            return
        days_open = (date.today() - od).days if od else 0
        new_row = {
            "ID":               int(existing["ID"]) if is_edit else D.next_id(get_df()),
            "Topic Group":      tg.strip(), "Sub-Topic":  sub.strip(),
            "Category":         cat,        "Severity":   sev,
            "Opening Date":     pd.Timestamp(od),
            "Close Date":       pd.Timestamp(cd) if cd else pd.NaT,
            "PIC NED":          ned.strip(), "PIC HQ":    hq.strip(),
            "Status":           sta,         "Cust. Impact": ci,
            "Days Open":        days_open,
            "Aging Bucket":     D.compute_aging(days_open),
            "Taskforce":        tf,
            "Problem Description":    pd_.strip(),
            "Root Cause Analysis":    rca.strip(),
            "Corrective Actions":     ca.strip(),
            "Prevention of recurrence": prv.strip(),
            "Next Steps":             ns.strip(),
            "Milestones / Dates":     ms.strip(),
        }
        save_df(D.upsert_row(get_df(), new_row, is_edit))
        st.session_state["show_add_form"] = None
        st.session_state["edit_topic_id"] = None
        st.success(f"✅ Topic #{new_row['ID']} {'updated' if is_edit else 'created'}."); st.rerun()


# ─────────────────────────────────────────────────────────────
# IMAGE SECTION
# ─────────────────────────────────────────────────────────────
def render_image_section(tid: int, scope: str = "ov") -> None:
    attachments = get_attachments(tid)
    n = len(attachments)
    st.markdown(f"**📎 Attachments** {'· ' + str(n) + ' file(s)' if n else ''}")
    if can_edit():
        uploaded_imgs = st.file_uploader(
            f"upload_{scope}_{tid}",
            type=["png", "jpg", "jpeg", "gif", "webp", "bmp"],
            accept_multiple_files=True,
            key=f"upload_{scope}_{tid}",
            label_visibility="collapsed",
        )
        if uploaded_imgs:
            add_attachments(tid, uploaded_imgs)
            attachments = get_attachments(tid)
    if not attachments:
        st.caption("No images attached." + (" Drag & drop above." if can_edit() else ""))
        return
    for i in range(0, len(attachments), 4):
        row_imgs = attachments[i:i+4]
        img_cols = st.columns(len(row_imgs))
        for col, img in zip(img_cols, row_imgs):
            with col:
                b64 = base64.b64encode(img["data"]).decode()
                st.markdown(
                    f'<img src="data:{img["type"] or "image/png"};base64,{b64}" '
                    f'class="img-thumb" style="width:100%;max-height:120px;" title="{img["name"]}"/>',
                    unsafe_allow_html=True,
                )
                st.caption(img["name"][:22] + ("…" if len(img["name"]) > 22 else ""))
                if can_edit() and st.button("✕", key=f"del_{scope}_{tid}_{img['name']}", use_container_width=True):
                    remove_attachment(tid, img["name"]); st.rerun()


# ─────────────────────────────────────────────────────────────
# TOPIC DETAIL PANEL
# ─────────────────────────────────────────────────────────────
def _render_detail(row: pd.Series, scope: str) -> None:
    tid = int(row["ID"])
    ned = D.safe_str(row.get("PIC NED", ""), fallback="")
    hq  = D.safe_str(row.get("PIC HQ", ""),  fallback="")

    if can_edit():
        ac1, ac2, _ = st.columns([1, 1, 6])
        with ac1:
            if st.button("✏️ Edit", key=f"edit_btn_{scope}_{tid}", use_container_width=True):
                st.session_state["edit_topic_id"] = f"{scope}_{tid}"
                st.session_state["show_add_form"] = None
                st.rerun()
        with ac2:
            if st.button("🗑 Delete", key=f"del_btn_{scope}_{tid}", use_container_width=True):
                st.session_state[f"confirm_delete_{scope}_{tid}"] = True
        if st.session_state.get(f"confirm_delete_{scope}_{tid}"):
            st.error(f"⚠ Permanently delete Topic #{tid}?")
            cy, cn, _ = st.columns([1, 1, 5])
            with cy:
                if st.button("✅ Yes, delete", key=f"cy_{scope}_{tid}", use_container_width=True):
                    save_df(D.delete_row(get_df(), tid))
                    st.session_state["topic_images"].pop(tid, None)
                    st.session_state.pop(f"confirm_delete_{scope}_{tid}", None)
                    st.success(f"Deleted #{tid}."); st.rerun()
            with cn:
                if st.button("✕", key=f"cn_{scope}_{tid}", use_container_width=True):
                    st.session_state.pop(f"confirm_delete_{scope}_{tid}", None); st.rerun()

        if st.session_state.get("edit_topic_id") == f"{scope}_{tid}":
            st.markdown("---")
            _topic_form("edit", existing=row, scope=scope)
            st.markdown("---"); return

    st.markdown("---")
    ca, cb, cc, cd = st.columns([1.3, 1.3, 1, 1])
    with ca:
        st.markdown(f"**Category:** {D.CAT_EMOJI.get(row['Category'],'')} {row['Category']}")
        st.markdown(f"**Severity:** {sev_badge(D.safe_str(row.get('Severity',''), fallback='—'))}", unsafe_allow_html=True)
        st.markdown(f"**Status:** {stat_badge(row['Status'])}", unsafe_allow_html=True)
        tf_val = row.get("Taskforce", "No")
        tf_html = '<span style="color:#DC2626;font-weight:700;font-size:.75rem;">🔴 YES</span>' if tf_val == "YES" else '<span style="color:#CBD5E1;font-size:.75rem;">—</span>'
        st.markdown(f"**Taskforce:** {tf_html}", unsafe_allow_html=True)
    with cb:
        st.markdown(f"**PIC NED:** {ned if ned else '⚠ Not assigned'}")
        st.markdown(f"**PIC HQ:** {hq if hq else '⚠ Not assigned'}")
        ci = D.safe_str(row.get("Cust. Impact", "No"))
        st.markdown(f"**Cust. Impact:** {badge('yes' if ci == 'Yes' else 'no', ci)}", unsafe_allow_html=True)
    with cc:
        dc = D.days_cls(row["Days Open"])
        dc_color = {"red": styles.DANGER, "amber": styles.WARNING, "green": styles.SUCCESS}[dc]
        st.markdown(f"**Days Open:** <span class='td-days {dc}' style='color:{dc_color};'>{row['Days Open']}d</span>", unsafe_allow_html=True)
        st.markdown(f"**Aging:** {D.safe_str(row.get('Aging Bucket'))}")
    with cd:
        st.markdown(f"**Opened:** {D.format_date(row.get('Opening Date'))}")
        cv = row.get("Close Date")
        st.markdown(f"**Closed:** {D.format_date(cv) if pd.notna(cv) else 'Open'}")
        ms = D.safe_str(row.get("Milestones / Dates"))
        if ms != "—": st.markdown(f"**Milestone:** `{ms}`")

    st.markdown("---")
    d1, d2 = st.columns(2)
    with d1:
        st.markdown("**🔍 Problem Description**"); st.info(D.safe_str(row.get("Problem Description")))
        st.markdown("**🧪 Root Cause Analysis**"); st.info(D.safe_str(row.get("Root Cause Analysis")))
    with d2:
        st.markdown("**🔧 Corrective Actions**"); st.success(D.safe_str(row.get("Corrective Actions")))
        st.markdown("**➡ Next Steps**"); st.warning(D.safe_str(row.get("Next Steps")))
    prev = D.safe_str(row.get("Prevention of recurrence"))
    if prev != "—":
        st.markdown("**🛡 Prevention of Recurrence**"); st.markdown(f"> {prev}")

    st.markdown("---")
    render_image_section(tid, scope=scope)

    # ── AI assistant ──
    render_ai_topic_assistant(row, scope)


# ─────────────────────────────────────────────────────────────
# TABLE ROW HTML
# ─────────────────────────────────────────────────────────────
_SEV_BG   = {"Critical": "#FEE2E2", "High": "#FDECEA", "Medium": "#FEF9C3", "Low": "#DCFCE7"}
_SEV_COL  = {"Critical": "#7F1D1D", "High": "#B91C1C", "Medium": "#78350F", "Low": "#14532D"}
_STAT_BG  = {"Open": "#DBEAFE", "In Progress": "#FEF3C7", "Blocked": "#FEE2E2", "Closed": "#D1FAE5"}
_STAT_COL = {"Open": "#1D4ED8", "In Progress": "#92400E", "Blocked": "#B91C1C", "Closed": "#065F46"}
_DC_COLOR = {"red": "#E03535", "amber": "#E5890A", "green": "#059669"}


def _row_html(row: pd.Series) -> str:
    tid   = int(row["ID"])
    cat   = row.get("Category", "")
    emoji = D.CAT_EMOJI.get(cat, "")
    sub   = row.get("Sub-Topic", "")
    sev   = D.safe_str(row.get("Severity", ""), fallback="")
    sta   = row.get("Status", "")
    pic   = D.safe_str(row.get("PIC NED", ""), fallback="—")
    days  = int(row["Days Open"])
    aging = D.safe_str(row.get("Aging Bucket"))
    ci    = D.safe_str(row.get("Cust. Impact", "No"))
    tf    = row.get("Taskforce", "No")

    dc = D.days_cls(days)
    days_col = _DC_COLOR.get(dc, "#64748B")
    sev_bg   = _SEV_BG.get(sev, "#F1F5F9")
    sev_col  = _SEV_COL.get(sev, "#475569")
    sta_bg   = _STAT_BG.get(sta, "#F1F5F9")
    sta_col  = _STAT_COL.get(sta, "#475569")
    tf_html  = '<span style="color:#DC2626;font-weight:700;font-size:.71rem;">🔴 YES</span>' if tf == "YES" else '<span style="color:#CBD5E1;font-size:.71rem;">—</span>'
    ci_html  = '<span style="color:#B91C1C;font-weight:600;font-size:.71rem;">Yes</span>' if ci == "Yes" else '<span style="color:#94A3B8;font-size:.71rem;">—</span>'

    return (
        f'<tr>'
        f'<td class="td-id">{tid}</td>'
        f'<td><span style="font-size:.78rem;">{emoji} {cat}</span></td>'
        f'<td style="max-width:220px;"><span style="font-weight:500;font-size:.78rem;">{sub}</span></td>'
        f'<td><span style="background:{sev_bg};color:{sev_col};padding:2px 8px;border-radius:5px;font-size:.66rem;font-weight:700;">{sev}</span></td>'
        f'<td><span style="background:{sta_bg};color:{sta_col};padding:2px 8px;border-radius:5px;font-size:.66rem;font-weight:700;">{sta}</span></td>'
        f'<td style="font-size:.76rem;">{pic}</td>'
        f'<td class="td-days {dc}" style="color:{days_col};">{days}d</td>'
        f'<td style="font-size:.71rem;color:#64748B;">{aging}</td>'
        f'<td>{ci_html}</td>'
        f'<td>{tf_html}</td>'
        f'</tr>'
    )


# ─────────────────────────────────────────────────────────────
# TOPIC TABLE
# ─────────────────────────────────────────────────────────────
def render_topic_table(df: pd.DataFrame, scope: str = "ov") -> None:
    n = len(df)

    hc, bc = st.columns([5, 1])
    with hc:
        st.markdown(
            f'<div style="padding:.2rem 0 .6rem;">'
            f'<span style="font-size:.75rem;font-weight:700;color:{styles.PRIMARY};text-transform:uppercase;letter-spacing:.1em;">📋 Topic Overview</span>'
            f'<span style="margin-left:10px;font-size:.71rem;color:{styles.TEXT_MUTED};">{n} {"Issue" if n == 1 else "Issues"}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
    if can_edit():
        with bc:
            if st.button("➕ Add Topic", use_container_width=True, key=f"add_topic_btn_{scope}"):
                st.session_state["show_add_form"] = scope
                st.session_state["edit_topic_id"] = None
    else:
        with bc:
            st.info("🔒 Read-only")

    if st.session_state.get("show_add_form") == scope:
        _topic_form("add", scope=scope)

    # ── Search / sort controls ──
    f1, f2, f3 = st.columns([3, 1.5, 1])
    with f1:
        search = st.text_input("s", placeholder="🔍  Search topics…", label_visibility="collapsed", key=f"search_{scope}")
    with f2:
        sort_by = st.selectbox("sort", ["ID", "Days Open", "Status", "Category", "Severity"], label_visibility="collapsed", key=f"sort_{scope}")
    with f3:
        asc = st.selectbox("dir", ["↑ Asc", "↓ Desc"], label_visibility="collapsed", key=f"dir_{scope}") == "↑ Asc"

    dfs = D.apply_filters(df, [], [], [], [], 99999, search)
    if sort_by == "Status":
        dfs["_r"] = dfs["Status"].map(D.STAT_RANK)
        dfs = dfs.sort_values("_r", ascending=asc).drop(columns="_r")
    else:
        dfs = dfs.sort_values(sort_by, ascending=asc)

    st.caption(f"{len(dfs)} topic(s) shown")

    # ── Flat HTML table ──
    rows_html = "".join(_row_html(row) for _, row in dfs.iterrows())
    st.markdown(f"""
    <div class="topic-table-wrap">
    <table class="qm-table">
      <thead><tr>
        <th>ID</th><th>CATEGORY</th><th>SUB-TOPIC</th><th>SEVERITY</th>
        <th>STATUS</th><th>PIC</th><th>DAYS</th><th>AGING</th>
        <th>CUST.</th><th>TASKFORCE</th>
      </tr></thead>
      <tbody>{rows_html}</tbody>
    </table></div>
    """, unsafe_allow_html=True)

    # ── Detail expanders ──
    st.markdown(f'<div class="section-label">🔍 Detail View</div>', unsafe_allow_html=True)
    for _, row in dfs.iterrows():
        tid   = int(row["ID"])
        n_img = len(get_attachments(tid))
        img_f = f" 📎{n_img}" if n_img else ""
        label = f"#{tid} · {row['Sub-Topic']} — {row['Topic Group']}{img_f}"
        with st.expander(label, expanded=False, key=f"exp_{scope}_{tid}"):
            _render_detail(row, scope)


# ─────────────────────────────────────────────────────────────
# ANALYTICS TAB
# ─────────────────────────────────────────────────────────────
def render_analytics(df: pd.DataFrame) -> None:
    # ── AI summary ──
    render_ai_executive_panel(df)

    # ── Trend ──
    st.markdown('<div class="section-label">📈 Trend</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.plotly_chart(C.opening_trend(df), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Category / status / aging ──
    st.markdown('<div class="section-label">📊 Distribution</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1.6, 1.1, 1.1])
    with c1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(C.category_status_bar(df), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(C.status_donut(df), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(C.aging_bar(df), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Severity / CI / Owner ──
    st.markdown('<div class="section-label">👤 People & Risk</div>', unsafe_allow_html=True)
    sv, cv, wl = st.columns(3)
    with sv:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(C.severity_bar(df), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with cv:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(C.customer_impact_donut(df), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with wl:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(C.pic_workload_bar(df), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Risk heatmap ──
    render_risk_heatmap(df)


# ─────────────────────────────────────────────────────────────
# EXPORT
# ─────────────────────────────────────────────────────────────
def render_export(df: pd.DataFrame) -> None:
    st.markdown("---")
    c1, c2 = st.columns([1, 5])
    with c1:
        st.download_button(
            label="⬇ Export Excel",
            data=D.make_excel_bytes(df),
            file_name=f"QM_Topics_{date.today().isoformat()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    with c2:
        st.caption(f"Exporting {len(df)} filtered topic(s) · Generated {date.today().strftime('%d %B %Y')}")


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────
def main() -> None:
    require_auth()
    _init()
    _ensure_data()
    styles.inject()
    render_auth_header()

    df_raw, df = render_sidebar()

    render_header(n_shown=len(df), n_total=len(df_raw))
    render_kpi_row(df, df_raw)

    st.markdown("<div style='margin:.5rem 0'></div>", unsafe_allow_html=True)

    tab_overview, tab_analytics, tab_topics = st.tabs([
        "  📋  Overview  ",
        "  📊  Analytics  ",
        "  📁  All Topics  ",
    ])

    with tab_overview:
        left, right = st.columns([2.2, 1])
        with left:
            render_topic_table(df, scope="ov")
        with right:
            st.markdown('<div class="section-label">Status</div>', unsafe_allow_html=True)
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            st.plotly_chart(C.status_donut(df, h=210), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown('<div class="section-label">Aging</div>', unsafe_allow_html=True)
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            st.plotly_chart(C.aging_bar(df, orientation="v", h=185), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    with tab_analytics:
        render_analytics(df)

    with tab_topics:
        render_topic_table(df, scope="all")
        render_export(df)


if __name__ == "__main__":
    main()

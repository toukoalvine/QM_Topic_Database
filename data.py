"""data.py – all data logic, zero Streamlit imports."""
from __future__ import annotations

import io
from datetime import date
from typing import Optional

import pandas as pd

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
CATEGORIES  = ["Elements", "Assembly", "Cross"]
SEVERITIES  = ["Critical", "High", "Medium", "Low"]
STATUSES    = ["Open", "In Progress", "Blocked", "Closed"]
TASKFORCES  = ["YES", "No"]
CUST_IMPACT = ["No", "Yes"]

SEV_ORDER   = ["Critical", "High", "Medium", "Low"]
STAT_ORDER  = ["Open", "In Progress", "Blocked", "Closed"]
AGING_ORDER = ["0–3 Months", "3–6 Months", "6–12 Months", "> 1 Year"]
STAT_RANK   = {"Blocked": 0, "Open": 1, "In Progress": 2, "Closed": 3}

STAT_COLOR  = {
    "Open": "#2563EB", "In Progress": "#D97706",
    "Blocked": "#DC2626", "Closed": "#059669",
}
AGING_COLORS = ["#059669", "#D97706", "#EA580C", "#DC2626"]
CAT_EMOJI    = {"Elements": "🔵", "Assembly": "🟢", "Cross": "🟡"}

DAYS_RED    = 180
DAYS_ORANGE = 60

# ─────────────────────────────────────────────
# SAMPLE DATA
# ─────────────────────────────────────────────
SAMPLE_ROWS: list[dict] = [
    dict(ID=1, **{"Topic Group": "Welding Defects", "Sub-Topic": "Porosity in MIG Welds", "Category": "Elements", "Severity": "High", "Opening Date": "2026-02-24", "Close Date": None, "PIC NED": "J. Müller", "PIC HQ": "J. Müller", "Status": "Open", "Cust. Impact": "Yes", "Days Open": 38, "Taskforce": "YES", "Problem Description": "Porosity in batch WD-22; ~15% rejection rate.", "Root Cause Analysis": "Shielding gas contamination on line 3.", "Corrective Actions": "Replaced gas supply line; tightened fittings.", "Prevention of recurrence": "Monthly gas-line inspection added to PM schedule.", "Next Steps": "Requalification test next week.", "Milestones / Dates": "8D Due: 2026-03-23"}),
    dict(ID=2, **{"Topic Group": "Assembly Sequence", "Sub-Topic": "Bolt torque out-of-spec", "Category": "Assembly", "Severity": "Medium", "Opening Date": "2025-11-06", "Close Date": "2026-03-06", "PIC NED": "A. Schmidt", "PIC HQ": "A. Schmidt", "Status": "Closed", "Cust. Impact": "No", "Days Open": 120, "Taskforce": "No", "Problem Description": "Torque 10% below spec on rear bracket.", "Root Cause Analysis": "Calibration drift on station 7.", "Corrective Actions": "Wrench recalibrated; audit done.", "Prevention of recurrence": "Quarterly calibration schedule established.", "Next Steps": None, "Milestones / Dates": None}),
    dict(ID=3, **{"Topic Group": "Supplier Quality", "Sub-Topic": "Dimensional deviation – X401", "Category": "Cross", "Severity": "Critical", "Opening Date": "2025-07-09", "Close Date": None, "PIC NED": "L. Bauer", "PIC HQ": "", "Status": "Blocked", "Cust. Impact": "Yes", "Days Open": 268, "Taskforce": "YES", "Problem Description": "OD of X401 exceeds tolerance +0.3 mm.", "Root Cause Analysis": "Under investigation – supplier audit planned.", "Corrective Actions": "Interim: 100% incoming inspection.", "Prevention of recurrence": "Supplier qualification criteria to be tightened.", "Next Steps": "Awaiting supplier 8D response.", "Milestones / Dates": "Supplier response due: 2026-03-19"}),
    dict(ID=4, **{"Topic Group": "Paint & Coating", "Sub-Topic": "Surface adhesion failure", "Category": "Elements", "Severity": "High", "Opening Date": "2025-02-09", "Close Date": None, "PIC NED": "", "PIC HQ": "K. Vogel", "Status": "Open", "Cust. Impact": "No", "Days Open": 418, "Taskforce": "YES", "Problem Description": "Peeling after 48h salt-spray test.", "Root Cause Analysis": "Pre-treatment bath concentration out of range.", "Corrective Actions": "Bath replenished; batch quarantined.", "Prevention of recurrence": "Auto-dosing system approved for installation.", "Next Steps": "Retest batch after rework.", "Milestones / Dates": None}),
    dict(ID=5, **{"Topic Group": "Welding Defects", "Sub-Topic": "Undercut on fillet welds", "Category": "Elements", "Severity": "Medium", "Opening Date": "2026-01-30", "Close Date": None, "PIC NED": "J. Müller", "PIC HQ": "J. Müller", "Status": "In Progress", "Cust. Impact": "No", "Days Open": 63, "Taskforce": "No", "Problem Description": "Undercut >0.5 mm on fillet joints zone B.", "Root Cause Analysis": "Travel speed too high; welder technique.", "Corrective Actions": "Additional welder training completed.", "Prevention of recurrence": "Travel speed added to CNC process parameters.", "Next Steps": "Monitor next 3 production runs.", "Milestones / Dates": None}),
    dict(ID=6, **{"Topic Group": "Supplier Quality", "Sub-Topic": "Late delivery – Component Y7", "Category": "Cross", "Severity": "Medium", "Opening Date": "2026-01-15", "Close Date": None, "PIC NED": "M. Weber", "PIC HQ": "M. Weber", "Status": "Open", "Cust. Impact": "Yes", "Days Open": 78, "Taskforce": "No", "Problem Description": "Supplier 3-5 days late consistently.", "Root Cause Analysis": "Raw material shortage at supplier.", "Corrective Actions": "Dual-sourcing approval in progress.", "Prevention of recurrence": "Safety stock level raised to 3 weeks.", "Next Steps": "Qualify second supplier by month-end.", "Milestones / Dates": None}),
    dict(ID=7, **{"Topic Group": "Assembly Sequence", "Sub-Topic": "Misaligned bracket – Stn 4", "Category": "Assembly", "Severity": "Low", "Opening Date": "2026-03-01", "Close Date": None, "PIC NED": "A. Schmidt", "PIC HQ": "A. Schmidt", "Status": "In Progress", "Cust. Impact": "No", "Days Open": 33, "Taskforce": "No", "Problem Description": "Bracket deviation 2mm on 8% of parts.", "Root Cause Analysis": "Fixture wear on station 4.", "Corrective Actions": "Fixture replaced and re-qualified.", "Prevention of recurrence": "Fixture wear added to 500-cycle PM checklist.", "Next Steps": "Monitor next 3 runs.", "Milestones / Dates": None}),
    dict(ID=8, **{"Topic Group": "Paint & Coating", "Sub-Topic": "Orange peel texture", "Category": "Elements", "Severity": "Low", "Opening Date": "2025-08-28", "Close Date": None, "PIC NED": "K. Vogel", "PIC HQ": "K. Vogel", "Status": "Blocked", "Cust. Impact": "No", "Days Open": 218, "Taskforce": "YES", "Problem Description": "Orange peel on exterior panels.", "Root Cause Analysis": "Paint viscosity out of spec.", "Corrective Actions": "Viscosity adjusted; process frozen.", "Prevention of recurrence": "In-line viscosity sensor approved for Q3 install.", "Next Steps": "Waiting for customer waiver.", "Milestones / Dates": None}),
]


# ─────────────────────────────────────────────
# PURE HELPERS
# ─────────────────────────────────────────────
def compute_aging(days: int) -> str:
    if days <= 90:  return "0–3 Months"
    if days <= 180: return "3–6 Months"
    if days <= 365: return "6–12 Months"
    return "> 1 Year"


def days_cls(d: int) -> str:
    return "red" if d > DAYS_RED else ("amber" if d > DAYS_ORANGE else "green")


def format_date(v) -> str:
    return pd.Timestamp(v).strftime("%d %b %Y") if pd.notna(v) else "—"


def safe_str(v, fallback: str = "—") -> str:
    s = str(v) if pd.notna(v) else ""
    return s if s not in ("", "nan", "NaT") else fallback


def to_date_or_none(val) -> Optional[date]:
    if val is None or (hasattr(val, "__class__") and str(val) in ("", "nan", "NaT")):
        return None
    try:
        return pd.Timestamp(val).date()
    except Exception:
        return None


def normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]
    df = df.dropna(subset=["ID"])
    df["ID"] = df["ID"].astype(int)
    if "Escalated" in df.columns and "Taskforce" not in df.columns:
        df = df.rename(columns={"Escalated": "Taskforce"})
    df["Taskforce"] = (
        df["Taskforce"].astype(str).str.strip().str.upper()
        .map(lambda x: "YES" if x == "YES" else "No")
    )
    if "Cust. Impact" not in df.columns:
        df["Cust. Impact"] = "No"
    df["Cust. Impact"] = df["Cust. Impact"].fillna("No")
    for col in ("PIC NED", "PIC HQ"):
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].fillna("").astype(str).str.strip()
    for col in ("Opening Date", "Close Date"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    df["Days Open"] = (
        pd.to_numeric(df.get("Days Open", 0), errors="coerce").fillna(0).astype(int)
    )
    df["Aging Bucket"] = df["Days Open"].apply(compute_aging)
    return df.sort_values("ID").reset_index(drop=True)


def load_from_excel(file) -> pd.DataFrame:
    df = pd.read_excel(file, sheet_name="Topic Database", header=1)
    return normalize_df(df)


def load_sample() -> pd.DataFrame:
    return normalize_df(pd.DataFrame(SAMPLE_ROWS))


def make_excel_bytes(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    df.to_excel(buf, index=False, sheet_name="Filtered Topics")
    return buf.getvalue()


def apply_filters(
    df: pd.DataFrame,
    categories: list,
    statuses: list,
    taskforces: list,
    pics: list,
    max_days: int,
    search: str = "",
) -> pd.DataFrame:
    mask = pd.Series(True, index=df.index)
    if categories: mask &= df["Category"].isin(categories)
    if statuses:   mask &= df["Status"].isin(statuses)
    if taskforces: mask &= df["Taskforce"].isin(taskforces)
    if pics:       mask &= df["PIC NED"].isin(pics)
    mask &= df["Days Open"] <= max_days
    result = df[mask].copy()
    if search.strip():
        s = search.strip().lower()
        result = result[result.apply(
            lambda r: r.astype(str).str.lower().str.contains(s, na=False).any(), axis=1
        )]
    return result


def next_id(df: pd.DataFrame) -> int:
    return int(df["ID"].max()) + 1 if len(df) else 1


def upsert_row(df: pd.DataFrame, row: dict, is_edit: bool) -> pd.DataFrame:
    if is_edit:
        idx = df.index[df["ID"] == row["ID"]].tolist()
        if idx:
            df.loc[idx[0]] = row
    else:
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    return df.sort_values("ID").reset_index(drop=True)


def delete_row(df: pd.DataFrame, tid: int) -> pd.DataFrame:
    return df[df["ID"] != tid].reset_index(drop=True)

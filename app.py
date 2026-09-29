from __future__ import annotations

from pathlib import Path
import html

import pandas as pd
import streamlit as st

from fraud_rules import score_transaction, rapid_transaction_signal, enrich_score
from database import (
    init_db,
    upsert_case,
    get_case,
    save_checklist,
    save_decision,
    all_cases,
    get_checklist,
)
from investigation import build_case_id, SOP_STEPS, evaluate_chargeback, resolution_for
from report_generator import create_html_report


# ============================================================
# APP CONFIG
# ============================================================
st.set_page_config(
    page_title="Fraud Operations Console",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()
DATA_DIR = Path(__file__).resolve().parent / "data"


# ============================================================
# THEME + GLOBAL UI
# ============================================================
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False


def inject_theme(dark: bool) -> None:
    if dark:
        colors = {
            "page": "#0b1220",
            "panel": "#111a2b",
            "panel2": "#162137",
            "ink": "#edf3fb",
            "muted": "#9aa9bc",
            "muted2": "#75859b",
            "line": "#26344a",
            "line2": "#33445d",
            "input": "#0f1828",
            "blue": "#6ea8ff",
            "blue_soft": "#162946",
            "green": "#46c27a",
            "green_soft": "#112a20",
            "amber": "#f2c35d",
            "amber_soft": "#2f2613",
            "red": "#ff7f7f",
            "red_soft": "#32191b",
            "sidebar": "#07101e",
            "sidebar2": "#0c1728",
            "hero1": "#0b1628",
            "hero2": "#142746",
            "table_hover": "#17263c",
        }
    else:
        colors = {
            "page": "#f3f6fa",
            "panel": "#ffffff",
            "panel2": "#f8fafc",
            "ink": "#152033",
            "muted": "#718096",
            "muted2": "#8d99aa",
            "line": "#dfe5ed",
            "line2": "#cbd5e1",
            "input": "#ffffff",
            "blue": "#2f6fed",
            "blue_soft": "#edf4ff",
            "green": "#197a43",
            "green_soft": "#edf8f1",
            "amber": "#9a6700",
            "amber_soft": "#fff7e6",
            "red": "#b42318",
            "red_soft": "#fff0f0",
            "sidebar": "#0a1322",
            "sidebar2": "#101d31",
            "hero1": "#0b1628",
            "hero2": "#19355a",
            "table_hover": "#f7faff",
        }

    st.markdown(
        f"""
        <style>
        :root {{
            --page: {colors['page']};
            --panel: {colors['panel']};
            --panel2: {colors['panel2']};
            --ink: {colors['ink']};
            --muted: {colors['muted']};
            --muted2: {colors['muted2']};
            --line: {colors['line']};
            --line2: {colors['line2']};
            --input: {colors['input']};
            --blue: {colors['blue']};
            --blue-soft: {colors['blue_soft']};
            --green: {colors['green']};
            --green-soft: {colors['green_soft']};
            --amber: {colors['amber']};
            --amber-soft: {colors['amber_soft']};
            --red: {colors['red']};
            --red-soft: {colors['red_soft']};
            --sidebar: {colors['sidebar']};
            --sidebar2: {colors['sidebar2']};
            --hero1: {colors['hero1']};
            --hero2: {colors['hero2']};
            --table-hover: {colors['table_hover']};
        }}

        .stApp {{
            background: var(--page);
            color: var(--ink);
        }}

        .block-container {{
            max-width: 1500px;
            padding: 1.35rem 2rem 3rem;
        }}

        [data-testid="stHeader"] {{
            background: transparent;
        }}

        /* Sidebar */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, var(--sidebar) 0%, var(--sidebar2) 100%);
            border-right: 1px solid rgba(255,255,255,.07);
        }}

        [data-testid="stSidebar"] * {{
            color: #e9eff8;
        }}

        [data-testid="stSidebar"] .stMarkdown p,
        [data-testid="stSidebar"] .stCaption {{
            color: #9aabc1 !important;
        }}

        [data-testid="stSidebar"] hr {{
            border-color: rgba(255,255,255,.09);
        }}

        [data-testid="stSidebar"] [data-testid="stRadio"] label {{
            border-radius: 10px;
            padding: 6px 9px;
            margin: 2px 0;
            transition: .18s ease;
        }}

        [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {{
            background: rgba(255,255,255,.07);
        }}

        [data-testid="stSidebar"] [data-testid="stToggle"] label {{
            color: #dbe6f5 !important;
        }}

        /* Typography */
        h1, h2, h3, h4, h5, h6,
        p, label, span, small, li {{
            color: var(--ink);
        }}

        h1 {{
            font-size: 2rem !important;
            font-weight: 820 !important;
            letter-spacing: -.035em;
        }}

        h2, h3 {{
            font-weight: 780 !important;
            letter-spacing: -.022em;
        }}

        [data-testid="stCaptionContainer"] p {{
            color: var(--muted) !important;
        }}

        /* Hero */
        .hero {{
            background: linear-gradient(135deg, var(--hero1) 0%, var(--hero2) 100%);
            border: 1px solid rgba(255,255,255,.07);
            border-radius: 20px;
            padding: 26px 28px 24px;
            margin-bottom: 18px;
            box-shadow: 0 14px 34px rgba(7,16,30,.12);
        }}

        .hero-eyebrow {{
            color: #83b8ff;
            font-size: 10px;
            font-weight: 850;
            letter-spacing: .16em;
            text-transform: uppercase;
        }}

        .hero-title {{
            color: #ffffff;
            font-size: 29px;
            line-height: 1.12;
            font-weight: 820;
            letter-spacing: -.035em;
            margin: 5px 0 7px;
        }}

        .hero-sub {{
            color: #b9c7d9;
            max-width: 860px;
            font-size: 13px;
            line-height: 1.55;
            margin: 0;
        }}

        .hero-meta {{
            margin-top: 15px;
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }}

        .pill {{
            display: inline-block;
            padding: 5px 9px;
            border-radius: 999px;
            font-size: 9px;
            font-weight: 780;
            letter-spacing: .04em;
        }}

        .pill-blue {{ background: rgba(110,168,255,.12); color: #9ac4ff; border: 1px solid rgba(110,168,255,.2); }}
        .pill-green {{ background: rgba(70,194,122,.12); color: #7fe0a5; border: 1px solid rgba(70,194,122,.2); }}

        /* Cards */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(5, minmax(0,1fr));
            gap: 12px;
            margin-bottom: 18px;
        }}

        .kpi {{
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 15px;
            padding: 16px 17px;
            min-height: 108px;
            box-shadow: 0 4px 16px rgba(31,45,61,.035);
        }}

        .kpi-label {{
            color: var(--muted) !important;
            font-size: 10px;
            font-weight: 720;
            text-transform: uppercase;
            letter-spacing: .06em;
        }}

        .kpi-value {{
            color: var(--ink) !important;
            font-size: 27px;
            line-height: 1;
            font-weight: 830;
            margin-top: 9px;
        }}

        .kpi-note {{
            color: var(--muted2) !important;
            font-size: 10px;
            margin-top: 8px;
        }}

        .soft-panel {{
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 15px;
            padding: 15px 16px;
            box-shadow: 0 4px 16px rgba(31,45,61,.03);
        }}

        .section-head {{
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            gap: 15px;
            margin: 15px 0 8px;
        }}

        .section-title {{
            color: var(--ink) !important;
            font-size: 14px;
            font-weight: 820;
        }}

        .section-caption {{
            color: var(--muted2) !important;
            font-size: 10px;
        }}

        .priority-banner {{
            display:flex;
            align-items:center;
            justify-content:space-between;
            gap:12px;
            background: var(--blue-soft);
            border: 1px solid var(--line2);
            border-radius: 13px;
            padding: 11px 14px;
            margin-bottom: 10px;
        }}

        .priority-banner-title {{
            color: var(--ink) !important;
            font-size: 12px;
            font-weight: 800;
        }}

        .priority-banner-sub {{
            color: var(--muted) !important;
            font-size: 10px;
            margin-top: 2px;
        }}

        .top-status {{
            font-size: 10px;
            font-weight: 800;
            color: var(--green) !important;
            background: var(--green-soft);
            border: 1px solid var(--line);
            border-radius: 999px;
            padding: 6px 9px;
            white-space: nowrap;
        }}

        /* Buttons */
        div[data-testid="stButton"] > button,
        div[data-testid="stDownloadButton"] > button {{
            border-radius: 10px !important;
            border: 1px solid var(--line2) !important;
            background: var(--panel) !important;
            color: var(--ink) !important;
            font-weight: 720 !important;
            min-height: 40px;
            box-shadow: 0 2px 8px rgba(15,23,42,.035);
            transition: all .16s ease;
        }}

        div[data-testid="stButton"] > button:hover,
        div[data-testid="stDownloadButton"] > button:hover {{
            border-color: var(--blue) !important;
            color: var(--blue) !important;
            background: var(--blue-soft) !important;
            transform: translateY(-1px);
        }}

        div[data-testid="stButton"] > button[kind="primary"] {{
            background: var(--blue) !important;
            border-color: var(--blue) !important;
            color: white !important;
            box-shadow: 0 8px 18px rgba(47,111,237,.18);
        }}

        div[data-testid="stButton"] > button[kind="primary"]:hover {{
            filter: brightness(1.05);
            color: white !important;
        }}

        /* Inputs, selects and forms */
        input, textarea {{
            background: var(--input) !important;
            color: var(--ink) !important;
            border-color: var(--line2) !important;
        }}

        input::placeholder, textarea::placeholder {{
            color: var(--muted2) !important;
        }}

        div[data-baseweb="select"] > div {{
            background: var(--input) !important;
            color: var(--ink) !important;
            border-color: var(--line2) !important;
            border-radius: 10px !important;
        }}

        div[data-baseweb="select"] * {{
            color: var(--ink) !important;
        }}

        div[data-baseweb="popover"] {{
            background: var(--panel) !important;
        }}

        [role="listbox"] {{
            background: var(--panel) !important;
            border: 1px solid var(--line) !important;
        }}

        [role="option"] {{
            color: var(--ink) !important;
        }}

        [role="option"]:hover {{
            background: var(--blue-soft) !important;
        }}

        div[data-testid="stTextInput"] label,
        div[data-testid="stTextArea"] label,
        div[data-testid="stNumberInput"] label,
        div[data-testid="stSelectbox"] label,
        div[data-testid="stMultiSelect"] label,
        div[data-testid="stRadio"] label,
        div[data-testid="stCheckbox"] label,
        div[data-testid="stToggle"] label {{
            color: var(--ink) !important;
            font-weight: 650;
        }}

        /* Tabs */
        div[data-baseweb="tab-list"] {{
            gap: 4px;
            border-bottom: 1px solid var(--line) !important;
        }}

        button[data-baseweb="tab"] {{
            color: var(--muted) !important;
            border-radius: 9px 9px 0 0 !important;
            padding: 9px 13px !important;
            font-weight: 700 !important;
        }}

        button[data-baseweb="tab"][aria-selected="true"] {{
            color: var(--blue) !important;
            background: var(--blue-soft) !important;
        }}

        /* Expanders */
        div[data-testid="stExpander"] {{
            background: var(--panel) !important;
            border: 1px solid var(--line) !important;
            border-radius: 13px !important;
        }}

        div[data-testid="stExpander"] summary span {{
            color: var(--ink) !important;
            font-weight: 700 !important;
        }}

        /* Alerts */
        div[data-testid="stAlert"] {{
            border-radius: 12px !important;
            border-width: 1px !important;
        }}

        /* JSON viewer */
        div[data-testid="stJson"] {{
            background: var(--panel2) !important;
            border: 1px solid var(--line) !important;
            border-radius: 12px !important;
            padding: 8px !important;
        }}

        /* Dataframes */
        div[data-testid="stDataFrame"] {{
            border: 1px solid var(--line) !important;
            border-radius: 12px !important;
            overflow: hidden;
        }}

        /* Metrics */
        [data-testid="stMetric"] {{
            background: var(--panel) !important;
            border: 1px solid var(--line) !important;
            border-radius: 12px !important;
            padding: 10px 12px !important;
        }}

        [data-testid="stMetricLabel"] p {{
            color: var(--muted) !important;
        }}

        [data-testid="stMetricValue"] {{
            color: var(--ink) !important;
        }}

        .footer-note {{
            color: var(--muted2) !important;
            font-size: 9px;
            text-align: center;
            padding-top: 20px;
        }}

        .sidebar-brand {{ padding: 7px 3px 16px; }}
        .sidebar-title {{ color: #ffffff !important; font-size: 17px; font-weight: 820; }}
        .sidebar-sub {{ color: #9eb0c6 !important; font-size: 10px; margin-top: 3px; line-height: 1.5; }}
        .sidebar-tag {{ display:inline-block; margin-top:10px; padding:4px 7px; border-radius:999px; background:rgba(255,255,255,.08); color:#c2d1e4 !important; font-size:9px; font-weight:760; }}

        @media (max-width: 1100px) {{
            .kpi-grid {{ grid-template-columns: repeat(2, minmax(0,1fr)); }}
            .block-container {{ padding-left: 1rem; padding-right: 1rem; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_theme(st.session_state.dark_mode)


# ============================================================
# UI HELPERS
# ============================================================
def render_kpi(label: str, value, note: str = "") -> None:
    st.markdown(
        f"""
        <div class="kpi">
            <div class="kpi-label">{html.escape(str(label))}</div>
            <div class="kpi-value">{html.escape(str(value))}</div>
            <div class="kpi-note">{html.escape(str(note))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_head(title: str, caption: str = "") -> None:
    st.markdown(
        f"""
        <div class="section-head">
            <div class="section-title">{html.escape(str(title))}</div>
            <div class="section-caption">{html.escape(str(caption))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_header(eyebrow: str, title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-eyebrow">{html.escape(eyebrow)}</div>
            <div class="hero-title">{html.escape(title)}</div>
            <p class="hero-sub">{html.escape(subtitle)}</p>
            <div class="hero-meta">
                <span class="pill pill-blue">LOCAL DEMO</span>
                <span class="pill pill-green">SYNTHETIC DATA</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def priority_banner(title: str, subtitle: str, status: str | None = None) -> None:
    status_html = (
        f'<div class="top-status">{html.escape(status)}</div>' if status else ""
    )
    st.markdown(
        f"""
        <div class="priority-banner">
            <div>
                <div class="priority-banner-title">{html.escape(title)}</div>
                <div class="priority-banner-sub">{html.escape(subtitle)}</div>
            </div>
            {status_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def safe_number(series: pd.Series) -> float:
    return float(pd.to_numeric(series, errors="coerce").fillna(0).sum())


# ============================================================
# DATA
# ============================================================
@st.cache_data
def load_data():
    return (
        pd.read_csv(DATA_DIR / "transactions.csv"),
        pd.read_csv(DATA_DIR / "customers.csv"),
        pd.read_csv(DATA_DIR / "claims.csv"),
    )


tx_df, customers_df, claims_df = load_data()
all_tx = tx_df.astype(object).where(pd.notna(tx_df), None).to_dict("records")


def tx_by_id(txid):
    m = tx_df[tx_df["transaction_id"] == txid]
    return m.iloc[0].to_dict() if not m.empty else None


def claim_for_tx(txid):
    m = claims_df[claims_df["transaction_id"] == txid]
    return m.iloc[0].to_dict() if not m.empty else None


def history_for_customer(cid, exclude=None):
    m = tx_df[tx_df["customer_id"] == cid].copy()
    if exclude:
        m = m[m["transaction_id"] != exclude]
    return m.sort_values("timestamp", ascending=False).to_dict("records")


@st.cache_data
def build_scores():
    data = []
    for tx in all_tx:
        base = score_transaction(tx)
        rapid = rapid_transaction_signal(all_tx, tx["customer_id"], tx["timestamp"])
        result = enrich_score(base, rapid)
        result["transaction_id"] = tx["transaction_id"]
        data.append(result)
    return pd.DataFrame(data)


scores_df = build_scores()


# ============================================================
# CASE INITIALIZATION
# ============================================================
for _, row in scores_df.iterrows():
    tx = tx_by_id(row["transaction_id"])
    claim = claim_for_tx(row["transaction_id"])
    case_id = build_case_id(row["transaction_id"])

    if tx is None:
        continue

    if not get_case(case_id):
        upsert_case(
            {
                "case_id": case_id,
                "transaction_id": row["transaction_id"],
                "customer_id": tx["customer_id"],
                "claim_id": claim["claim_id"] if claim else None,
                "risk_score": int(row["score"]),
                "risk_level": row["level"],
                "alert_status": "New",
            }
        )


# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.markdown(
    """
    <div class="sidebar-brand">
        <div class="sidebar-title">🛡️ Fraud Operations</div>
        <div class="sidebar-sub">Client Protection Investigation Console</div>
        <div class="sidebar-tag">SYNTHETIC DATA • LOCAL DEMO</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown("### Workspace")

page = st.sidebar.radio(
    "Navigate",
    [
        "Dashboard",
        "Alert Queue",
        "Customer Claims",
        "Investigation",
        "Case Search",
        "Resolved Cases",
        "About Project",
    ],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")

st.sidebar.toggle(
    "Dark mode",
    key="dark_mode",
    help="Switch between light and dark analyst-console themes.",
)

st.sidebar.caption("Theme applies instantly • Analyst workspace v1.1")


# ============================================================
# DASHBOARD
# ============================================================
if page == "Dashboard":
    cases = pd.DataFrame(all_cases())

    fraud_count = int(
        (cases["decision"] == "Fraud Confirmed").sum()
    ) if not cases.empty and "decision" in cases else 0

    genuine_count = int(
        (cases["decision"] == "Genuine / No Fraud").sum()
    ) if not cases.empty and "decision" in cases else 0

    escalated = int(
        (cases["decision"] == "Escalate").sum()
    ) if not cases.empty and "decision" in cases else 0

    resolved = int(
        (cases["alert_status"] == "Resolved").sum()
    ) if not cases.empty else 0

    high_count = int(
        (cases["risk_level"] == "HIGH").sum()
    ) if not cases.empty else 0

    open_count = (
        int((cases["alert_status"] == "New").sum())
        if not cases.empty and "alert_status" in cases
        else 0
    )

    recovery = safe_number(cases["recovery_amount"]) if not cases.empty and "recovery_amount" in cases else 0.0
    total_value = safe_number(tx_df["amount"])
    reviewed = fraud_count + genuine_count + escalated
    review_rate = reviewed / len(cases) * 100 if len(cases) else 0
    claim_rate = len(claims_df) / len(cases) * 100 if len(cases) else 0

    page_header(
        "CLIENT PROTECTION • FRAUD OPERATIONS",
        "Banking Fraud Investigation Console",
        "Transaction monitoring, customer claim review and structured case decisioning in one analyst workspace.",
    )

    st.markdown('<div class="kpi-grid">', unsafe_allow_html=True)
    render_kpi("Total Alerts", len(cases), "Cases in current queue")
    render_kpi("High Risk", high_count, "Priority review")
    render_kpi("Customer Claims", len(claims_df), f"{claim_rate:.1f}% of alerts")
    render_kpi("Resolved", resolved, f"{review_rate:.1f}% decisioned")
    render_kpi("Open Cases", open_count, "Awaiting analyst action")
    st.markdown('</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2, gap="large")

    with c1:
        section_head("Risk distribution", "Queue health")
        if not cases.empty:
            risk_counts = (
                cases["risk_level"]
                .value_counts()
                .reindex(["HIGH", "MEDIUM", "LOW"])
                .fillna(0)
            )
            st.bar_chart(risk_counts, height=245)
        else:
            st.info("No case data available.")

    with c2:
        section_head("Decision status", "Analyst outcomes")
        if not cases.empty and "decision" in cases:
            decision_counts = (
                cases["decision"]
                .fillna("Pending")
                .replace("", "Pending")
                .value_counts()
            )
            st.bar_chart(decision_counts, height=245)
        else:
            st.info("No decisions recorded yet.")

    c3, c4 = st.columns(2, gap="large")

    with c3:
        section_head("Transaction channels", "Activity mix")
        st.bar_chart(tx_df["channel"].value_counts(), height=220)

    with c4:
        section_head("Operational snapshot", "Portfolio indicators")
        x1, x2 = st.columns(2)
        with x1:
            st.markdown(
                f'<div class="soft-panel"><div class="kpi-label">Value Reviewed</div><div class="kpi-value" style="font-size:22px">₹{total_value:,.0f}</div></div>',
                unsafe_allow_html=True,
            )
        with x2:
            st.markdown(
                f'<div class="soft-panel"><div class="kpi-label">Potential Recovery</div><div class="kpi-value" style="font-size:22px">₹{recovery:,.0f}</div></div>',
                unsafe_allow_html=True,
            )
        st.write("")
        st.markdown(
            f'<div class="soft-panel"><div class="kpi-label">Claim Rate</div><div class="kpi-value" style="font-size:22px">{claim_rate:.1f}%</div><div class="kpi-note">Customer-reported cases across current queue</div></div>',
            unsafe_allow_html=True,
        )

    section_head("Priority review queue", "Highest-risk cases first")
    priority_banner(
        "Analyst attention queue",
        "Use Investigation to validate evidence, complete the SOP checklist and record a decision.",
        f"{high_count} HIGH RISK",
    )

    if not cases.empty:
        tx_display = tx_df.drop(columns=["customer_id"], errors="ignore")
        queue = cases.merge(tx_display, on="transaction_id", how="left")
        queue = queue.sort_values(
            ["risk_score", "amount"],
            ascending=[False, False],
        ).head(8)
        cols = [
            c for c in [
                "case_id",
                "transaction_id",
                "customer_id",
                "amount",
                "channel",
                "risk_score",
                "risk_level",
                "alert_status",
            ]
            if c in queue.columns
        ]
        st.dataframe(
            queue[cols],
            width="stretch",
            hide_index=True,
            height=300,
        )
    else:
        st.info("No cases available.")

    st.markdown(
        '<div class="footer-note">Educational simulation • Synthetic transaction/customer data • No connection to real banking or card-network infrastructure</div>',
        unsafe_allow_html=True,
    )


# ============================================================
# ALERT QUEUE
# ============================================================
elif page == "Alert Queue":
    page_header(
        "CASE MANAGEMENT",
        "Alert Queue",
        "Prioritize suspicious activity using risk, status, transaction channel and card type filters.",
    )

    cases = pd.DataFrame(all_cases())

    if cases.empty:
        st.info("No cases available in the alert queue.")
    else:
        tx_display = tx_df.drop(columns=["customer_id"], errors="ignore")
        merged = cases.merge(tx_display, on="transaction_id", how="left")

        col1, col2, col3, col4 = st.columns(4)
        risk = col1.selectbox("Risk", ["All", "HIGH", "MEDIUM", "LOW"])
        status = col2.selectbox("Status", ["All", "New", "Resolved", "Escalated"])
        channel = col3.selectbox("Channel", ["All", "Online", "POS", "ATM"])
        card = col4.selectbox("Card", ["All", "Debit", "Credit"])

        df = merged.copy()
        if risk != "All":
            df = df[df["risk_level"] == risk]
        if status != "All":
            df = df[df["alert_status"] == status]
        if channel != "All":
            df = df[df["channel"] == channel]
        if card != "All":
            df = df[df["card_type"] == card]

        display_cols = [
            "case_id",
            "transaction_id",
            "customer_id",
            "amount",
            "channel",
            "location",
            "risk_score",
            "risk_level",
            "alert_status",
        ]
        display = df[display_cols].sort_values(
            "risk_score",
            ascending=False,
        )

        priority_banner(
            "Filtered case queue",
            f"{len(display)} case(s) match the current filters.",
            "ANALYST REVIEW",
        )

        st.dataframe(
            display,
            width="stretch",
            hide_index=True,
            height=520,
        )

        st.info("Open Investigation to perform a structured case review and record the final decision.")


# ============================================================
# CUSTOMER CLAIMS
# ============================================================
elif page == "Customer Claims":
    page_header(
        "CLAIMS OPERATIONS",
        "Customer Claims",
        "Review customer-reported disputes and compare the claim with linked transaction risk indicators.",
    )

    if claims_df.empty:
        st.info("No customer claims available.")
    else:
        st.dataframe(
            claims_df,
            width="stretch",
            hide_index=True,
            height=290,
        )

        claim_id = st.selectbox(
            "Select Claim",
            claims_df["claim_id"].tolist(),
        )

        claim = (
            claims_df[claims_df["claim_id"] == claim_id]
            .iloc[0]
            .to_dict()
        )
        tx = tx_by_id(claim["transaction_id"])
        score_match = scores_df[
            scores_df["transaction_id"] == claim["transaction_id"]
        ]

        section_head("Claim details", "Customer-reported information")

        a, b, c = st.columns(3)
        with a:
            st.markdown(
                f'<div class="soft-panel"><div class="kpi-label">Customer</div><div class="kpi-value" style="font-size:20px">{html.escape(str(claim["customer_id"]))}</div></div>',
                unsafe_allow_html=True,
            )
        with b:
            amount = f"₹{tx['amount']:,.2f}" if tx else "N/A"
            st.markdown(
                f'<div class="soft-panel"><div class="kpi-label">Claim Transaction</div><div class="kpi-value" style="font-size:20px">{html.escape(str(claim["transaction_id"]))}</div><div class="kpi-note">{amount}</div></div>',
                unsafe_allow_html=True,
            )
        with c:
            risk_text = "Unavailable"
            if not score_match.empty:
                score = score_match.iloc[0]
                risk_text = f"{score['level']} • {int(score['score'])}/100"
            st.markdown(
                f'<div class="soft-panel"><div class="kpi-label">Current Risk</div><div class="kpi-value" style="font-size:20px">{html.escape(risk_text)}</div></div>',
                unsafe_allow_html=True,
            )

        st.markdown(
            f'<div class="soft-panel" style="margin-top:12px"><div class="kpi-label">Claim Type</div><div style="font-size:14px;font-weight:760;color:var(--ink);margin-top:5px">{html.escape(str(claim["claim_type"]))}</div><div class="kpi-label" style="margin-top:12px">Customer Statement</div><div style="font-size:13px;color:var(--muted);margin-top:5px;line-height:1.6">{html.escape(str(claim["customer_statement"]))}</div></div>',
            unsafe_allow_html=True,
        )


# ============================================================
# INVESTIGATION
# ============================================================
elif page == "Investigation":
    page_header(
        "ANALYST WORKSPACE",
        "Case Investigation",
        "Review the transaction, customer history, suspicious indicators and claim evidence before decisioning.",
    )

    cases = all_cases()

    if not cases:
        st.info("No cases available for investigation.")
    else:
        selected = st.selectbox(
            "Select Case",
            [c["case_id"] for c in cases],
        )
        case = get_case(selected)

        if not case:
            st.error("Selected case could not be loaded.")
            st.stop()

        tx = tx_by_id(case["transaction_id"])
        if not tx:
            st.error("Transaction linked to this case could not be found.")
            st.stop()

        claim = claim_for_tx(case["transaction_id"]) or {}
        history = history_for_customer(
            tx["customer_id"],
            exclude=tx["transaction_id"],
        )
        score_match = scores_df[
            scores_df["transaction_id"] == tx["transaction_id"]
        ]

        if score_match.empty:
            st.error("Fraud score could not be calculated for this transaction.")
            st.stop()

        score = score_match.iloc[0]
        reasons = score["reasons"]

        priority_banner(
            f"{case['case_id']} • {tx['transaction_id']}",
            "Complete the review workflow before final resolution.",
            f"{case['risk_level']} RISK",
        )

        a, b, c, d, e = st.columns(5)
        a.metric("Case", case["case_id"])
        b.metric("Amount", f"₹{tx['amount']:,.2f}")
        c.metric("Risk", case["risk_level"])
        d.metric("Score", case["risk_score"])
        e.metric("Status", case["alert_status"])

        tab1, tab2, tab3 = st.tabs(
            [
                "Transaction & Claim",
                "Investigation Checklist",
                "Decision & Resolution",
            ]
        )

        with tab1:
            left, right = st.columns(2, gap="large")

            with left:
                section_head("Transaction details", "Primary case evidence")
                st.json(
                    {
                        "transaction_id": tx["transaction_id"],
                        "customer_id": tx["customer_id"],
                        "card_type": tx["card_type"],
                        "amount": tx["amount"],
                        "merchant": tx["merchant_name"],
                        "category": tx["merchant_category"],
                        "timestamp": tx["timestamp"],
                        "location": tx["location"],
                        "channel": tx["channel"],
                        "domestic_international": tx["domestic_international"],
                    }
                )

            with right:
                section_head("Suspicious indicators", "Rule explanations")
                if reasons:
                    for reason in reasons:
                        st.markdown(
                            f'<div class="soft-panel" style="margin-bottom:7px;padding:10px 12px"><span style="color:var(--blue);font-weight:800">✓</span> <span style="color:var(--ink)">{html.escape(str(reason))}</span></div>',
                            unsafe_allow_html=True,
                        )
                else:
                    st.info("No specific rule indicator triggered.")

            section_head("Customer claim", "Customer-reported context")
            if claim:
                st.markdown(
                    f'<div class="soft-panel"><div class="kpi-label">Claim ID</div><div style="font-weight:780;color:var(--ink);margin-top:4px">{html.escape(str(claim["claim_id"]))}</div><div class="kpi-label" style="margin-top:10px">Type</div><div style="color:var(--ink);margin-top:4px">{html.escape(str(claim["claim_type"]))}</div><div class="kpi-label" style="margin-top:10px">Statement</div><div style="color:var(--muted);margin-top:4px;line-height:1.6">{html.escape(str(claim["customer_statement"]))}</div></div>',
                    unsafe_allow_html=True,
                )
            else:
                st.info("No customer claim linked to this transaction.")

            section_head("Customer history", "Previous transactions")
            hist = pd.DataFrame(history)
            if not hist.empty:
                history_cols = [
                    "transaction_id",
                    "amount",
                    "merchant_name",
                    "timestamp",
                    "location",
                    "channel",
                    "transaction_status",
                ]
                available = [c for c in history_cols if c in hist.columns]
                st.dataframe(
                    hist[available],
                    width="stretch",
                    hide_index=True,
                    height=280,
                )
            else:
                st.info("No previous transactions found for this customer.")

        with tab2:
            existing = get_checklist(case["case_id"])
            check_values = {}

            priority_banner(
                "Structured SOP review",
                "Mark every applicable investigation step before submitting the final decision.",
                "REQUIRED",
            )

            c1, c2 = st.columns(2, gap="large")
            for idx, (key, label) in enumerate(SOP_STEPS):
                column = c1 if idx % 2 == 0 else c2
                check_values[key] = column.checkbox(
                    label,
                    value=bool(existing.get(key, 0)),
                    key=f"{case['case_id']}_{key}",
                )

            if st.button("Save Checklist"):
                save_checklist(case["case_id"], check_values)
                st.success("Checklist saved successfully.")

        with tab3:
            section_head("Analyst decision", "Evidence-based case resolution")

            decision = st.radio(
                "Analyst Decision",
                [
                    "Fraud Confirmed",
                    "Genuine / No Fraud",
                    "Escalate",
                ],
                horizontal=True,
            )

            notes = st.text_area(
                "Analyst Notes",
                placeholder="Explain the decision using case evidence.",
                height=110,
            )

            evidence = st.text_area(
                "Evidence Summary",
                placeholder="Summarize transaction, history, indicators and customer claim.",
                height=110,
            )

            recommended = st.text_area(
                "Recommended Action",
                placeholder="Protect customer, deny claim or escalate.",
                height=90,
            )

            section_head("Recovery review", "Potential loss recovery")
            r1, r2 = st.columns(2)
            with r1:
                recovery = st.selectbox(
                    "Recovery Opportunity",
                    ["Yes", "No", "Review"],
                )
            with r2:
                recovery_amount = st.number_input(
                    "Potential Recovery Amount (₹)",
                    min_value=0.0,
                    step=100.0,
                )

            recovery_reason = st.text_input(
                "Recovery Reason",
                placeholder="Why is recovery considered possible?",
            )

            section_head("Chargeback simulation", "Educational workflow only")
            cb_elig, cb_reason = evaluate_chargeback(decision)
            st.markdown(
                f'<div class="soft-panel"><div class="kpi-label">Simulated Eligibility</div><div style="font-size:16px;font-weight:800;color:var(--ink);margin-top:5px">{html.escape(str(cb_elig))}</div><div style="font-size:11px;color:var(--muted);margin-top:5px">{html.escape(str(cb_reason))}</div></div>',
                unsafe_allow_html=True,
            )

            cb_status = st.selectbox(
                "Simulated Chargeback Status",
                [
                    "Not Initiated",
                    "Simulated Submitted",
                    "Merchant Response Simulated",
                    "Resolved",
                ],
            )

            resolution = resolution_for(decision)

            if st.button(
                "Save Final Decision",
                type="primary",
            ):
                checks = dict(check_values)
                checks["decision_documented"] = True

                if not all(checks.values()):
                    st.error(
                        "Complete every checklist item before final resolution."
                    )
                elif not notes.strip() or not evidence.strip():
                    st.error(
                        "Analyst Notes and Evidence Summary are required."
                    )
                else:
                    save_checklist(case["case_id"], checks)
                    save_decision(
                        case["case_id"],
                        decision,
                        notes,
                        evidence,
                        recommended,
                        recovery,
                        recovery_amount,
                        recovery_reason,
                        cb_elig,
                        cb_status,
                        resolution,
                    )
                    st.success("Case decision saved successfully.")

            final_case = get_case(case["case_id"])
            final_checks = get_checklist(case["case_id"])

            if final_case and final_case.get("decision"):
                report = create_html_report(
                    final_case,
                    tx,
                    claim,
                    history,
                    reasons,
                    final_checks,
                )
                st.download_button(
                    "⬇️ Download Case Report",
                    report,
                    file_name=f"{case['case_id']}_report.html",
                    mime="text/html",
                )


# ============================================================
# CASE SEARCH
# ============================================================
elif page == "Case Search":
    page_header(
        "CASE MANAGEMENT",
        "Case Search",
        "Find cases by case ID, transaction ID, customer ID or claim ID.",
    )

    query = st.text_input(
        "Search Case ID, Transaction ID, Customer ID or Claim ID",
        placeholder="e.g. CASE-1021 or CUST-1004",
    )

    if query.strip():
        matches = []
        for case in all_cases():
            claim = claim_for_tx(case["transaction_id"])
            hay = " ".join(
                [
                    str(case.get("case_id", "")),
                    str(case.get("transaction_id", "")),
                    str(case.get("customer_id", "")),
                    str(claim.get("claim_id", "") if claim else ""),
                ]
            ).lower()
            if query.lower() in hay:
                matches.append(case)

        if matches:
            priority_banner(
                "Search results",
                f"{len(matches)} case(s) matched your query.",
                "FOUND",
            )
            st.dataframe(
                pd.DataFrame(matches),
                width="stretch",
                hide_index=True,
                height=430,
            )
        else:
            st.warning("No matching case found.")


# ============================================================
# RESOLVED CASES
# ============================================================
elif page == "Resolved Cases":
    page_header(
        "CASE OUTCOMES",
        "Resolved & Escalated Cases",
        "Review completed analyst decisions and escalated investigations.",
    )

    cases = pd.DataFrame(all_cases())
    if cases.empty:
        st.info("No cases available.")
    else:
        resolved_cases = cases[
            cases["alert_status"].isin(["Resolved", "Escalated"])
        ]
        if resolved_cases.empty:
            st.info("No resolved or escalated cases yet.")
        else:
            priority_banner(
                "Completed case outcomes",
                f"{len(resolved_cases)} case(s) have reached an outcome state.",
                "HISTORY",
            )
            st.dataframe(
                resolved_cases,
                width="stretch",
                hide_index=True,
                height=500,
            )


# ============================================================
# ABOUT
# ============================================================
else:
    page_header(
        "PROJECT OVERVIEW",
        "About This Project",
        "A portfolio simulation demonstrating fraud operations and client-protection workflows using synthetic banking data.",
    )

    c1, c2 = st.columns(2, gap="large")
    with c1:
        section_head("What this demonstrates", "Core analyst workflow")
        st.markdown(
            """
            <div class="soft-panel">
            <div style="color:var(--ink);line-height:1.9;font-size:13px">
            • Transaction monitoring<br>
            • Suspicious activity analysis<br>
            • Customer claim review<br>
            • Evidence validation<br>
            • SOP-driven investigation<br>
            • Fraud / genuine / escalation decisioning<br>
            • Recovery opportunity review<br>
            • Simplified chargeback workflow<br>
            • Case documentation<br>
            • KPI reporting
            </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        section_head("Project boundaries", "Keep the demo truthful")
        st.markdown(
            """
            <div class="soft-panel">
            <div style="color:var(--ink);line-height:1.8;font-size:12px">
            This is an <b>educational simulation using synthetic data</b>.<br><br>
            It does not connect to Bank of America, Visa, Mastercard, real banking systems, real customer data, or real chargeback infrastructure.<br><br>
            Fraud rules and the chargeback workflow are demonstration logic only.
            </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


st.markdown(
    '<div class="footer-note">Fraud Operations Console • Portfolio demonstration</div>',
    unsafe_allow_html=True,
)

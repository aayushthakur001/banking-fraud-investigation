from __future__ import annotations
from pathlib import Path
import pandas as pd
import streamlit as st

from fraud_rules import score_transaction, rapid_transaction_signal, enrich_score
from database import init_db, upsert_case, get_case, save_checklist, save_decision, all_cases, get_checklist
from investigation import build_case_id, SOP_STEPS, evaluate_chargeback, resolution_for
from report_generator import create_html_report

st.set_page_config(page_title="Banking Fraud Investigation Simulator", page_icon="🛡️", layout="wide")
init_db()
DATA_DIR = Path(__file__).resolve().parent / "data"

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

# Create one case per synthetic transaction
for _, row in scores_df.iterrows():
    tx = tx_by_id(row["transaction_id"])
    claim = claim_for_tx(row["transaction_id"])
    case_id = build_case_id(row["transaction_id"])
    if not get_case(case_id):
        upsert_case({
            "case_id": case_id,
            "transaction_id": row["transaction_id"],
            "customer_id": tx["customer_id"],
            "claim_id": claim["claim_id"] if claim else None,
            "risk_score": int(row["score"]),
            "risk_level": row["level"],
            "alert_status": "New"
        })

st.sidebar.title("🛡️ Fraud Case Console")
st.sidebar.caption("Synthetic portfolio simulation")
page = st.sidebar.radio("Navigate", [
    "Dashboard", "Alert Queue", "Customer Claims", "Investigation",
    "Case Search", "Resolved Cases", "About Project"
])

if page == "Dashboard":
    st.title("Banking Fraud & Customer Claim Investigation Simulator")
    st.caption("Educational simulation using synthetic data; not a real bank/payment-network system.")
    cases = pd.DataFrame(all_cases())
    fraud_count = int((cases["decision"] == "Fraud Confirmed").sum()) if not cases.empty else 0
    genuine_count = int((cases["decision"] == "Genuine / No Fraud").sum()) if not cases.empty else 0
    escalated = int((cases["decision"] == "Escalate").sum()) if not cases.empty else 0
    resolved = int((cases["alert_status"] == "Resolved").sum()) if not cases.empty else 0
    open_cases = len(cases) - resolved - escalated if not cases.empty else 0
    recovery = float(cases["recovery_amount"].fillna(0).sum()) if not cases.empty else 0
    cols = st.columns(6)
    metrics = [
        ("Total Alerts", len(cases)),
        ("Customer Claims", len(claims_df)),
        ("Fraud Confirmed", fraud_count),
        ("Genuine", genuine_count),
        ("Escalated", escalated),
        ("Open Cases", max(open_cases, 0))
    ]
    for col, (label, value) in zip(cols, metrics):
        col.metric(label, value)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Cases by Decision")
        st.bar_chart(cases["decision"].fillna("Pending").value_counts())
    with c2:
        st.subheader("Cases by Risk Level")
        st.bar_chart(cases["risk_level"].value_counts())
    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Transactions by Channel")
        st.bar_chart(tx_df["channel"].value_counts())
    with c4:
        st.subheader("Operational Snapshot")
        st.write(f"**Transaction value reviewed:** ₹{tx_df['amount'].sum():,.2f}")
        st.write(f"**Potential recovery recorded:** ₹{recovery:,.2f}")

elif page == "Alert Queue":
    st.title("🚨 Fraud Alert Queue")
    cases = pd.DataFrame(all_cases())
    merged = cases.merge(tx_df, on="transaction_id", how="left")
    col1, col2, col3, col4 = st.columns(4)
    risk = col1.selectbox("Risk", ["All","HIGH","MEDIUM","LOW"])
    status = col2.selectbox("Status", ["All","New","Resolved","Escalated"])
    channel = col3.selectbox("Channel", ["All","Online","POS","ATM"])
    card = col4.selectbox("Card", ["All","Debit","Credit"])
    df = merged.copy()
    if risk != "All": df = df[df["risk_level"] == risk]
    if status != "All": df = df[df["alert_status"] == status]
    if channel != "All": df = df[df["channel"] == channel]
    if card != "All": df = df[df["card_type"] == card]
    display = df[[
        "case_id","transaction_id","customer_id","amount","channel","location",
        "risk_score","risk_level","alert_status"
    ]].sort_values("risk_score", ascending=False)
    st.dataframe(display, use_container_width=True, hide_index=True)
    st.info("Open the Investigation page to perform a structured case review.")

elif page == "Customer Claims":
    st.title("📄 Customer Claims")
    st.dataframe(claims_df, use_container_width=True, hide_index=True)
    claim_id = st.selectbox("Select Claim", claims_df["claim_id"].tolist())
    claim = claims_df[claims_df["claim_id"] == claim_id].iloc[0].to_dict()
    tx = tx_by_id(claim["transaction_id"])
    score = scores_df[scores_df["transaction_id"] == claim["transaction_id"]].iloc[0]
    st.subheader("Claim Details")
    st.write(f"**Customer:** {claim['customer_id']}")
    st.write(f"**Transaction:** {claim['transaction_id']} — ₹{tx['amount']:,.2f}")
    st.write(f"**Claim Type:** {claim['claim_type']}")
    st.write(f"**Statement:** {claim['customer_statement']}")
    st.write(f"**Current Risk:** {score['level']} ({int(score['score'])}/100)")

elif page == "Investigation":
    st.title("🔎 Analyst Investigation")
    cases = all_cases()
    selected = st.selectbox("Select Case", [c["case_id"] for c in cases])
    case = get_case(selected)
    tx = tx_by_id(case["transaction_id"])
    claim = claim_for_tx(case["transaction_id"]) or {}
    history = history_for_customer(tx["customer_id"], exclude=tx["transaction_id"])
    score = scores_df[scores_df["transaction_id"] == tx["transaction_id"]].iloc[0]
    reasons = score["reasons"]

    a,b,c,d,e = st.columns(5)
    a.metric("Case", case["case_id"])
    b.metric("Amount", f"₹{tx['amount']:,.2f}")
    c.metric("Risk", case["risk_level"])
    d.metric("Score", case["risk_score"])
    e.metric("Status", case["alert_status"])

    left, right = st.columns(2)
    with left:
        st.subheader("Transaction Details")
        st.json({
            "transaction_id": tx["transaction_id"],
            "customer_id": tx["customer_id"],
            "card_type": tx["card_type"],
            "amount": tx["amount"],
            "merchant": tx["merchant_name"],
            "category": tx["merchant_category"],
            "timestamp": tx["timestamp"],
            "location": tx["location"],
            "channel": tx["channel"],
            "domestic_international": tx["domestic_international"]
        })
    with right:
        st.subheader("Suspicious Indicators")
        if reasons:
            for reason in reasons:
                st.write("✓ " + reason)
        else:
            st.write("No specific rule indicator triggered.")

    st.subheader("Customer Claim")
    if claim:
        st.write(f"**Claim ID:** {claim['claim_id']}")
        st.write(f"**Type:** {claim['claim_type']}")
        st.write(f"**Statement:** {claim['customer_statement']}")
    else:
        st.write("No customer claim linked to this transaction.")

    st.subheader("Customer History")
    hist = pd.DataFrame(history)
    if not hist.empty:
        st.dataframe(
            hist[["transaction_id","amount","merchant_name","timestamp","location","channel","transaction_status"]],
            use_container_width=True, hide_index=True
        )

    st.subheader("Investigation SOP Checklist")
    existing = get_checklist(case["case_id"])
    check_values = {}
    c1, c2 = st.columns(2)
    for idx, (key, label) in enumerate(SOP_STEPS):
        check_values[key] = (c1 if idx % 2 == 0 else c2).checkbox(
            label, value=bool(existing.get(key, 0)), key=f"{case['case_id']}_{key}"
        )
    if st.button("Save Checklist"):
        save_checklist(case["case_id"], check_values)
        st.success("Checklist saved.")

    st.subheader("Decision & Resolution")
    decision = st.radio("Analyst Decision", [
        "Fraud Confirmed", "Genuine / No Fraud", "Escalate"
    ], horizontal=True)
    notes = st.text_area("Analyst Notes", placeholder="Explain the decision using case evidence.")
    evidence = st.text_area("Evidence Summary", placeholder="Summarize transaction, history, indicators and claim.")
    recommended = st.text_area("Recommended Action", placeholder="Protect customer, deny claim or escalate.")
    recovery = st.selectbox("Recovery Opportunity", ["Yes","No","Review"])
    recovery_amount = st.number_input("Potential Recovery Amount (₹)", min_value=0.0, step=100.0)
    recovery_reason = st.text_input("Recovery Reason")
    cb_elig, cb_reason = evaluate_chargeback(decision)
    st.write(f"**Simulated chargeback eligibility:** {cb_elig}")
    st.caption(cb_reason)
    cb_status = st.selectbox("Simulated Chargeback Status", [
        "Not Initiated","Simulated Submitted","Merchant Response Simulated","Resolved"
    ])
    resolution = resolution_for(decision)

    if st.button("Save Final Decision", type="primary"):
        checks = dict(check_values)
        checks["decision_documented"] = True
        if not all(checks.values()):
            st.error("Complete every checklist item before final resolution.")
        elif not notes.strip() or not evidence.strip():
            st.error("Analyst Notes and Evidence Summary are required.")
        else:
            save_checklist(case["case_id"], checks)
            save_decision(
                case["case_id"], decision, notes, evidence, recommended,
                recovery, recovery_amount, recovery_reason,
                cb_elig, cb_status, resolution
            )
            st.success("Case decision saved successfully.")

    final_case = get_case(case["case_id"])
    final_checks = get_checklist(case["case_id"])
    if final_case and final_case.get("decision"):
        report = create_html_report(final_case, tx, claim, history, reasons, final_checks)
        st.download_button(
            "⬇️ Download Case Report",
            report,
            file_name=f"{case['case_id']}_report.html",
            mime="text/html"
        )

elif page == "Case Search":
    st.title("🔍 Case Search")
    query = st.text_input("Search Case ID, Transaction ID, Customer ID or Claim ID")
    if query.strip():
        matches = []
        for case in all_cases():
            claim = claim_for_tx(case["transaction_id"])
            hay = " ".join([
                str(case.get("case_id","")),
                str(case.get("transaction_id","")),
                str(case.get("customer_id","")),
                str(claim.get("claim_id","") if claim else "")
            ]).lower()
            if query.lower() in hay:
                matches.append(case)
        if matches:
            st.dataframe(pd.DataFrame(matches), use_container_width=True, hide_index=True)
        else:
            st.warning("No matching case found.")

elif page == "Resolved Cases":
    st.title("✅ Resolved / Escalated Cases")
    cases = pd.DataFrame(all_cases())
    if cases.empty:
        st.info("No cases.")
    else:
        st.dataframe(cases[cases["alert_status"].isin(["Resolved","Escalated"])], use_container_width=True, hide_index=True)

else:
    st.title("ℹ️ About This Project")
    st.markdown("""
### What this demonstrates
- Transaction monitoring
- Suspicious activity analysis
- Customer claim review
- Evidence validation
- SOP-driven investigation
- Fraud / genuine / escalation decisioning
- Recovery opportunity review
- Simplified chargeback workflow
- Case documentation
- KPI reporting

### Important limitation
This is an **educational simulation using synthetic data**. It does not connect to Bank of America, Visa, Mastercard, real banking systems, real customer data, or real chargeback infrastructure. The fraud rules and workflow are demonstration logic only.
""")

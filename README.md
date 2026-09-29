# Banking Fraud & Customer Claim Investigation Simulator

A lightweight portfolio project that simulates a banking fraud / client protection analyst workflow using synthetic transaction data.

## Objective

Demonstrate practical understanding of:
- Fraud detection
- Suspicious activity analysis
- Transaction review
- Customer claims
- Evidence validation
- SOP/checklist-driven investigation
- Case decisioning
- Recovery opportunity review
- Simplified chargeback concepts
- Case documentation
- KPI reporting

## Workflow

Transaction Data → Fraud Rules → Alert Queue → Customer Claim → Investigation → Decision → Simulated Chargeback → Resolution → KPI Dashboard

## Technology

Python, Pandas, SQLite, Streamlit, CSV.

## Features

### Fraud Alert Queue
Filter cases by risk, status, channel and card type.

### Customer Claims
Review synthetic unauthorized transaction, ATM, duplicate and dispute claims.

### Investigation Workspace
Review transaction details, customer history, suspicious indicators and a structured checklist.

### Decisioning
Choose:
- Fraud Confirmed
- Genuine / No Fraud
- Escalate

Analyst notes and evidence summary are required before final resolution.

### Recovery Opportunity
Record a simulated potential recovery amount.

### Chargeback Simulation
Demonstrates a simplified educational workflow. It is not a real Visa/Mastercard processor or rule engine.

### KPI Dashboard
Tracks alerts, claims, decisions, escalations, resolved cases and recovery.

### Case Reports
Generate downloadable HTML case reports.

## Installation

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

## Demo Flow

1. Open Alert Queue.
2. Select a HIGH-risk case.
3. Open Investigation.
4. Review transaction + customer history + indicators.
5. Complete every SOP checklist item.
6. Add analyst notes and evidence.
7. Select Fraud Confirmed / Genuine / Escalate.
8. Review simulated recovery and chargeback eligibility.
9. Save final decision.
10. Download case report.

## Fraud Rules

The project uses explainable demonstration rules:
- High transaction amount
- International transaction
- New location
- New merchant
- Higher-risk merchant category
- Rapid repeated transaction
- ATM activity

Risk:
- 0–29 Low
- 30–59 Medium
- 60–100 High

These are portfolio rules only, not real bank rules.

## Limitations

This application is not:
- A real banking system
- A production fraud engine
- A real Visa/Mastercard integration
- A real chargeback processor
- A Bank of America internal process

All customer and transaction data is synthetic.

## Future Enhancements

- Advanced anomaly detection
- Machine-learning risk scoring
- Real-time transaction ingestion
- Rule management interface
- Audit logging
- Role-based access control
- Email notifications
- Enterprise fraud-system integrations

## Interview Explanation

**Problem:** Fraud operations need a repeatable way to review suspicious transactions and customer claims.

**Solution:** I built a lightweight simulator that scores synthetic transactions, creates a review queue, supports customer-claim investigation, captures evidence-based decisions, and records simulated recovery/chargeback outcomes.

**Why rule-based instead of ML?** The project is focused on explainable analyst decisioning rather than model performance.

**Why Streamlit?** It provides a simple local interface without building a heavy frontend/backend application.

**Why SQLite?** It provides lightweight local persistence without a separate database server.

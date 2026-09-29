# Banking Fraud & Customer Claim Investigation Simulator

A lightweight **Fraud Operations / Client Protection** portfolio application that simulates how an analyst can review suspicious banking transactions, investigate customer claims, make evidence-based decisions, assess recovery opportunities, and document case outcomes.

The project uses **synthetic transaction, customer, and claim data** and is designed for learning, portfolio demonstration, and interview discussion. It is **not a real banking, Visa, Mastercard, chargeback, or Bank of America system**.

---

## Project Overview

The simulator models a simple analyst workflow:

```text
Synthetic Transactions
        ↓
Rule-Based Fraud Scoring
        ↓
Fraud Alert Queue
        ↓
Customer Claim Review
        ↓
Investigation
        ↓
Evidence & SOP Checklist
        ↓
Analyst Decision
        ↓
Recovery Assessment
        ↓
Simulated Chargeback
        ↓
Case Resolution
        ↓
Case Report / KPI View
```

The main objective is to demonstrate practical understanding of:

- Fraud detection and suspicious activity review
- Transaction analysis
- Customer claim investigation
- Evidence validation
- SOP/checklist-driven case handling
- Fraud / genuine / escalation decisioning
- Recovery opportunity identification
- Simplified chargeback concepts
- Case documentation
- Operational KPI reporting

---

## Key Features

### 1. Fraud Alert Queue

The Alert Queue provides a centralized view of synthetic fraud cases.

Analysts can filter cases by:

- Risk level
- Alert status
- Transaction channel
- Card type

Cases are sorted by risk score so that higher-risk transactions can be reviewed first.

---

### 2. Rule-Based Fraud Risk Scoring

The project uses explainable demonstration rules rather than a black-box machine-learning model.

Example indicators include:

- High transaction amount
- International transaction
- New location
- New merchant
- Higher-risk merchant category
- Rapid repeated transaction activity
- ATM activity

Risk bands:

```text
0–29   → LOW
30–59  → MEDIUM
60–100 → HIGH
```

These thresholds and rules are **portfolio/demo logic only**. They do not represent real bank fraud models or production decision rules.

---

### 3. Customer Claims

The application includes synthetic customer claims covering scenarios such as:

- Unauthorized transaction
- Card transaction dispute
- ATM cash withdrawal dispute
- Duplicate transaction
- Other customer-reported issues

Each claim can be linked to the related transaction and reviewed alongside the calculated fraud risk.

---

### 4. Investigation Workspace

The Investigation page is the core analyst workflow.

For a selected case, the analyst can review:

**Transaction details**
- Customer
- Card type
- Amount
- Merchant
- Merchant category
- Timestamp
- Location
- Channel
- Domestic / international status

**Suspicious indicators**
- Triggered fraud-rule reasons

**Customer claim**
- Claim ID
- Claim type
- Customer statement

**Customer history**
- Previous transactions for the same customer

---

### 5. SOP Investigation Checklist

The analyst is required to complete the investigation checklist before final resolution.

The checklist is designed around a repeatable review process:

- Transaction details reviewed
- Customer history reviewed
- Suspicious indicators reviewed
- Customer claim reviewed
- Evidence validated
- Recovery opportunity checked
- Decision documented

This demonstrates a **procedure-driven and auditable investigation workflow**.

---

### 6. Analyst Decisioning

The analyst can choose one of three outcomes:

```text
Fraud Confirmed
Genuine / No Fraud
Escalate
```

Before the decision can be saved, the application requires:

- Completed investigation checklist
- Analyst notes
- Evidence summary

The analyst can also record a recommended action.

This is intended to demonstrate structured case decisioning rather than simply displaying a fraud score.

---

### 7. Recovery Opportunity Review

For each investigated case, the analyst can record:

- Recovery opportunity: Yes / No / Review
- Potential recovery amount
- Recovery reason

This models the idea of looking for recovery opportunities during fraud/claims investigation.

---

### 8. Simulated Chargeback Workflow

The application contains a simplified educational chargeback flow.

Based on the analyst decision, the simulator displays chargeback eligibility and allows a simulated status to be recorded:

```text
Not Initiated
        ↓
Simulated Submitted
        ↓
Merchant Response Simulated
        ↓
Resolved
```

### Important

This is **not** a Visa/Mastercard processor and does not connect to payment networks.

It does not implement real:

- Visa dispute processing
- Mastercard dispute processing
- Network APIs
- Merchant representment
- Real reason-code engines
- Real chargeback settlement

The workflow exists only to demonstrate the analyst concept from investigation through resolution.

---

### 9. KPI / Operational Dashboard

The dashboard provides a high-level operational view including:

- Total alerts
- Customer claims
- Fraud confirmed
- Genuine decisions
- Escalated cases
- Open cases
- Transaction value reviewed
- Potential recovery recorded

The dashboard also visualizes:

- Cases by decision
- Cases by risk level
- Transactions by channel

The purpose is to demonstrate basic **operations/KPI awareness**, not to replicate an enterprise fraud analytics platform.

---

### 10. Case Search

Cases can be searched by:

- Case ID
- Transaction ID
- Customer ID
- Claim ID

This helps demonstrate basic case retrieval and investigation workflow.

---

### 11. Resolved / Escalated Cases

The application provides a separate view for cases that have reached:

- Resolved
- Escalated

This creates a simple distinction between the active queue and completed/exception cases.

---

### 12. Case Reports

After a decision is saved, the application can generate a downloadable HTML case report containing investigation information such as:

- Case summary
- Transaction details
- Customer claim
- Suspicious indicators
- Investigation checklist
- Customer history
- Analyst notes
- Evidence summary
- Recovery details
- Simulated chargeback outcome

This demonstrates basic **case documentation and auditability**.

---

## Technology Stack

```text
Python
Pandas
SQLite
Streamlit
CSV
HTML
```

### Why these technologies?

**Python**  
Used for application logic, fraud scoring, data processing, and workflow orchestration.

**Pandas**  
Used for transaction data handling, filtering, analysis, and dashboard preparation.

**SQLite**  
Provides lightweight local persistence for fraud cases, checklists, decisions, and recovery information without requiring a separate database server.

**Streamlit**  
Provides a fast local web interface suitable for a portfolio application without requiring a separate frontend stack.

**CSV**  
Used for simple synthetic input datasets.

**HTML**  
Used for downloadable case reports.

---

## Project Structure

```text
banking-fraud-investigation/
│
├── app.py
├── fraud_rules.py
├── investigation.py
├── database.py
├── report_generator.py
├── requirements.txt
├── README.md
│
├── data/
│   ├── transactions.csv
│   ├── customers.csv
│   └── claims.csv
│
└── database/
    └── fraud_cases.db
```

### File Responsibilities

| File | Purpose |
|---|---|
| `app.py` | Streamlit application, UI, filtering, investigation workflow |
| `fraud_rules.py` | Fraud scoring and suspicious-indicator logic |
| `investigation.py` | Case IDs, SOP checklist, chargeback simulation and resolution logic |
| `database.py` | SQLite database operations and case persistence |
| `report_generator.py` | HTML case report generation |
| `transactions.csv` | Synthetic transaction data |
| `customers.csv` | Synthetic customer data |
| `claims.csv` | Synthetic customer claim data |
| `fraud_cases.db` | Local case-state persistence |

---

## Data Flow

```text
transactions.csv
       │
       ▼
Fraud Rule Engine
       │
       ├── Amount
       ├── Location
       ├── Merchant
       ├── Channel
       ├── International Activity
       ├── Rapid Transactions
       └── Other Indicators
       │
       ▼
Risk Score + Risk Level
       │
       ▼
Case Creation
       │
       ▼
SQLite Case Store
       │
       ├── Alert Queue
       ├── Investigation
       ├── Decision
       ├── Recovery
       └── Resolution
```

---

## Investigation Workflow

A typical case can be handled as follows:

```text
1. Open Alert Queue
2. Filter HIGH-risk cases
3. Select a case
4. Review transaction details
5. Review suspicious indicators
6. Review customer claim
7. Review customer transaction history
8. Complete SOP checklist
9. Record analyst notes
10. Record evidence summary
11. Select decision
12. Review recovery opportunity
13. Review simulated chargeback eligibility
14. Save final decision
15. Generate case report
```

---

## Example Investigation Scenario

Example synthetic case:

```text
Transaction: TX1121
Amount: ₹85,000
Channel: Online
Type: International
Location: New
Merchant: New
Category: Luxury
Risk: HIGH
```

Possible indicators:

```text
• Unusually high transaction amount
• International transaction
• New or unusual location
• New merchant
• Higher-risk merchant category
```

An analyst would then compare the transaction with:

- The customer claim
- Historical transaction behavior
- Triggered indicators
- Investigation checklist
- Available recovery information

The final outcome should be based on the evidence captured in the case, not only on the numerical risk score.

---

## Installation

### 1. Clone or extract the project

Open the project folder in VS Code.

### 2. Create a virtual environment

Windows:

```bash
py -m venv .venv
```

Activate:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

Using Python to avoid Windows launcher/path issues:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Start the application

```bash
python -m streamlit run app.py
```

The application will open in the browser at the local Streamlit address shown in the terminal.

---

## Demo Walkthrough

For an interview/demo, a short workflow is enough:

```text
Dashboard
   ↓
Alert Queue
   ↓
Select HIGH-risk case
   ↓
Investigation
   ↓
Review transaction + history + claim
   ↓
Complete SOP checklist
   ↓
Add evidence + analyst notes
   ↓
Make decision
   ↓
Review recovery
   ↓
Review simulated chargeback
   ↓
Save case
   ↓
Download report
```

A good demonstration should focus on the **analyst process**, not just the UI.

---

## Design Approach

The application follows three main principles:

### Explainability

Fraud scores are generated from visible rules so an analyst can understand why a case was flagged.

### Structured Decisioning

The application requires evidence and checklist completion before a final decision is stored.

### Lightweight Architecture

The project intentionally avoids unnecessary infrastructure. It can run locally using Python, SQLite, and Streamlit.

---

## Limitations

This project is intentionally a portfolio simulator.

It is **not**:

- A production banking application
- A real fraud detection engine
- A real Bank of America system
- A Visa integration
- A Mastercard integration
- A real chargeback processor
- A real-time payment monitoring platform
- A production ML fraud model
- A source of real customer data

All customer, transaction, and claim records are synthetic.

The fraud rules are demonstration logic and should not be treated as real financial-institution decision rules.

---

## Future Enhancements

Potential next-phase improvements:

### Fraud Analytics

- Advanced anomaly detection
- Behavioral transaction profiling
- Machine-learning risk scoring
- Merchant/customer velocity analysis

### Operations

- Decisions-per-hour KPI
- Queue aging
- SLA tracking
- Productivity reporting
- Decision accuracy measurement when labeled ground truth is available

### Claims & Chargebacks

- Dispute reason-code reference layer
- Visa/Mastercard educational rule mapping
- More detailed chargeback decision matrix
- Merchant response / representment simulation
- Provisional credit workflow simulation

### Platform

- Role-based access control
- Audit logging
- Case comments/history
- Rule management interface
- User authentication
- REST API
- Real-time transaction ingestion

### Notifications & Integration

- Email notifications
- Webhook integrations
- Enterprise fraud/SIEM integration concepts
- Scheduled reporting

---

## Interview Explanation

### 30-second explanation

> I built a Banking Fraud and Customer Claim Investigation Simulator using Python, Pandas, SQLite and Streamlit. The application takes synthetic transaction data, applies explainable fraud rules, creates a risk-based alert queue, supports customer claim investigation, captures evidence and SOP checklist completion, allows fraud/genuine/escalation decisioning, records recovery opportunities, and provides a simplified chargeback workflow and case report.

### Why rule-based scoring?

> I used rule-based scoring because the main objective was explainable analyst decisioning rather than training and evaluating a machine-learning model.

### Why Streamlit?

> I used Streamlit to create a lightweight analyst console quickly without introducing a separate frontend framework.

### Why SQLite?

> SQLite gives the project local persistence for cases and decisions without requiring a separate database server.

### Is the chargeback workflow real?

> No. It is a simplified educational simulation designed to demonstrate the investigation-to-resolution concept. It does not connect to Visa, Mastercard, or a real banking platform.

---

## Disclaimer

This project is created strictly for **educational and portfolio purposes**.

All transaction, customer, and claim information is synthetic.

No real customer information, banking credentials, payment-network credentials, or production financial systems are used.

---

## Author

**Ayush Kumar Thakur**

Cybersecurity / Fraud Operations Portfolio

LinkedIn: `linkedin.com/in/aayush-thakur-001`

GitHub: `github.com/aayushthakur001`

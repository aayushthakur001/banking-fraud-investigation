SOP_STEPS = [
    ("details_reviewed", "Transaction details reviewed"),
    ("history_reviewed", "Customer transaction history reviewed"),
    ("indicators_reviewed", "Suspicious indicators reviewed"),
    ("claim_reviewed", "Customer claim reviewed"),
    ("evidence_validated", "Evidence validated"),
    ("recovery_checked", "Recovery opportunity checked"),
    ("decision_documented", "Decision documented"),
]

def build_case_id(transaction_id: str) -> str:
    return f"CASE-{transaction_id.replace('TX','')}"

def evaluate_chargeback(decision: str):
    if decision == "Fraud Confirmed":
        return "Eligible", "Simulated educational eligibility after fraud confirmation."
    if decision == "Genuine / No Fraud":
        return "Not Eligible", "No fraud confirmed in the simulation."
    return "Needs Review", "Escalation required before simulated eligibility can be decided."

def resolution_for(decision: str) -> str:
    return {
        "Fraud Confirmed": "Fraud Confirmed – Customer Protected",
        "Genuine / No Fraud": "Genuine Transaction – Claim Denied",
        "Escalate": "Escalated for Further Review",
    }[decision]

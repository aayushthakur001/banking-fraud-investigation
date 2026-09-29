from __future__ import annotations
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "database" / "fraud_cases.db"

def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS fraud_cases (
        case_id TEXT PRIMARY KEY,
        transaction_id TEXT NOT NULL,
        customer_id TEXT NOT NULL,
        claim_id TEXT,
        risk_score INTEGER,
        risk_level TEXT,
        alert_status TEXT DEFAULT 'New',
        decision TEXT,
        analyst_notes TEXT,
        evidence_summary TEXT,
        resolution TEXT,
        recovery_applicable TEXT,
        recovery_amount REAL DEFAULT 0,
        chargeback_eligibility TEXT,
        chargeback_status TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS investigations (
        case_id TEXT PRIMARY KEY,
        details_reviewed INTEGER DEFAULT 0,
        history_reviewed INTEGER DEFAULT 0,
        indicators_reviewed INTEGER DEFAULT 0,
        claim_reviewed INTEGER DEFAULT 0,
        evidence_validated INTEGER DEFAULT 0,
        recovery_checked INTEGER DEFAULT 0,
        decision_documented INTEGER DEFAULT 0,
        checklist_complete INTEGER DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS case_decisions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id TEXT,
        decision TEXT,
        notes TEXT,
        evidence_summary TEXT,
        recommended_action TEXT,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS recovery_actions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id TEXT,
        applicable TEXT,
        amount REAL DEFAULT 0,
        reason TEXT,
        status TEXT,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    conn.close()

def upsert_case(case: dict):
    conn = get_conn()
    conn.execute("""
        INSERT INTO fraud_cases
        (case_id, transaction_id, customer_id, claim_id, risk_score, risk_level, alert_status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(case_id) DO UPDATE SET
        claim_id=excluded.claim_id,
        risk_score=excluded.risk_score,
        risk_level=excluded.risk_level
    """, (
        case["case_id"], case["transaction_id"], case["customer_id"], case.get("claim_id"),
        int(case["risk_score"]), case["risk_level"], case.get("alert_status","New")
    ))
    conn.commit()
    conn.close()

def get_case(case_id: str):
    conn = get_conn()
    row = conn.execute("SELECT * FROM fraud_cases WHERE case_id=?", (case_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def all_cases():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM fraud_cases ORDER BY updated_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_checklist(case_id: str, checks: dict):
    conn = get_conn()
    conn.execute("""
        INSERT INTO investigations
        (case_id, details_reviewed, history_reviewed, indicators_reviewed, claim_reviewed,
         evidence_validated, recovery_checked, decision_documented, checklist_complete)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(case_id) DO UPDATE SET
        details_reviewed=excluded.details_reviewed,
        history_reviewed=excluded.history_reviewed,
        indicators_reviewed=excluded.indicators_reviewed,
        claim_reviewed=excluded.claim_reviewed,
        evidence_validated=excluded.evidence_validated,
        recovery_checked=excluded.recovery_checked,
        decision_documented=excluded.decision_documented,
        checklist_complete=excluded.checklist_complete
    """, (
        case_id,
        int(checks["details_reviewed"]), int(checks["history_reviewed"]),
        int(checks["indicators_reviewed"]), int(checks["claim_reviewed"]),
        int(checks["evidence_validated"]), int(checks["recovery_checked"]),
        int(checks["decision_documented"]), int(all(checks.values()))
    ))
    conn.commit()
    conn.close()

def get_checklist(case_id: str):
    conn = get_conn()
    row = conn.execute("SELECT * FROM investigations WHERE case_id=?", (case_id,)).fetchone()
    conn.close()
    return dict(row) if row else {}

def save_decision(case_id, decision, notes, evidence_summary, recommended_action,
                  recovery_applicable, recovery_amount, recovery_reason,
                  chargeback_eligibility, chargeback_status, resolution):
    conn = get_conn()
    conn.execute("""
        UPDATE fraud_cases
        SET decision=?, analyst_notes=?, evidence_summary=?, resolution=?,
            recovery_applicable=?, recovery_amount=?, chargeback_eligibility=?,
            chargeback_status=?, alert_status=?, updated_at=CURRENT_TIMESTAMP
        WHERE case_id=?
    """, (
        decision, notes, evidence_summary, resolution, recovery_applicable,
        float(recovery_amount or 0), chargeback_eligibility, chargeback_status,
        "Escalated" if decision == "Escalate" else "Resolved", case_id
    ))
    conn.execute("""
        INSERT INTO case_decisions(case_id, decision, notes, evidence_summary, recommended_action)
        VALUES (?, ?, ?, ?, ?)
    """, (case_id, decision, notes, evidence_summary, recommended_action))
    conn.execute("""
        INSERT INTO recovery_actions(case_id, applicable, amount, reason, status)
        VALUES (?, ?, ?, ?, ?)
    """, (case_id, recovery_applicable, float(recovery_amount or 0), recovery_reason, "Reviewed"))
    conn.commit()
    conn.close()

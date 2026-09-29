from __future__ import annotations
from datetime import datetime

def score_transaction(tx: dict) -> dict:
    score = 0
    reasons = []
    amount = float(tx.get("amount", 0))
    if amount >= 50000:
        score += 30
        reasons.append("Unusually high transaction amount")
    elif amount >= 25000:
        score += 20
        reasons.append("High transaction amount")

    if str(tx.get("domestic_international", "")).lower() == "international":
        score += 20
        reasons.append("International transaction")
    if str(tx.get("is_new_location", "")).lower() == "yes":
        score += 20
        reasons.append("New or unusual location")
    if str(tx.get("is_new_merchant", "")).lower() == "yes":
        score += 10
        reasons.append("New merchant")
    category = str(tx.get("merchant_category", "")).lower()
    if category in {"high-risk", "electronics", "luxury"}:
        score += 15
        reasons.append("Higher-risk merchant category")
    if str(tx.get("channel", "")).upper() == "ATM":
        score += 5
        reasons.append("ATM transaction")

    score = min(score, 100)
    level = "HIGH" if score >= 60 else "MEDIUM" if score >= 30 else "LOW"
    return {"score": score, "level": level, "reasons": reasons}

def rapid_transaction_signal(transactions: list[dict], customer_id: str, current_timestamp: str) -> bool:
    try:
        current = datetime.strptime(current_timestamp, "%Y-%m-%d %H:%M")
    except Exception:
        return False
    for tx in transactions:
        if tx.get("customer_id") != customer_id or tx.get("timestamp") == current_timestamp:
            continue
        try:
            t = datetime.strptime(tx.get("timestamp"), "%Y-%m-%d %H:%M")
            diff = abs((current - t).total_seconds()) / 60
            if 0 < diff <= 5:
                return True
        except Exception:
            continue
    return False

def enrich_score(base_result: dict, rapid_flag: bool) -> dict:
    result = dict(base_result)
    result["reasons"] = list(base_result["reasons"])
    if rapid_flag:
        result["score"] = min(100, result["score"] + 15)
        result["reasons"].append("Rapid repeated transaction")
    result["level"] = "HIGH" if result["score"] >= 60 else "MEDIUM" if result["score"] >= 30 else "LOW"
    return result

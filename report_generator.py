from html import escape

def create_html_report(case, tx, claim, history, reasons, checklist):
    reason_html = "".join(f"<li>{escape(str(x))}</li>" for x in reasons)
    checks = [
        ("details_reviewed","Transaction details reviewed"),
        ("history_reviewed","Customer history reviewed"),
        ("indicators_reviewed","Suspicious indicators reviewed"),
        ("claim_reviewed","Customer claim reviewed"),
        ("evidence_validated","Evidence validated"),
        ("recovery_checked","Recovery opportunity checked"),
        ("decision_documented","Decision documented"),
    ]
    checklist_html = "".join(
        f"<li>{escape(label)}: {'Complete' if checklist.get(key) else 'Pending'}</li>"
        for key, label in checks
    )
    rows = []
    for r in history[:10]:
        rows.append(
            "<tr><td>{}</td><td>₹{:,.2f}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                escape(str(r.get("transaction_id",""))),
                float(r.get("amount",0)),
                escape(str(r.get("merchant_name",""))),
                escape(str(r.get("location",""))),
                escape(str(r.get("channel","")))
            )
        )
    history_html = "".join(rows)

    return """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Fraud Case Report {case_id}</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 32px; color: #222; }}
h1, h2 {{ margin-bottom: 8px; }}
table {{ border-collapse: collapse; width: 100%; margin: 12px 0 24px; }}
th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; font-size: 13px; }}
.box {{ border: 1px solid #ddd; padding: 14px; margin-bottom: 18px; border-radius: 6px; }}
small {{ color: #666; }}
</style>
</head>
<body>
<h1>Banking Fraud & Customer Claim Investigation Report</h1>
<small>Educational simulation using synthetic data. Not a real banking or payment-network report.</small>

<div class="box">
<h2>Case Summary</h2>
<p><b>Case:</b> {case_id}</p>
<p><b>Transaction:</b> {txid}</p>
<p><b>Customer:</b> {customer}</p>
<p><b>Risk:</b> {risk_level} ({risk_score}/100)</p>
<p><b>Decision:</b> {decision}</p>
<p><b>Resolution:</b> {resolution}</p>
</div>

<h2>Transaction Details</h2>
<table>
<tr><th>Amount</th><th>Merchant</th><th>Category</th><th>Location</th><th>Channel</th><th>Card</th></tr>
<tr><td>₹{amount:,.2f}</td><td>{merchant}</td><td>{category}</td><td>{location}</td><td>{channel}</td><td>{card}</td></tr>
</table>

<h2>Customer Claim</h2>
<div class="box">{claim}</div>

<h2>Suspicious Indicators</h2>
<ul>{reasons}</ul>

<h2>Investigation Checklist</h2>
<ul>{checklist}</ul>

<h2>Customer Transaction History</h2>
<table>
<tr><th>Transaction</th><th>Amount</th><th>Merchant</th><th>Location</th><th>Channel</th></tr>
{history}
</table>

<h2>Analyst Findings</h2>
<div class="box">
<p><b>Evidence Summary:</b><br>{evidence}</p>
<p><b>Analyst Notes:</b><br>{notes}</p>
<p><b>Recovery:</b> {recovery} | ₹{recovery_amount:,.2f}</p>
<p><b>Chargeback (simulated):</b> {cb_eligibility} / {cb_status}</p>
</div>
</body>
</html>""".format(
        case_id=escape(str(case.get("case_id",""))),
        txid=escape(str(tx.get("transaction_id",""))),
        customer=escape(str(tx.get("customer_id",""))),
        risk_level=escape(str(case.get("risk_level",""))),
        risk_score=int(case.get("risk_score") or 0),
        decision=escape(str(case.get("decision") or "Pending")),
        resolution=escape(str(case.get("resolution") or "Pending")),
        amount=float(tx.get("amount") or 0),
        merchant=escape(str(tx.get("merchant_name",""))),
        category=escape(str(tx.get("merchant_category",""))),
        location=escape(str(tx.get("location",""))),
        channel=escape(str(tx.get("channel",""))),
        card=escape(str(tx.get("card_type",""))),
        claim=escape(str(claim.get("customer_statement","No claim linked."))),
        reasons=reason_html or "<li>No specific indicators.</li>",
        checklist=checklist_html,
        history=history_html,
        evidence=escape(str(case.get("evidence_summary") or "Pending")),
        notes=escape(str(case.get("analyst_notes") or "Pending")),
        recovery=escape(str(case.get("recovery_applicable") or "Pending")),
        recovery_amount=float(case.get("recovery_amount") or 0),
        cb_eligibility=escape(str(case.get("chargeback_eligibility") or "Pending")),
        cb_status=escape(str(case.get("chargeback_status") or "Pending"))
    )

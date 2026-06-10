"""Fraud Impact Engine — estimates financial and organizational damage (INR)."""

import os
from typing import Any, Dict, List

# Amounts stored in Indian Rupees (approx. prior USD bands × 83)
_INR_FACTOR = float(os.getenv("FRAUD_USD_TO_INR", "83"))


def estimate_fraud_impact(findings: Dict[str, Any], risk_score: float) -> Dict[str, Any]:
    perms = findings.get("permissions", [])
    factors: List[str] = []
    financial_low, financial_high = 0, 0
    org_severity = "low"

    if any("SMS" in p or "CALL" in p for p in perms):
        factors.append("Telephony/SMS fraud vector")
        financial_low += int(500 * _INR_FACTOR)
        financial_high += int(15000 * _INR_FACTOR)
        org_severity = "high"

    if any("ACCESSIBILITY" in p for p in perms):
        factors.append("Accessibility-driven account takeover")
        financial_low += int(2000 * _INR_FACTOR)
        financial_high += int(50000 * _INR_FACTOR)
        org_severity = "critical"

    if findings.get("c2_communications"):
        factors.append("Active C2 — data exfiltration & ransomware staging")
        financial_low += int(1000 * _INR_FACTOR)
        financial_high += int(100000 * _INR_FACTOR)
        org_severity = "critical"

    if len(findings.get("urls", [])) > 5:
        factors.append("Multiple external endpoints — phishing or payload delivery")
        financial_low += int(300 * _INR_FACTOR)
        financial_high += int(8000 * _INR_FACTOR)

    risk_multiplier = 1 + (risk_score / 100)
    financial_low = int(financial_low * risk_multiplier)
    financial_high = int(financial_high * risk_multiplier)

    return {
        "currency": "INR",
        "currency_symbol": "₹",
        "estimated_loss_per_device": {"low": financial_low, "high": financial_high},
        "organizational_impact": org_severity,
        "affected_assets": [
            "End-user devices",
            "Corporate MDM estate" if risk_score > 60 else "Consumer devices",
        ],
        "risk_factors": factors or ["Limited high-risk indicators in static pass"],
        "remediation_priority": "P1" if org_severity in ("critical", "high") else "P2",
        "recommended_actions": [
            "Block package hash and signing certificate across MDM",
            "Rotate credentials if accessibility/SMS abuse suspected",
            "Add network IOCs to firewall and DNS sinkhole",
            "Notify fraud operations and affected user cohort",
        ],
    }

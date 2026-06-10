"""AI Reverse Engineering Assistant — human-readable explanations of suspicious patterns."""

from typing import Any, Dict, List


API_EXPLANATIONS = {
    "crypto": "Cryptographic APIs may hide payloads, encrypt C2 traffic, or protect stolen data at rest.",
    "networking": "Custom networking stacks often bypass security controls and reach attacker infrastructure.",
    "process_execution": "Shell execution enables dropping secondary malware or privilege escalation.",
    "reflection": "Reflection bypasses static analysis and loads malicious code at runtime.",
    "file_operations": "Broad file access supports credential theft and persistence mechanisms.",
}


def explain_suspicious_code(findings: Dict[str, Any]) -> Dict[str, Any]:
    explanations: List[Dict[str, str]] = []
    apis = findings.get("suspicious_apis") or {}

    if isinstance(apis, dict):
        for category, items in apis.items():
            sample = items[0] if isinstance(items, list) and items else str(category)
            explanations.append(
                {
                    "category": category,
                    "sample": sample,
                    "explanation": API_EXPLANATIONS.get(category, "Potentially malicious API usage detected."),
                    "severity": "high" if category in ("process_execution", "reflection") else "medium",
                }
            )

    for secret in findings.get("hardcoded_secrets", []):
        if isinstance(secret, dict) and secret.get("matches"):
            explanations.append(
                {
                    "category": "hardcoded_secret",
                    "sample": secret.get("type", "secret"),
                    "explanation": "Hardcoded secrets in mobile binaries are commonly abused for API fraud and C2 authentication.",
                    "severity": "critical",
                }
            )

    obf = findings.get("obfuscation", {})
    if obf.get("score", 0) > 0.3:
        explanations.append(
            {
                "category": "obfuscation",
                "sample": ", ".join(obf.get("indicators", [])[:3]),
                "explanation": "Obfuscation increases analyst effort and is a hallmark of crimeware packers.",
                "severity": "high",
            }
        )

    return {
        "assistant": "AI Reverse Engineering Assistant",
        "finding_count": len(explanations),
        "explanations": explanations[:20],
    }

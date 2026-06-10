"""Threat intelligence correlation (local heuristics + optional external feeds)."""

import os
from typing import Any, Dict, List


KNOWN_MALICIOUS_PATTERNS = [
    ("banking", "Banking trojan behavioral pattern"),
    ("spy", "Spyware / stalkerware pattern"),
    ("sms", "SMS fraud / premium service abuse"),
    ("rat", "Remote access trojan indicators"),
]


def correlate_threat_intel(findings: Dict[str, Any], file_hash: str) -> Dict[str, Any]:
    correlations: List[Dict[str, Any]] = []
    package = (findings.get("metadata") or {}).get("package_name", "").lower()

    for keyword, desc in KNOWN_MALICIOUS_PATTERNS:
        if keyword in package:
            correlations.append(
                {
                    "source": "behavioral_heuristic",
                    "match": desc,
                    "confidence": 0.72,
                    "indicator": package,
                }
            )

    for domain in findings.get("domains", [])[:10]:
        if any(tld in domain for tld in (".ru", ".cn", ".top", ".xyz")):
            correlations.append(
                {
                    "source": "domain_reputation",
                    "match": "High-risk TLD or bulletproof hosting pattern",
                    "confidence": 0.65,
                    "indicator": domain,
                }
            )

    vt_enabled = bool(os.getenv("VIRUSTOTAL_API_KEY"))
    correlations.append(
        {
            "source": "hash_lookup",
            "match": "SHA-256 ready for VirusTotal enrichment"
            if vt_enabled
            else "Configure VIRUSTOTAL_API_KEY for live TI lookup",
            "confidence": 0.5 if not vt_enabled else 0.9,
            "indicator": file_hash,
        }
    )

    return {
        "correlation_count": len(correlations),
        "correlations": correlations,
        "feeds_configured": {
            "virustotal": vt_enabled,
            "urlhaus": bool(os.getenv("URLHAUS_API_KEY")),
            "shodan": bool(os.getenv("SHODAN_API_KEY")),
        },
    }

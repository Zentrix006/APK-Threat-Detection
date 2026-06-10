"""Digital Malware Twin — predicted future behaviors from observed evidence."""

from typing import Any, Dict, List

from app.utils.safe_data import safe_dict


def build_digital_twin(findings: Dict[str, Any], risk_score: float) -> Dict[str, Any]:
    predictions: List[Dict[str, Any]] = []
    confidence_base = min(0.95, 0.45 + (risk_score / 200))

    if findings.get("c2_communications") or len(findings.get("urls", [])) > 3:
        predictions.append(
            {
                "behavior": "Persistent C2 beaconing",
                "likelihood": round(min(0.92, confidence_base + 0.2), 2),
                "timeframe": "Within 24–72 hours of install",
                "evidence": ["Network IOCs", "INTERNET permission"],
            }
        )

    perms = findings.get("permissions", [])
    if any("SMS" in p for p in perms):
        predictions.append(
            {
                "behavior": "SMS interception / premium fraud",
                "likelihood": round(confidence_base + 0.15, 2),
                "timeframe": "On first boot or SMS received",
                "evidence": ["SMS permissions"],
            }
        )

    if findings.get("obfuscation", {}).get("score", 0) > 0.4:
        predictions.append(
            {
                "behavior": "Delayed payload download",
                "likelihood": round(confidence_base + 0.1, 2),
                "timeframe": "After network connectivity confirmed",
                "evidence": ["Obfuscation indicators"],
            }
        )

    if any("ACCESSIBILITY" in p for p in perms):
        predictions.append(
            {
                "behavior": "Automated UI fraud (clicker / credential harvest)",
                "likelihood": round(confidence_base + 0.18, 2),
                "timeframe": "When target banking app is opened",
                "evidence": ["Accessibility service"],
            }
        )

    if not predictions:
        predictions.append(
            {
                "behavior": "Background data collection",
                "likelihood": round(confidence_base, 2),
                "timeframe": "Continuous while installed",
                "evidence": ["Baseline permission profile"],
            }
        )

    return {
        "twin_id": safe_dict(findings.get("metadata")).get("package_name", "unknown"),
        "model_version": "heuristic-v1",
        "predictions": predictions,
        "simulation_notes": (
            "Predictions are derived from static/dynamic evidence correlation. "
            "Connect an Android sandbox (ADB profile in Docker) for higher-fidelity twin modeling."
        ),
    }

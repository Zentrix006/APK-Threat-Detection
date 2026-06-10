"""Malware Story Mode — narrated attack flow from install to impact."""

from typing import Any, Dict, List


def generate_malware_story(
    findings: Dict[str, Any],
    risk_level: str,
    mitre_mappings: List[Dict[str, Any]],
) -> Dict[str, Any]:
    perms = findings.get("permissions", [])
    has_sms = any("SMS" in p for p in perms)
    has_overlay = any("SYSTEM_ALERT_WINDOW" in p or "overlay" in p.lower() for p in perms)
    has_accessibility = any("BIND_ACCESSIBILITY" in p for p in perms)
    has_c2 = bool(findings.get("c2_communications") or findings.get("urls"))
    obfuscation = findings.get("obfuscation", {}).get("score", 0) > 0.5

    chapters: List[Dict[str, str]] = [
        {
            "phase": "Installation",
            "title": "Victim installs the package",
            "narrative": (
                f"The user installs an application presenting as "
                f"'{findings.get('metadata', {}).get('app_name', 'a legitimate app')}'. "
                "At this stage the APK appears functional while requesting sensitive capabilities."
            ),
        },
        {
            "phase": "Permission abuse",
            "title": "Dangerous capabilities are activated",
            "narrative": _permission_chapter(perms, has_sms, has_overlay, has_accessibility),
        },
    ]

    if obfuscation:
        chapters.append(
            {
                "phase": "Defense evasion",
                "title": "Code hiding and anti-analysis",
                "narrative": (
                    "Static indicators suggest obfuscation or packing. Attackers use this to delay "
                    "signature detection and hinder reverse engineering by analysts."
                ),
            }
        )

    if has_c2:
        chapters.append(
            {
                "phase": "Command & control",
                "title": "Outbound communications to attacker infrastructure",
                "narrative": (
                    "Network indicators tie the sample to external hosts. This enables remote "
                    "commanding, payload updates, and exfiltration of stolen data."
                ),
            }
        )

    chapters.append(
        {
            "phase": "Impact",
            "title": "Fraud and organizational harm",
            "narrative": (
                f"Combined behaviors support a {risk_level} risk classification. "
                "Potential outcomes include credential theft, premium SMS fraud, banking overlays, "
                "and persistent surveillance of the device."
            ),
        }
    )

    return {
        "title": "Malware Story Mode",
        "risk_level": risk_level,
        "chapter_count": len(chapters),
        "chapters": chapters,
        "mitre_highlights": [m.get("technique") for m in mitre_mappings[:5]],
    }


def _permission_chapter(perms: List[str], sms: bool, overlay: bool, accessibility: bool) -> str:
    parts = [f"The application requests {len(perms)} Android permissions."]
    if sms:
        parts.append("SMS read/send capabilities may enable OTP interception or premium-rate fraud.")
    if overlay:
        parts.append("Overlay permissions can facilitate banking trojan fake login screens.")
    if accessibility:
        parts.append("Accessibility abuse allows UI automation and credential harvesting without user awareness.")
    if not (sms or overlay or accessibility):
        parts.append("Several permissions expand surveillance and data collection beyond typical app needs.")
    return " ".join(parts)

"""AI threat reasoning engine — capabilities, intent, and SOC narrative."""

import os
import json
import logging
from typing import Any, Dict, List

import httpx

logger = logging.getLogger(__name__)


async def run_threat_reasoning(
    findings: Dict[str, Any],
    risk_score: float,
    risk_level: str,
    mitre_mappings: List[Dict[str, Any]],
    apk_name: str,
) -> Dict[str, Any]:
    """Produce interpretable threat reasoning; uses Ollama when available in Docker."""
    ollama_url = os.getenv("OLLAMA_URL", "http://ollama:11434")
    model = os.getenv("OLLAMA_MODEL", "qwen3")

    capabilities = _derive_capabilities(findings)
    intent = _derive_intent(findings, risk_level)

    ai_narrative = None
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            prompt = _build_prompt(findings, risk_score, risk_level, mitre_mappings, apk_name, capabilities)
            resp = await client.post(
                f"{ollama_url}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False, "temperature": 0.4},
            )
            if resp.status_code == 200:
                ai_narrative = resp.json().get("response")
    except Exception as e:
        logger.warning(f"Ollama reasoning unavailable: {e}")

    return {
        "engine": "AI Threat Reasoning Engine",
        "risk_score": risk_score,
        "risk_level": risk_level,
        "malicious_intent": intent,
        "capabilities": capabilities,
        "mitre_summary": _mitre_summary(mitre_mappings),
        "analyst_narrative": ai_narrative or _fallback_narrative(capabilities, intent, risk_level),
        "confidence": 0.78 if ai_narrative else 0.65,
    }


def _derive_capabilities(findings: Dict[str, Any]) -> List[str]:
    caps = []
    perms = findings.get("permissions", [])
    if any("INTERNET" in p for p in perms):
        caps.append("Network communication")
    if any("SMS" in p for p in perms):
        caps.append("SMS interception / fraud")
    if any("ACCESSIBILITY" in p for p in perms):
        caps.append("Accessibility abuse")
    if any("CAMERA" in p or "RECORD_AUDIO" in p for p in perms):
        caps.append("Surveillance")
    if findings.get("c2_communications"):
        caps.append("Command and control")
    if findings.get("obfuscation", {}).get("score", 0) > 0.4:
        caps.append("Code obfuscation / anti-analysis")
    return caps or ["Limited capabilities identified in static pass"]


def _derive_intent(findings: Dict[str, Any], risk_level: str) -> str:
    if risk_level in ("critical", "high"):
        return "Financial fraud, credential theft, or persistent surveillance"
    if findings.get("c2_communications"):
        return "Remote operator control and data exfiltration"
    return "Potentially unwanted or privacy-invasive behavior"


def _mitre_summary(mappings: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    seen = set()
    out = []
    for m in mappings:
        key = m.get("technique", "")
        if key and key not in seen:
            seen.add(key)
            out.append({"tactic": m.get("tactic", ""), "technique": key})
    return out[:15]


def _build_prompt(
    findings: Dict[str, Any],
    risk_score: float,
    risk_level: str,
    mitre: List[Dict],
    apk_name: str,
    capabilities: List[str],
) -> str:
    return f"""You are a senior mobile threat analyst. Write a concise SOC investigation summary for APK "{apk_name}".
Risk: {risk_score}/100 ({risk_level}).
Capabilities: {json.dumps(capabilities)}.
Permissions count: {len(findings.get('permissions', []))}.
URLs: {len(findings.get('urls', []))}, IPs: {len(findings.get('ips', []))}.
MITRE: {json.dumps(mitre[:8])}.
Explain malicious intent, attack chain, and 3 remediation steps. Max 400 words."""


def _fallback_narrative(capabilities: List[str], intent: str, risk_level: str) -> str:
    return (
        f"Automated assessment classifies this sample as {risk_level} risk. "
        f"Observed capabilities include: {', '.join(capabilities)}. "
        f"Assessed intent: {intent}. "
        "Recommend blocking the package, rotating exposed credentials, and hunting for related IOCs across the estate."
    )

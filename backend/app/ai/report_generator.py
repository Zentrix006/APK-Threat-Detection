"""
AI-Powered Report Generation
Uses Ollama with Qwen3 for intelligent analysis
"""

import httpx
import json
import os
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate AI-powered threat intelligence reports"""
    
    def __init__(self, ollama_url: str = None, model: str = None):
        self.ollama_url = ollama_url or os.getenv("OLLAMA_URL", "http://ollama:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "qwen3")
        self.client = httpx.AsyncClient(timeout=300.0)

    async def generate_report(self, analysis_data: Dict[str, Any], apk_name: str) -> str:
        """Generate comprehensive threat report using LLM"""
        try:
            # Prepare context for LLM
            context = self._prepare_context(analysis_data, apk_name)
            
            # Generate report using Ollama
            report = await self._call_ollama(context)
            
            return report
        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}")
            return self._fallback_report(analysis_data, apk_name)

    def _prepare_context(self, analysis_data: Dict[str, Any], apk_name: str) -> str:
        """Prepare context for LLM"""
        context = f"""
Analyze this mobile threat intelligence report for APK: {apk_name}

ANALYSIS SUMMARY:
- Risk Score: {analysis_data.get('risk_score', 0)}/100
- Risk Level: {analysis_data.get('risk_level', 'unknown')}
- Analysis Type: {analysis_data.get('analysis_type', 'hybrid')}

PERMISSIONS ({len(analysis_data.get('permissions', []))}):
{json.dumps(analysis_data.get('permissions', [])[:5], indent=2)}

SUSPICIOUS APIs:
{json.dumps(analysis_data.get('suspicious_apis', [])[:5], indent=2)}

NETWORK INDICATORS:
- URLs: {len(analysis_data.get('urls', []))}
- IPs: {len(analysis_data.get('ips', []))}
- Domains: {len(analysis_data.get('domains', []))}
- C2 Communications: {len(analysis_data.get('c2_communications', []))}

C2 DETECTED:
{json.dumps(analysis_data.get('c2_communications', []), indent=2)}

ARTIFACTS:
- Activities: {len(analysis_data.get('activities', []))}
- Services: {len(analysis_data.get('services', []))}
- Broadcast Receivers: {len(analysis_data.get('broadcast_receivers', []))}

MITRE ATT&CK MAPPING:
{json.dumps(analysis_data.get('mitre_mapping', [])[:3], indent=2)}

Please provide:
1. Executive Summary
2. Key Findings
3. Threat Assessment
4. Recommended Actions
5. Confidence Level
"""
        return context

    async def _call_ollama(self, context: str) -> str:
        """Call Ollama API for report generation"""
        try:
            response = await self.client.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": context,
                    "stream": False,
                    "temperature": 0.7,
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "Report generation failed")
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Ollama call failed: {str(e)}")
            return None

    def _fallback_report(self, analysis_data: Dict[str, Any], apk_name: str) -> str:
        """Generate fallback report if LLM is unavailable"""
        risk_level = analysis_data.get("risk_level", "unknown").upper()
        risk_score = analysis_data.get("risk_score", 0)
        
        report = f"""
# APK THREAT INTELLIGENCE REPORT
## {apk_name}

### Executive Summary
This APK has been analyzed and assigned a risk score of {risk_score}/100 ({risk_level}).

### Key Findings
- Permissions Requested: {len(analysis_data.get("permissions", []))}
- Suspicious APIs Detected: {len(analysis_data.get("suspicious_apis", []))}
- Network Connections: {len(analysis_data.get("network_traffic", []))}
- Potential C2 Communications: {len(analysis_data.get("c2_communications", []))}

### Threat Assessment
Risk Level: **{risk_level}**

The application exhibits the following risk indicators:
"""
        
        # Add indicators
        if analysis_data.get("c2_communications"):
            report += "\n- Command & Control communications detected"
        
        if analysis_data.get("suspicious_apis"):
            report += "\n- Suspicious API usage detected"
        
        if analysis_data.get("urls"):
            report += f"\n- {len(analysis_data.get('urls', []))} external URLs embedded"
        
        report += """

### Recommended Actions
1. Review permissions and network connections
2. Check for known malware signatures
3. Monitor network traffic during execution
4. Consider sandboxing before installation
5. Report to your security team if malware is confirmed

### Confidence Level
70% (based on heuristic analysis)
"""
        return report


class MitreMapper:
    """Map detected behaviors to MITRE ATT&CK framework"""
    
    # Simplified MITRE ATT&CK mapping
    BEHAVIOR_TO_MITRE = {
        "RECORD_AUDIO": {
            "tactic": "Collection",
            "technique": "T1429: Capture Audio"
        },
        "CAMERA": {
            "tactic": "Collection",
            "technique": "T1512: Capture Screen Content"
        },
        "ACCESS_FINE_LOCATION": {
            "tactic": "Collection",
            "technique": "T1430: Location Tracking"
        },
        "READ_SMS": {
            "tactic": "Collection",
            "technique": "T1407: Capture SMS Messages"
        },
        "SEND_SMS": {
            "tactic": "Impact",
            "technique": "T1432: Exfiltration Over SMS"
        },
        "CALL_PHONE": {
            "tactic": "Impact",
            "technique": "T1401: Modify System Partition"
        },
        "READ_CONTACTS": {
            "tactic": "Collection",
            "technique": "T1433: Exfiltrate Contact List"
        },
        "INTERNET": {
            "tactic": "Command and Control",
            "technique": "T1571: Non-Standard Port"
        },
    }
    
    @staticmethod
    def map_behaviors(analysis_data: Dict[str, Any]) -> List[Dict]:
        """Map detected behaviors to MITRE ATT&CK"""
        mappings = []
        
        permissions = analysis_data.get("permissions", [])
        for perm in permissions:
            perm_name = perm.split(".")[-1]
            if perm_name in MitreMapper.BEHAVIOR_TO_MITRE:
                mapping = MitreMapper.BEHAVIOR_TO_MITRE[perm_name].copy()
                mapping["permission"] = perm
                mappings.append(mapping)
        
        # Map API calls
        suspicious_apis = analysis_data.get("suspicious_apis", {})
        for category, apis in suspicious_apis.items():
            if category == "crypto":
                mappings.append({
                    "tactic": "Defense Evasion",
                    "technique": "T1406: Obfuscated Files or Information",
                    "category": category
                })
            elif category == "reflection":
                mappings.append({
                    "tactic": "Defense Evasion",
                    "technique": "T1418: Weaken Encryption",
                    "category": category
                })
        
        return mappings


async def generate_comprehensive_report(
    analysis_data: Dict[str, Any],
    apk_name: str,
    include_graph: bool = True,
) -> Dict[str, Any]:
    """Generate comprehensive SOC investigation report with all intelligence modules."""
    generator = ReportGenerator()
    mapper = MitreMapper()
    intelligence = analysis_data.get("intelligence") or {}

    ai_report = await generator.generate_report(analysis_data, apk_name)
    mitre_mappings = intelligence.get("mitre_mappings") or mapper.map_behaviors(analysis_data)

    return {
        "title": f"SOC Investigation Report: {apk_name}",
        "timestamp": analysis_data.get("timestamp"),
        "risk_score": analysis_data.get("risk_score", 0),
        "risk_level": analysis_data.get("risk_level", "unknown"),
        "ai_report": ai_report,
        "executive_summary": (intelligence.get("threat_reasoning") or {}).get("analyst_narrative"),
        "mitre_mappings": mitre_mappings,
        "threat_graph": intelligence.get("threat_graph"),
        "malware_story": intelligence.get("malware_story"),
        "digital_twin": intelligence.get("digital_twin"),
        "fraud_impact": intelligence.get("fraud_impact"),
        "reverse_engineering": intelligence.get("reverse_engineering"),
        "ti_correlation": intelligence.get("ti_correlation"),
        "iocs": intelligence.get("iocs"),
        "indicators": {
            "permissions": len(analysis_data.get("permissions", [])),
            "urls": len(analysis_data.get("urls", [])),
            "ips": len(analysis_data.get("ips", [])),
            "c2_communications": len(analysis_data.get("c2_communications", [])),
            "suspicious_apis": len(analysis_data.get("suspicious_apis", {})),
        },
        "recommendations": (intelligence.get("fraud_impact") or {}).get(
            "recommended_actions",
            [
                "Block package and signing certificate across MDM",
                "Hunt related IOCs on network perimeter",
                "Escalate to incident response if fraud impact is critical",
            ],
        ),
    }

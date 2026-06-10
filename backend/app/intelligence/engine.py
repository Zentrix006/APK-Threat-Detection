"""End-to-end investigation orchestration after static/dynamic analysis."""

import os
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

from sqlalchemy.orm import Session

from app.db import APKFile, Analysis
from app.analysis.static import StaticAnalyzer, PermissionAnalyzer
from app.analysis.dynamic import DynamicAnalyzer
from app.ml.risk_scorer import RiskScorer, MalwareClassifier
from app.ai.report_generator import MitreMapper
from app.intelligence.persistence import persist_investigation
from app.intelligence.threat_graph import build_threat_graph
from app.intelligence.story_mode import generate_malware_story
from app.intelligence.digital_twin import build_digital_twin
from app.intelligence.fraud_impact import estimate_fraud_impact
from app.intelligence.reverse_assistant import explain_suspicious_code
from app.intelligence.ti_correlation import correlate_threat_intel
from app.intelligence.reasoning import run_threat_reasoning
from app.services.progress import set_progress
from app.utils.safe_data import safe_dict

logger = logging.getLogger(__name__)


class InvestigationEngine:
    """Autonomous APK investigation pipeline for Docker and local deployments."""

    @staticmethod
    async def run_full_investigation(
        db: Session,
        apk_id: str,
        file_path: str,
        *,
        run_dynamic: Optional[bool] = None,
    ) -> Tuple[Dict[str, Any], str]:
        """
        Static → optional dynamic → intelligence → persistence.
        Returns (combined_findings, analysis_id).
        """
        apk = db.query(APKFile).filter(APKFile.id == apk_id).first()
        if not apk:
            raise ValueError("APK not found")

        apk.status = "analyzing"
        apk.error_message = None
        db.commit()

        set_progress(apk_id, "queued", "Investigation queued…", 100)
        set_progress(apk_id, "static_analysis", "Extracting manifest, permissions, and IOCs…", 10)
        findings = await StaticAnalyzer(file_path).analyze()
        if not isinstance(findings.get("metadata"), dict):
            findings["metadata"] = safe_dict(findings.get("metadata"))
        set_progress(apk_id, "static_analysis", "Static analysis complete", 100)
        perm_analysis = PermissionAnalyzer.analyze_permissions(findings.get("permissions", []))
        findings["permission_analysis"] = perm_analysis
        findings["dangerous_permissions"] = [
            d["permission"] for d in perm_analysis.get("dangerous_permissions", [])
        ]

        if run_dynamic is None:
            run_dynamic = os.getenv("ENABLE_DYNAMIC_ANALYSIS", "true").lower() == "true"

        package = (findings.get("metadata") or {}).get("package_name")
        if run_dynamic and package:
            set_progress(apk_id, "dynamic_analysis", "Running sandbox / network capture…", 20)
            try:
                dynamic = await DynamicAnalyzer(file_path, package).analyze()
                set_progress(apk_id, "dynamic_analysis", "Dynamic analysis complete", 100)
                findings["dynamic"] = dynamic
                if dynamic.get("c2_communications"):
                    findings["c2_communications"] = dynamic["c2_communications"]
                if dynamic.get("network_traffic"):
                    findings["network_traffic"] = dynamic["network_traffic"]
            except Exception as e:
                logger.warning(f"Dynamic analysis skipped: {e}")
                findings["dynamic"] = {"status": "skipped", "reason": str(e)}
        else:
            findings["dynamic"] = {
                "status": "skipped",
                "reason": "No package name or dynamic disabled",
            }

        set_progress(apk_id, "risk_scoring", "Calculating ML risk score…", 50)
        scorer = RiskScorer()
        risk_score, risk_level = scorer.calculate_risk_score(findings)
        classifier = MalwareClassifier()
        findings["classifications"] = classifier.classify(findings)
        findings["timestamp"] = datetime.now(timezone.utc).isoformat()
        set_progress(apk_id, "risk_scoring", "Risk score calculated", 100)

        mitre_mappings = MitreMapper.map_behaviors(findings)
        set_progress(apk_id, "ai_reasoning", "AI threat reasoning & MITRE mapping…", 30)
        intelligence = await InvestigationEngine._build_intelligence(
            apk_id=apk_id,
            filename=apk.filename,
            file_hash=apk.file_hash,
            findings=findings,
            risk_score=risk_score,
            risk_level=risk_level,
            mitre_mappings=mitre_mappings,
        )

        analysis = Analysis(
            apk_id=apk_id,
            analysis_type="hybrid" if findings.get("dynamic", {}).get("network_traffic") else "static",
            status="completed",
            findings=findings,
            risk_score=risk_score,
            risk_level=risk_level,
            completed_at=datetime.utcnow(),
        )
        db.add(analysis)
        db.flush()

        meta = safe_dict(findings.get("metadata"))
        apk.package_name = meta.get("package_name") or apk.package_name
        apk.app_name = meta.get("app_name") or apk.app_name
        apk.version_name = meta.get("version_name") or apk.version_name
        apk.version_code = str(meta.get("version_code")) if meta.get("version_code") else apk.version_code
        apk.status = "analyzed"

        set_progress(apk_id, "persisting", "Saving IOCs, threat graph, and detections…", 50)
        persist_investigation(db, apk_id, analysis.id, findings, intelligence)
        db.commit()

        set_progress(apk_id, "completed", "Investigation complete", 100)
        logger.info(f"Investigation completed for {apk_id}")
        return findings, analysis.id

    @staticmethod
    async def _build_intelligence(
        apk_id: str,
        filename: str,
        file_hash: str,
        findings: Dict[str, Any],
        risk_score: float,
        risk_level: str,
        mitre_mappings: list,
    ) -> Dict[str, Any]:
        graph = build_threat_graph(apk_id, filename, file_hash, findings, mitre_mappings)
        reasoning = await run_threat_reasoning(
            findings, risk_score, risk_level, mitre_mappings, filename
        )
        return {
            "threat_graph": graph,
            "threat_reasoning": reasoning,
            "malware_story": generate_malware_story(findings, risk_level, mitre_mappings),
            "digital_twin": build_digital_twin(findings, risk_score),
            "fraud_impact": estimate_fraud_impact(findings, risk_score),
            "reverse_engineering": explain_suspicious_code(findings),
            "ti_correlation": correlate_threat_intel(findings, file_hash),
            "mitre_mappings": mitre_mappings,
            "iocs": {
                "urls": findings.get("urls", [])[:30],
                "ips": findings.get("ips", [])[:30],
                "domains": findings.get("domains", [])[:30],
                "permissions": findings.get("permissions", [])[:50],
                "file_hash": file_hash,
            },
        }

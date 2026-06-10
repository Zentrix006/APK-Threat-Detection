"""Persist analysis artifacts, detections, threats, and graphs to the database."""

from typing import Any, Dict, List
from sqlalchemy.orm import Session

from app.db import APKFile, Analysis, Artifact, Detection, Threat, ThreatGraph
from app.utils.safe_data import clean_str, safe_dict, safe_list, safe_str_list, sanitize_for_db


def _clear_apk_intel(db: Session, apk_id: str) -> None:
    db.query(Artifact).filter(Artifact.apk_id == apk_id).delete()
    db.query(Threat).filter(Threat.apk_id == apk_id).delete()
    db.query(ThreatGraph).filter(ThreatGraph.apk_id == apk_id).delete()
    analyses = db.query(Analysis).filter(Analysis.apk_id == apk_id).all()
    for a in analyses:
        db.query(Detection).filter(Detection.analysis_id == a.id).delete()


def persist_investigation(
    db: Session,
    apk_id: str,
    analysis_id: str,
    findings: Dict[str, Any],
    intelligence: Dict[str, Any],
) -> None:
    """Write IOCs, MITRE detections, threats, and threat graph."""
    _clear_apk_intel(db, apk_id)

    apk = db.query(APKFile).filter(APKFile.id == apk_id).first()
    if apk:
        meta = safe_dict(findings.get("metadata"))
        apk.package_name = clean_str(meta.get("package_name") or apk.package_name, 256) or apk.package_name
        apk.app_name = clean_str(meta.get("app_name") or apk.app_name, 256) or apk.app_name
        apk.version_name = clean_str(meta.get("version_name") or apk.version_name, 64) or apk.version_name
        if meta.get("version_code"):
            apk.version_code = clean_str(meta.get("version_code"), 32)

    for url in safe_str_list(findings.get("urls"))[:50]:
        db.add(
            Artifact(
                apk_id=apk_id,
                artifact_type="url",
                value=clean_str(url, 512),
                source="static",
                is_suspicious=True,
            )
        )
    for ip in safe_str_list(findings.get("ips"))[:50]:
        db.add(
            Artifact(
                apk_id=apk_id,
                artifact_type="ip",
                value=clean_str(ip, 64),
                source="static",
                is_suspicious=True,
            )
        )
    for domain in safe_str_list(findings.get("domains"))[:50]:
        db.add(
            Artifact(
                apk_id=apk_id,
                artifact_type="domain",
                value=clean_str(domain, 256),
                source="static",
                is_suspicious="." in domain,
            )
        )
    for perm in safe_str_list(findings.get("permissions"))[:80]:
        db.add(
            Artifact(
                apk_id=apk_id,
                artifact_type="permission",
                value=clean_str(perm, 256),
                source="manifest",
                is_suspicious=perm in set(findings.get("dangerous_permissions", [])),
            )
        )

    for c2 in safe_list(findings.get("c2_communications"))[:20]:
        if not isinstance(c2, dict):
            continue
        db.add(
            Threat(
                apk_id=apk_id,
                threat_type="c2",
                description=clean_str(c2.get("description", "C2 communication observed"), 512),
                severity="critical",
                is_c2=True,
                c2_protocol=clean_str(c2.get("protocol"), 32) or None,
                c2_domain=clean_str(c2.get("domain"), 256) or None,
                c2_ip=clean_str(c2.get("ip"), 64) or None,
                c2_port=c2.get("port"),
            )
        )

    for mapping in safe_list(intelligence.get("mitre_mappings")):
        if not isinstance(mapping, dict):
            continue
        db.add(
            Detection(
                analysis_id=analysis_id,
                detection_type="behavior",
                name=clean_str(mapping.get("technique", "Unknown technique"), 256),
                category=clean_str(mapping.get("tactic"), 128) or None,
                description=clean_str(mapping.get("description") or mapping.get("permission"), 512) or None,
                confidence=0.85,
                mitre_tactics=[mapping],
            )
        )

    graph = safe_dict(intelligence.get("threat_graph"))
    if graph.get("nodes"):
        db.add(
            ThreatGraph(
                apk_id=apk_id,
                nodes=sanitize_for_db(graph.get("nodes", [])),
                edges=sanitize_for_db(graph.get("edges", [])),
            )
        )

    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if analysis:
        merged = sanitize_for_db(dict(findings))
        merged["intelligence"] = sanitize_for_db(intelligence)
        analysis.findings = merged

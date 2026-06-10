"""Investigation and SOC intelligence API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db, APKFile, Analysis, Artifact, Threat, ThreatGraph, Report
from app.services.progress import get_progress
from app.utils.safe_data import safe_dict, safe_list

router = APIRouter()


def _failure_hint(message: str) -> str:
    m = message.lower()
    if "nul" in m or "0x00" in m:
        return "Binary junk in extracted strings was stripped — retry the investigation."
    if "nonetype" in m or "not subscriptable" in m:
        return "Internal data shape error — retry after update; partial analysis may remain."
    if "connection" in m or "refused" in m:
        return "A dependent service (Ollama, Redis, sandbox) may be unreachable."
    if "file" in m and "not found" in m:
        return "APK file missing on disk — re-upload the sample."
    if "timeout" in m:
        return "Analysis timed out — try again or disable dynamic/sandbox steps."
    return "Check backend logs (docker compose logs backend) for full traceback."


@router.get("/investigation/{apk_id}/progress", tags=["Investigation"])
async def get_investigation_progress(apk_id: str, db: Session = Depends(get_db)):
    """Live progress for an ongoing or recent investigation."""
    apk = db.query(APKFile).filter(APKFile.id == apk_id).first()
    if not apk:
        raise HTTPException(status_code=404, detail="APK not found")

    stored = get_progress(apk_id)
    if apk.status == "failed":
        return {
            "apk_id": apk_id,
            "phase": "failed",
            "message": apk.error_message or "Investigation failed",
            "percent": 100,
            "eta_seconds": 0,
            "status": "failed",
            "error": apk.error_message,
        }

    if stored:
        return {**stored, "status": apk.status, "error": apk.error_message}

    if apk.status in ("uploaded", "analyzing"):
        return {
            "apk_id": apk_id,
            "phase": "static_analysis",
            "message": "Investigation in progress…",
            "percent": 15,
            "phase_percent": 0,
            "eta_seconds": 120,
            "status": apk.status,
        }

    return {
        "apk_id": apk_id,
        "phase": "completed" if apk.status == "analyzed" else apk.status,
        "message": "No active job" if apk.status == "analyzed" else apk.error_message or apk.status,
        "percent": 100 if apk.status == "analyzed" else 0,
        "eta_seconds": 0,
        "status": apk.status,
    }


@router.get("/investigation/{apk_id}", tags=["Investigation"])
async def get_investigation(apk_id: str, db: Session = Depends(get_db)):
    """Full SOC investigation bundle for an APK."""
    apk = db.query(APKFile).filter(APKFile.id == apk_id).first()
    if not apk:
        raise HTTPException(status_code=404, detail="APK not found")

    analysis = (
        db.query(Analysis)
        .filter(Analysis.apk_id == apk_id)
        .order_by(Analysis.created_at.desc())
        .first()
    )

    findings = safe_dict(analysis.findings if analysis else {})
    intelligence = safe_dict(findings.get("intelligence"))

    artifacts = db.query(Artifact).filter(Artifact.apk_id == apk_id).limit(200).all()
    threats = db.query(Threat).filter(Threat.apk_id == apk_id).all()
    graph = (
        db.query(ThreatGraph)
        .filter(ThreatGraph.apk_id == apk_id)
        .order_by(ThreatGraph.generated_at.desc())
        .first()
    )
    reports = db.query(Report).filter(Report.apk_id == apk_id).order_by(Report.created_at.desc()).limit(5).all()

    progress = get_progress(apk_id)
    failure = None
    if apk.status == "failed":
        failure = {
            "message": apk.error_message or "Unknown error",
            "phase": progress.get("phase") if progress else None,
            "progress_message": progress.get("message") if progress else None,
            "hint": _failure_hint(apk.error_message or ""),
        }

    return {
        "apk": {
            "id": apk.id,
            "filename": apk.filename,
            "file_hash": apk.file_hash,
            "package_name": apk.package_name,
            "app_name": apk.app_name,
            "status": apk.status,
            "error_message": apk.error_message,
        },
        "failure": failure,
        "analysis": {
            "id": analysis.id if analysis else None,
            "status": analysis.status if analysis else None,
            "type": analysis.analysis_type if analysis else None,
            "risk_score": analysis.risk_score if analysis else None,
            "risk_level": analysis.risk_level if analysis else None,
            "findings": {
                "permissions": safe_list(findings.get("permissions")),
                "urls": safe_list(findings.get("urls")),
                "ips": safe_list(findings.get("ips")),
                "domains": safe_list(findings.get("domains")),
                "certificates": safe_list(findings.get("certificates")),
                "obfuscation": safe_dict(findings.get("obfuscation")),
                "suspicious_apis": findings.get("suspicious_apis") or {},
                "dynamic": safe_dict(findings.get("dynamic")),
                "metadata": safe_dict(findings.get("metadata")),
            },
        },
        "intelligence": intelligence,
        "threat_graph": graph.nodes if graph else intelligence.get("threat_graph", {}),
        "threat_graph_edges": graph.edges if graph else (intelligence.get("threat_graph") or {}).get("edges", []),
        "artifacts": [
            {
                "type": a.artifact_type,
                "value": a.value,
                "suspicious": a.is_suspicious,
                "source": a.source,
            }
            for a in artifacts
        ],
        "threats": [
            {
                "type": t.threat_type,
                "severity": t.severity,
                "description": t.description,
                "is_c2": t.is_c2,
                "c2_domain": t.c2_domain,
            }
            for t in threats
        ],
        "reports": [
            {"id": r.id, "status": r.status, "title": r.title, "created_at": r.created_at}
            for r in reports
        ],
    }

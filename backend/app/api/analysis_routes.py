"""
Analysis Routes
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import logging
import os
from datetime import datetime

from app.db import get_db, Analysis, APKFile
from app.db.background import background_db
from app.analysis.static import StaticAnalyzer, PermissionAnalyzer
from app.ml.risk_scorer import RiskScorer, MalwareClassifier

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/analysis/static/{apk_id}", tags=["Analysis"])
async def run_static_analysis(
    apk_id: str,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
):
    """Run static analysis on APK"""
    try:
        apk = db.query(APKFile).filter(APKFile.id == apk_id).first()
        if not apk:
            raise HTTPException(status_code=404, detail="APK not found")

        if not apk.file_path or not os.path.exists(apk.file_path):
            raise HTTPException(status_code=400, detail="APK file is missing on disk")

        analysis = Analysis(
            apk_id=apk_id,
            analysis_type="static",
            status="pending",
        )
        db.add(analysis)
        apk.status = "analyzing"
        apk.error_message = None
        db.commit()
        db.refresh(analysis)

        if background_tasks:
            background_tasks.add_task(_perform_static_analysis, analysis.id, apk.file_path)

        return {
            "analysis_id": analysis.id,
            "status": "queued",
            "message": "Static analysis queued",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Static analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to queue static analysis")


@router.get("/analysis/{analysis_id}", tags=["Analysis"])
async def get_analysis_results(analysis_id: str, db: Session = Depends(get_db)):
    """Get analysis results"""
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return {
        "id": analysis.id,
        "apk_id": analysis.apk_id,
        "type": analysis.analysis_type,
        "status": analysis.status,
        "risk_score": analysis.risk_score,
        "risk_level": analysis.risk_level,
        "findings": analysis.findings,
        "started_at": analysis.started_at,
        "completed_at": analysis.completed_at,
        "duration": analysis.duration_seconds,
    }


@router.get("/analysis/apk/{apk_id}/latest", tags=["Analysis"])
async def get_latest_analysis(apk_id: str, db: Session = Depends(get_db)):
    """Get the most recent analysis for an APK"""
    apk = db.query(APKFile).filter(APKFile.id == apk_id).first()
    if not apk:
        raise HTTPException(status_code=404, detail="APK not found")

    analysis = (
        db.query(Analysis)
        .filter(Analysis.apk_id == apk_id)
        .order_by(Analysis.created_at.desc())
        .first()
    )

    if not analysis:
        return {
            "apk_id": apk_id,
            "apk_status": apk.status,
            "analysis": None,
            "message": "No analysis has been run yet",
        }

    return {
        "apk_id": apk_id,
        "apk_status": apk.status,
        "error_message": apk.error_message,
        "analysis": {
            "id": analysis.id,
            "type": analysis.analysis_type,
            "status": analysis.status,
            "risk_score": analysis.risk_score,
            "risk_level": analysis.risk_level,
            "started_at": analysis.started_at,
            "completed_at": analysis.completed_at,
        },
    }


@router.post("/analysis/dynamic/{apk_id}", tags=["Analysis"])
async def run_dynamic_analysis(
    apk_id: str,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
):
    """Run dynamic analysis on APK"""
    try:
        apk = db.query(APKFile).filter(APKFile.id == apk_id).first()
        if not apk:
            raise HTTPException(status_code=404, detail="APK not found")

        if not apk.package_name:
            raise HTTPException(
                status_code=400,
                detail="Static analysis must be run first to extract package name",
            )

        analysis = Analysis(
            apk_id=apk_id,
            analysis_type="dynamic",
            status="pending",
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)

        if background_tasks:
            background_tasks.add_task(
                _perform_dynamic_analysis,
                analysis.id,
                apk.file_path,
                apk.package_name,
            )

        return {
            "analysis_id": analysis.id,
            "status": "queued",
            "message": "Dynamic analysis queued (requires Android emulator)",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Dynamic analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to queue dynamic analysis")


@router.get("/analysis/{apk_id}/risk-score", tags=["Analysis"])
async def get_risk_score(apk_id: str, db: Session = Depends(get_db)):
    """Get risk score for APK"""
    apk = db.query(APKFile).filter(APKFile.id == apk_id).first()
    if not apk:
        raise HTTPException(status_code=404, detail="APK not found")

    analyses = db.query(Analysis).filter(Analysis.apk_id == apk_id).all()

    if apk.status == "failed":
        return {
            "apk_id": apk_id,
            "status": "failed",
            "risk_score": None,
            "risk_level": None,
            "classifications": [],
            "confidence": 0,
            "message": apk.error_message or "Analysis failed",
        }

    in_progress = apk.status in ("uploaded", "analyzing") or any(
        a.status in ("pending", "running") for a in analyses
    )
    if in_progress and not any(a.status == "completed" and a.findings for a in analyses):
        return {
            "apk_id": apk_id,
            "status": "pending",
            "risk_score": None,
            "risk_level": None,
            "classifications": [],
            "confidence": 0,
            "message": "Analysis in progress. Check back shortly.",
        }

    completed = [a for a in analyses if a.status == "completed" and a.findings]
    if not completed:
        return {
            "apk_id": apk_id,
            "status": "unavailable",
            "risk_score": None,
            "risk_level": None,
            "classifications": [],
            "confidence": 0,
            "message": "No analysis results available yet",
        }

    combined_findings: dict = {}
    for analysis in completed:
        if analysis.findings:
            combined_findings.update(analysis.findings)

    scorer = RiskScorer()
    risk_score, risk_level = scorer.calculate_risk_score(combined_findings)

    classifier = MalwareClassifier()
    classifications = classifier.classify(combined_findings)

    return {
        "apk_id": apk_id,
        "status": "ready",
        "risk_score": risk_score,
        "risk_level": risk_level,
        "classifications": classifications,
        "confidence": 0.75,
        "message": None,
    }


async def _perform_static_analysis(analysis_id: str, file_path: str):
    """Background task for static analysis"""
    with background_db() as db:
        analysis = None
        try:
            analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
            if not analysis:
                return

            analysis.status = "running"
            analysis.started_at = datetime.utcnow()
            db.commit()

            analyzer = StaticAnalyzer(file_path)
            findings = await analyzer.analyze()

            scorer = RiskScorer()
            risk_score, risk_level = scorer.calculate_risk_score(findings)

            PermissionAnalyzer.analyze_permissions(findings.get("permissions", []))

            analysis.status = "completed"
            analysis.findings = findings
            analysis.risk_score = risk_score
            analysis.risk_level = risk_level
            analysis.completed_at = datetime.utcnow()

            if analysis.started_at:
                delta = analysis.completed_at - analysis.started_at
                analysis.duration_seconds = int(delta.total_seconds())

            apk = db.query(APKFile).filter(APKFile.id == analysis.apk_id).first()
            if apk:
                apk.status = "analyzed"
                apk.error_message = None

            db.commit()
            logger.info(f"Static analysis completed: {analysis_id}")

        except Exception as e:
            logger.error(f"Static analysis error: {str(e)}")
            db.rollback()
            if analysis:
                analysis.status = "failed"
                analysis.completed_at = datetime.utcnow()
                apk = db.query(APKFile).filter(APKFile.id == analysis.apk_id).first()
                if apk:
                    apk.status = "failed"
                    apk.error_message = str(e)
                db.commit()


async def _perform_dynamic_analysis(analysis_id: str, file_path: str, package_name: str):
    """Background task for dynamic analysis"""
    with background_db() as db:
        analysis = None
        try:
            from app.analysis.dynamic import DynamicAnalyzer

            analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
            if not analysis:
                return

            analysis.status = "running"
            analysis.started_at = datetime.utcnow()
            db.commit()

            analyzer = DynamicAnalyzer(file_path, package_name)
            findings = await analyzer.analyze()

            analysis.status = "completed"
            analysis.findings = findings
            analysis.completed_at = datetime.utcnow()

            if analysis.started_at:
                delta = analysis.completed_at - analysis.started_at
                analysis.duration_seconds = int(delta.total_seconds())

            db.commit()
            logger.info(f"Dynamic analysis completed: {analysis_id}")

        except Exception as e:
            logger.error(f"Dynamic analysis error: {str(e)}")
            db.rollback()
            if analysis:
                analysis.status = "failed"
                analysis.completed_at = datetime.utcnow()
                db.commit()

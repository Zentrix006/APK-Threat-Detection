"""
APK Management Routes
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import os
import hashlib
import logging

from app.db import get_db, APKFile, Analysis, ThreatGraph
from app.db.background import background_db
from app.schemas import APKResponse, APKDetailResponse
from app.ml.risk_scorer import RiskScorer
from app.intelligence.engine import InvestigationEngine

logger = logging.getLogger(__name__)
router = APIRouter()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_SIZE_MB", "500")) * 1024 * 1024
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _latest_analysis(db: Session, apk_id: str) -> Analysis | None:
    return (
        db.query(Analysis)
        .filter(Analysis.apk_id == apk_id)
        .order_by(Analysis.created_at.desc())
        .first()
    )


def _apk_risk_from_analyses(db: Session, apk_id: str) -> tuple[float | None, str | None]:
    analyses = (
        db.query(Analysis)
        .filter(Analysis.apk_id == apk_id, Analysis.status == "completed")
        .all()
    )
    if not analyses:
        return None, None

    combined: dict = {}
    for analysis in analyses:
        if analysis.findings:
            combined.update(analysis.findings)

    if not combined:
        latest = analyses[0]
        if latest.risk_score is not None:
            return latest.risk_score, latest.risk_level
        return None, None

    scorer = RiskScorer()
    score, level = scorer.calculate_risk_score(combined)
    return score, level


@router.post("/apks/upload", response_model=APKResponse, tags=["APK Management"])
async def upload_apk(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
):
    """Upload APK file for analysis"""
    try:
        if not file.filename or not file.filename.lower().endswith(".apk"):
            raise HTTPException(status_code=400, detail="Only .apk files are allowed")

        content = await file.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        if len(content) > MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"File exceeds maximum size of {MAX_UPLOAD_BYTES // (1024 * 1024)} MB",
            )

        file_hash = hashlib.sha256(content).hexdigest()

        existing_apk = db.query(APKFile).filter(APKFile.file_hash == file_hash).first()
        if existing_apk:
            return APKResponse(
                id=existing_apk.id,
                filename=existing_apk.filename,
                file_hash=file_hash,
                status=existing_apk.status,
                message="This APK has already been uploaded",
            )

        file_path = os.path.join(UPLOAD_DIR, file_hash[:16] + ".apk")
        with open(file_path, "wb") as f:
            f.write(content)

        apk = APKFile(
            filename=file.filename,
            file_hash=file_hash,
            file_size=len(content),
            file_path=file_path,
            status="uploaded",
            error_message=None,
        )
        db.add(apk)
        db.commit()
        db.refresh(apk)

        if background_tasks:
            background_tasks.add_task(_analyze_apk, apk.id, file_path)

        logger.info(f"APK uploaded: {file.filename} ({file_hash})")

        return APKResponse(
            id=apk.id,
            filename=apk.filename,
            file_hash=file_hash,
            status="uploaded",
            message="APK uploaded successfully. Analysis started.",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Upload failed. Please try again later.")


@router.get("/apks/stats", tags=["APK Management"])
async def get_apk_stats(db: Session = Depends(get_db)):
    """Dashboard aggregate statistics"""
    total = db.query(APKFile).count()
    failed = db.query(APKFile).filter(APKFile.status == "failed").count()

    completed_analyses = (
        db.query(Analysis)
        .filter(Analysis.status == "completed", Analysis.risk_score.isnot(None))
        .all()
    )

    scores = [a.risk_score for a in completed_analyses if a.risk_score is not None]
    avg_risk = round(sum(scores) / len(scores), 1) if scores else 0

    critical = sum(1 for a in completed_analyses if (a.risk_level or "").lower() == "critical")
    high = sum(1 for a in completed_analyses if (a.risk_level or "").lower() == "high")

    return {
        "total_apks": total,
        "failed_apks": failed,
        "avg_risk_score": avg_risk,
        "critical_threats": critical + high,
        "analyzed_count": len(completed_analyses),
    }


@router.get("/apks/{apk_id}", response_model=APKDetailResponse, tags=["APK Management"])
async def get_apk(apk_id: str, db: Session = Depends(get_db)):
    """Get APK details"""
    apk = db.query(APKFile).filter(APKFile.id == apk_id).first()
    if not apk:
        raise HTTPException(status_code=404, detail="APK not found")

    analyses = db.query(Analysis).filter(Analysis.apk_id == apk_id).all()
    latest = _latest_analysis(db, apk_id)
    risk_score, risk_level = _apk_risk_from_analyses(db, apk_id)

    return APKDetailResponse(
        id=apk.id,
        filename=apk.filename,
        file_hash=apk.file_hash,
        file_size=apk.file_size,
        package_name=apk.package_name,
        app_name=apk.app_name,
        version_code=apk.version_code,
        version_name=apk.version_name,
        status=apk.status,
        error_message=apk.error_message,
        upload_date=apk.upload_date,
        analysis_count=len(analyses),
        latest_analysis_status=latest.status if latest else None,
        risk_level=risk_level,
        risk_score=risk_score,
        created_at=apk.created_at,
    )


@router.get("/apks", tags=["APK Management"])
async def list_apks(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """List uploaded APKs"""
    apks = (
        db.query(APKFile)
        .order_by(APKFile.upload_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    items = []
    for apk in apks:
        try:
            _, risk_level = _apk_risk_from_analyses(db, apk.id)
        except Exception:
            risk_level = None
        items.append(
            {
                "id": apk.id,
                "filename": apk.filename,
                "file_hash": apk.file_hash,
                "status": apk.status,
                "upload_date": apk.upload_date,
                "risk_level": risk_level or "unknown",
                "error_message": apk.error_message,
            }
        )

    return {
        "total": db.query(APKFile).count(),
        "skip": skip,
        "limit": limit,
        "apks": items,
    }


@router.delete("/apks/{apk_id}", tags=["APK Management"])
async def delete_apk(apk_id: str, db: Session = Depends(get_db)):
    """Delete APK and associated data"""
    apk = db.query(APKFile).filter(APKFile.id == apk_id).first()
    if not apk:
        raise HTTPException(status_code=404, detail="APK not found")

    file_path = apk.file_path

    try:
        db.query(ThreatGraph).filter(
            ThreatGraph.apk_id == apk_id
        ).delete(synchronize_session=False)

        db.commit()

        db.delete(apk)
        db.commit()

        if file_path and os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        db.rollback()
        logger.exception(f"Failed to delete APK {apk_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to delete APK. Please try again later.",
        )

    return {"message": "APK deleted successfully"}


async def _analyze_apk(apk_id: str, file_path: str):
    """Background task: full autonomous investigation pipeline."""
    with background_db() as db:
        from app.services.progress import get_progress, set_progress

        try:
            logger.info(f"Starting investigation for APK: {apk_id}")
            await InvestigationEngine.run_full_investigation(db, apk_id, file_path)
        except Exception as e:
            logger.exception(f"Investigation failed for {apk_id}: {e}")
            db.rollback()
            phase = (get_progress(apk_id) or {}).get("phase", "unknown")
            apk = db.query(APKFile).filter(APKFile.id == apk_id).first()
            if apk:
                apk.status = "failed"
                apk.error_message = f"[{phase}] {type(e).__name__}: {e}"
                db.commit()
            set_progress(
                apk_id,
                "failed",
                f"Investigation failed during {phase}: {e}",
                100,
            )


@router.post("/apks/{apk_id}/retry-investigation", tags=["APK Management"])
async def retry_investigation(
    apk_id: str,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
):
    """Re-run investigation for a failed or incomplete APK."""
    apk = db.query(APKFile).filter(APKFile.id == apk_id).first()
    if not apk:
        raise HTTPException(status_code=404, detail="APK not found")
    if not apk.file_path or not os.path.exists(apk.file_path):
        raise HTTPException(status_code=400, detail="APK file missing on disk; upload again")

    apk.status = "uploaded"
    apk.error_message = None
    db.commit()

    if background_tasks:
        background_tasks.add_task(_analyze_apk, apk.id, apk.file_path)

    return {
        "id": apk.id,
        "status": "uploaded",
        "message": "Investigation re-queued",
    }

"""
Report Generation Routes
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import logging
import os
from datetime import datetime

from app.db import get_db, Report, Analysis, APKFile
from app.db.background import background_db
from app.ai.report_generator import generate_comprehensive_report
from app.reporting.pdf_generator import PDFReportGenerator

logger = logging.getLogger(__name__)
router = APIRouter()

REPORTS_DIR = os.getenv("REPORTS_DIR", "./reports")
os.makedirs(REPORTS_DIR, exist_ok=True)


@router.post("/reports/generate/{apk_id}", tags=["Reports"])
async def generate_report(
    apk_id: str,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """Generate threat intelligence report"""
    try:
        apk = db.query(APKFile).filter(APKFile.id == apk_id).first()
        if not apk:
            raise HTTPException(status_code=404, detail="APK not found")
        
        # Get latest analysis
        analysis = db.query(Analysis).filter(
            Analysis.apk_id == apk_id
        ).order_by(Analysis.created_at.desc()).first()
        
        if not analysis or not analysis.findings:
            raise HTTPException(
                status_code=400,
                detail="Run investigation first before generating report",
            )

        findings = dict(analysis.findings)
        findings["risk_score"] = analysis.risk_score
        findings["risk_level"] = analysis.risk_level
        
        # Create report record
        report = Report(
            apk_id=apk_id,
            report_type="executive_summary",
            status="pending"
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        
        if background_tasks:
            background_tasks.add_task(
                _generate_report,
                report.id,
                apk.filename,
                findings,
            )
        
        return {
            "report_id": report.id,
            "status": "queued",
            "message": "Report generation started"
        }
    except Exception as e:
        logger.error(f"Report generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/{report_id}", tags=["Reports"])
async def get_report(report_id: str, db: Session = Depends(get_db)):
    """Get report details"""
    report = db.query(Report).filter(Report.id == report_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return {
        "id": report.id,
        "apk_id": report.apk_id,
        "type": report.report_type,
        "status": report.status,
        "title": report.title,
        "summary": report.summary,
        "created_at": report.created_at,
        "updated_at": report.updated_at,
        "pdf_available": bool(report.pdf_path)
    }


@router.get("/reports/{report_id}/download", tags=["Reports"])
async def download_report(report_id: str, db: Session = Depends(get_db)):
    """Download report as PDF"""
    report = db.query(Report).filter(Report.id == report_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if not report.pdf_path or not os.path.exists(report.pdf_path):
        raise HTTPException(status_code=400, detail="PDF not available")
    
    return FileResponse(
        report.pdf_path,
        filename=f"threat_report_{report.id}.pdf"
    )


@router.get("/reports/apk/{apk_id}", tags=["Reports"])
async def list_reports(apk_id: str, db: Session = Depends(get_db)):
    """List all reports for an APK"""
    reports = db.query(Report).filter(Report.apk_id == apk_id).all()
    
    return {
        "apk_id": apk_id,
        "total": len(reports),
        "reports": [
            {
                "id": r.id,
                "type": r.report_type,
                "status": r.status,
                "created_at": r.created_at,
                "ai_generated": r.ai_generated
            }
            for r in reports
        ]
    }


async def _generate_report(report_id: str, apk_name: str, analysis_findings: dict):
    """Background task to generate report"""
    with background_db() as db:
        report = None
        try:
            report = db.query(Report).filter(Report.id == report_id).first()
            if not report:
                return

            report.status = "generating"
            db.commit()

            report_data = await generate_comprehensive_report(
                analysis_findings,
                apk_name,
            )

            report.title = report_data.get("title")
            report.summary = report_data.get("ai_report", "")[:500]
            report.content = str(report_data)
            report.ai_generated = True
            report.generated_by = "qwen3"

            pdf_generator = PDFReportGenerator()
            pdf_path = os.path.join(REPORTS_DIR, f"{report_id}.pdf")
            pdf_generator.generate(report_data, pdf_path)
            report.pdf_path = pdf_path

            report.status = "completed"
            db.commit()

            logger.info(f"Report generated: {report_id}")

        except Exception as e:
            logger.error(f"Report generation error: {str(e)}")
            db.rollback()
            if report:
                report.status = "failed"
                db.commit()

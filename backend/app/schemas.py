"""
Pydantic schemas for API requests/responses
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any


class APKResponse(BaseModel):
    id: str
    filename: str
    file_hash: str
    status: str
    message: Optional[str] = None


class APKDetailResponse(BaseModel):
    id: str
    filename: str
    file_hash: str
    file_size: int
    package_name: Optional[str] = None
    app_name: Optional[str] = None
    version_code: Optional[str] = None
    version_name: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    upload_date: datetime
    analysis_count: int
    latest_analysis_status: Optional[str] = None
    risk_level: Optional[str] = None
    risk_score: Optional[float] = None
    created_at: datetime


class AnalysisResponse(BaseModel):
    id: str
    apk_id: str
    analysis_type: str
    status: str
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None
    findings: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration: Optional[int] = None


class RiskScoreResponse(BaseModel):
    apk_id: str
    risk_score: float
    risk_level: str
    classifications: List[Dict[str, Any]]
    confidence: float


class ReportResponse(BaseModel):
    id: str
    apk_id: str
    report_type: str
    status: str
    title: Optional[str] = None
    summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    pdf_available: bool


class ThreatResponse(BaseModel):
    type: str
    indicator: str
    confidence: float
    description: Optional[str] = None

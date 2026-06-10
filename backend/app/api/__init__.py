"""
API Routes Package
"""

from .apk_routes import router as apk_router
from .analysis_routes import router as analysis_router
from .report_routes import router as report_router

__all__ = ["apk_router", "analysis_router", "report_router"]

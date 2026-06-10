"""
Main FastAPI Application
"""

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import logging
import os
from datetime import datetime, timezone

from app.db import init_db, get_db
from app.api import apk_routes, analysis_routes, report_routes, intelligence_routes

# Configure logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting APK Threat Intelligence Platform...")
    init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")

app = FastAPI(
    title="APK Threat Intelligence Platform",
    description="Advanced APK analysis and threat detection system",
    version="1.0.0",
    lifespan=lifespan
)

# Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost,http://127.0.0.1",
    ).split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health Check
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0"
    }

# ADDED: Native Config Endpoint to handle frontend telemetry initialization handshake
@app.get("/api/v1/config", tags=["Configuration"])
async def get_frontend_config():
    """Provides configuration metadata for the Next.js frontend initialization"""
    return {
        "status": "active",
        "version": "1.0.0",
        "environment": os.getenv("DEBUG", "false").lower() == "true" and "development" or "production",
        "settings": {
            "allow_uploads": True,
            "max_file_size_mb": int(os.getenv("MAX_UPLOAD_SIZE_MB", "500")),
            "supported_extensions": [".apk"],
            "features": [
                "static_analysis",
                "dynamic_analysis",
                "ai_reasoning",
                "threat_graph",
                "malware_story",
                "digital_twin",
                "fraud_impact",
                "mitre_attack",
                "soc_reports",
            ],
        },
    }

# Include routers
app.include_router(apk_routes.router, prefix="/api/v1", tags=["APK"])
app.include_router(analysis_routes.router, prefix="/api/v1", tags=["Analysis"])
app.include_router(report_routes.router, prefix="/api/v1", tags=["Reports"])
app.include_router(intelligence_routes.router, prefix="/api/v1", tags=["Investigation"])

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """API Documentation"""
    return {
        "name": "APK Threat Intelligence Platform",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "endpoints": {
            "apks": "/api/v1/apks",
            "analysis": "/api/v1/analysis",
            "reports": "/api/v1/reports",
            "config": "/api/v1/config",
            "health": "/health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv("DEBUG", "false").lower() == "true"
    )
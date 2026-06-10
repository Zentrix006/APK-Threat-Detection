from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, JSON, ForeignKey, LargeBinary, Enum
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import enum
import uuid

Base = declarative_base()

class APKFile(Base):
    __tablename__ = "apk_files"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False, index=True)
    file_hash = Column(String, unique=True, nullable=False, index=True)
    file_size = Column(Integer, nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # APK Metadata
    package_name = Column(String, nullable=True, index=True)
    app_name = Column(String, nullable=True)
    version_code = Column(String, nullable=True)
    version_name = Column(String, nullable=True)
    min_sdk = Column(Integer, nullable=True)
    target_sdk = Column(Integer, nullable=True)
    
    # Storage
    file_path = Column(String, nullable=False)
    
    # Status
    status = Column(String, default="uploaded", nullable=False)  # uploaded, analyzing, completed, failed
    error_message = Column(Text, nullable=True)
    
    # Relationships
    analyses = relationship("Analysis", back_populates="apk_file", cascade="all, delete-orphan")
    artifacts = relationship("Artifact", back_populates="apk_file", cascade="all, delete-orphan")
    threats = relationship("Threat", back_populates="apk_file", cascade="all, delete-orphan")
    threat_graphs = relationship("ThreatGraph", back_populates="apk_file", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="apk_file", cascade="all, delete-orphan")
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    apk_id = Column(String, ForeignKey("apk_files.id"), nullable=False, index=True)
    
    analysis_type = Column(String, nullable=False)  # static, dynamic, hybrid
    status = Column(String, default="pending", nullable=False)  # pending, running, completed, failed
    
    # Results
    findings = Column(JSON, nullable=True)
    risk_score = Column(Float, nullable=True)
    risk_level = Column(String, nullable=True)  # critical, high, medium, low
    
    # Execution Details
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    # Relationships
    apk_file = relationship("APKFile", back_populates="analyses")
    detections = relationship("Detection", back_populates="analysis", cascade="all, delete-orphan")
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Detection(Base):
    __tablename__ = "detections"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = Column(String, ForeignKey("analyses.id"), nullable=False, index=True)
    
    detection_type = Column(String, nullable=False)  # malware, suspicious, benign
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)
    
    # MITRE ATT&CK Mapping
    mitre_tactics = Column(JSON, nullable=True)  # [{"tactic": "...", "technique": "..."}]
    
    # Relationships
    analysis = relationship("Analysis", back_populates="detections")
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Artifact(Base):
    __tablename__ = "artifacts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    apk_id = Column(String, ForeignKey("apk_files.id"), nullable=False, index=True)
    
    artifact_type = Column(String, nullable=False, index=True)  # url, ip, domain, permission, intent_filter
    value = Column(String, nullable=False, index=True)
    
    # Context
    source = Column(String, nullable=True)  # where it was found (manifest, code, dynamic)
    frequency = Column(Integer, default=1)
    is_suspicious = Column(Boolean, default=False)
    
    # Relationships
    apk_file = relationship("APKFile", back_populates="artifacts")
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Threat(Base):
    __tablename__ = "threats"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    apk_id = Column(String, ForeignKey("apk_files.id"), nullable=False, index=True)
    
    threat_type = Column(String, nullable=False)  # malware, trojan, adware, pua, etc.
    description = Column(Text, nullable=True)
    severity = Column(String, nullable=False)  # critical, high, medium, low
    
    # C2 Communication
    is_c2 = Column(Boolean, default=False)
    c2_protocol = Column(String, nullable=True)  # http, https, dns, tcp, etc.
    c2_domain = Column(String, nullable=True)
    c2_ip = Column(String, nullable=True)
    c2_port = Column(Integer, nullable=True)
    
    # Relationships
    apk_file = relationship("APKFile", back_populates="threats")
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class ThreatGraph(Base):
    __tablename__ = "threat_graphs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    apk_id = Column(
        String,
        ForeignKey("apk_files.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Graph nodes and edges
    nodes = Column(JSON, nullable=False)  # [{id, type, label, data}, ...]
    edges = Column(JSON, nullable=False)  # [{source, target, type, label}, ...]
    
    # Metadata
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    apk_file = relationship("APKFile", back_populates="threat_graphs")


class Report(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    apk_id = Column(String, ForeignKey("apk_files.id"), nullable=False, index=True)
    
    report_type = Column(String, nullable=False)  # static, dynamic, executive_summary
    status = Column(String, default="pending", nullable=False)  # pending, generating, completed, failed
    
    # Content
    title = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=True)  # JSON or HTML
    
    # Files
    pdf_path = Column(String, nullable=True)
    json_path = Column(String, nullable=True)
    
    # Metadata
    ai_generated = Column(Boolean, default=False)
    generated_by = Column(String, nullable=True)  # ollama, qwen3, manual

    # Relationships
    apk_file = relationship("APKFile", back_populates="reports")
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class MLModel(Base):
    __tablename__ = "ml_models"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    model_name = Column(String, nullable=False, unique=True)
    model_type = Column(String, nullable=False)  # risk_scorer, classifier
    version = Column(String, nullable=False)
    
    # Performance metrics
    accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    
    # Storage
    model_path = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Training info
    trained_at = Column(DateTime, nullable=False)
    training_samples = Column(Integer, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Cache(Base):
    __tablename__ = "cache"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    cache_key = Column(String, unique=True, nullable=False, index=True)
    cache_value = Column(JSON, nullable=False)
    
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

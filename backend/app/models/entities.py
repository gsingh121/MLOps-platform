import enum
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Enum, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base

class LifecycleStage(str, enum.Enum):
    DRAFT = "DRAFT"
    VALIDATED = "VALIDATED"
    APPROVED = "APPROVED"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"
    ARCHIVED = "ARCHIVED"

class DeploymentState(str, enum.Enum):
    REQUESTED = "REQUESTED"
    VALIDATING = "VALIDATING"
    DEPLOYING = "DEPLOYING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"

class MLModel(Base):
    __tablename__ = "ml_models"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(128), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    tags = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    versions = relationship("ModelVersion", back_populates="model", cascade="all, delete-orphan")

class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(String(64), primary_key=True, index=True)
    model_id = Column(String(64), ForeignKey("ml_models.id"), nullable=False)
    version = Column(String(32), nullable=False)
    framework = Column(String(64), nullable=False)
    algorithm = Column(String(64), nullable=False)
    artifact_uri = Column(String(512), nullable=False)
    training_data_ref = Column(String(256), nullable=False)
    stage = Column(Enum(LifecycleStage), default=LifecycleStage.DRAFT, nullable=False)
    is_approved = Column(Integer, default=0, nullable=False)
    metadata_info = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    model = relationship("MLModel", back_populates="versions")
    deployments = relationship("Deployment", back_populates="model_version")
    metrics = relationship("ModelMetric", back_populates="model_version")

class Deployment(Base):
    __tablename__ = "deployments"

    id = Column(String(64), primary_key=True, index=True)
    version_id = Column(String(64), ForeignKey("model_versions.id"), nullable=False)
    environment = Column(String(32), nullable=False)
    state = Column(Enum(DeploymentState), default=DeploymentState.REQUESTED, nullable=False)
    idempotency_key = Column(String(128), unique=True, index=True, nullable=True)
    error_message = Column(Text, nullable=True)
    previous_deployment_id = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    model_version = relationship("ModelVersion", back_populates="deployments")

class ModelMetric(Base):
    __tablename__ = "model_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    version_id = Column(String(64), ForeignKey("model_versions.id"), nullable=False)
    prediction_latency_ms = Column(Float, nullable=False)
    throughput_qps = Column(Float, nullable=False)
    error_rate = Column(Float, nullable=False)
    quality_score = Column(Float, nullable=False)
    drift_score = Column(Float, nullable=False)
    availability = Column(Float, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow)

    model_version = relationship("ModelVersion", back_populates="metrics")

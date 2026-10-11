from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models.entities import LifecycleStage, DeploymentState

class ModelCreate(BaseModel):
    id: str = Field(..., description="Unique model identifier")
    name: str
    description: Optional[str] = None
    tags: List[str] = []

class VersionCreate(BaseModel):
    version: str
    framework: str
    algorithm: str
    artifact_uri: str
    training_data_ref: str
    metadata_info: Dict[str, Any] = {}

class VersionApproval(BaseModel):
    is_approved: bool
    stage: LifecycleStage

class DeploymentRequest(BaseModel):
    version_id: str
    environment: str
    idempotency_key: Optional[str] = None
    simulate_failure: bool = False

class DeploymentResponse(BaseModel):
    id: str
    version_id: str
    environment: str
    state: DeploymentState
    idempotency_key: Optional[str]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MetricResponse(BaseModel):
    prediction_latency_ms: float
    throughput_qps: float
    error_rate: float
    quality_score: float
    drift_score: float
    availability: float
    recorded_at: datetime

    class Config:
        from_attributes = True

import uuid
import time
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import engine, Base, get_db
from app.models.entities import MLModel, ModelVersion, Deployment, ModelMetric
from app.schemas.domain import (
    ModelCreate, VersionCreate, VersionApproval, DeploymentRequest, DeploymentResponse, MetricResponse
)
from app.services.mlops_service import MLOpsService
from app.core.logging_config import setup_logging

logger = setup_logging()
app = FastAPI(title="MLOps Platform API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def correlation_and_logging_middleware(request: Request, call_next):
    corr_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    response.headers["X-Correlation-ID"] = corr_id
    logger.info("HTTP Request completed", extra={
        "correlation_id": corr_id,
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "latency_ms": round(duration * 1000, 2)
    })
    return response

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/health")
async def health():
    return {"status": "healthy", "database": "connected"}

@app.post("/models", status_code=201)
async def create_model(payload: ModelCreate, db: AsyncSession = Depends(get_db)):
    return await MLOpsService.create_model(db, payload)

@app.get("/models")
async def list_models(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MLModel))
    return result.scalars().all()

@app.get("/models/{model_id}")
async def get_model(model_id: str, db: AsyncSession = Depends(get_db)):
    model = await db.get(MLModel, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model

@app.post("/models/{model_id}/versions", status_code=201)
async def create_version(model_id: str, payload: VersionCreate, db: AsyncSession = Depends(get_db)):
    return await MLOpsService.add_version(db, model_id, payload)

@app.get("/models/{model_id}/versions")
async def list_versions(model_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ModelVersion).where(ModelVersion.model_id == model_id))
    return result.scalars().all()

@app.patch("/models/versions/{version_id}/approve")
async def approve_version(version_id: str, payload: VersionApproval, db: AsyncSession = Depends(get_db)):
    return await MLOpsService.approve_version(db, version_id, payload)

@app.post("/deployments", response_model=DeploymentResponse, status_code=201)
async def deploy(payload: DeploymentRequest, db: AsyncSession = Depends(get_db)):
    return await MLOpsService.create_deployment(db, payload)

@app.get("/deployments", response_model=list[DeploymentResponse])
async def list_deployments(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Deployment).order_by(Deployment.created_at.desc()))
    return result.scalars().all()

@app.post("/deployments/{deployment_id}/retry", response_model=DeploymentResponse, status_code=201)
async def retry_deployment(deployment_id: str, db: AsyncSession = Depends(get_db)):
    dep = await db.get(Deployment, deployment_id)
    if not dep:
        raise HTTPException(status_code=404, detail="Deployment not found")
    retry_req = DeploymentRequest(version_id=dep.version_id, environment=dep.environment)
    return await MLOpsService.create_deployment(db, retry_req)

@app.post("/deployments/{deployment_id}/rollback", response_model=DeploymentResponse)
async def rollback_deployment(deployment_id: str, db: AsyncSession = Depends(get_db)):
    return await MLOpsService.rollback(db, deployment_id)

@app.get("/models/{model_id}/metrics", response_model=list[MetricResponse])
async def get_metrics(model_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(ModelMetric).join(ModelVersion).where(ModelVersion.model_id == model_id)
    result = await db.execute(stmt)
    return result.scalars().all()

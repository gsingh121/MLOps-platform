import uuid
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from app.models.entities import MLModel, ModelVersion, Deployment, ModelMetric, LifecycleStage, DeploymentState
from app.schemas.domain import ModelCreate, VersionCreate, VersionApproval, DeploymentRequest

class MLOpsService:
    @staticmethod
    async def create_model(db: AsyncSession, data: ModelCreate):
        existing = await db.get(MLModel, data.id)
        if existing:
            raise HTTPException(status_code=409, detail=f'Model {data.id} already exists')
        model = MLModel(**data.model_dump())
        db.add(model)
        await db.commit()
        await db.refresh(model)
        return model

    @staticmethod
    async def add_version(db: AsyncSession, model_id: str, data: VersionCreate):
        model = await db.get(MLModel, model_id)
        if not model:
            raise HTTPException(status_code=404, detail='Model not found')
        v_id = f'{model_id}-{data.version}'
        version = ModelVersion(id=v_id, model_id=model_id, **data.model_dump())
        db.add(version)
        await db.commit()
        await db.refresh(version)
        return version

    @staticmethod
    async def approve_version(db: AsyncSession, version_id: str, approval: VersionApproval):
        version = await db.get(ModelVersion, version_id)
        if not version:
            raise HTTPException(status_code=404, detail='Version not found')
        
        version.is_approved = 1 if approval.is_approved else 0
        version.stage = approval.stage
        await db.commit()
        await db.refresh(version)
        return version

    @staticmethod
    async def create_deployment(db: AsyncSession, data: DeploymentRequest):
        if data.idempotency_key:
            stmt = select(Deployment).where(Deployment.idempotency_key == data.idempotency_key)
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            if existing:
                return existing

        version = await db.get(ModelVersion, data.version_id)
        if not version:
            raise HTTPException(status_code=404, detail='Version not found')

        if data.environment.upper() == 'PRODUCTION':
            if not version.is_approved or version.stage != LifecycleStage.APPROVED:
                raise HTTPException(
                    status_code=422,
                    detail='Governance Violation: Only APPROVED versions can be deployed to PRODUCTION'
                )

        dep_id = f'dep-{uuid.uuid4().hex[:8]}'
        deployment = Deployment(
            id=dep_id,
            version_id=data.version_id,
            environment=data.environment.upper(),
            state=DeploymentState.REQUESTED,
            idempotency_key=data.idempotency_key
        )
        db.add(deployment)
        await db.commit()
        await db.refresh(deployment)

        asyncio.create_task(MLOpsService._execute_deployment_workflow(dep_id, data.simulate_failure))
        return deployment

    @staticmethod
    async def _execute_deployment_workflow(deployment_id: str, simulate_failure: bool):
        from app.db.session import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            dep = await session.get(Deployment, deployment_id)
            if not dep:
                return
            dep.state = DeploymentState.DEPLOYING
            await session.commit()
            
            await asyncio.sleep(2)
            
            if simulate_failure:
                dep.state = DeploymentState.FAILED
                dep.error_message = 'Runtime deployment failed: Container health check timeout.'
            else:
                dep.state = DeploymentState.SUCCEEDED
                metric = ModelMetric(
                    version_id=dep.version_id,
                    prediction_latency_ms=18.4,
                    throughput_qps=420.0,
                    error_rate=0.002,
                    quality_score=0.94,
                    drift_score=0.012,
                    availability=99.99
                )
                session.add(metric)
            await session.commit()

    @staticmethod
    async def rollback(db: AsyncSession, deployment_id: str):
        target = await db.get(Deployment, deployment_id)
        if not target:
            raise HTTPException(status_code=404, detail='Deployment not found')
        if target.environment != 'PRODUCTION':
            raise HTTPException(status_code=400, detail='Rollback is only permitted in PRODUCTION')
        
        target.state = DeploymentState.ROLLED_BACK
        await db.commit()
        await db.refresh(target)
        return target

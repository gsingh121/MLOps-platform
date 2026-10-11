import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.session import Base, engine

@pytest_asyncio.fixture(autouse=True)
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield

@pytest.mark.asyncio
async def test_full_mlops_lifecycle_scenarios():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.post("/models", json={"id": "predictive-maintenance", "name": "Pump Failure Predictor"})
        assert res.status_code == 201

        v1_res = await ac.post("/models/predictive-maintenance/versions", json={
            "version": "1.0.0", "framework": "scikit-learn", "algorithm": "RandomForest",
            "artifact_uri": "s3://models/v1.tar.gz", "training_data_ref": "snowflake://data/v1"
        })
        assert v1_res.status_code == 201

        v2_res = await ac.post("/models/predictive-maintenance/versions", json={
            "version": "2.0.0", "framework": "xgboost", "algorithm": "GradientBoostedTrees",
            "artifact_uri": "s3://models/v2.tar.gz", "training_data_ref": "snowflake://data/v2"
        })
        assert v2_res.status_code == 201

        appr_res = await ac.patch("/models/versions/predictive-maintenance-1.0.0/approve", json={
            "is_approved": True, "stage": "APPROVED"
        })
        assert appr_res.status_code == 200

        unappr_dep = await ac.post("/deployments", json={
            "version_id": "predictive-maintenance-2.0.0", "environment": "PRODUCTION"
        })
        assert unappr_dep.status_code == 422

        appr_dep = await ac.post("/deployments", json={
            "version_id": "predictive-maintenance-1.0.0", "environment": "PRODUCTION", "idempotency_key": "tx-123"
        })
        assert appr_dep.status_code == 201
        dep_id = appr_dep.json()["id"]

        dup_dep = await ac.post("/deployments", json={
            "version_id": "predictive-maintenance-1.0.0", "environment": "PRODUCTION", "idempotency_key": "tx-123"
        })
        assert dup_dep.status_code == 201
        assert dup_dep.json()["id"] == dep_id

        rb_res = await ac.post(f"/deployments/{dep_id}/rollback")
        assert rb_res.status_code == 200
        assert rb_res.json()["state"] == "ROLLED_BACK"

        fail_dep = await ac.post("/deployments", json={
            "version_id": "predictive-maintenance-1.0.0", "environment": "STAGING", "simulate_failure": True
        })
        fail_id = fail_dep.json()["id"]
        retry_res = await ac.post(f"/deployments/{fail_id}/retry")
        assert retry_res.status_code == 201

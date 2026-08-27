import uuid
import pytest
from sqlalchemy import select

from packages.domain.database import AsyncSessionLocal
from packages.domain.entities import (
    User, Project, GenerationRequest, GenerationJob, JobStatus,
    GenerationPlan, Scene, MediaAsset, Render
)
from packages.generation.orchestrator import PipelineOrchestrator
from packages.providers import DevMockLLMProvider, DevMockMediaProvider
from packages.generation import GenerationPlanner
from services.worker.main import WorkerProcess


async def is_db_available() -> bool:
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(select(1))
            return True
    except Exception:
        return False


@pytest.mark.asyncio
async def test_successful_pipeline_execution():
    """Test full pipeline execution from QUEUED to COMPLETED."""
    if not await is_db_available():
        pytest.skip("PostgreSQL database is not reachable.")

    async with AsyncSessionLocal() as db_session:
        # 1. Setup User and Project
        user = User(
            email=f"orchestrator_test_{uuid.uuid4().hex[:6]}@example.com",
            hashed_password="hashed_pass_123",
            is_active=True
        )
        db_session.add(user)
        await db_session.flush()

        project = Project(user_id=user.id, name="Pipeline Test Project")
        db_session.add(project)
        await db_session.flush()

        # 2. Setup GenerationRequest & GenerationJob in QUEUED status
        gen_req = GenerationRequest(
            project_id=project.id,
            user_id=user.id,
            prompt="A vibrant Cyberpunk cityscape with glowing holographic billboards",
            style="cyberpunk",
            target_duration_seconds=15,
            aspect_ratio="16:9"
        )
        db_session.add(gen_req)
        await db_session.flush()

        job = GenerationJob(
            generation_request_id=gen_req.id,
            project_id=project.id,
            status=JobStatus.QUEUED,
            current_stage="INIT",
            progress_percentage=0
        )
        db_session.add(job)
        await db_session.commit()

        # 3. Execute Pipeline Orchestrator with Dev Mocks
        planner = GenerationPlanner(provider=DevMockLLMProvider())
        media_provider = DevMockMediaProvider()
        orchestrator = PipelineOrchestrator(planner=planner, media_provider=media_provider)

        completed_job = await orchestrator.execute_job(job.id, db_session)

        # 4. Assertions
        assert completed_job.status == JobStatus.COMPLETED
        assert completed_job.progress_percentage == 100
        assert completed_job.current_stage == "COMPLETED"

        # Verify GenerationPlan created
        plan_res = await db_session.execute(select(GenerationPlan).where(GenerationPlan.generation_request_id == gen_req.id))
        plan = plan_res.scalar_one_or_none()
        assert plan is not None

        # Verify Scenes created
        scenes_res = await db_session.execute(select(Scene).where(Scene.generation_plan_id == plan.id))
        scenes = scenes_res.scalars().all()
        assert len(scenes) == 3

        # Verify MediaAssets created (3 images + 3 audio clips)
        assets_res = await db_session.execute(select(MediaAsset).where(MediaAsset.project_id == project.id))
        assets = assets_res.scalars().all()
        assert len(assets) == 6

        # Verify Render created
        render_res = await db_session.execute(select(Render).where(Render.job_id == job.id))
        render = render_res.scalar_one_or_none()
        assert render is not None
        assert render.format == "mp4"


@pytest.mark.asyncio
async def test_stage_visual_failure():
    """Test pipeline failure when visual asset generation fails."""
    if not await is_db_available():
        pytest.skip("PostgreSQL database is not reachable.")

    async with AsyncSessionLocal() as db_session:
        user = User(
            email=f"fail_test_{uuid.uuid4().hex[:6]}@example.com",
            hashed_password="hashed_pass_123",
            is_active=True
        )
        db_session.add(user)
        await db_session.flush()

        project = Project(user_id=user.id, name="Failure Test Project")
        db_session.add(project)
        await db_session.flush()

        gen_req = GenerationRequest(
            project_id=project.id,
            user_id=user.id,
            prompt="Test visual failure scene",
            style="cinematic"
        )
        db_session.add(gen_req)
        await db_session.flush()

        job = GenerationJob(
            generation_request_id=gen_req.id,
            project_id=project.id,
            status=JobStatus.QUEUED
        )
        db_session.add(job)
        await db_session.commit()

        failing_media_provider = DevMockMediaProvider(force_visual_failure=True)
        orchestrator = PipelineOrchestrator(
            planner=GenerationPlanner(provider=DevMockLLMProvider()),
            media_provider=failing_media_provider
        )

        with pytest.raises(Exception):
            await orchestrator.execute_job(job.id, db_session)

        job_res = await db_session.execute(select(GenerationJob).where(GenerationJob.id == job.id))
        failed_job = job_res.scalar_one()
        assert failed_job.status == JobStatus.FAILED
        assert failed_job.error_code == "PIPELINE_ERROR"


@pytest.mark.asyncio
async def test_job_cancellation_during_execution():
    """Test job cancellation mid-execution stops processing cleanly."""
    if not await is_db_available():
        pytest.skip("PostgreSQL database is not reachable.")

    async with AsyncSessionLocal() as db_session:
        user = User(
            email=f"cancel_test_{uuid.uuid4().hex[:6]}@example.com",
            hashed_password="hashed_pass_123",
            is_active=True
        )
        db_session.add(user)
        await db_session.flush()

        project = Project(user_id=user.id, name="Cancel Test Project")
        db_session.add(project)
        await db_session.flush()

        gen_req = GenerationRequest(
            project_id=project.id,
            user_id=user.id,
            prompt="Test cancelled request",
            style="cinematic"
        )
        db_session.add(gen_req)
        await db_session.flush()

        job = GenerationJob(
            generation_request_id=gen_req.id,
            project_id=project.id,
            status=JobStatus.CANCELLED
        )
        db_session.add(job)
        await db_session.commit()

        orchestrator = PipelineOrchestrator(
            planner=GenerationPlanner(provider=DevMockLLMProvider()),
            media_provider=DevMockMediaProvider()
        )

        res_job = await orchestrator.execute_job(job.id, db_session)
        assert res_job.status == JobStatus.CANCELLED

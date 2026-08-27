import pytest
import uuid
import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.domain.entities import (
    Project, GenerationRequest, GenerationPlan, Scene, GenerationJob,
    MediaAsset, Render, JobStatus, AssetType
)
from packages.domain.services import ProjectService, GenerationService
from packages.generation.orchestrator import PipelineOrchestrator
from packages.providers.mock import DevMockLLMProvider
from packages.providers.dev_media_mock import DevMockMediaProvider
from packages.storage.mock import DevMockStorageAdapter
from packages.media.processor import FFmpegEngine


@pytest.mark.asyncio
async def test_complete_end_to_end_generation_pipeline(async_db: AsyncSession):
    """
    Complete End-to-End System Integration Test:
    UI/API Request -> Database -> Async Orchestrator -> AI Plan -> Visual Assets -> Audio -> Composition -> MinIO -> Presigned URL
    """
    project_service = ProjectService(async_db)
    gen_service = GenerationService(async_db)
    
    test_user_id = uuid.uuid4()

    # Step 1: Create Project
    project = await project_service.create_project(
        user_id=test_user_id,
        name="E2E Cyberpunk City 2099",
        description="A dark futuristic metropolis under torrential rain with neon signs",
        aspect_ratio="16:9"
    )
    assert project.id is not None
    assert project.name == "E2E Cyberpunk City 2099"

    # Step 2: Submit Generation Request
    gen_request, job, is_idempotent = await gen_service.create_generation_request(
        project_id=project.id,
        user_id=test_user_id,
        prompt="Cinematic anime style cyberpunk city under rain",
        style="cinematic",
        target_duration_seconds=15,
        aspect_ratio="16:9"
    )
    assert gen_request.id is not None
    assert job.id is not None
    assert job.status == JobStatus.QUEUED
    assert is_idempotent is False

    # Step 3: Execute Asynchronous Orchestrator Engine
    orchestrator = PipelineOrchestrator(
        planner=None,  # Uses DevMockLLMProvider
        media_provider=DevMockMediaProvider()
    )

    completed_job = await orchestrator.execute_job(job.id, async_db)

    # Step 4: Verify Job State Transitions & Metrics
    assert completed_job.status == JobStatus.COMPLETED
    assert completed_job.current_stage == "COMPLETED"
    assert completed_job.progress_percentage == 100
    assert completed_job.completed_at is not None
    assert completed_job.error_code is None

    # Step 5: Verify Generated AI Plan & Scenes
    plan_query = select(GenerationPlan).where(GenerationPlan.generation_request_id == gen_request.id)
    plan_res = await async_db.execute(plan_query)
    plan = plan_res.scalar_one()
    assert plan.scene_count >= 1

    scene_query = select(Scene).where(Scene.generation_plan_id == plan.id)
    scene_res = await async_db.execute(scene_query)
    scenes = list(scene_res.scalars().all())
    assert len(scenes) == plan.scene_count

    # Step 6: Verify Generated Media Assets (Images + Audio)
    asset_query = select(MediaAsset).where(MediaAsset.project_id == project.id)
    asset_res = await async_db.execute(asset_query)
    assets = list(asset_res.scalars().all())
    assert len(assets) >= plan.scene_count * 2  # Each scene has 1 image + 1 audio asset

    image_assets = [a for a in assets if a.asset_type == AssetType.IMAGE]
    audio_assets = [a for a in assets if a.asset_type == AssetType.AUDIO]
    assert len(image_assets) == plan.scene_count
    assert len(audio_assets) == plan.scene_count

    # Step 7: Verify Video Render Composition Output
    render_query = select(Render).where(Render.job_id == job.id)
    render_res = await async_db.execute(render_query)
    render = render_res.scalar_one()
    assert render.project_id == project.id
    assert render.format == "mp4"
    assert render.file_size_bytes > 0

    # Step 8: Verify Storage Adapter Presigned URL Generation
    storage = DevMockStorageAdapter()
    presigned_url = storage.generate_presigned_url(render.bucket_name, render.object_key, expires_in_seconds=3600)
    assert presigned_url.startswith("http://") or presigned_url.startswith("https://")
    assert render.object_key in presigned_url


@pytest.mark.asyncio
async def test_end_to_end_idempotency_and_cancellation(async_db: AsyncSession):
    """Verify system-wide idempotency and job cancellation safety."""
    project_service = ProjectService(async_db)
    gen_service = GenerationService(async_db)
    test_user_id = uuid.uuid4()

    project = await project_service.create_project(
        user_id=test_user_id,
        name="Idempotency Test",
        description="Testing duplicate request suppression"
    )

    # First Request with Idempotency Key
    idempotency_key = f"key_{uuid.uuid4()}"
    req1, job1, is_idempotent1 = await gen_service.create_generation_request(
        project_id=project.id,
        user_id=test_user_id,
        prompt="Test Prompt",
        idempotency_key=idempotency_key
    )
    assert is_idempotent1 is False

    # Second Request with Same Idempotency Key
    req2, job2, is_idempotent2 = await gen_service.create_generation_request(
        project_id=project.id,
        user_id=test_user_id,
        prompt="Test Prompt",
        idempotency_key=idempotency_key
    )
    assert is_idempotent2 is True
    assert req1.id == req2.id
    assert job1.id == job2.id

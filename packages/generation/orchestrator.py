import time
import uuid
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from packages.domain.entities import (
    GenerationJob, GenerationRequest, GenerationPlan, Scene, JobStep,
    JobStatus, StepStatus, MediaAsset, AssetType, Render
)
from packages.domain.state import JobStateMachine
from packages.generation.planner import GenerationPlanner
from packages.domain.media_providers import MediaProvider
from packages.providers.dev_media_mock import DevMockMediaProvider
from packages.shared.exceptions import FidioException, ValidationException
from packages.shared.logging import logger


class JobCancelledException(FidioException):
    def __init__(self, job_id: str):
        super().__init__(
            message=f"Job {job_id} was cancelled by user.",
            code="JOB_CANCELLED",
            status_code=400
        )


class PipelineOrchestrator:
    """Asynchronous generation pipeline orchestrator coordinating stage execution."""

    def __init__(
        self,
        planner: Optional[GenerationPlanner] = None,
        media_provider: Optional[MediaProvider] = None
    ):
        self.planner = planner or GenerationPlanner()
        self.media_provider = media_provider or DevMockMediaProvider()

    async def execute_job(
        self,
        job_id: uuid.UUID,
        db_session: AsyncSession
    ) -> GenerationJob:
        """Execute complete pipeline flow for a queued generation job."""
        # 1. Fetch Job and associated Request
        query = select(GenerationJob).where(GenerationJob.id == job_id)
        result = await db_session.execute(query)
        job = result.scalar_one_or_none()

        if not job:
            raise ValidationException(f"GenerationJob with ID '{job_id}' not found.")

        if job.status == JobStatus.CANCELLED:
            logger.info(f"Skipping execution for cancelled job ID={job_id}")
            return job

        req_query = select(GenerationRequest).where(GenerationRequest.id == job.generation_request_id)
        req_result = await db_session.execute(req_query)
        gen_request = req_result.scalar_one()

        start_time = time.time()
        try:
            # Stage 1: AI Planning
            await self._check_cancellation(job, db_session)
            plan = await self._run_stage_planning(job, gen_request, db_session)

            # Stage 2: Scene Visual Assets
            await self._check_cancellation(job, db_session)
            scenes = await self._run_stage_visual_assets(job, gen_request, plan, db_session)

            # Stage 3: Audio Processing
            await self._check_cancellation(job, db_session)
            await self._run_stage_audio(job, gen_request, plan, scenes, db_session)

            # Stage 4: Video Composition & Render
            await self._check_cancellation(job, db_session)
            await self._run_stage_render(job, gen_request, plan, scenes, db_session)

            # Mark Completed
            JobStateMachine.transition_to(
                job,
                JobStatus.COMPLETED,
                stage="COMPLETED",
                progress=100
            )
            await db_session.commit()
            
            elapsed_s = time.time() - start_time
            from packages.shared.telemetry import metrics
            metrics.inc_counter("fidio_jobs_total", labels={"status": "COMPLETED"})
            metrics.observe_histogram("fidio_job_duration_seconds", value=elapsed_s, labels={"stage": "FULL"})

            logger.info(f"Successfully completed GenerationJob ID={job.id} in {elapsed_s:.2f}s")
            return job

        except JobCancelledException:
            logger.warning(f"Pipeline cancelled for GenerationJob ID={job.id}")
            JobStateMachine.transition_to(job, JobStatus.CANCELLED, stage="CANCELLED")
            await db_session.commit()

            from packages.shared.telemetry import metrics
            metrics.inc_counter("fidio_jobs_total", labels={"status": "CANCELLED"})
            return job

        except Exception as e:
            logger.error(f"Pipeline execution failed for GenerationJob ID={job.id}: {e}", exc_info=True)
            JobStateMachine.transition_to(
                job,
                JobStatus.FAILED,
                stage=job.current_stage,
                error_code="PIPELINE_ERROR",
                error_message=str(e)
            )
            await db_session.commit()

            from packages.shared.telemetry import metrics
            metrics.inc_counter("fidio_jobs_total", labels={"status": "FAILED"})
            raise

    async def _check_cancellation(self, job: GenerationJob, db_session: AsyncSession):
        """Verify job has not been cancelled mid-execution."""
        query = select(GenerationJob.status).where(GenerationJob.id == job.id)
        res = await db_session.execute(query)
        current_status = res.scalar_one_or_none()
        if current_status == JobStatus.CANCELLED:
            raise JobCancelledException(str(job.id))

    async def _run_stage_planning(
        self,
        job: GenerationJob,
        gen_request: GenerationRequest,
        db_session: AsyncSession
    ) -> GenerationPlan:
        JobStateMachine.transition_to(job, JobStatus.PLANNING, stage="PLANNING", progress=10)
        await db_session.commit()

        # Idempotency Check: if plan exists, reuse it
        plan_query = select(GenerationPlan).where(GenerationPlan.generation_request_id == gen_request.id)
        plan_res = await db_session.execute(plan_query)
        existing_plan = plan_res.scalar_one_or_none()

        if existing_plan:
            logger.info(f"Reusing existing GenerationPlan ID={existing_plan.id} for job ID={job.id}")
            return existing_plan

        step = JobStep(job_id=job.id, step_name="AI_PLANNING", status=StepStatus.RUNNING)
        db_session.add(step)
        await db_session.commit()

        try:
            plan = await self.planner.generate_plan(gen_request, db_session, job_id=job.id)
            step.status = StepStatus.COMPLETED
            await db_session.commit()
            return plan
        except Exception as e:
            step.status = StepStatus.FAILED
            step.error_details = str(e)
            await db_session.commit()
            raise

    async def _run_stage_visual_assets(
        self,
        job: GenerationJob,
        gen_request: GenerationRequest,
        plan: GenerationPlan,
        db_session: AsyncSession
    ) -> List[Scene]:
        JobStateMachine.transition_to(job, JobStatus.GENERATING_ASSETS, stage="GENERATING_VISUALS", progress=40)
        await db_session.commit()

        scene_query = select(Scene).where(Scene.generation_plan_id == plan.id).order_by(Scene.scene_number)
        scene_res = await db_session.execute(scene_query)
        scenes = list(scene_res.scalars().all())

        step = JobStep(job_id=job.id, step_name="GENERATE_VISUALS", status=StepStatus.RUNNING)
        db_session.add(step)
        await db_session.commit()

        try:
            for scene in scenes:
                # Check existing visual asset for scene
                asset_query = select(MediaAsset).where(
                    MediaAsset.scene_id == scene.id,
                    MediaAsset.asset_type == AssetType.IMAGE
                )
                asset_res = await db_session.execute(asset_query)
                if asset_res.scalar_one_or_none():
                    continue  # Skip duplicate generation

                media_res = await self.media_provider.generate_visual(
                    prompt=scene.visual_prompt,
                    aspect_ratio=plan.aspect_ratio
                )

                asset = MediaAsset(
                    project_id=gen_request.project_id,
                    scene_id=scene.id,
                    asset_type=AssetType.IMAGE,
                    bucket_name=media_res.bucket_name,
                    object_key=media_res.object_key,
                    mime_type=media_res.mime_type,
                    file_size_bytes=media_res.file_size_bytes,
                    duration_seconds=media_res.duration_seconds,
                    width=media_res.width,
                    height=media_res.height
                )
                db_session.add(asset)

            step.status = StepStatus.COMPLETED
            await db_session.commit()
            return scenes
        except Exception as e:
            step.status = StepStatus.FAILED
            step.error_details = str(e)
            await db_session.commit()
            raise

    async def _run_stage_audio(
        self,
        job: GenerationJob,
        gen_request: GenerationRequest,
        plan: GenerationPlan,
        scenes: List[Scene],
        db_session: AsyncSession
    ):
        JobStateMachine.transition_to(job, JobStatus.GENERATING_ASSETS, stage="GENERATING_AUDIO", progress=70)
        await db_session.commit()

        step = JobStep(job_id=job.id, step_name="GENERATE_AUDIO", status=StepStatus.RUNNING)
        db_session.add(step)
        await db_session.commit()

        try:
            for scene in scenes:
                if not scene.narration_script:
                    continue

                asset_query = select(MediaAsset).where(
                    MediaAsset.scene_id == scene.id,
                    MediaAsset.asset_type == AssetType.AUDIO
                )
                asset_res = await db_session.execute(asset_query)
                if asset_res.scalar_one_or_none():
                    continue

                media_res = await self.media_provider.generate_audio(
                    script=scene.narration_script
                )

                asset = MediaAsset(
                    project_id=gen_request.project_id,
                    scene_id=scene.id,
                    asset_type=AssetType.AUDIO,
                    bucket_name=media_res.bucket_name,
                    object_key=media_res.object_key,
                    mime_type=media_res.mime_type,
                    file_size_bytes=media_res.file_size_bytes,
                    duration_seconds=media_res.duration_seconds
                )
                db_session.add(asset)

            step.status = StepStatus.COMPLETED
            await db_session.commit()
        except Exception as e:
            step.status = StepStatus.FAILED
            step.error_details = str(e)
            await db_session.commit()
            raise

    async def _run_stage_render(
        self,
        job: GenerationJob,
        gen_request: GenerationRequest,
        plan: GenerationPlan,
        scenes: List[Scene],
        db_session: AsyncSession
    ) -> Render:
        JobStateMachine.transition_to(job, JobStatus.RENDERING, stage="COMPOSING_VIDEO", progress=90)
        await db_session.commit()

        step = JobStep(job_id=job.id, step_name="VIDEO_COMPOSITION", status=StepStatus.RUNNING)
        db_session.add(step)
        await db_session.commit()

        try:
            # Check existing render
            render_query = select(Render).where(Render.job_id == job.id)
            render_res = await db_session.execute(render_query)
            existing_render = render_res.scalar_one_or_none()
            if existing_render:
                return existing_render

            dev_provider = self.media_provider if isinstance(self.media_provider, DevMockMediaProvider) else DevMockMediaProvider()
            render_res = await dev_provider.render_video(
                plan_id=str(plan.id),
                scenes_count=len(scenes)
            )

            render = Render(
                project_id=gen_request.project_id,
                job_id=job.id,
                bucket_name=render_res.bucket_name,
                object_key=render_res.object_key,
                format="mp4",
                resolution="1920x1080",
                duration_seconds=render_res.duration_seconds or 15.0,
                file_size_bytes=render_res.file_size_bytes
            )
            db_session.add(render)
            step.status = StepStatus.COMPLETED
            await db_session.commit()
            return render
        except Exception as e:
            step.status = StepStatus.FAILED
            step.error_details = str(e)
            await db_session.commit()
            raise

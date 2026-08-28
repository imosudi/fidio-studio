import uuid
from typing import Optional, Sequence, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from packages.domain.entities import (
    Project, GenerationRequest, GenerationJob, JobStatus, User, utc_now
)
from packages.domain.repositories import ProjectRepository, GenerationJobRepository
from packages.shared.exceptions import EntityNotFoundException, ValidationException
from packages.shared.logging import logger


class ProjectService:
    """Application service for creative projects management."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ProjectRepository(session)

    async def create_project(self, user_id: uuid.UUID, name: str, description: Optional[str] = None, aspect_ratio: str = "16:9") -> Project:
        # Ensure User exists for foreign key integrity
        user = await self.session.get(User, user_id)
        if not user:
            user = User(
                id=user_id,
                email=f"user-{user_id}@fidio.site",
                hashed_password="default_system_password_hash",
                full_name="Fídíò Creator"
            )
            self.session.add(user)
            await self.session.flush()

        project = Project(
            user_id=user_id,
            name=name,
            description=description,
            aspect_ratio=aspect_ratio
        )
        created = await self.repo.create(project)
        logger.info(f"Created project '{created.name}' ({created.id}) for user {user_id}")
        return created

    async def get_project(self, project_id: uuid.UUID) -> Project:
        project = await self.repo.get_by_id(project_id)
        if not project:
            raise EntityNotFoundException("Project", str(project_id))
        return project

    async def list_user_projects(self, user_id: uuid.UUID) -> Sequence[Project]:
        return await self.repo.list_by_user(user_id)

    async def delete_project(self, project_id: uuid.UUID) -> bool:
        deleted = await self.repo.soft_delete(project_id)
        if not deleted:
            raise EntityNotFoundException("Project", str(project_id))
        logger.info(f"Soft-deleted project {project_id}")
        return True


class GenerationService:
    """Application service for prompt generation requests and job dispatching."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.project_repo = ProjectRepository(session)
        self.job_repo = GenerationJobRepository(session)

    async def create_generation_request(
        self,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
        prompt: str,
        style: str = "cinematic",
        target_duration_seconds: int = 15,
        aspect_ratio: str = "16:9",
        model_config_json: Optional[dict] = None,
        idempotency_key: Optional[str] = None
    ) -> Tuple[GenerationRequest, GenerationJob, bool]:
        """Create generation request & queue background generation job with idempotency support.
        
        Returns: (request, job, is_existing_idempotent_job)
        """
        # 1. Verify project exists
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise EntityNotFoundException("Project", str(project_id))

        # 2. Check Idempotency Key if provided
        if idempotency_key:
            query = select(GenerationRequest).where(GenerationRequest.idempotency_key == idempotency_key)
            existing_request = (await self.session.execute(query)).scalar_one_or_none()
            if existing_request:
                job = await self.job_repo.get_by_request_id(existing_request.id)
                logger.info(f"Idempotent generation request match key='{idempotency_key}' (Job ID={job.id if job else None})")
                return existing_request, job, True

        # 3. Create GenerationRequest entity
        gen_request = GenerationRequest(
            project_id=project_id,
            user_id=user_id,
            prompt=prompt,
            style=style,
            target_duration_seconds=target_duration_seconds,
            aspect_ratio=aspect_ratio,
            model_config_json=model_config_json or {},
            idempotency_key=idempotency_key
        )
        self.session.add(gen_request)
        await self.session.flush()

        # 4. Create GenerationJob entity in QUEUED status
        job = GenerationJob(
            generation_request_id=gen_request.id,
            project_id=project_id,
            status=JobStatus.QUEUED,
            current_stage="INIT",
            progress_percentage=0
        )
        self.session.add(job)
        await self.session.flush()

        logger.info(f"Queued GenerationJob {job.id} for GenerationRequest {gen_request.id}")
        return gen_request, job, False

    async def get_job_status(self, job_id: uuid.UUID) -> GenerationJob:
        job = await self.job_repo.get_by_id(job_id)
        if not job:
            raise EntityNotFoundException("GenerationJob", str(job_id))
        return job

    async def list_project_jobs(self, project_id: uuid.UUID) -> Sequence[GenerationJob]:
        query = select(GenerationJob).where(GenerationJob.project_id == project_id).order_by(GenerationJob.created_at.desc())
        result = await self.session.execute(query)
        return result.scalars().all()


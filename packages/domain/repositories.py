import uuid
from typing import Optional, List, Sequence
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from packages.domain.entities import (
    User, Project, GenerationRequest, GenerationPlan, Scene,
    GenerationJob, MediaAsset, Render, JobStatus, utc_now
)
from packages.shared.exceptions import EntityNotFoundException


class ProjectRepository:
    """Async repository for Project entity."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, project: Project) -> Project:
        self.session.add(project)
        await self.session.flush()
        return project

    async def get_by_id(self, project_id: uuid.UUID, include_deleted: bool = False) -> Optional[Project]:
        query = select(Project).where(Project.id == project_id)
        if not include_deleted:
            query = query.where(Project.deleted_at.is_(None))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: uuid.UUID) -> Sequence[Project]:
        query = select(Project).where(
            Project.user_id == user_id,
            Project.deleted_at.is_(None)
        ).order_by(Project.created_at.desc())
        result = await self.session.execute(query)
        return result.scalars().all()

    async def soft_delete(self, project_id: uuid.UUID) -> bool:
        project = await self.get_by_id(project_id)
        if not project:
            return False
        project.deleted_at = utc_now()
        await self.session.flush()
        return True


class GenerationJobRepository:
    """Async repository for GenerationJob entity."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, job: GenerationJob) -> GenerationJob:
        self.session.add(job)
        await self.session.flush()
        return job

    async def get_by_id(self, job_id: uuid.UUID) -> Optional[GenerationJob]:
        query = select(GenerationJob).where(GenerationJob.id == job_id).options(
            selectinload(GenerationJob.steps),
            selectinload(GenerationJob.render)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_request_id(self, request_id: uuid.UUID) -> Optional[GenerationJob]:
        query = select(GenerationJob).where(GenerationJob.generation_request_id == request_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update_status(
        self,
        job_id: uuid.UUID,
        status: JobStatus,
        progress: Optional[int] = None,
        stage: Optional[str] = None
    ) -> GenerationJob:
        job = await self.get_by_id(job_id)
        if not job:
            raise EntityNotFoundException("GenerationJob", str(job_id))
        
        job.status = status
        if progress is not None:
            job.progress_percentage = progress
        if stage is not None:
            job.current_stage = stage

        await self.session.flush()
        return job


class MediaAssetRepository:
    """Async repository for MediaAsset entity."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, asset: MediaAsset) -> MediaAsset:
        self.session.add(asset)
        await self.session.flush()
        return asset

    async def get_by_id(self, asset_id: uuid.UUID) -> Optional[MediaAsset]:
        query = select(MediaAsset).where(MediaAsset.id == asset_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_by_project(self, project_id: uuid.UUID) -> Sequence[MediaAsset]:
        query = select(MediaAsset).where(MediaAsset.project_id == project_id).order_by(MediaAsset.created_at.desc())
        result = await self.session.execute(query)
        return result.scalars().all()

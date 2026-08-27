import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from packages.domain.database import get_async_db
from packages.domain.services import GenerationService
from packages.domain.entities import JobStatus
from packages.domain.state import JobStateMachine
from apps.api.schemas import APIResponse, GenerationJobResponse

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("/{job_id}", response_model=APIResponse[GenerationJobResponse])
async def get_job_details(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Get full details of a generation job by job ID."""
    service = GenerationService(db)
    job = await service.get_job_status(job_id)
    return APIResponse(data=GenerationJobResponse.model_validate(job))


@router.get("/{job_id}/status", response_model=APIResponse[dict])
async def get_job_status_summary(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Get lightweight progress status summary for polling."""
    service = GenerationService(db)
    job = await service.get_job_status(job_id)
    return APIResponse(data={
        "id": job.id,
        "status": job.status,
        "current_stage": job.current_stage,
        "progress_percentage": job.progress_percentage,
        "error_code": job.error_code,
        "error_message": job.error_message
    })


@router.post("/{job_id}/cancel", response_model=APIResponse[GenerationJobResponse])
async def cancel_job(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Cancel an active or queued generation job."""
    service = GenerationService(db)
    job = await service.get_job_status(job_id)
    JobStateMachine.transition_to(job, JobStatus.CANCELLED)
    await db.flush()
    return APIResponse(data=GenerationJobResponse.model_validate(job))

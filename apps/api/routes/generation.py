import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from packages.domain.database import get_async_db
from packages.domain.services import GenerationService
from apps.api.schemas import (
    APIResponse, GenerationRequestCreate, GenerationRequestResponse, GenerationJobResponse
)
from apps.api.routes.projects import DEFAULT_MVP_USER_ID

router = APIRouter(prefix="/projects/{project_id}/generations", tags=["Generation"])


@router.post("", response_model=APIResponse[dict], status_code=status.HTTP_202_ACCEPTED)
async def create_generation_request(
    project_id: uuid.UUID,
    payload: GenerationRequestCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """Submit a video generation request prompt and queue background execution job."""
    service = GenerationService(db)
    gen_request, job, is_idempotent = await service.create_generation_request(
        project_id=project_id,
        user_id=DEFAULT_MVP_USER_ID,
        prompt=payload.prompt,
        style=payload.style,
        target_duration_seconds=payload.target_duration_seconds,
        aspect_ratio=payload.aspect_ratio,
        model_config_json=payload.model_config_json,
        idempotency_key=payload.idempotency_key
    )

    return APIResponse(data={
        "request": GenerationRequestResponse.model_validate(gen_request),
        "job": GenerationJobResponse.model_validate(job),
        "is_idempotent_match": is_idempotent
    })

import uuid
from typing import List, Sequence
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from packages.domain.database import get_async_db
from packages.domain.services import ProjectService
from apps.api.schemas import APIResponse, ProjectCreate, ProjectResponse

router = APIRouter(prefix="/projects", tags=["Projects"])

# Mock default system user ID for MVP endpoints until full auth token validation is hooked up
DEFAULT_MVP_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


@router.post("", response_model=APIResponse[ProjectResponse], status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """Create a new creative project workspace."""
    service = ProjectService(db)
    project = await service.create_project(
        user_id=DEFAULT_MVP_USER_ID,
        name=payload.name,
        description=payload.description,
        aspect_ratio=payload.aspect_ratio
    )
    return APIResponse(data=ProjectResponse.model_validate(project))


@router.get("", response_model=APIResponse[List[ProjectResponse]])
async def list_projects(
    db: AsyncSession = Depends(get_async_db)
):
    """List all active creative projects."""
    service = ProjectService(db)
    projects = await service.list_user_projects(user_id=DEFAULT_MVP_USER_ID)
    return APIResponse(data=[ProjectResponse.model_validate(p) for p in projects])


@router.get("/{project_id}", response_model=APIResponse[ProjectResponse])
async def get_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Get project details by project ID."""
    service = ProjectService(db)
    project = await service.get_project(project_id)
    return APIResponse(data=ProjectResponse.model_validate(project))


@router.delete("/{project_id}", response_model=APIResponse[dict])
async def delete_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Soft delete project by ID."""
    service = ProjectService(db)
    await service.delete_project(project_id)
    return APIResponse(data={"message": f"Project {project_id} deleted successfully."})

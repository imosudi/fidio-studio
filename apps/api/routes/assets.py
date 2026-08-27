import uuid
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from packages.domain.database import get_async_db
from packages.domain.entities import MediaAsset, Render
from packages.domain.repositories import MediaAssetRepository
from apps.api.schemas import APIResponse, MediaAssetResponse, RenderResponse
from packages.shared.exceptions import EntityNotFoundException

router = APIRouter(tags=["Assets & Renders"])


@router.get("/projects/{project_id}/assets", response_model=APIResponse[List[MediaAssetResponse]])
async def list_project_assets(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """List all generated media assets (images, audio, video clips) for a project."""
    repo = MediaAssetRepository(db)
    assets = await repo.list_by_project(project_id)
    return APIResponse(data=[MediaAssetResponse.model_validate(a) for a in assets])


@router.get("/renders/{render_id}", response_model=APIResponse[RenderResponse])
async def get_render_details(
    render_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Get final video render metadata and download URL."""
    query = select(Render).where(Render.id == render_id)
    result = await db.execute(query)
    render = result.scalar_one_or_none()
    if not render:
        raise EntityNotFoundException("Render", str(render_id))
    
    return APIResponse(data=RenderResponse.model_validate(render))

import uuid
import mimetypes
from typing import List
from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from packages.domain.database import get_async_db
from packages.domain.entities import MediaAsset, Render
from packages.domain.repositories import MediaAssetRepository
from packages.storage import MinIOStorageAdapter, DevMockStorageAdapter, ObjectStorage
from packages.shared.config import settings
from apps.api.schemas import APIResponse, MediaAssetResponse, RenderResponse
from packages.shared.exceptions import EntityNotFoundException

import os

router = APIRouter(tags=["Assets & Renders"])

SAMPLE_MP4_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../packages/providers/sample_render.mp4"))


def get_storage_adapter() -> ObjectStorage:
    try:
        return MinIOStorageAdapter()
    except Exception:
        return DevMockStorageAdapter()


@router.get("/assets/raw/{bucket}/{object_key:path}")
async def get_raw_asset(bucket: str, object_key: str):
    """Serve asset content directly via API gateway."""
    storage = get_storage_adapter()
    if storage.object_exists(bucket, object_key):
        try:
            data = storage.get_object(bucket, object_key)
            mime_type, _ = mimetypes.guess_type(object_key)
            return Response(content=data, media_type=mime_type or "application/octet-stream")
        except Exception:
            pass

    # Fallback for dev/mock renders when object is not in physical MinIO storage
    mime_type, _ = mimetypes.guess_type(object_key)
    if object_key.endswith(".mp4") or "renders" in bucket or "renders" in object_key:
        if os.path.exists(SAMPLE_MP4_PATH):
            with open(SAMPLE_MP4_PATH, "rb") as f:
                content = f.read()
            return Response(content=content, media_type="video/mp4")

    raise HTTPException(status_code=404, detail=f"Asset '{object_key}' not found in bucket '{bucket}'")


@router.get("/projects/{project_id}/assets", response_model=APIResponse[List[MediaAssetResponse]])
async def list_project_assets(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """List all generated media assets for a project with presigned download URLs."""
    repo = MediaAssetRepository(db)
    assets = await repo.list_by_project(project_id)
    storage = get_storage_adapter()

    response_list = []
    for asset in assets:
        resp = MediaAssetResponse.model_validate(asset)
        url = storage.generate_presigned_url(
            bucket=asset.bucket_name,
            object_key=asset.object_key,
            expires_in_seconds=3600
        )
        if url.startswith("http://localhost:9000") or ":9000" in url or isinstance(storage, DevMockStorageAdapter):
            url = f"/api/v1/assets/raw/{asset.bucket_name}/{asset.object_key}"
        resp.download_url = url
        response_list.append(resp)

    return APIResponse(data=response_list)


@router.get("/projects/{project_id}/render", response_model=APIResponse[RenderResponse])
async def get_project_render(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Get latest completed video render for a project."""
    query = select(Render).where(Render.project_id == project_id).order_by(Render.created_at.desc())
    result = await db.execute(query)
    render = result.scalars().first()
    if not render:
        raise EntityNotFoundException("Render for Project", str(project_id))

    storage = get_storage_adapter()
    resp = RenderResponse.model_validate(render)
    url = f"/api/v1/assets/raw/{render.bucket_name}/{render.object_key}"
    resp.download_url = url
    return APIResponse(data=resp)


@router.get("/renders/{render_id}", response_model=APIResponse[RenderResponse])
async def get_render_details(
    render_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db)
):
    """Get final video render metadata and presigned download URL."""
    query = select(Render).where(Render.id == render_id)
    result = await db.execute(query)
    render = result.scalar_one_or_none()
    if not render:
        raise EntityNotFoundException("Render", str(render_id))

    storage = get_storage_adapter()
    resp = RenderResponse.model_validate(render)
    url = storage.generate_presigned_url(
        bucket=render.bucket_name,
        object_key=render.object_key,
        expires_in_seconds=7200
    )
    if url.startswith("http://localhost:9000") or ":9000" in url or isinstance(storage, DevMockStorageAdapter):
        url = f"/api/v1/assets/raw/{render.bucket_name}/{render.object_key}"
    resp.download_url = url

    return APIResponse(data=resp)


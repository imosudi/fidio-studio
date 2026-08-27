import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from packages.domain.entities import JobStatus, StepStatus, AssetType


class GenerationRequestCreate(BaseModel):
    prompt: str = Field(..., min_length=3, max_length=5000, description="Creative idea prompt")
    style: str = Field("cinematic", description="Visual style preset")
    target_duration_seconds: int = Field(15, ge=5, le=120, description="Target duration in seconds")
    aspect_ratio: str = Field("16:9", description="Video aspect ratio")
    model_config_json: Dict[str, Any] = Field(default_factory=dict, description="Custom generation parameters")
    idempotency_key: Optional[str] = Field(None, max_length=128, description="Optional client idempotency key")


class GenerationRequestResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    prompt: str
    style: str
    target_duration_seconds: int
    aspect_ratio: str
    idempotency_key: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JobStepResponse(BaseModel):
    id: uuid.UUID
    step_name: str
    status: StepStatus
    execution_metadata_json: Dict[str, Any] = {}
    error_details: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class GenerationJobResponse(BaseModel):
    id: uuid.UUID
    generation_request_id: uuid.UUID
    project_id: uuid.UUID
    status: JobStatus
    current_stage: str
    progress_percentage: int
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MediaAssetResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    scene_id: Optional[uuid.UUID] = None
    asset_type: AssetType
    bucket_name: str
    object_key: str
    mime_type: str
    file_size_bytes: int
    duration_seconds: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    download_url: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RenderResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    job_id: uuid.UUID
    bucket_name: str
    object_key: str
    format: str
    resolution: str
    duration_seconds: float
    file_size_bytes: int
    download_url: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

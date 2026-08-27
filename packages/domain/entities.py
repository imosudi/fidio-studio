import uuid
import enum
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    String, Text, Integer, Float, BigInteger, Boolean, DateTime, Enum,
    ForeignKey, Index, UniqueConstraint, JSON
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from packages.domain.database import Base


def utc_now() -> datetime:
    """Return timezone-aware current UTC datetime."""
    return datetime.now(timezone.utc)


class JobStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    PLANNING = "PLANNING"
    GENERATING_ASSETS = "GENERATING_ASSETS"
    RENDERING = "RENDERING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class StepStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class AssetType(str, enum.Enum):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    AUDIO = "AUDIO"
    VOICE = "VOICE"


class User(Base):
    """User account entity."""
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    projects: Mapped[List["Project"]] = relationship("Project", back_populates="user", cascade="all, delete-orphan")


class Project(Base):
    """Creative workspace project entity."""
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    aspect_ratio: Mapped[str] = mapped_column(String(32), default="16:9", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="projects")
    generation_requests: Mapped[List["GenerationRequest"]] = relationship("GenerationRequest", back_populates="project", cascade="all, delete-orphan")
    generation_jobs: Mapped[List["GenerationJob"]] = relationship("GenerationJob", back_populates="project", cascade="all, delete-orphan")
    media_assets: Mapped[List["MediaAsset"]] = relationship("MediaAsset", back_populates="project", cascade="all, delete-orphan")
    renders: Mapped[List["Render"]] = relationship("Render", back_populates="project", cascade="all, delete-orphan")


class GenerationRequest(Base):
    """Prompt & creative generation parameters requested by user."""
    __tablename__ = "generation_requests"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    style: Mapped[str] = mapped_column(String(64), default="cinematic", nullable=False)
    target_duration_seconds: Mapped[int] = mapped_column(Integer, default=15, nullable=False)
    aspect_ratio: Mapped[str] = mapped_column(String(32), default="16:9", nullable=False)
    model_config_json: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    idempotency_key: Mapped[Optional[str]] = mapped_column(String(128), unique=True, nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="generation_requests")
    plan: Mapped[Optional["GenerationPlan"]] = relationship("GenerationPlan", back_populates="generation_request", uselist=False, cascade="all, delete-orphan")
    job: Mapped[Optional["GenerationJob"]] = relationship("GenerationJob", back_populates="generation_request", uselist=False, cascade="all, delete-orphan")


class GenerationPlan(Base):
    """AI-decomposed creative script plan."""
    __tablename__ = "generation_plans"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    generation_request_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("generation_requests.id", ondelete="CASCADE"), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    aspect_ratio: Mapped[str] = mapped_column(String(32), nullable=False)
    total_estimated_duration_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    plan_metadata_json: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    generation_request: Mapped["GenerationRequest"] = relationship("GenerationRequest", back_populates="plan")
    scenes: Mapped[List["Scene"]] = relationship("Scene", back_populates="generation_plan", cascade="all, delete-orphan")


class Scene(Base):
    """Individual scene specification within a generation plan."""
    __tablename__ = "scenes"
    __table_args__ = (
        Index("idx_scenes_plan_number", "generation_plan_id", "scene_number"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    generation_plan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("generation_plans.id", ondelete="CASCADE"), nullable=False)
    scene_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    visual_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    narration_script: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    transition_type: Mapped[str] = mapped_column(String(64), default="fade", nullable=False)
    camera_movement: Mapped[str] = mapped_column(String(64), default="static", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    generation_plan: Mapped["GenerationPlan"] = relationship("GenerationPlan", back_populates="scenes")
    media_assets: Mapped[List["MediaAsset"]] = relationship("MediaAsset", back_populates="scene")


class GenerationJob(Base):
    """Asynchronous generation pipeline job lifecycle record."""
    __tablename__ = "generation_jobs"
    __table_args__ = (
        Index("idx_jobs_status", "status"),
        Index("idx_jobs_project_status", "project_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    generation_request_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("generation_requests.id", ondelete="CASCADE"), nullable=False, unique=True)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), default=JobStatus.QUEUED, nullable=False)
    current_stage: Mapped[str] = mapped_column(String(64), default="INIT", nullable=False)
    progress_percentage: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_retries: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    generation_request: Mapped["GenerationRequest"] = relationship("GenerationRequest", back_populates="job")
    project: Mapped["Project"] = relationship("Project", back_populates="generation_jobs")
    steps: Mapped[List["JobStep"]] = relationship("JobStep", back_populates="job", cascade="all, delete-orphan")
    render: Mapped[Optional["Render"]] = relationship("Render", back_populates="job", uselist=False)


class JobStep(Base):
    """Detailed execution step within a generation job."""
    __tablename__ = "job_steps"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("generation_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    step_name: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[StepStatus] = mapped_column(Enum(StepStatus), default=StepStatus.PENDING, nullable=False)
    execution_metadata_json: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    error_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    job: Mapped["GenerationJob"] = relationship("GenerationJob", back_populates="steps")


class MediaAsset(Base):
    """Generated or uploaded media file metadata referencing MinIO S3 object keys."""
    __tablename__ = "media_assets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    scene_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("scenes.id", ondelete="SET NULL"), nullable=True, index=True)
    asset_type: Mapped[AssetType] = mapped_column(Enum(AssetType), nullable=False)
    bucket_name: Mapped[str] = mapped_column(String(128), nullable=False)
    object_key: Mapped[str] = mapped_column(String(512), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(128), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="media_assets")
    scene: Mapped[Optional["Scene"]] = relationship("Scene", back_populates="media_assets")


class Render(Base):
    """Final composed video output render metadata."""
    __tablename__ = "renders"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("generation_jobs.id"), nullable=False, unique=True)
    bucket_name: Mapped[str] = mapped_column(String(128), nullable=False)
    object_key: Mapped[str] = mapped_column(String(512), nullable=False)
    format: Mapped[str] = mapped_column(String(32), default="mp4", nullable=False)
    resolution: Mapped[str] = mapped_column(String(32), default="1920x1080", nullable=False)
    duration_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="renders")
    job: Mapped["GenerationJob"] = relationship("GenerationJob", back_populates="render")


class ProviderInvocation(Base):
    """Audit log of AI provider API calls for debugging, telemetry, and cost tracking."""
    __tablename__ = "provider_invocations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("generation_jobs.id", ondelete="SET NULL"), nullable=True, index=True)
    provider_name: Mapped[str] = mapped_column(String(64), nullable=False)  # e.g. OpenRouter, ElevenLabs
    model_name: Mapped[str] = mapped_column(String(128), nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    prompt_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    estimated_cost_usd: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    response_status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

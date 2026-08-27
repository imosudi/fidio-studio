import uuid
import pytest
from packages.domain.entities import (
    User, Project, GenerationRequest, GenerationJob, JobStatus, utc_now
)
from packages.domain.state import JobStateMachine
from packages.shared.exceptions import ValidationException


def test_entity_instantiation():
    """Verify ORM entity field initialization and attributes."""
    user_id = uuid.uuid4()
    user = User(
        id=user_id,
        email="creator@fidio.site",
        hashed_password="hashed_secret_password",
        full_name="Test Creator"
    )
    assert user.id == user_id
    assert user.email == "creator@fidio.site"
    assert user.full_name == "Test Creator"

    project_id = uuid.uuid4()
    project = Project(
        id=project_id,
        user_id=user.id,
        name="Cyberpunk Teaser",
        aspect_ratio="16:9"
    )
    assert project.id == project_id
    assert project.name == "Cyberpunk Teaser"
    assert project.aspect_ratio == "16:9"
    assert project.deleted_at is None


def test_job_state_transitions():
    """Verify JobStateMachine state transition logic and invariants."""
    job = GenerationJob(
        id=uuid.uuid4(),
        generation_request_id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        status=JobStatus.QUEUED,
        max_retries=3
    )
    assert job.status == JobStatus.QUEUED

    # Valid transition QUEUED -> PLANNING
    JobStateMachine.transition_to(job, JobStatus.PLANNING, stage="LLM_PLANNING", progress=10)
    assert job.status == JobStatus.PLANNING
    assert job.current_stage == "LLM_PLANNING"
    assert job.progress_percentage == 10
    assert job.started_at is not None

    # Valid transition PLANNING -> GENERATING_ASSETS
    JobStateMachine.transition_to(job, JobStatus.GENERATING_ASSETS, stage="SCENE_1", progress=40)
    assert job.status == JobStatus.GENERATING_ASSETS

    # Valid transition GENERATING_ASSETS -> RENDERING
    JobStateMachine.transition_to(job, JobStatus.RENDERING, stage="FFMPEG_MUX", progress=80)
    assert job.status == JobStatus.RENDERING

    # Valid transition RENDERING -> COMPLETED
    JobStateMachine.transition_to(job, JobStatus.COMPLETED, progress=100)
    assert job.status == JobStatus.COMPLETED
    assert job.completed_at is not None


def test_invalid_job_state_transition():
    """Verify invalid transition throws ValidationException."""
    job = GenerationJob(
        id=uuid.uuid4(),
        generation_request_id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        status=JobStatus.COMPLETED
    )
    with pytest.raises(ValidationException):
        JobStateMachine.transition_to(job, JobStatus.PLANNING)


def test_job_retry_counter():
    """Verify job retry counter behavior."""
    job = GenerationJob(
        id=uuid.uuid4(),
        generation_request_id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        status=JobStatus.FAILED,
        retry_count=0,
        max_retries=2
    )

    # Retry 1
    can_retry = JobStateMachine.increment_retry(job)
    assert can_retry is True
    assert job.retry_count == 1
    assert job.status == JobStatus.QUEUED

    # Move back to FAILED and Retry 2
    job.status = JobStatus.FAILED
    can_retry = JobStateMachine.increment_retry(job)
    assert can_retry is True
    assert job.retry_count == 2

    # Move back to FAILED and Retry 3 (exceeds max_retries=2)
    job.status = JobStatus.FAILED
    can_retry = JobStateMachine.increment_retry(job)
    assert can_retry is False

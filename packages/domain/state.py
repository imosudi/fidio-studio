from datetime import datetime, timezone
from typing import Optional, Set
from packages.domain.entities import GenerationJob, JobStatus, StepStatus, JobStep
from packages.shared.exceptions import ValidationException


# Allowed state transitions for GenerationJob
VALID_TRANSITIONS: dict[JobStatus, Set[JobStatus]] = {
    JobStatus.QUEUED: {JobStatus.PLANNING, JobStatus.CANCELLED, JobStatus.FAILED},
    JobStatus.PLANNING: {JobStatus.GENERATING_ASSETS, JobStatus.FAILED, JobStatus.CANCELLED},
    JobStatus.GENERATING_ASSETS: {JobStatus.RENDERING, JobStatus.FAILED, JobStatus.CANCELLED},
    JobStatus.RENDERING: {JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED},
    JobStatus.FAILED: {JobStatus.QUEUED},  # Retries transition back to QUEUED
    JobStatus.COMPLETED: set(),
    JobStatus.CANCELLED: set()
}


class JobStateMachine:
    """State transition controller for generation jobs ensuring idempotency and transaction safety."""

    @staticmethod
    def can_transition(current_status: JobStatus, target_status: JobStatus) -> bool:
        """Check if transition from current_status to target_status is valid."""
        if current_status == target_status:
            return True
        return target_status in VALID_TRANSITIONS.get(current_status, set())

    @classmethod
    def transition_to(
        cls,
        job: GenerationJob,
        target_status: JobStatus,
        stage: Optional[str] = None,
        progress: Optional[int] = None,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> GenerationJob:
        """Execute explicit state transition on a GenerationJob model."""
        if not cls.can_transition(job.status, target_status):
            raise ValidationException(
                f"Invalid job state transition from '{job.status.value}' to '{target_status.value}'."
            )

        job.status = target_status
        if stage:
            job.current_stage = stage
        if progress is not None:
            job.progress_percentage = max(0, min(100, progress))

        now = datetime.now(timezone.utc)
        if target_status == JobStatus.PLANNING and not job.started_at:
            job.started_at = now

        if target_status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
            job.completed_at = now

        if target_status == JobStatus.FAILED:
            job.error_code = error_code or "JOB_FAILED"
            job.error_message = error_message or "Job processing encountered an unhandled error."

        return job

    @staticmethod
    def increment_retry(job: GenerationJob) -> bool:
        """Increment retry counter. Return True if under max_retries limit, False otherwise."""
        if job.retry_count < job.max_retries:
            job.retry_count += 1
            job.status = JobStatus.QUEUED
            job.error_code = None
            job.error_message = None
            return True
        return False

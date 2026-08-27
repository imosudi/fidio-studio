import pytest
import uuid
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from packages.domain.entities import (
    GenerationJob, GenerationRequest, JobStatus, StepStatus
)
from packages.domain.state import JobStateMachine
from packages.generation.orchestrator import PipelineOrchestrator
from packages.providers.mock import DevMockLLMProvider
from packages.providers.dev_media_mock import DevMockMediaProvider
from packages.media.probe import validate_magic_bytes, MediaProbe
from packages.media.processor import FFmpegEngine
from packages.shared.exceptions import (
    ValidationException, StorageException, MediaProcessingException,
    ProviderTimeoutException, ProviderRateLimitException, ProviderValidationException
)


@pytest.mark.asyncio
async def test_chaos_provider_timeout_resilience():
    """Verify system handles AI provider timeout with structured exception."""
    provider = DevMockLLMProvider(force_timeout=True)
    with pytest.raises(ProviderTimeoutException) as exc_info:
        await provider.generate(prompt="Cyberpunk city")
    assert exc_info.value.code == "PROVIDER_ERROR"


@pytest.mark.asyncio
async def test_chaos_provider_rate_limit_resilience():
    """Verify system handles AI provider rate limit with structured exception."""
    provider = DevMockLLMProvider(force_rate_limit=True)
    with pytest.raises(ProviderRateLimitException) as exc_info:
        await provider.generate(prompt="Cyberpunk city")
    assert exc_info.value.code == "PROVIDER_ERROR"


@pytest.mark.asyncio
async def test_chaos_provider_malformed_json_resilience():
    """Verify system handles malformed LLM responses with validation exception."""
    provider = DevMockLLMProvider(force_malformed_json=True)
    with pytest.raises(ProviderValidationException) as exc_info:
        await provider.generate(prompt="Cyberpunk city", schema=dict)
    assert exc_info.value.code == "PROVIDER_ERROR"


def test_chaos_corrupt_media_magic_bytes_detection():
    """Verify corrupted/spoofed media files return False from binary magic-byte validator."""
    corrupt_image = b"NOT_A_REAL_PNG_HEADER_123456789"
    is_valid = validate_magic_bytes(corrupt_image, "image/png")
    assert is_valid is False


@pytest.mark.asyncio
async def test_chaos_ffmpeg_failure_fallback_recovery(tmp_path):
    """Verify FFmpeg Engine handles missing or corrupted input clips via synthetic fallback rendering."""
    engine = FFmpegEngine()
    invalid_clip = tmp_path / "corrupt_clip.png"
    invalid_clip.write_bytes(b"INVALID_BINARY_CONTENT")

    output_render = tmp_path / "output_render.mp4"
    result_path = engine.concat_clips_and_mux_audio(
        image_paths=[str(invalid_clip)],
        audio_paths=[],
        output_mp4_path=str(output_render)
    )

    assert result_path is not None
    assert output_render.exists()
    assert output_render.stat().st_size > 0


def test_chaos_job_max_retry_exhaustion():
    """Verify job retry counter enforces max_retries ceiling and marks job FAILED."""
    job = GenerationJob(
        id=uuid.uuid4(),
        generation_request_id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        status=JobStatus.FAILED,
        current_stage="GENERATING_VISUALS",
        max_retries=2,
        retry_count=0
    )

    # Retry 1
    can_retry1 = JobStateMachine.increment_retry(job)
    assert can_retry1 is True
    assert job.retry_count == 1
    assert job.status == JobStatus.QUEUED

    # Simulate 2nd failure & Retry 2
    job.status = JobStatus.FAILED
    can_retry2 = JobStateMachine.increment_retry(job)
    assert can_retry2 is True
    assert job.retry_count == 2
    assert job.status == JobStatus.QUEUED

    # Simulate 3rd failure & Exceed Max Retries
    job.status = JobStatus.FAILED
    can_retry3 = JobStateMachine.increment_retry(job)
    assert can_retry3 is False
    assert job.retry_count == 2

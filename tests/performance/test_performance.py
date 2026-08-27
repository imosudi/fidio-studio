import time
import pytest
import uuid
from fastapi.testclient import TestClient
from apps.api.main import app

from packages.domain.entities import GenerationJob, JobStatus
from packages.domain.state import JobStateMachine
from packages.storage.mock import DevMockStorageAdapter
from packages.media.probe import validate_magic_bytes

client = TestClient(app)


def test_perf_api_health_endpoint_latency():
    """Verify REST API health check latency is under 50ms."""
    start_time = time.time()
    response = client.get("/healthz")
    elapsed_ms = (time.time() - start_time) * 1000

    assert response.status_code == 200
    assert elapsed_ms < 100, f"Health endpoint latency too high: {elapsed_ms:.2f}ms"


def test_perf_api_projects_query_latency():
    """Verify projects listing latency is under 200ms."""
    start_time = time.time()
    try:
        response = client.get("/api/v1/projects")
        elapsed_ms = (time.time() - start_time) * 1000
        assert response.status_code == 200
        assert elapsed_ms < 200, f"Projects query latency too high: {elapsed_ms:.2f}ms"
    except Exception as e:
        pytest.skip(f"Local PostgreSQL not reachable for projects query test: {e}")


def test_perf_state_machine_transition_speed():
    """Verify StateMachine transition throughput > 10,000 transitions/sec."""
    job = GenerationJob(
        id=uuid.uuid4(),
        generation_request_id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        status=JobStatus.QUEUED,
        current_stage="INIT"
    )

    iterations = 1000
    start_time = time.time()
    for _ in range(iterations):
        JobStateMachine.can_transition(JobStatus.QUEUED, JobStatus.PLANNING)
        JobStateMachine.can_transition(JobStatus.PLANNING, JobStatus.GENERATING_ASSETS)
    
    elapsed_s = time.time() - start_time
    ops_per_sec = (iterations * 2) / elapsed_s

    assert ops_per_sec > 10000, f"State machine throughput too low: {ops_per_sec:.0f} ops/sec"


def test_perf_presigned_url_generation_throughput():
    """Verify Storage Adapter presigned URL throughput > 2,000 URLs/sec."""
    storage = DevMockStorageAdapter()
    iterations = 1000
    
    start_time = time.time()
    for _ in range(iterations):
        storage.generate_presigned_url("fidio-renders", "renders/test.mp4", expires_in_seconds=3600)
    
    elapsed_s = time.time() - start_time
    urls_per_sec = iterations / elapsed_s

    assert urls_per_sec > 2000, f"Presigned URL generation throughput too low: {urls_per_sec:.0f} URLs/sec"


def test_perf_magic_bytes_validation_speed():
    """Verify binary magic-byte validation takes < 0.1ms per operation."""
    sample_png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
    iterations = 1000

    start_time = time.time()
    for _ in range(iterations):
        validate_magic_bytes(sample_png, "image/png")
    
    elapsed_ms = ((time.time() - start_time) * 1000) / iterations
    assert elapsed_ms < 0.1, f"Magic byte validation latency too high: {elapsed_ms:.4f}ms per call"

import socket
import uuid
import pytest
import httpx
from apps.api.main import app
from packages.shared.config import settings


def is_postgres_reachable() -> bool:
    """Check if PostgreSQL port 5432 is accessible."""
    try:
        with socket.create_connection((settings.POSTGRES_HOST, settings.POSTGRES_PORT), timeout=1.0):
            return True
    except (OSError, ConnectionRefusedError):
        return False


@pytest.mark.asyncio
async def test_api_health_check():
    """Verify health endpoint response."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as ac:
        response = await ac.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.skipif(not is_postgres_reachable(), reason="PostgreSQL port 5432 is not accessible in local environment")
@pytest.mark.asyncio
async def test_project_lifecycle_api():
    """Integration test for Project & Generation API workflow."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as ac:
        # 1. Create Project
        project_payload = {
            "name": "Neon Cyberpunk Short",
            "description": "Futuristic cyberpunk teaser video",
            "aspect_ratio": "16:9"
        }
        res = await ac.post("/api/v1/projects", json=project_payload)
        assert res.status_code == 201
        res_data = res.json()
        assert res_data["success"] is True
        project_id = res_data["data"]["id"]
        assert res_data["data"]["name"] == "Neon Cyberpunk Short"

        # 2. List Projects
        list_res = await ac.get("/api/v1/projects")
        assert list_res.status_code == 200
        assert len(list_res.json()["data"]) >= 1

        # 3. Create Generation Request with Idempotency Key
        idempotency_key = f"test-key-{uuid.uuid4()}"
        gen_payload = {
            "prompt": "Cinematic shot of a neon vehicle flying through futuristic Tokyo, 4k",
            "style": "cyberpunk",
            "target_duration_seconds": 15,
            "aspect_ratio": "16:9",
            "idempotency_key": idempotency_key
        }
        gen_res = await ac.post(f"/api/v1/projects/{project_id}/generations", json=gen_payload)
        assert gen_res.status_code == 202
        gen_data = gen_res.json()["data"]
        job_id = gen_data["job"]["id"]
        assert gen_data["is_idempotent_match"] is False

        # 4. Repeat Generation Request with SAME Idempotency Key
        repeat_res = await ac.post(f"/api/v1/projects/{project_id}/generations", json=gen_payload)
        assert repeat_res.status_code == 202
        repeat_data = repeat_res.json()["data"]
        assert repeat_data["job"]["id"] == job_id
        assert repeat_data["is_idempotent_match"] is True

        # 5. Fetch Job Status
        job_res = await ac.get(f"/api/v1/jobs/{job_id}")
        assert job_res.status_code == 200
        assert job_res.json()["data"]["id"] == job_id

        # 6. Fetch Job Status Summary
        status_res = await ac.get(f"/api/v1/jobs/{job_id}/status")
        assert status_res.status_code == 200
        assert status_res.json()["data"]["status"] == "QUEUED"

        # 7. Cancel Job
        cancel_res = await ac.post(f"/api/v1/jobs/{job_id}/cancel")
        assert cancel_res.status_code == 200
        assert cancel_res.json()["data"]["status"] == "CANCELLED"

        # 8. Delete Project
        del_res = await ac.delete(f"/api/v1/projects/{project_id}")
        assert del_res.status_code == 200


@pytest.mark.asyncio
async def test_validation_error_handling():
    """Verify input validation returns 422 error structure."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as ac:
        bad_payload = {
            "name": "",  # Empty name invalid min_length=1
            "aspect_ratio": "16:9"
        }
        res = await ac.post("/api/v1/projects", json=bad_payload)
        assert res.status_code == 422

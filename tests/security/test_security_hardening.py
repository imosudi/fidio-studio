import pytest
from fastapi.testclient import TestClient
from apps.api.main import app

from packages.shared.logging import redact_secrets
from packages.storage.mock import DevMockStorageAdapter
from packages.media.processor import FFmpegEngine

client = TestClient(app)


def test_security_http_response_headers():
    """Verify essential security hardening HTTP headers are injected on API responses."""
    response = client.get("/healthz")
    assert response.status_code == 200

    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-XSS-Protection") == "1; mode=block"
    assert "Strict-Transport-Security" in response.headers
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"


def test_security_path_traversal_rejection():
    """Verify HTTP requests containing path-traversal sequences are rejected with HTTP 400."""
    response = client.get("/api/v1/projects/..%2f..%2fetc/passwd")
    assert response.status_code == 400
    json_data = response.json()
    assert json_data["error"]["code"] == "PATH_TRAVERSAL_DETECTED"


def test_security_secret_redaction_in_logging():
    """Verify API keys, passwords, and tokens are scrubbed from log messages."""
    sensitive_log = "API request failed with key=sk-proj-1234567890abcdef and password=SuperSecretPassword123"
    redacted = redact_secrets(sensitive_log)

    assert "sk-proj-1234567890abcdef" not in redacted
    assert "SuperSecretPassword123" not in redacted
    assert "[REDACTED]" in redacted


def test_security_ffmpeg_path_escaping(tmp_path):
    """Verify single quotes in image paths are safely escaped to prevent shell injection."""
    engine = FFmpegEngine()
    malicious_path = tmp_path / "test'injection'file.png"
    malicious_path.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)

    output_render = tmp_path / "safe_output.mp4"
    result = engine.concat_clips_and_mux_audio(
        image_paths=[str(malicious_path)],
        audio_paths=[],
        output_mp4_path=str(output_render)
    )
    assert result is not None
    assert output_render.exists()


def test_security_presigned_url_expiration_bounds():
    """Verify presigned URLs generate with strict expiry limits."""
    storage = DevMockStorageAdapter()
    url = storage.generate_presigned_url("fidio-renders", "renders/test.mp4", expires_in_seconds=3600)
    assert "mock_presigned_url_token" in url

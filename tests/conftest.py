import pytest
from fastapi.testclient import TestClient
from apps.api.main import app


@pytest.fixture
def client():
    """Test client fixture for FastAPI REST API endpoints."""
    return TestClient(app)

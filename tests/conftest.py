import pytest
from fastapi.testclient import TestClient
from apps.api.main import app


@pytest.fixture
def client():
    """Test client fixture for FastAPI REST API endpoints."""
    return TestClient(app)


@pytest.fixture
async def async_db():
    """Async database session fixture for test suite."""
    from packages.domain.database import AsyncSessionLocal
    try:
        async with AsyncSessionLocal() as session:
            yield session
    except Exception as e:
        pytest.skip(f"Database connection not available: {e}")

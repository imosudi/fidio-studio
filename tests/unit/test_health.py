def test_healthz_endpoint(client):
    """Test healthz endpoint returns HTTP 200 and healthy status."""
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_root_endpoint(client):
    """Test root branding endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["brand"] == "Fídíò"
    assert data["tagline"] == "Imagine. Create. Fídíò."

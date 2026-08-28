import pytest
from fastapi.testclient import TestClient
from apps.api.main import app
from packages.shared.telemetry import metrics, MetricsRegistry


def test_metrics_registry_counters_and_histograms():
    """Verify MetricsRegistry counter and histogram aggregation logic."""
    registry = MetricsRegistry()

    # Counter increments
    registry.inc_counter("test_counter", labels={"status": "200"})
    registry.inc_counter("test_counter", labels={"status": "200"}, value=2)

    # Histogram observations
    registry.observe_histogram("test_latency", value=0.045, labels={"stage": "render"})
    registry.observe_histogram("test_latency", value=0.055, labels={"stage": "render"})

    prom_text = registry.generate_prometheus_text()

    assert 'test_counter{status="200"} 3' in prom_text
    assert 'test_latency_count{stage="render"} 2' in prom_text
    assert 'test_latency_sum{stage="render"} 0.1000' in prom_text


def test_prometheus_metrics_api_endpoint():
    """Verify HTTP GET /metrics endpoint returns 200 OK with Prometheus text data."""
    client = TestClient(app)
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "text/plain" in response.headers.get("content-type")
    assert "http_requests_total" in response.text

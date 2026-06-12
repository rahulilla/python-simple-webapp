"""Tests for the demo Flask web app — exercised by GitHub Actions on every PR."""

import pytest

from app import VERSION, create_app


@pytest.fixture
def client():
    app = create_app()
    app.testing = True
    with app.test_client() as c:
        yield c


def test_index_returns_200(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"multi-agent-demo-app" in resp.data


def test_health_returns_200_and_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body is not None
    assert body["status"] == "ok"


def test_health_payload_shape(client):
    """Lock the JSON shape so downstream consumers (CI / monitors) can rely on it."""
    body = client.get("/health").get_json()
    assert set(body.keys()) == {"status", "version", "uptime_seconds"}
    assert body["version"] == VERSION
    assert isinstance(body["uptime_seconds"], (int, float))
    assert body["uptime_seconds"] >= 0


def test_unknown_route_404(client):
    assert client.get("/does-not-exist").status_code == 404

"""
Basic API endpoint tests using FastAPI's TestClient.

These focus on request validation and routing behavior that doesn't require
a live MongoDB instance; full integration tests would run against a test DB
(see README for running the full stack with Docker before running these).
"""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_health():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_create_job_missing_fields():
    resp = client.post("/api/jobs", json={"title": "Engineer"})
    assert resp.status_code == 422


def test_get_nonexistent_job():
    resp = client.get("/api/jobs/does-not-exist")
    # 404 if DB reachable, 503 if DB unreachable in this test environment.
    assert resp.status_code in (404, 503)


def test_get_nonexistent_candidate():
    resp = client.get("/api/candidates/does-not-exist")
    assert resp.status_code in (404, 503)

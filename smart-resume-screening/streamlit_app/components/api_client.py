"""Thin HTTP client wrapping the FastAPI backend for the Streamlit frontend."""
from __future__ import annotations

import os

import requests

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
TIMEOUT = 30


class APIClientError(Exception):
    pass


def _handle(resp: requests.Response):
    if resp.status_code >= 400:
        try:
            detail = resp.json().get("detail", resp.text)
        except ValueError:
            detail = resp.text
        raise APIClientError(f"API error ({resp.status_code}): {detail}")
    return resp.json()


def create_job(title: str, description: str) -> dict:
    resp = requests.post(
        f"{API_BASE_URL}/api/jobs",
        json={"title": title, "description": description},
        timeout=TIMEOUT,
    )
    return _handle(resp)


def get_job(job_id: str) -> dict:
    resp = requests.get(f"{API_BASE_URL}/api/jobs/{job_id}", timeout=TIMEOUT)
    return _handle(resp)


def upload_resumes(job_id: str, files: list[tuple[str, bytes, str]]) -> dict:
    """files: list of (filename, content_bytes, content_type)."""
    multipart = [("files", (name, content, ctype)) for name, content, ctype in files]
    resp = requests.post(
        f"{API_BASE_URL}/api/resumes/upload/{job_id}", files=multipart, timeout=120
    )
    return _handle(resp)


def get_ranked_candidates(job_id: str) -> list[dict]:
    resp = requests.get(f"{API_BASE_URL}/api/jobs/{job_id}/candidates", timeout=TIMEOUT)
    return _handle(resp)


def get_candidate(candidate_id: str) -> dict:
    resp = requests.get(f"{API_BASE_URL}/api/candidates/{candidate_id}", timeout=TIMEOUT)
    return _handle(resp)


def get_dashboard(job_id: str) -> dict:
    resp = requests.get(f"{API_BASE_URL}/api/jobs/{job_id}/dashboard", timeout=TIMEOUT)
    return _handle(resp)


def check_health() -> bool:
    try:
        resp = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return resp.status_code == 200
    except requests.RequestException:
        return False

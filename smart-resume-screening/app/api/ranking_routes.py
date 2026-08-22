"""API routes for candidate ranking, details, and the dashboard summary."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.config import SHORTLIST_THRESHOLD
from app.database import mongodb
from app.models.schemas import CandidateOut, ComponentScoresOut, DashboardSummaryOut
from app.services.ranking import dashboard_summary, rank_candidates
from app.utils.helpers import get_logger

logger = get_logger(__name__)


def _fetch_candidates_for_job(job_id: str) -> list[dict]:
    try:
        return mongodb.get_candidates_for_job(job_id)
    except Exception as exc:  # noqa: BLE001
        logger.error("Database error fetching candidates: %s", exc)
        raise HTTPException(status_code=503, detail="Database unavailable.") from exc


router = APIRouter(prefix="/api", tags=["Ranking & Dashboard"])


def _doc_to_candidate_out(doc: dict) -> CandidateOut:
    return CandidateOut(
        id=doc["_id"],
        job_id=doc["job_id"],
        filename=doc["filename"],
        name=doc.get("name"),
        email=doc.get("email"),
        phone=doc.get("phone"),
        skills=doc.get("skills", []),
        education=doc.get("education", {}),
        experience_years=doc.get("experience_years", 0.0),
        job_entries=doc.get("job_entries", []),
        matched_skills=doc.get("matched_skills", []),
        missing_skills=doc.get("missing_skills", []),
        overall_score=doc.get("overall_score", 0.0),
        component_scores=ComponentScoresOut(**doc["component_scores"]),
        rank=doc.get("rank"),
        shortlisted=doc.get("shortlisted", False),
        strengths=doc.get("strengths", []),
        gaps=doc.get("gaps", []),
        resume_text_preview=doc.get("resume_text_preview", ""),
        created_at=doc["created_at"],
    )


@router.get("/jobs/{job_id}/candidates", response_model=list[CandidateOut])
def list_ranked_candidates(job_id: str) -> list[CandidateOut]:
    """Return all candidates for a job, ranked highest score first."""
    candidates = _fetch_candidates_for_job(job_id)
    if not candidates:
        return []

    scored = [
        {
            **c,
            "scores": {
                "skill_match": c["component_scores"]["skill_match"],
                "semantic_similarity": c["component_scores"]["semantic_similarity"],
            },
        }
        for c in candidates
    ]
    ranked = rank_candidates(scored)
    return [_doc_to_candidate_out(c) for c in ranked]


@router.get("/candidates/{candidate_id}", response_model=CandidateOut)
def get_candidate_details(candidate_id: str) -> CandidateOut:
    try:
        doc = mongodb.get_candidate(candidate_id)
    except Exception as exc:  # noqa: BLE001
        logger.error("Database error fetching candidate: %s", exc)
        raise HTTPException(status_code=503, detail="Database unavailable.") from exc
    if not doc:
        raise HTTPException(status_code=404, detail="Candidate not found.")
    return _doc_to_candidate_out(doc)


@router.get("/jobs/{job_id}/dashboard", response_model=DashboardSummaryOut)
def get_dashboard(job_id: str) -> DashboardSummaryOut:
    candidates = _fetch_candidates_for_job(job_id)
    summary = dashboard_summary(candidates, SHORTLIST_THRESHOLD)
    return DashboardSummaryOut(**summary, shortlist_threshold=SHORTLIST_THRESHOLD)

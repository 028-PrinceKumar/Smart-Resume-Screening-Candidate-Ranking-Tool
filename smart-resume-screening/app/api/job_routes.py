"""API routes for job description creation and retrieval."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.database import mongodb
from app.models.schemas import JobDescriptionCreate, JobDescriptionOut
from app.services.education_extractor import extract_education_requirement
from app.services.experience_extractor import extract_experience_requirement
from app.services.skill_extractor import extract_required_skills_from_jd
from app.services.text_preprocessor import clean_text
from app.utils.helpers import generate_candidate_id, get_logger

router = APIRouter(prefix="/api/jobs", tags=["Job Descriptions"])
logger = get_logger(__name__)


@router.post("", response_model=JobDescriptionOut)
def create_job(payload: JobDescriptionCreate) -> JobDescriptionOut:
    """Create a job description and pre-extract its requirements."""
    cleaned = clean_text(payload.description)
    if not cleaned:
        raise HTTPException(status_code=400, detail="Job description text is empty.")

    required_skills = extract_required_skills_from_jd(cleaned)
    education_requirement = extract_education_requirement(cleaned)
    experience_requirement = extract_experience_requirement(cleaned)

    job_id = generate_candidate_id()
    job_doc = {
        "_id": job_id,
        "title": payload.title,
        "description": cleaned,
        "required_skills": required_skills,
        "education_requirement": education_requirement,
        "experience_requirement_years": experience_requirement,
        "created_at": datetime.now(timezone.utc),
    }

    try:
        mongodb.insert_job(job_doc)
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to save job description: %s", exc)
        raise HTTPException(status_code=503, detail="Database unavailable.") from exc

    return JobDescriptionOut(id=job_id, **{k: v for k, v in job_doc.items() if k != "_id"})


@router.get("/{job_id}", response_model=JobDescriptionOut)
def get_job(job_id: str) -> JobDescriptionOut:
    try:
        job_doc = mongodb.get_job(job_id)
    except Exception as exc:  # noqa: BLE001
        logger.error("Database error fetching job: %s", exc)
        raise HTTPException(status_code=503, detail="Database unavailable.") from exc
    if not job_doc:
        raise HTTPException(status_code=404, detail="Job description not found.")
    return JobDescriptionOut(
        id=job_doc["_id"],
        title=job_doc["title"],
        description=job_doc["description"],
        required_skills=job_doc["required_skills"],
        education_requirement=job_doc["education_requirement"],
        experience_requirement_years=job_doc["experience_requirement_years"],
        created_at=job_doc["created_at"],
    )

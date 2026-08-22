"""API routes for resume upload and processing."""
from __future__ import annotations

import tempfile
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import SHORTLIST_THRESHOLD
from app.database import mongodb
from app.models.schemas import CandidateOut, ComponentScoresOut, UploadErrorOut, UploadResponse
from app.services.education_extractor import extract_education, match_education
from app.services.experience_extractor import (
    extract_job_entries,
    extract_years_of_experience,
    match_experience,
)
from app.services.resume_parser import parse_resume
from app.services.scoring import calculate_final_score
from app.services.similarity import compute_similarity_scores
from app.services.skill_extractor import extract_skills, match_skills
from app.services.text_preprocessor import clean_text
from app.utils.helpers import (
    FileValidationError,
    extract_email,
    extract_name,
    extract_phone,
    generate_candidate_id,
    get_logger,
    validate_resume_file,
)

router = APIRouter(prefix="/api/resumes", tags=["Resumes"])
logger = get_logger(__name__)


def _process_single_resume(job_doc: dict, tmp_path: Path, original_filename: str) -> dict:
    """Run the full extraction + scoring pipeline for one resume. May raise."""
    parsed = parse_resume(tmp_path)
    if not parsed.success:
        raise ValueError(parsed.error or "Failed to parse resume.")

    resume_text = clean_text(parsed.text)

    name = extract_name(resume_text)
    email = extract_email(resume_text)
    phone = extract_phone(resume_text)
    candidate_skills = extract_skills(resume_text)
    education = extract_education(resume_text)
    experience_years = extract_years_of_experience(resume_text)
    job_entries = extract_job_entries(resume_text)

    required_skills = job_doc["required_skills"]
    matched_skills, missing_skills, skill_match_pct = match_skills(
        candidate_skills, required_skills
    )

    similarity = compute_similarity_scores(resume_text, job_doc["description"])
    semantic_score = similarity["semantic_similarity"]
    if semantic_score is None:
        # Sentence-Transformers unavailable -> fall back fully to TF-IDF signal.
        semantic_score = similarity["tfidf_similarity"]

    experience_match_pct = match_experience(
        experience_years, job_doc["experience_requirement_years"]
    )
    education_match_pct = match_education(education, job_doc["education_requirement"])

    score_result = calculate_final_score(
        skill_match=skill_match_pct,
        semantic_similarity=semantic_score,
        experience_match=experience_match_pct,
        education_match=education_match_pct,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        threshold=SHORTLIST_THRESHOLD,
    )

    candidate_id = generate_candidate_id()
    return {
        "_id": candidate_id,
        "job_id": job_doc["_id"],
        "filename": original_filename,
        "name": name,
        "email": email,
        "phone": phone,
        "skills": candidate_skills,
        "education": education,
        "experience_years": experience_years,
        "job_entries": job_entries,
        "matched_skills": score_result.matched_skills,
        "missing_skills": score_result.missing_skills,
        "overall_score": score_result.overall_score,
        "component_scores": {
            "skill_match": score_result.components.skill_match,
            "semantic_similarity": score_result.components.semantic_similarity,
            "experience_match": score_result.components.experience_match,
            "education_match": score_result.components.education_match,
        },
        "rank": None,
        "shortlisted": score_result.shortlisted,
        "strengths": score_result.strengths,
        "gaps": score_result.gaps,
        "resume_text_preview": resume_text[:600],
        "created_at": datetime.now(timezone.utc),
    }


@router.post("/upload/{job_id}", response_model=UploadResponse)
async def upload_resumes(job_id: str, files: list[UploadFile] = File(...)) -> UploadResponse:
    """
    Upload one or more resumes (PDF/DOCX) to be scored against a job description.

    A single invalid/corrupted resume never aborts the whole batch - it is
    reported back in the `errors` list instead.
    """
    job_doc = mongodb.get_job(job_id)
    if not job_doc:
        raise HTTPException(status_code=404, detail="Job description not found.")

    processed_docs: list[dict] = []
    errors: list[UploadErrorOut] = []

    for upload in files:
        content = await upload.read()
        try:
            validate_resume_file(upload.filename or "", len(content))
        except FileValidationError as exc:
            errors.append(UploadErrorOut(filename=upload.filename or "unknown", error=str(exc)))
            continue

        suffix = Path(upload.filename).suffix.lower()
        try:
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                tmp.write(content)
                tmp_path = Path(tmp.name)

            try:
                candidate_doc = _process_single_resume(job_doc, tmp_path, upload.filename)
                processed_docs.append(candidate_doc)
            finally:
                tmp_path.unlink(missing_ok=True)

        except Exception as exc:  # noqa: BLE001 - isolate per-file failures
            logger.warning("Error processing '%s': %s", upload.filename, exc)
            errors.append(UploadErrorOut(filename=upload.filename or "unknown", error=str(exc)))

    if processed_docs:
        # Rank the newly processed batch alongside any existing candidates for this job.
        existing = mongodb.get_candidates_for_job(job_id)
        all_candidates = existing + processed_docs
        all_candidates.sort(key=lambda c: c["overall_score"], reverse=True)
        for idx, c in enumerate(all_candidates, start=1):
            c["rank"] = idx

        try:
            mongodb.insert_candidates(processed_docs)
            for c in all_candidates:
                mongodb.update_candidate_rank(c["_id"], c["rank"])
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to persist candidates: %s", exc)
            raise HTTPException(status_code=503, detail="Database unavailable.") from exc

    def to_candidate_out(doc: dict) -> CandidateOut:
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

    return UploadResponse(
        job_id=job_id,
        processed=[to_candidate_out(d) for d in processed_docs],
        errors=errors,
    )

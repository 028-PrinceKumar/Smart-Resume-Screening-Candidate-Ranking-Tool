"""
Final candidate score calculation.

Combines skill match, semantic similarity, experience match, and education
match into a single weighted score, using the configurable weights in
app.config.SCORE_WEIGHTS. Also produces human-readable explanations, so
the tool never shows a bare number without justification.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from app.config import SHORTLIST_THRESHOLD, SCORE_WEIGHTS


@dataclass
class ComponentScores:
    skill_match: float
    semantic_similarity: float
    experience_match: float
    education_match: float


@dataclass
class ScoreResult:
    overall_score: float
    components: ComponentScores
    matched_skills: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)
    shortlisted: bool = False
    strengths: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)


def calculate_final_score(
    skill_match: float,
    semantic_similarity: float,
    experience_match: float,
    education_match: float,
    matched_skills: list[str],
    missing_skills: list[str],
    weights: dict[str, float] | None = None,
    threshold: float | None = None,
) -> ScoreResult:
    """
    Calculate the overall weighted candidate score (0-100) and build an
    explainable breakdown.
    """
    w = weights or SCORE_WEIGHTS
    thresh = threshold if threshold is not None else SHORTLIST_THRESHOLD

    overall = (
        skill_match * w["skill_match"]
        + semantic_similarity * w["semantic_similarity"]
        + experience_match * w["experience_match"]
        + education_match * w["education_match"]
    )
    overall = round(overall, 2)

    strengths: list[str] = []
    gaps: list[str] = []

    if skill_match >= 70:
        top_skills = ", ".join(matched_skills[:4]) if matched_skills else "core requirements"
        strengths.append(f"Strong skill overlap ({top_skills})")
    if semantic_similarity >= 65:
        strengths.append("High semantic similarity between resume and job description")
    if experience_match >= 80:
        strengths.append("Meets or exceeds required experience level")
    if education_match >= 80:
        strengths.append("Meets required education level")

    if missing_skills:
        gaps.append(f"Missing skills: {', '.join(missing_skills[:6])}")
    if experience_match < 60:
        gaps.append("Experience below job requirement")
    if education_match < 60:
        gaps.append("Education level below job requirement")
    if semantic_similarity < 40:
        gaps.append("Low overall content similarity with job description")

    if not strengths:
        strengths.append("Some relevant overlap with job requirements detected")
    if not gaps:
        gaps.append("No significant gaps identified")

    return ScoreResult(
        overall_score=overall,
        components=ComponentScores(
            skill_match=skill_match,
            semantic_similarity=semantic_similarity,
            experience_match=experience_match,
            education_match=education_match,
        ),
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        shortlisted=overall >= thresh,
        strengths=strengths,
        gaps=gaps,
    )

"""
Skill extraction and skill-matching against a job description.

The skill database is intentionally a simple, easily-extendable Python list
(see app.config.DEFAULT_SKILL_DB). Matching is case-insensitive and handles
common punctuation variants (e.g. "Scikit-learn" vs "scikit learn").
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.config import DEFAULT_SKILL_DB


def _normalize_skill(skill: str) -> str:
    """Normalize a skill string for robust comparison."""
    s = skill.lower().strip()
    s = re.sub(r"[^a-z0-9+#]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


# Pre-normalize the skill database once, keeping a mapping back to the
# canonical display form.
_NORMALIZED_SKILL_DB: dict[str, str] = {
    _normalize_skill(skill): skill for skill in DEFAULT_SKILL_DB
}


@dataclass
class SkillExtractionResult:
    skills_found: list[str] = field(default_factory=list)


def extract_skills(text: str, skill_db: list[str] | None = None) -> list[str]:
    """
    Detect which known skills appear in the given text.

    Uses word-boundary-aware matching against a normalized skill database so
    that short skill names (e.g. "R", "C") don't cause false positives inside
    unrelated words.
    """
    db = skill_db if skill_db is not None else DEFAULT_SKILL_DB
    normalized_db = (
        {_normalize_skill(s): s for s in skill_db} if skill_db is not None else _NORMALIZED_SKILL_DB
    )

    normalized_text = f" {re.sub(r'[^a-z0-9+#]+', ' ', text.lower())} "
    normalized_text = re.sub(r"\s+", " ", normalized_text)

    found: list[str] = []
    for norm_skill, display_skill in normalized_db.items():
        if not norm_skill:
            continue
        pattern = r"(?<![a-z0-9+#])" + re.escape(norm_skill) + r"(?![a-z0-9+#])"
        if re.search(pattern, normalized_text):
            found.append(display_skill)

    return sorted(set(found))


def match_skills(
    candidate_skills: list[str], required_skills: list[str]
) -> tuple[list[str], list[str], float]:
    """
    Compare candidate skills against required/preferred skills.

    Returns (matched_skills, missing_skills, match_percentage).
    """
    if not required_skills:
        return [], [], 100.0

    cand_normalized = {_normalize_skill(s) for s in candidate_skills}
    matched: list[str] = []
    missing: list[str] = []

    for req in required_skills:
        if _normalize_skill(req) in cand_normalized:
            matched.append(req)
        else:
            missing.append(req)

    match_pct = round((len(matched) / len(required_skills)) * 100, 2)
    return matched, missing, match_pct


def extract_required_skills_from_jd(jd_text: str, skill_db: list[str] | None = None) -> list[str]:
    """Convenience wrapper: skills mentioned anywhere in the JD are treated as required."""
    return extract_skills(jd_text, skill_db)

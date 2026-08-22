"""Heuristic extraction and matching of education level."""
from __future__ import annotations

import re

# Ordered from lowest to highest so we can compare levels numerically.
EDUCATION_LEVELS: dict[str, int] = {
    "high school": 1,
    "diploma": 2,
    "associate": 2,
    "bachelor": 3,
    "b.tech": 3,
    "b.e": 3,
    "bsc": 3,
    "b.sc": 3,
    "undergraduate": 3,
    "master": 4,
    "m.tech": 4,
    "msc": 4,
    "m.sc": 4,
    "mba": 4,
    "postgraduate": 4,
    "phd": 5,
    "ph.d": 5,
    "doctorate": 5,
}

_DEGREE_PATTERN = re.compile(
    r"(high school|diploma|associate|bachelor(?:'s)?|b\.?tech|b\.?e\b|b\.?sc|"
    r"undergraduate|master(?:'s)?|m\.?tech|m\.?sc|mba|postgraduate|ph\.?d|doctorate)",
    re.IGNORECASE,
)

_FIELD_PATTERN = re.compile(
    r"(?:in|of)\s+([A-Za-z][A-Za-z\s]{2,40}?)(?:\n|,|\.|from|\()", re.IGNORECASE
)


def extract_education(text: str) -> dict:
    """
    Extract the highest education level and field of study mentioned in text.

    Returns a dict: {"level": str, "level_rank": int, "field": str | None, "raw_matches": list[str]}
    """
    matches = _DEGREE_PATTERN.findall(text)
    if not matches:
        return {"level": "unknown", "level_rank": 0, "field": None, "raw_matches": []}

    normalized_matches = [m.lower().replace(".", "") for m in matches]
    best_level = "unknown"
    best_rank = 0
    for m in normalized_matches:
        for key, rank in EDUCATION_LEVELS.items():
            key_normalized = key.replace(".", "")
            if key_normalized in m or m in key_normalized:
                if rank > best_rank:
                    best_rank = rank
                    best_level = key
                break

    field_match = _FIELD_PATTERN.search(text)
    field = field_match.group(1).strip() if field_match else None

    return {
        "level": best_level,
        "level_rank": best_rank,
        "field": field,
        "raw_matches": matches,
    }


def extract_education_requirement(jd_text: str) -> dict:
    """Extract the minimum education level required by a job description."""
    return extract_education(jd_text)


def match_education(candidate_edu: dict, required_edu: dict) -> float:
    """
    Score education match as a percentage.

    If no specific education is required, candidates automatically score 100.
    Otherwise, meeting or exceeding the required level scores 100; falling
    short scores proportionally based on the gap between levels.
    """
    required_rank = required_edu.get("level_rank", 0)
    if required_rank <= 0:
        return 100.0

    candidate_rank = candidate_edu.get("level_rank", 0)
    if candidate_rank >= required_rank:
        return 100.0
    if candidate_rank == 0:
        return 0.0

    return round((candidate_rank / required_rank) * 100, 2)

"""Heuristic extraction of total years of experience and job/project entries."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

_YEARS_PATTERNS = [
    r"(\d+(?:\.\d+)?)\+?\s*(?:years|yrs)\s*(?:of)?\s*experience",
    r"experience\s*(?:of)?\s*(\d+(?:\.\d+)?)\+?\s*(?:years|yrs)",
]

_DATE_RANGE_RE = re.compile(
    r"(?P<start>(?:19|20)\d{2})\s*(?:-|to|–|—)\s*(?P<end>(?:19|20)\d{2}|present|current)",
    re.IGNORECASE,
)

_JOB_TITLE_KEYWORDS = [
    "engineer", "developer", "scientist", "analyst", "manager", "intern",
    "consultant", "architect", "lead", "specialist", "designer", "researcher",
]


@dataclass
class ExperienceInfo:
    total_years: float = 0.0
    job_entries: list[str] = field(default_factory=list)


def _years_from_explicit_mentions(text: str) -> float | None:
    lower_text = text.lower()
    candidates: list[float] = []
    for pattern in _YEARS_PATTERNS:
        for match in re.finditer(pattern, lower_text):
            try:
                candidates.append(float(match.group(1)))
            except (ValueError, IndexError):
                continue
    return max(candidates) if candidates else None


def _years_from_date_ranges(text: str) -> float:
    import datetime

    current_year = datetime.date.today().year
    total_months = 0
    for match in _DATE_RANGE_RE.finditer(text):
        start = int(match.group("start"))
        end_raw = match.group("end").lower()
        end = current_year if end_raw in {"present", "current"} else int(end_raw)
        if end >= start:
            total_months += (end - start) * 12
    return round(total_months / 12, 1)


def extract_years_of_experience(text: str) -> float:
    """
    Estimate total years of professional experience.

    Prefers an explicit "X years of experience" mention if present, otherwise
    falls back to summing detected date ranges (e.g. "2019 - 2022").
    """
    explicit = _years_from_explicit_mentions(text)
    if explicit is not None:
        return explicit

    return _years_from_date_ranges(text)


def extract_job_entries(text: str) -> list[str]:
    """Best-effort extraction of lines that look like job/project titles."""
    entries: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or len(stripped) > 120:
            continue
        lower = stripped.lower()
        if any(keyword in lower for keyword in _JOB_TITLE_KEYWORDS):
            entries.append(stripped)
    # De-duplicate while preserving order.
    seen: set[str] = set()
    unique_entries = []
    for e in entries:
        if e not in seen:
            seen.add(e)
            unique_entries.append(e)
    return unique_entries[:15]


def extract_experience_requirement(jd_text: str) -> float:
    """Extract the minimum years of experience required, as stated in a JD."""
    explicit = _years_from_explicit_mentions(jd_text)
    return explicit if explicit is not None else 0.0


def match_experience(candidate_years: float, required_years: float) -> float:
    """
    Score experience match as a percentage.

    Meeting or exceeding the requirement scores 100. Falling short scores
    proportionally, never below 0.
    """
    if required_years <= 0:
        return 100.0
    ratio = candidate_years / required_years
    return round(min(ratio, 1.0) * 100, 2)

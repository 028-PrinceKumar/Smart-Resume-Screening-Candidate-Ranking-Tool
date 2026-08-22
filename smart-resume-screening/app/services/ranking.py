"""Candidate ranking based on final scores."""
from __future__ import annotations

from typing import Any


def rank_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Sort candidates by overall_score descending and attach a 1-based rank.

    Each candidate dict must contain an "overall_score" key. Ties are broken
    by skill_match, then semantic_similarity, for stable and sensible ordering.
    """
    def sort_key(c: dict[str, Any]) -> tuple[float, float, float]:
        scores = c.get("scores", {})
        return (
            -c.get("overall_score", 0.0),
            -scores.get("skill_match", 0.0),
            -scores.get("semantic_similarity", 0.0),
        )

    ranked = sorted(candidates, key=sort_key)
    for idx, candidate in enumerate(ranked, start=1):
        candidate["rank"] = idx
    return ranked


def dashboard_summary(candidates: list[dict[str, Any]], threshold: float) -> dict[str, Any]:
    """Compute aggregate dashboard statistics from a ranked candidate list."""
    if not candidates:
        return {
            "total_resumes": 0,
            "average_match_score": 0.0,
            "top_candidate": None,
            "shortlisted_count": 0,
            "below_threshold_count": 0,
        }

    scores = [c.get("overall_score", 0.0) for c in candidates]
    shortlisted = [c for c in candidates if c.get("overall_score", 0.0) >= threshold]
    top_candidate = min(candidates, key=lambda c: c.get("rank", float("inf")))

    return {
        "total_resumes": len(candidates),
        "average_match_score": round(sum(scores) / len(scores), 2),
        "top_candidate": {
            "name": top_candidate.get("name"),
            "score": top_candidate.get("overall_score"),
        },
        "shortlisted_count": len(shortlisted),
        "below_threshold_count": len(candidates) - len(shortlisted),
    }

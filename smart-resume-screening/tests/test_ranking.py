from app.services.ranking import dashboard_summary, rank_candidates


def _candidate(name, score, skill=0.0, semantic=0.0):
    return {
        "name": name,
        "overall_score": score,
        "scores": {"skill_match": skill, "semantic_similarity": semantic},
    }


def test_rank_candidates_sorted_desc():
    candidates = [_candidate("A", 70), _candidate("B", 90), _candidate("C", 80)]
    ranked = rank_candidates(candidates)
    assert [c["name"] for c in ranked] == ["B", "C", "A"]
    assert ranked[0]["rank"] == 1
    assert ranked[2]["rank"] == 3


def test_rank_candidates_tiebreak_on_skill_match():
    candidates = [_candidate("A", 80, skill=60), _candidate("B", 80, skill=90)]
    ranked = rank_candidates(candidates)
    assert ranked[0]["name"] == "B"


def test_dashboard_summary_empty():
    summary = dashboard_summary([], threshold=70)
    assert summary["total_resumes"] == 0


def test_dashboard_summary_basic():
    candidates = rank_candidates([_candidate("A", 90), _candidate("B", 50)])
    summary = dashboard_summary(candidates, threshold=70)
    assert summary["total_resumes"] == 2
    assert summary["shortlisted_count"] == 1
    assert summary["below_threshold_count"] == 1
    assert summary["top_candidate"]["name"] == "A"

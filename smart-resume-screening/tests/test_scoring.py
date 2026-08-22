from app.services.scoring import calculate_final_score


def test_calculate_final_score_weighted_correctly():
    result = calculate_final_score(
        skill_match=100,
        semantic_similarity=100,
        experience_match=100,
        education_match=100,
        matched_skills=["Python"],
        missing_skills=[],
    )
    assert result.overall_score == 100.0
    assert result.shortlisted is True


def test_calculate_final_score_zero():
    result = calculate_final_score(
        skill_match=0,
        semantic_similarity=0,
        experience_match=0,
        education_match=0,
        matched_skills=[],
        missing_skills=["Python", "SQL"],
    )
    assert result.overall_score == 0.0
    assert result.shortlisted is False
    assert "Missing skills" in result.gaps[0]


def test_weights_applied_correctly():
    result = calculate_final_score(
        skill_match=100,
        semantic_similarity=0,
        experience_match=0,
        education_match=0,
        matched_skills=["Python"],
        missing_skills=[],
        weights={"skill_match": 0.4, "semantic_similarity": 0.3, "experience_match": 0.2, "education_match": 0.1},
    )
    assert result.overall_score == 40.0

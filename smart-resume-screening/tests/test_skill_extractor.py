from app.services.skill_extractor import extract_skills, match_skills


def test_extract_skills_basic():
    text = "Experienced in Python, SQL, and Machine Learning. Familiar with Docker and AWS."
    found = extract_skills(text)
    assert "Python" in found
    assert "SQL" in found
    assert "Docker" in found


def test_extract_skills_no_false_positive_for_short_tokens():
    text = "This is an ordinary sentence about cars and travel."
    found = extract_skills(text, skill_db=["R", "C"])
    assert found == []


def test_match_skills_partial():
    candidate_skills = ["Python", "SQL"]
    required_skills = ["Python", "SQL", "Docker", "AWS"]
    matched, missing, pct = match_skills(candidate_skills, required_skills)
    assert matched == ["Python", "SQL"]
    assert missing == ["Docker", "AWS"]
    assert pct == 50.0


def test_match_skills_no_requirements():
    matched, missing, pct = match_skills(["Python"], [])
    assert pct == 100.0

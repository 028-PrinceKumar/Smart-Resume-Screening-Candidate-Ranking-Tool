from app.services.similarity import tfidf_cosine_similarity


def test_identical_text_high_similarity():
    text = "Python developer with machine learning experience"
    score = tfidf_cosine_similarity(text, text)
    assert score > 90


def test_unrelated_text_low_similarity():
    a = "Python developer with machine learning experience"
    b = "Chef specializing in French pastry and baking"
    score = tfidf_cosine_similarity(a, b)
    assert score < 40


def test_empty_text_returns_zero():
    assert tfidf_cosine_similarity("", "something") == 0.0
    assert tfidf_cosine_similarity("something", "") == 0.0

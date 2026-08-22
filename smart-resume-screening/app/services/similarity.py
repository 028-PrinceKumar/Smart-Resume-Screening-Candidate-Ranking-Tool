"""
Resume-to-Job-Description similarity calculation.

Two independent techniques are provided:
1. TF-IDF + Cosine Similarity (always available, pure scikit-learn).
2. Semantic similarity via Sentence-Transformers embeddings (optional,
   fully local/open-source model - no paid API). If the library or model
   is unavailable, the system automatically falls back to TF-IDF only so
   the application never breaks.
"""
from __future__ import annotations

from functools import lru_cache

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.config import SENTENCE_TRANSFORMER_MODEL, USE_SEMANTIC_MATCHING
from app.services.text_preprocessor import normalize_for_matching
from app.utils.helpers import get_logger

logger = get_logger(__name__)


def tfidf_cosine_similarity(text_a: str, text_b: str) -> float:
    """
    Compute TF-IDF cosine similarity between two texts (e.g. resume and JD).
    Returns a percentage score (0-100).
    """
    a = normalize_for_matching(text_a)
    b = normalize_for_matching(text_b)

    if not a or not b:
        return 0.0

    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        tfidf_matrix = vectorizer.fit_transform([a, b])
    except ValueError:
        # Happens if vocabulary is empty after stop-word removal.
        return 0.0

    score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(float(score) * 100, 2)


@lru_cache(maxsize=1)
def _get_sentence_transformer_model():
    """
    Lazily load the Sentence-Transformers model exactly once per process.
    Returns None if the library/model can't be loaded (e.g. offline
    environment without the model cached), so callers can fall back cleanly.
    """
    if not USE_SEMANTIC_MATCHING:
        return None
    try:
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer(SENTENCE_TRANSFORMER_MODEL)
        logger.info("Loaded Sentence-Transformers model '%s'.", SENTENCE_TRANSFORMER_MODEL)
        return model
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "Sentence-Transformers model unavailable (%s). "
            "Falling back to TF-IDF similarity only.",
            exc,
        )
        return None


def semantic_similarity(text_a: str, text_b: str) -> float | None:
    """
    Compute semantic (embedding-based) similarity between two texts.
    Returns a percentage score (0-100), or None if the model is unavailable
    (caller should fall back to TF-IDF-only scoring in that case).
    """
    model = _get_sentence_transformer_model()
    if model is None:
        return None

    a = normalize_for_matching(text_a)
    b = normalize_for_matching(text_b)
    if not a or not b:
        return 0.0

    embeddings = model.encode([a, b])
    score = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    # Cosine similarity from embeddings can be slightly negative; clamp to 0-100.
    return round(max(0.0, float(score)) * 100, 2)


def compute_similarity_scores(resume_text: str, jd_text: str) -> dict:
    """
    Compute both similarity metrics for a resume/JD pair.

    Returns:
        {
            "tfidf_similarity": float,
            "semantic_similarity": float | None,  # None if model unavailable
        }
    """
    return {
        "tfidf_similarity": tfidf_cosine_similarity(resume_text, jd_text),
        "semantic_similarity": semantic_similarity(resume_text, jd_text),
    }

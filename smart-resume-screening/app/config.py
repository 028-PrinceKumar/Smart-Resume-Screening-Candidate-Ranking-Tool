"""
Central configuration for the Smart Resume Screening & Candidate Ranking Tool.

All tunable parameters (scoring weights, thresholds, file limits, DB settings)
live here so the rest of the codebase never hard-codes "magic numbers".
Values are read from environment variables where relevant, with sane defaults
for local development.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SAMPLE_RESUME_DIR = DATA_DIR / "sample_resumes"
SAMPLE_JD_DIR = DATA_DIR / "sample_job_descriptions"
MODELS_DIR = BASE_DIR / "models"

# --------------------------------------------------------------------------
# MongoDB
# --------------------------------------------------------------------------
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "resume_screening")

# --------------------------------------------------------------------------
# API
# --------------------------------------------------------------------------
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_BASE_URL = os.getenv("API_BASE_URL", f"http://localhost:{API_PORT}")

# --------------------------------------------------------------------------
# File upload limits
# --------------------------------------------------------------------------
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "5"))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_RESUME_EXTENSIONS = {".pdf", ".docx"}

# --------------------------------------------------------------------------
# Scoring weights (must sum to 1.0). Configurable without touching logic.
# --------------------------------------------------------------------------
SCORE_WEIGHTS = {
    "skill_match": float(os.getenv("WEIGHT_SKILL_MATCH", "0.40")),
    "semantic_similarity": float(os.getenv("WEIGHT_SEMANTIC_SIMILARITY", "0.30")),
    "experience_match": float(os.getenv("WEIGHT_EXPERIENCE_MATCH", "0.20")),
    "education_match": float(os.getenv("WEIGHT_EDUCATION_MATCH", "0.10")),
}

_weight_sum = sum(SCORE_WEIGHTS.values())
if not abs(_weight_sum - 1.0) < 1e-6:
    raise ValueError(
        f"SCORE_WEIGHTS must sum to 1.0, got {_weight_sum}. Check your .env overrides."
    )

# --------------------------------------------------------------------------
# Shortlisting
# --------------------------------------------------------------------------
SHORTLIST_THRESHOLD = float(os.getenv("SHORTLIST_THRESHOLD", "70.0"))

# --------------------------------------------------------------------------
# Semantic similarity model
# --------------------------------------------------------------------------
# Sentence-Transformers model used for semantic matching. Fully local/open
# source - no paid API involved. If the model/library is unavailable the
# system automatically falls back to TF-IDF cosine similarity only.
SENTENCE_TRANSFORMER_MODEL = os.getenv(
    "SENTENCE_TRANSFORMER_MODEL", "all-MiniLM-L6-v2"
)
USE_SEMANTIC_MATCHING = os.getenv("USE_SEMANTIC_MATCHING", "true").lower() == "true"

# --------------------------------------------------------------------------
# Skill database (extendable). Kept as a plain Python list so it is trivial
# to extend from code or load from a JSON/YAML file in the future.
# --------------------------------------------------------------------------
DEFAULT_SKILL_DB = [
    "Python", "C++", "C", "Java", "JavaScript", "TypeScript", "SQL", "MySQL",
    "PostgreSQL", "MongoDB", "Pandas", "NumPy", "Scikit-learn", "TensorFlow",
    "PyTorch", "Keras", "NLP", "Natural Language Processing", "Machine Learning",
    "Deep Learning", "Computer Vision", "FastAPI", "Flask", "Django", "Docker",
    "Kubernetes", "AWS", "Azure", "GCP", "Git", "GitHub", "GitLab", "CI/CD",
    "Power BI", "Excel", "Tableau", "Spark", "Hadoop", "Airflow", "REST API",
    "GraphQL", "React", "Node.js", "Streamlit", "Linux", "Bash", "R",
    "Data Analysis", "Data Visualization", "Statistics", "A/B Testing",
    "ETL", "Data Engineering", "MLOps", "HTML", "CSS", "Sentence Transformers",
]

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

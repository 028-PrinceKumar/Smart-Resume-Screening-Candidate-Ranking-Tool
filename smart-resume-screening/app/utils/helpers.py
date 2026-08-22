"""General-purpose helper utilities used across the application."""
from __future__ import annotations

import logging
import re
import uuid
from pathlib import Path
from typing import Any

from app.config import ALLOWED_RESUME_EXTENSIONS, LOG_LEVEL, MAX_FILE_SIZE_BYTES


def get_logger(name: str) -> logging.Logger:
    """Return a configured module-level logger (idempotent)."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(LOG_LEVEL)
    return logger


logger = get_logger(__name__)


class FileValidationError(Exception):
    """Raised when an uploaded resume fails validation."""


def validate_resume_file(filename: str, file_size: int) -> None:
    """
    Validate an uploaded resume before any processing happens.

    Raises FileValidationError with a clear, user-facing message on failure.
    Never lets a single bad file crash the whole batch upload.
    """
    if not filename:
        raise FileValidationError("Uploaded file has no filename.")

    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_RESUME_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_RESUME_EXTENSIONS))
        raise FileValidationError(
            f"Unsupported file type '{ext}' for '{filename}'. Allowed types: {allowed}."
        )

    if file_size <= 0:
        raise FileValidationError(f"'{filename}' appears to be empty.")

    if file_size > MAX_FILE_SIZE_BYTES:
        max_mb = MAX_FILE_SIZE_BYTES / (1024 * 1024)
        raise FileValidationError(
            f"'{filename}' exceeds the maximum allowed size of {max_mb:.1f} MB."
        )


def generate_candidate_id() -> str:
    """Generate a short unique identifier for a candidate record."""
    return uuid.uuid4().hex[:12]


def extract_email(text: str) -> str | None:
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return match.group(0) if match else None


def extract_phone(text: str) -> str | None:
    # Matches common phone formats, incl. optional country code.
    pattern = r"(\+?\d{1,3}[-.\s]?)?(\(?\d{3,5}\)?[-.\s]?)?\d{3}[-.\s]?\d{3,4}"
    for match in re.finditer(pattern, text):
        candidate = match.group(0).strip()
        digits = re.sub(r"\D", "", candidate)
        if 8 <= len(digits) <= 13:
            return candidate
    return None


def extract_name(text: str) -> str | None:
    """
    Best-effort name guess: the first non-empty line that looks like a name
    (no digits, no @ symbol, 2-4 words, title-cased-ish).
    Resumes vary wildly in layout, so this is heuristic, not guaranteed.
    """
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    for line in lines[:8]:
        if "@" in line or any(ch.isdigit() for ch in line):
            continue
        words = line.split()
        if 1 <= len(words) <= 4 and all(w.replace(".", "").isalpha() for w in words):
            return line.title()
    return None


def safe_get(d: dict[str, Any], key: str, default: Any = None) -> Any:
    return d.get(key, default) if isinstance(d, dict) else default

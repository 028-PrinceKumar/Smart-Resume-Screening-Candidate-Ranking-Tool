"""Text cleaning and preprocessing shared by all extractors and matchers."""
from __future__ import annotations

import re

_MULTI_SPACE_RE = re.compile(r"[ \t]+")
_MULTI_NEWLINE_RE = re.compile(r"\n{2,}")
_BULLET_RE = re.compile(r"^[\u2022\-\*\u25CF\u25A0]\s*", re.MULTILINE)
_NON_PRINTABLE_RE = re.compile(r"[^\x20-\x7E\n]")


def clean_text(raw_text: str) -> str:
    """
    Normalize resume/JD text for downstream NLP:
    - strip non-printable characters
    - normalize whitespace
    - remove bullet characters
    - lowercase-safe (case is preserved for name/entity extraction upstream;
      callers that need lowercase should call .lower() themselves)
    """
    if not raw_text:
        return ""

    text = _NON_PRINTABLE_RE.sub(" ", raw_text)
    text = _BULLET_RE.sub("", text)
    text = _MULTI_SPACE_RE.sub(" ", text)
    text = _MULTI_NEWLINE_RE.sub("\n", text)
    return text.strip()


def normalize_for_matching(text: str) -> str:
    """Lowercase + collapse whitespace, used specifically for TF-IDF/embedding input."""
    text = clean_text(text)
    text = text.lower()
    text = re.sub(r"[^a-z0-9+#.\s]", " ", text)
    text = _MULTI_SPACE_RE.sub(" ", text)
    return text.strip()


def split_sections(text: str) -> dict[str, str]:
    """
    Best-effort split of a resume into common sections based on header keywords.
    Not perfect (resumes are unstructured) but helps downstream extractors
    focus on the right region of text.
    """
    section_headers = {
        "experience": r"(work experience|professional experience|experience)",
        "education": r"(education|academic background)",
        "skills": r"(skills|technical skills|core competencies)",
        "projects": r"(projects|personal projects|academic projects)",
    }

    lower_text = text.lower()
    positions: list[tuple[int, str]] = []
    for name, pattern in section_headers.items():
        match = re.search(pattern, lower_text)
        if match:
            positions.append((match.start(), name))

    positions.sort(key=lambda x: x[0])
    sections: dict[str, str] = {}
    for idx, (start, name) in enumerate(positions):
        end = positions[idx + 1][0] if idx + 1 < len(positions) else len(text)
        sections[name] = text[start:end].strip()

    if not sections:
        sections["full_text"] = text

    return sections

"""
Resume text extraction from PDF and DOCX files.

Designed to never raise an unhandled exception for a single bad resume -
callers get a ParsedResumeText result with an `error` field set instead,
so batch processing of many resumes can continue safely.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.utils.helpers import get_logger

logger = get_logger(__name__)


@dataclass
class ParsedResumeText:
    filename: str
    text: str
    success: bool
    error: str | None = None


def _extract_pdf_text(file_path: Path) -> str:
    import pdfplumber

    text_parts: list[str] = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
    return "\n".join(text_parts)


def _extract_docx_text(file_path: Path) -> str:
    import docx2txt

    text = docx2txt.process(str(file_path))
    return text or ""


def parse_resume(file_path: str | Path) -> ParsedResumeText:
    """
    Extract raw text from a resume file (.pdf or .docx).

    Handles empty files, corrupted files, and unsupported formats gracefully.
    """
    path = Path(file_path)
    filename = path.name

    if not path.exists():
        return ParsedResumeText(filename, "", False, "File does not exist.")

    if path.stat().st_size == 0:
        return ParsedResumeText(filename, "", False, "File is empty.")

    ext = path.suffix.lower()
    try:
        if ext == ".pdf":
            text = _extract_pdf_text(path)
        elif ext == ".docx":
            text = _extract_docx_text(path)
        else:
            return ParsedResumeText(
                filename, "", False, f"Unsupported file format: {ext}"
            )
    except Exception as exc:  # noqa: BLE001 - we intentionally isolate failures
        logger.warning("Failed to parse resume '%s': %s", filename, exc)
        return ParsedResumeText(
            filename, "", False, f"Could not read file (corrupted or unreadable): {exc}"
        )

    text = text.strip()
    if not text:
        return ParsedResumeText(
            filename, "", False, "No extractable text found (possibly a scanned/image resume)."
        )

    return ParsedResumeText(filename, text, True, None)

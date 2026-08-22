from pathlib import Path

from app.services.resume_parser import parse_resume


def test_parse_nonexistent_file():
    result = parse_resume("/tmp/does_not_exist_12345.pdf")
    assert result.success is False
    assert "does not exist" in result.error.lower()


def test_parse_empty_file(tmp_path: Path):
    empty_file = tmp_path / "empty.pdf"
    empty_file.write_bytes(b"")
    result = parse_resume(empty_file)
    assert result.success is False
    assert "empty" in result.error.lower()


def test_parse_unsupported_format(tmp_path: Path):
    bad_file = tmp_path / "resume.txt"
    bad_file.write_text("Hello world")
    result = parse_resume(bad_file)
    assert result.success is False
    assert "unsupported" in result.error.lower()

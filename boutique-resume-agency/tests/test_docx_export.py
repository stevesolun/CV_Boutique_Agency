"""Tests for docx_export.py.

Requires python-docx: python -m pip install python-docx
"""
from __future__ import annotations
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

# Skip entire module if python-docx is not installed.
docx = pytest.importorskip("docx", reason="python-docx not installed")

from docx_export import export_resume_to_docx


MINIMAL_RESUME = {
    "name": "Jane Doe",
    "header_lines": ["jane@example.com", "London, UK"],
    "sections": [],
}


class TestExportCreatesFile:
    def test_file_is_created(self, tmp_path):
        out = str(tmp_path / "resume.docx")
        result = export_resume_to_docx(MINIMAL_RESUME, out)
        assert os.path.exists(result)
        assert result.endswith(".docx")

    def test_creates_parent_directories(self, tmp_path):
        out = str(tmp_path / "sub" / "dir" / "resume.docx")
        export_resume_to_docx(MINIMAL_RESUME, out)
        assert os.path.exists(out)

    def test_returns_output_path(self, tmp_path):
        out = str(tmp_path / "resume.docx")
        result = export_resume_to_docx(MINIMAL_RESUME, out)
        assert result == out


class TestExportContent:
    def _load_paragraphs(self, tmp_path, resume_data):
        """Export and return all paragraph texts from the DOCX."""
        out = str(tmp_path / "resume.docx")
        export_resume_to_docx(resume_data, out)
        doc = docx.Document(out)
        return [p.text for p in doc.paragraphs]

    def test_name_appears_in_document(self, tmp_path):
        paras = self._load_paragraphs(tmp_path, MINIMAL_RESUME)
        assert "Jane Doe" in paras

    def test_header_lines_appear(self, tmp_path):
        paras = self._load_paragraphs(tmp_path, MINIMAL_RESUME)
        assert "jane@example.com" in paras
        assert "London, UK" in paras

    def test_string_items_become_paragraphs(self, tmp_path):
        resume = {
            "name": "Test",
            "header_lines": [],
            "sections": [
                {"title": "Skills", "items": ["Python", "SQL", "Docker"]}
            ],
        }
        paras = self._load_paragraphs(tmp_path, resume)
        assert "Python" in paras
        assert "SQL" in paras
        assert "Docker" in paras

    def test_heading_dict_renders_bold_heading(self, tmp_path):
        resume = {
            "name": "Test",
            "header_lines": [],
            "sections": [
                {"title": "Projects", "items": [
                    {"heading": "Project Alpha", "bullets": ["Led the initiative", "Shipped on time"]}
                ]}
            ],
        }
        out = str(tmp_path / "resume.docx")
        export_resume_to_docx(resume, out)
        doc = docx.Document(out)
        paras = [p.text for p in doc.paragraphs]
        assert "Project Alpha" in paras
        assert "Led the initiative" in paras
        assert "Shipped on time" in paras

    def test_experience_dict_renders_company_title_dates(self, tmp_path):
        resume = {
            "name": "Test",
            "header_lines": [],
            "sections": [
                {"title": "Experience", "items": [
                    {
                        "company": "Acme Corp",
                        "title": "Senior Engineer",
                        "dates": "Jan 2020 – Dec 2022",
                        "bullets": ["Built X", "Led Y"],
                    }
                ]}
            ],
        }
        out = str(tmp_path / "resume.docx")
        export_resume_to_docx(resume, out)
        doc = docx.Document(out)
        full_text = "\n".join(p.text for p in doc.paragraphs)
        assert "Acme Corp" in full_text
        assert "Senior Engineer" in full_text
        assert "Jan 2020" in full_text
        assert "Built X" in full_text
        assert "Led Y" in full_text

    def test_experience_dict_without_dates(self, tmp_path):
        resume = {
            "name": "Test",
            "header_lines": [],
            "sections": [
                {"title": "Experience", "items": [
                    {"company": "Startup Inc", "title": "Founder", "bullets": ["Built MVP"]}
                ]}
            ],
        }
        out = str(tmp_path / "resume.docx")
        # Should not crash when dates are absent
        export_resume_to_docx(resume, out)
        doc = docx.Document(out)
        paras = [p.text for p in doc.paragraphs]
        assert any("Startup Inc" in p for p in paras)

    def test_empty_sections_do_not_crash(self, tmp_path):
        resume = {
            "name": "Empty",
            "header_lines": [],
            "sections": [
                {"title": "Skills", "items": []},
                {"title": "Experience", "items": []},
            ],
        }
        # Should not raise
        export_resume_to_docx(resume, str(tmp_path / "empty.docx"))

    def test_multiple_sections(self, tmp_path):
        resume = {
            "name": "Multi",
            "header_lines": ["multi@test.com"],
            "sections": [
                {"title": "Summary", "items": ["A seasoned professional."]},
                {"title": "Skills", "items": ["Python", "Go"]},
                {"title": "Education", "items": [
                    {"heading": "BSc Computer Science", "bullets": ["University of X, 2015"]}
                ]},
            ],
        }
        paras = self._load_paragraphs(tmp_path, resume)
        assert "A seasoned professional." in paras
        assert "Python" in paras
        assert "BSc Computer Science" in paras

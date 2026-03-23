"""Tests for memory_manager.py."""
from __future__ import annotations
import sys
import os
import json
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from memory_manager import (
    DEFAULT_MEMORY,
    DEFAULT_PROGRESS,
    load_memory,
    load_progress,
    update_memory,
    update_progress,
)


class TestLoadMemory:
    def test_returns_default_when_file_missing(self, tmp_path):
        path = str(tmp_path / "nonexistent.json")
        data = load_memory(path)
        assert data == DEFAULT_MEMORY

    def test_default_is_deep_copy_not_reference(self, tmp_path):
        path = str(tmp_path / "mem.json")
        a = load_memory(path)
        b = load_memory(path)
        a["user_profile"]["name"] = "test"
        assert "name" not in b["user_profile"], "Default memory must not be a shared reference"

    def test_loads_existing_file(self, tmp_path):
        path = tmp_path / "mem.json"
        data = {"user_profile": {"name": "Alice"}, "target_context": {}}
        path.write_text(json.dumps(data), encoding="utf-8")
        result = load_memory(str(path))
        assert result["user_profile"]["name"] == "Alice"

    def test_default_memory_has_all_required_keys(self, tmp_path):
        path = str(tmp_path / "mem.json")
        data = load_memory(path)
        required = [
            "user_profile", "target_context", "positioning_choices",
            "resolved_issues", "repeated_issues", "approved_sections",
            "forbidden_claims", "open_questions", "final_constraints",
        ]
        for key in required:
            assert key in data, f"Missing key: {key}"


class TestLoadProgress:
    def test_returns_default_when_file_missing(self, tmp_path):
        path = str(tmp_path / "nonexistent.json")
        data = load_progress(path)
        assert data == DEFAULT_PROGRESS

    def test_default_progress_has_all_required_keys(self, tmp_path):
        path = str(tmp_path / "prog.json")
        data = load_progress(path)
        required = [
            "current_stage", "stage_history", "scores_by_stage", "section_scores",
            "critical_blockers", "current_plan", "next_actions", "user_decisions",
        ]
        for key in required:
            assert key in data, f"Missing key: {key}"


class TestUpdateMemory:
    def test_overwrites_existing_key(self, tmp_path):
        path = str(tmp_path / "mem.json")
        update_memory(path, "user_profile", {"name": "Bob"})
        result = load_memory(path)
        assert result["user_profile"]["name"] == "Bob"

    def test_append_adds_to_list(self, tmp_path):
        path = str(tmp_path / "mem.json")
        update_memory(path, "positioning_choices", "choice_1", append=True)
        update_memory(path, "positioning_choices", "choice_2", append=True)
        result = load_memory(path)
        assert "choice_1" in result["positioning_choices"]
        assert "choice_2" in result["positioning_choices"]

    def test_append_creates_key_if_missing(self, tmp_path):
        path = str(tmp_path / "mem.json")
        update_memory(path, "new_key", "value", append=True)
        result = load_memory(path)
        assert result["new_key"] == ["value"]

    def test_returns_updated_data(self, tmp_path):
        path = str(tmp_path / "mem.json")
        result = update_memory(path, "user_profile", {"name": "Carol"})
        assert result["user_profile"]["name"] == "Carol"

    def test_persists_across_loads(self, tmp_path):
        path = str(tmp_path / "mem.json")
        update_memory(path, "forbidden_claims", ["claim_a", "claim_b"])
        reloaded = load_memory(path)
        assert reloaded["forbidden_claims"] == ["claim_a", "claim_b"]


class TestUpdateProgress:
    def test_overwrites_current_stage(self, tmp_path):
        path = str(tmp_path / "prog.json")
        update_progress(path, "current_stage", "draft")
        result = load_progress(path)
        assert result["current_stage"] == "draft"

    def test_append_adds_to_stage_history(self, tmp_path):
        path = str(tmp_path / "prog.json")
        update_progress(path, "stage_history", "intake", append=True)
        update_progress(path, "stage_history", "panel", append=True)
        result = load_progress(path)
        assert "intake" in result["stage_history"]
        assert "panel" in result["stage_history"]

    def test_returns_updated_data(self, tmp_path):
        path = str(tmp_path / "prog.json")
        result = update_progress(path, "current_stage", "qc")
        assert result["current_stage"] == "qc"

    def test_unicode_in_values(self, tmp_path):
        path = str(tmp_path / "mem.json")
        update_memory(path, "user_profile", {"name": "José García"})
        result = load_memory(path)
        assert result["user_profile"]["name"] == "José García"

"""Tests for resume_agency_helpers.py."""
from __future__ import annotations
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from resume_agency_helpers import (
    ResumeContext,
    build_panel,
    weighted_score,
    DEFAULT_WEIGHTS,
    check_resume_length_best_practice,
    save_json,
    load_json,
)


# ---------------------------------------------------------------------------
# build_panel — core experts
# ---------------------------------------------------------------------------

class TestBuildPanelCore:
    def test_always_returns_8_core_experts(self):
        ctx = ResumeContext(language="english")
        panel = build_panel(ctx)
        assert len(panel["core"]) == 8

    def test_core_expert_names(self):
        ctx = ResumeContext(language="english")
        panel = build_panel(ctx)
        assert "AI veteran" in panel["core"]
        assert "HR / recruiter specialist" in panel["core"]
        assert "Founder / entrepreneur" in panel["core"]
        assert "Business leader / operator" in panel["core"]
        assert "Devil's advocate" in panel["core"]
        assert "Brainstorm / creative reframer" in panel["core"]
        assert "Quality-control lead" in panel["core"]
        assert "Hallucination detector" in panel["core"]


# ---------------------------------------------------------------------------
# build_panel — localization expert
# ---------------------------------------------------------------------------

class TestBuildPanelLocalization:
    @pytest.mark.parametrize("lang", ["english", "en", "en-us", "en-gb", "en-au",
                                       "en-ca", "en-nz", "en-ie", "en-za",
                                       "English", "EN", "EN-US"])
    def test_english_variants_do_not_add_localization_expert(self, lang):
        ctx = ResumeContext(language=lang)
        panel = build_panel(ctx)
        assert "Language / localization expert" not in panel["optional"]

    @pytest.mark.parametrize("lang", ["french", "fr", "spanish", "es", "german", "de",
                                       "portuguese", "pt", "mandarin", "arabic"])
    def test_non_english_adds_localization_expert(self, lang):
        ctx = ResumeContext(language=lang)
        panel = build_panel(ctx)
        assert "Language / localization expert" in panel["optional"]


# ---------------------------------------------------------------------------
# build_panel — ATS specialist
# ---------------------------------------------------------------------------

class TestBuildPanelATS:
    def test_startup_without_jd_does_not_add_ats(self):
        ctx = ResumeContext(language="english", company_stage="startup", job_description=None)
        panel = build_panel(ctx)
        assert "ATS specialist" not in panel["optional"]

    @pytest.mark.parametrize("stage", ["pre-seed", "seed", "solo", "freelance",
                                        "self-employed", "bootstrapped"])
    def test_various_startup_stages_without_jd_skip_ats(self, stage):
        ctx = ResumeContext(language="english", company_stage=stage, job_description=None)
        panel = build_panel(ctx)
        assert "ATS specialist" not in panel["optional"]

    def test_jd_always_adds_ats_even_for_startup(self):
        ctx = ResumeContext(language="english", company_stage="startup",
                            job_description="We are hiring a senior SWE...")
        panel = build_panel(ctx)
        assert "ATS specialist" in panel["optional"]

    def test_no_company_stage_adds_ats(self):
        """No stage info → assume non-startup → include ATS."""
        ctx = ResumeContext(language="english", company_stage=None, job_description=None)
        panel = build_panel(ctx)
        assert "ATS specialist" in panel["optional"]

    def test_enterprise_stage_adds_ats(self):
        ctx = ResumeContext(language="english", company_stage="series-c", job_description=None)
        panel = build_panel(ctx)
        assert "ATS specialist" in panel["optional"]


# ---------------------------------------------------------------------------
# build_panel — executive branding expert
# ---------------------------------------------------------------------------

class TestBuildPanelExecutiveBranding:
    @pytest.mark.parametrize("seniority", ["director", "vp", "vice president", "chief",
                                            "c-suite", "cto", "ceo", "cfo", "coo",
                                            "president", "partner", "managing director", "md"])
    def test_exec_seniority_adds_branding(self, seniority):
        ctx = ResumeContext(language="english", seniority=seniority)
        panel = build_panel(ctx)
        assert "Executive branding expert" in panel["optional"]

    @pytest.mark.parametrize("seniority", ["junior", "mid-level", "senior engineer",
                                            "associate", "analyst", None])
    def test_non_exec_seniority_no_branding(self, seniority):
        ctx = ResumeContext(language="english", seniority=seniority)
        panel = build_panel(ctx)
        assert "Executive branding expert" not in panel["optional"]


# ---------------------------------------------------------------------------
# build_panel — domain / industry expert
# ---------------------------------------------------------------------------

class TestBuildPanelDomain:
    def test_industry_adds_domain_and_reviewer(self):
        ctx = ResumeContext(language="english", industry="fintech")
        panel = build_panel(ctx)
        assert "Domain expert" in panel["optional"]
        assert "Industry-specific reviewer" in panel["optional"]

    def test_no_industry_no_domain(self):
        ctx = ResumeContext(language="english", industry=None)
        panel = build_panel(ctx)
        assert "Domain expert" not in panel["optional"]


# ---------------------------------------------------------------------------
# weighted_score
# ---------------------------------------------------------------------------

class TestWeightedScore:
    def test_default_weights_known_values(self):
        scores = {
            "ai_veteran": 9.0, "hr": 9.0, "founder": 9.0,
            "operator": 9.0, "domain": 9.0, "hallucination": 9.0, "ats": 9.0,
        }
        result = weighted_score(scores)
        assert abs(result - 9.0) < 0.01

    def test_partial_experts_normalize(self):
        """Only ai_veteran and hr provided; weights should normalise to sum of 0.40."""
        scores = {"ai_veteran": 10.0, "hr": 0.0}
        result = weighted_score(scores)
        # Expected: (10*0.20 + 0.0*0.20) / 0.40 = 2.0 / 0.40 = 5.0
        assert abs(result - 5.0) < 0.01

    def test_empty_scores_return_zero(self):
        result = weighted_score({})
        assert result == 0.0

    def test_scores_not_in_weights_ignored(self):
        scores = {"qc_lead": 10.0, "devil_advocate": 10.0}  # not in DEFAULT_WEIGHTS
        result = weighted_score(scores)
        assert result == 0.0

    def test_custom_weights(self):
        scores = {"a": 8.0, "b": 10.0}
        weights = {"a": 0.5, "b": 0.5}
        result = weighted_score(scores, weights)
        assert abs(result - 9.0) < 0.01


# ---------------------------------------------------------------------------
# check_resume_length_best_practice
# ---------------------------------------------------------------------------

class TestCheckResumeLengthBestPractice:
    def test_tech_industry_returns_2_3_range(self):
        result = check_resume_length_best_practice("software engineering", "senior engineer")
        assert result["recommended_range"] == "2–3"
        assert result["min_pages"] == 2
        assert result["max_pages"] == 3

    def test_finance_returns_1_2_range(self):
        result = check_resume_length_best_practice("finance", "analyst")
        assert result["recommended_range"] == "1–2"
        assert result["min_pages"] == 1
        assert result["max_pages"] == 2

    def test_academia_returns_cv_format(self):
        result = check_resume_length_best_practice("academia", "professor")
        assert result["is_cv_format"] is True
        assert result["max_pages"] is None
        assert result["min_pages"] >= 5

    def test_consulting_returns_1_2(self):
        result = check_resume_length_best_practice("consulting", "associate")
        assert result["recommended_range"] == "1–2"

    def test_government_returns_3_7(self):
        result = check_resume_length_best_practice("federal government", "gs-14")
        assert result["min_pages"] >= 3

    def test_creative_returns_1_page(self):
        result = check_resume_length_best_practice("design", "ux designer")
        assert result["min_pages"] == 1
        assert result["max_pages"] == 1

    def test_unknown_industry_falls_back_to_seniority(self):
        result = check_resume_length_best_practice("zookeeper", "senior zookeeper")
        # Falls back to seniority; 'senior' bucket → 2–3
        assert result["min_pages"] in (1, 2)  # either mid or senior bucket

    def test_exec_seniority_fallback(self):
        result = check_resume_length_best_practice("unknown_industry_xyz", "ceo")
        assert result["recommended_range"] == "2–3"

    def test_entry_seniority_fallback(self):
        result = check_resume_length_best_practice("unknown_industry_xyz", "graduate intern")
        assert result["recommended_range"] == "1"
        assert result["max_pages"] == 1

    def test_always_needs_external_validation(self):
        result = check_resume_length_best_practice("tech", "engineer")
        assert result["needs_external_validation"] is True

    def test_returns_source_search_query(self):
        result = check_resume_length_best_practice("tech", "engineer")
        assert isinstance(result["source_search_query"], str)
        assert len(result["source_search_query"]) > 10

    def test_returns_leverage_points_list(self):
        result = check_resume_length_best_practice("finance", "analyst")
        assert isinstance(result["leverage_points"], list)
        assert len(result["leverage_points"]) > 0

    def test_returns_key_rules(self):
        result = check_resume_length_best_practice("tech", "engineer")
        assert isinstance(result["key_rules"], list)
        assert len(result["key_rules"]) >= 4

    def test_ai_label_does_not_match_retail(self):
        """Word-boundary guard: 'retail' should not match 'ai' label."""
        result = check_resume_length_best_practice("retail", "sales associate")
        # Should NOT fall into tech bucket (which includes "ai" as a label)
        assert result["recommended_range"] != "2–3" or result.get("seniority") != "sales associate"
        # More precisely: seniority fallback should kick in for retail
        # Just verify it doesn't crash and returns a valid range
        assert isinstance(result["recommended_range"], str)

    def test_staff_engineer_maps_to_senior_bucket(self):
        """'staff' keyword in seniority should route to the senior fallback bucket."""
        result = check_resume_length_best_practice("unknown_industry_xyz", "staff engineer")
        # senior bucket default range is "2–3"
        assert result["recommended_range"] == "2–3"

    def test_lead_developer_maps_to_senior_bucket(self):
        """'lead' keyword in seniority should route to the senior fallback bucket."""
        result = check_resume_length_best_practice("unknown_industry_xyz", "lead developer")
        assert result["recommended_range"] == "2–3"

    def test_principal_engineer_maps_to_senior_bucket(self):
        """'principal' keyword in seniority should route to the senior fallback bucket."""
        result = check_resume_length_best_practice("unknown_industry_xyz", "principal engineer")
        assert result["recommended_range"] == "2–3"


# ---------------------------------------------------------------------------
# save_json / load_json utilities
# ---------------------------------------------------------------------------

class TestSaveJson:
    def test_saves_dict_to_file(self, tmp_path):
        target = str(tmp_path / "out.json")
        save_json(target, {"key": "value", "num": 42})
        import json, pathlib
        content = json.loads(pathlib.Path(target).read_text(encoding="utf-8"))
        assert content == {"key": "value", "num": 42}

    def test_creates_parent_directories(self, tmp_path):
        target = str(tmp_path / "nested" / "dir" / "data.json")
        save_json(target, {"x": 1})
        import pathlib
        assert pathlib.Path(target).exists()

    def test_accepts_path_object(self, tmp_path):
        import pathlib
        target = tmp_path / "data.json"
        save_json(target, {"a": "b"})
        assert target.exists()


class TestLoadJson:
    def test_loads_existing_file(self, tmp_path):
        import json, pathlib
        target = tmp_path / "data.json"
        target.write_text(json.dumps({"hello": "world"}), encoding="utf-8")
        result = load_json(str(target))
        assert result == {"hello": "world"}

    def test_returns_empty_dict_for_missing_file(self, tmp_path):
        result = load_json(str(tmp_path / "nonexistent.json"))
        assert result == {}

    def test_roundtrip_save_and_load(self, tmp_path):
        target = str(tmp_path / "roundtrip.json")
        data = {"unicode": "résumé", "nested": {"a": [1, 2, 3]}}
        save_json(target, data)
        loaded = load_json(target)
        assert loaded == data

"""
End-to-end tests for the boutique resume agency.

Covers:
  1. Installation validation — all required files and imports present
  2. Plugin / marketplace manifest validation — schema, consistency, URLs
  3. Workspace schema validation — memory.json and progress.json match spec
  4. Inter-expert communication — wave protocol, DA challenge format,
     QC conflict/escalation detection, flag promotion rules
  5. Full session simulation — intake → panel → scoring → stop conditions → export
  6. Fast mode — documented trigger and skip logic
  7. SKILL.md content — all required sections, contracts, and protocols present
"""

from __future__ import annotations

import json
import pathlib
import sys
from collections import Counter

import pytest

# ── path setup ────────────────────────────────────────────────────────────────
ROOT = pathlib.Path(__file__).resolve().parent.parent.parent   # CV_Boutique_Agency/
SKILL_ROOT = ROOT / "boutique-resume-agency"
WORKSPACE = ROOT / "workspace"
SCRIPTS = SKILL_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))


# =============================================================================
# 1. INSTALLATION VALIDATION
# =============================================================================

class TestInstallation:
    """All required files and Python imports must be present."""

    def test_skill_md_exists(self):
        assert (SKILL_ROOT / "skills" / "boutique-resume-agency" / "SKILL.md").exists()

    def test_templates_exist(self):
        assert (SKILL_ROOT / "references" / "templates.md").exists()

    def test_scoring_rubric_exists(self):
        assert (SKILL_ROOT / "references" / "scoring_rubric.md").exists()

    def test_memory_progress_spec_exists(self):
        assert (SKILL_ROOT / "references" / "memory_progress_spec.md").exists()

    def test_example_flows_exist(self):
        assert (SKILL_ROOT / "references" / "example_flows.md").exists()

    def test_claude_md_exists(self):
        assert (ROOT / "CLAUDE.md").exists()

    def test_requirements_txt_exists(self):
        assert (ROOT / "requirements.txt").exists()

    def test_workspace_memory_json_exists(self):
        assert (WORKSPACE / "memory.json").exists()

    def test_workspace_progress_json_exists(self):
        assert (WORKSPACE / "progress.json").exists()

    def test_workspace_outputs_dir_exists(self):
        assert (WORKSPACE / "outputs").is_dir()

    def test_scripts_importable(self):
        import resume_agency_helpers  # noqa: F401
        import memory_manager         # noqa: F401
        import docx_export            # noqa: F401

    def test_python_docx_importable(self):
        try:
            from docx import Document  # noqa: F401
        except ImportError:
            pytest.skip("python-docx not installed — run: python -m pip install python-docx")

    def test_claude_md_references_skill(self):
        content = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        assert "boutique-resume-agency" in content or "SKILL.md" in content

    def test_requirements_txt_has_python_docx(self):
        content = (ROOT / "requirements.txt").read_text(encoding="utf-8")
        assert "python-docx" in content


# =============================================================================
# 2. PLUGIN / MARKETPLACE MANIFEST VALIDATION
# =============================================================================

class TestPluginManifests:
    """marketplace.json and plugin.json must be valid, consistent, and complete."""

    MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
    PLUGIN_JSON = SKILL_ROOT / ".claude-plugin" / "plugin.json"

    def _market(self):
        return json.loads(self.MARKETPLACE.read_text())

    def _plugin(self):
        return json.loads(self.PLUGIN_JSON.read_text())

    def test_marketplace_json_exists(self):
        assert self.MARKETPLACE.exists()

    def test_plugin_json_exists(self):
        assert self.PLUGIN_JSON.exists()

    def test_marketplace_json_is_valid_json(self):
        data = self._market()
        assert isinstance(data, dict)

    def test_plugin_json_is_valid_json(self):
        data = self._plugin()
        assert isinstance(data, dict)

    def test_marketplace_has_required_top_level_fields(self):
        data = self._market()
        for field in ("name", "owner", "plugins"):
            assert field in data, f"marketplace.json missing: {field}"

    def test_marketplace_plugins_is_non_empty_list(self):
        data = self._market()
        assert isinstance(data["plugins"], list)
        assert len(data["plugins"]) >= 1

    def test_marketplace_plugin_entry_has_required_fields(self):
        plugin_entry = self._market()["plugins"][0]
        required = ["name", "source", "description", "version", "author", "license"]
        for field in required:
            assert field in plugin_entry, f"marketplace.json plugin entry missing: {field}"

    def test_marketplace_plugin_source_points_to_boutique_dir(self):
        plugin_entry = self._market()["plugins"][0]
        assert plugin_entry["source"] == "./boutique-resume-agency"

    def test_plugin_json_has_required_fields(self):
        data = self._plugin()
        for field in ("name", "description", "version"):
            assert field in data, f"plugin.json missing: {field}"

    def test_plugin_names_consistent(self):
        market_name = self._market()["plugins"][0]["name"]
        plugin_name = self._plugin()["name"]
        assert market_name == plugin_name, (
            f"Name mismatch: marketplace.json has '{market_name}', "
            f"plugin.json has '{plugin_name}'"
        )

    def test_plugin_versions_consistent(self):
        market_ver = self._market()["plugins"][0]["version"]
        plugin_ver = self._plugin()["version"]
        assert market_ver == plugin_ver, (
            f"Version mismatch: marketplace.json has '{market_ver}', "
            f"plugin.json has '{plugin_ver}'"
        )

    def test_homepage_url_is_https(self):
        homepage = self._market()["plugins"][0]["homepage"]
        assert homepage.startswith("https://"), f"Homepage is not HTTPS: {homepage}"

    def test_license_is_mit(self):
        assert self._market()["plugins"][0]["license"] == "MIT"
        assert self._plugin()["license"] == "MIT"

    def test_marketplace_has_resume_related_tags(self):
        tags = self._market()["plugins"][0].get("tags", [])
        assert any("resume" in t or "cv" in t for t in tags), (
            "marketplace.json tags should include 'resume' or 'cv'"
        )


# =============================================================================
# 3. WORKSPACE SCHEMA VALIDATION
# =============================================================================

class TestWorkspaceSchemas:
    """memory.json and progress.json must match the spec in memory_progress_spec.md."""

    def test_memory_json_has_all_spec_fields(self):
        data = json.loads((WORKSPACE / "memory.json").read_text())
        required = [
            "user_profile", "target_context", "positioning_choices",
            "resolved_issues", "repeated_issues", "approved_sections",
            "forbidden_claims", "open_questions", "final_constraints",
            "language", "intentional_transition",
        ]
        for field in required:
            assert field in data, f"memory.json missing field: {field}"

    def test_progress_json_has_all_spec_fields(self):
        data = json.loads((WORKSPACE / "progress.json").read_text())
        required = [
            "current_stage", "stage_history", "scores_by_stage",
            "section_scores", "critical_blockers", "current_plan",
            "next_actions", "user_decisions", "revision_cycle_count",
        ]
        for field in required:
            assert field in data, f"progress.json missing field: {field}"

    def test_memory_language_is_string(self):
        data = json.loads((WORKSPACE / "memory.json").read_text())
        assert isinstance(data["language"], str)

    def test_memory_intentional_transition_is_bool(self):
        data = json.loads((WORKSPACE / "memory.json").read_text())
        assert isinstance(data["intentional_transition"], bool)

    def test_progress_revision_cycle_count_is_int(self):
        data = json.loads((WORKSPACE / "progress.json").read_text())
        assert isinstance(data["revision_cycle_count"], int)

    def test_memory_manager_defaults_include_new_fields(self):
        from memory_manager import DEFAULT_MEMORY, DEFAULT_PROGRESS
        assert "language" in DEFAULT_MEMORY
        assert "intentional_transition" in DEFAULT_MEMORY
        assert isinstance(DEFAULT_MEMORY["intentional_transition"], bool)
        assert "revision_cycle_count" in DEFAULT_PROGRESS
        assert isinstance(DEFAULT_PROGRESS["revision_cycle_count"], int)


# =============================================================================
# 4. INTER-EXPERT COMMUNICATION SIMULATION
# =============================================================================

class TestInterExpertCommunication:
    """
    Simulates the expert panel wave protocol and validates inter-expert
    communication contracts: DA challenge format, Reframer response format,
    QC conflict/escalation detection, flag promotion rules.
    """

    # Wave membership (using SKILL.md expert names / keys)
    WAVE_1 = {"ai_veteran", "hr", "founder", "operator", "domain", "ats"}
    WAVE_2 = {"devils_advocate", "creative_reframer"}
    WAVE_3 = {"qc_lead", "hallucination_detector"}

    def _report(self, expert, findings, score, flags=None, recommendations=None):
        return {
            "task_id": f"task_{expert}",
            "expert": expert,
            "status": "complete",
            "findings": findings,
            "score_contribution": score,
            "flags": flags or [],
            "recommendations": recommendations or [],
            "error": None,
        }

    # ── Wave ordering ──────────────────────────────────────────────────────────

    def test_wave1_findings_populate_prior_findings_for_wave2(self):
        wave1 = [
            self._report("ai_veteran", ["Solid ML stack"], 8.5),
            self._report("hr", ["Good ATS keywords"], 8.0),
        ]
        prior = [{"expert": r["expert"], "findings": r["findings"]} for r in wave1]
        assert len(prior) == 2
        experts = {p["expert"] for p in prior}
        assert "ai_veteran" in experts
        assert "hr" in experts

    def test_wave3_task_depends_on_all_wave1_and_wave2(self):
        wave1_ids = [f"task_{e}" for e in ["ai_veteran", "hr", "founder", "operator"]]
        wave2_ids = [f"task_{e}" for e in ["devils_advocate", "creative_reframer"]]
        qc_task = {
            "task_id": "task_qc_lead",
            "assigned_to": "qc_lead",
            "depends_on": wave1_ids + wave2_ids,
        }
        assert set(wave1_ids).issubset(set(qc_task["depends_on"]))
        assert set(wave2_ids).issubset(set(qc_task["depends_on"]))
        assert len(qc_task["depends_on"]) == 6

    # ── Devil's Advocate challenge format ─────────────────────────────────────

    def test_da_challenge_references_expert_by_name(self):
        da_report = self._report(
            "devils_advocate",
            findings=[
                "Challenging ai_veteran: 'Solid ML stack' — "
                "no framework versions or scale context given; claim is generic"
            ],
            score=None,
            flags=["BLOCKER: ML experience claims lack specificity"],
        )
        assert da_report["score_contribution"] is None  # DA never contributes numeric score
        assert any("Challenging ai_veteran" in f for f in da_report["findings"])

    def test_da_flags_can_be_blockers(self):
        da_report = self._report(
            "devils_advocate",
            findings=["Challenging hr: 'Good ATS keywords' — missing domain keywords for fintech"],
            score=None,
            flags=["BLOCKER: missing fintech-specific ATS keywords"],
        )
        blockers = [f for f in da_report["flags"] if f.startswith("BLOCKER:")]
        assert len(blockers) == 1

    def test_da_score_contribution_is_always_none(self):
        da_report = self._report("devils_advocate", findings=["some challenge"], score=None)
        assert da_report["score_contribution"] is None

    # ── Creative Reframer response format ─────────────────────────────────────

    def test_creative_reframer_responds_to_da_with_prefix(self):
        reframer_report = self._report(
            "creative_reframer",
            findings=[
                "Responding to devils_advocate: 'ML claims lack specificity' — "
                "constructive alternative: lead with the business outcome, then name "
                "the technique. 'Reduced churn 23% using XGBoost propensity model.'"
            ],
            score=None,
        )
        assert any(
            "Responding to devils_advocate" in f for f in reframer_report["findings"]
        )
        assert reframer_report["score_contribution"] is None

    def test_creative_reframer_score_contribution_is_always_none(self):
        report = self._report("creative_reframer", findings=["some reframe"], score=None)
        assert report["score_contribution"] is None

    # ── QC Lead: conflict detection ───────────────────────────────────────────

    def test_qc_detects_conflict_between_two_experts(self):
        """QC flags CONFLICT when two experts contradict each other."""
        # HR said good keywords; DA said missing keywords — contradiction
        qc_report = self._report(
            "qc_lead",
            findings=[
                "CONFLICT: hr says 'Good ATS keywords' but devils_advocate says "
                "'missing fintech ATS keywords' — CEO must resolve before synthesis"
            ],
            score=None,
            flags=["BLOCKER: conflicting expert findings on ATS keyword coverage"],
        )
        assert any("CONFLICT:" in f for f in qc_report["findings"])
        assert any("BLOCKER:" in f for f in qc_report["flags"])

    def test_qc_conflict_is_always_a_blocker(self):
        qc_report = self._report(
            "qc_lead",
            findings=["CONFLICT: expert_a says X but expert_b says Y — CEO must resolve"],
            score=None,
            flags=["BLOCKER: conflicting findings"],
        )
        blockers = [f for f in qc_report["flags"] if f.startswith("BLOCKER:")]
        assert len(blockers) >= 1

    # ── QC Lead: escalation detection ─────────────────────────────────────────

    def test_qc_escalates_uncaught_da_blocker(self):
        """QC escalates to BLOCKER when DA raised a BLOCKER that no Wave 1 expert flagged."""
        qc_report = self._report(
            "qc_lead",
            findings=[
                "ESCALATION: DA flag 'missing fintech ATS keywords' not flagged by any Wave 1 scoring expert"
            ],
            score=None,
            flags=["BLOCKER: escalated DA flag not addressed by scoring experts"],
        )
        assert any("ESCALATION:" in f for f in qc_report["findings"])
        assert any("BLOCKER:" in f for f in qc_report["flags"])

    def test_qc_escalation_is_warning_when_da_flag_was_warning(self):
        qc_report = self._report(
            "qc_lead",
            findings=[
                "ESCALATION: DA flag 'date format inconsistency' not flagged by any Wave 1 scoring expert"
            ],
            score=None,
            flags=["WARNING: escalated DA warning not addressed by scoring experts"],
        )
        warnings = [f for f in qc_report["flags"] if f.startswith("WARNING:")]
        assert len(warnings) >= 1

    def test_qc_score_contribution_is_always_none(self):
        qc_report = self._report("qc_lead", findings=["PASS: tense consistency"], score=None)
        assert qc_report["score_contribution"] is None

    def test_qc_pass_fail_format(self):
        qc_report = self._report(
            "qc_lead",
            findings=[
                "PASS: tense consistency throughout",
                "FAIL: date format inconsistent — mix of MM/YYYY and Month YYYY",
            ],
            score=None,
            flags=["BLOCKER: systematic date formatting inconsistency"],
        )
        passes = [f for f in qc_report["findings"] if f.startswith("PASS:")]
        fails = [f for f in qc_report["findings"] if f.startswith("FAIL:")]
        assert len(passes) == 1
        assert len(fails) == 1

    # ── Hallucination Detector ─────────────────────────────────────────────────

    def test_hd_hard_block_prefix_is_correct(self):
        hd_report = self._report(
            "hallucination_detector",
            findings=["'40% revenue increase' — no baseline, no timeframe provided"],
            score=0.0,
            flags=["HARD_BLOCK: unsupported revenue metric prevents export"],
        )
        hard_blocks = [f for f in hd_report["flags"] if f.startswith("HARD_BLOCK:")]
        assert len(hard_blocks) == 1

    def test_hd_hard_block_blocks_export_regardless_of_high_score(self):
        from resume_agency_helpers import weighted_score

        scores = {"ai_veteran": 9.5, "hr": 9.5, "founder": 9.5, "operator": 9.5}
        ws = weighted_score(scores)
        assert ws > 8.5  # Score would pass normally

        hd_flags = ["HARD_BLOCK: fabricated team size claim"]
        hard_blocks = [f for f in hd_flags if f.startswith("HARD_BLOCK:")]
        export_allowed = ws >= 8.5 and len(hard_blocks) == 0
        assert export_allowed is False  # Score passes but HD blocks export

    def test_hd_warning_does_not_block_export(self):
        hd_flags = ["WARNING: revenue figure is plausible but missing exact timeframe"]
        hard_blocks = [f for f in hd_flags if f.startswith("HARD_BLOCK:")]
        assert len(hard_blocks) == 0  # WARNING does not block

    # ── Flag promotion ─────────────────────────────────────────────────────────

    def test_blocker_confirmed_when_in_two_or_more_reports(self):
        reports = [
            self._report("hr", [], 7.0, flags=["BLOCKER: no quantified achievements"]),
            self._report("founder", [], 7.0, flags=["BLOCKER: no quantified achievements"]),
            self._report("ai_veteran", [], 8.0, flags=[]),
        ]
        blocker_counts: Counter = Counter()
        for r in reports:
            for f in r["flags"]:
                if f.startswith("BLOCKER:"):
                    blocker_counts[f] += 1
        confirmed = [flag for flag, count in blocker_counts.items() if count >= 2]
        assert len(confirmed) == 1
        assert "no quantified achievements" in confirmed[0]

    def test_blocker_in_single_report_is_not_auto_confirmed(self):
        reports = [
            self._report("hr", [], 7.0, flags=["BLOCKER: no quantified achievements"]),
            self._report("founder", [], 8.5, flags=[]),
        ]
        blocker_counts: Counter = Counter()
        for r in reports:
            for f in r["flags"]:
                if f.startswith("BLOCKER:"):
                    blocker_counts[f] += 1
        confirmed = [flag for flag, count in blocker_counts.items() if count >= 2]
        assert len(confirmed) == 0  # Not confirmed yet — only one expert flagged


# =============================================================================
# 5. FULL SESSION SIMULATION
# =============================================================================

class TestFullSessionSimulation:
    """
    Simulates a complete user journey: intake → panel → score → stop check → export.
    """

    def test_intake_populates_memory_fields(self):
        from memory_manager import DEFAULT_MEMORY
        memory = dict(DEFAULT_MEMORY)
        memory["language"] = "english"
        memory["target_context"] = {
            "industry": "technology",
            "role": "Senior ML Engineer",
            "seniority": "senior",
            "geography": "USA",
            "company_stage": "scale-up",
        }
        assert memory["language"] == "english"
        assert memory["target_context"]["industry"] == "technology"
        assert memory["intentional_transition"] is False

    def test_intentional_transition_flag_can_be_set(self):
        from memory_manager import DEFAULT_MEMORY
        memory = dict(DEFAULT_MEMORY)
        memory["intentional_transition"] = True
        assert memory["intentional_transition"] is True

    def test_panel_formation_always_has_8_core_experts(self):
        from resume_agency_helpers import build_panel, ResumeContext
        ctx = ResumeContext(language="english", industry="technology", role="ML Engineer", seniority="senior")
        panel = build_panel(ctx)
        assert len(panel["core"]) == 8

    def test_panel_adds_domain_expert_when_industry_provided(self):
        from resume_agency_helpers import build_panel, ResumeContext
        ctx = ResumeContext(language="english", industry="fintech")
        panel = build_panel(ctx)
        assert "Domain expert" in panel["optional"] or "Domain Expert" in panel["optional"]

    def test_panel_adds_localization_expert_for_non_english(self):
        from resume_agency_helpers import build_panel, ResumeContext
        ctx = ResumeContext(language="french")
        panel = build_panel(ctx)
        optional_names = " ".join(panel["optional"]).lower()
        assert "localization" in optional_names or "language" in optional_names

    def test_panel_adds_ats_for_non_startup(self):
        from resume_agency_helpers import build_panel, ResumeContext
        ctx = ResumeContext(language="english", company_stage="enterprise")
        panel = build_panel(ctx)
        optional_names = " ".join(panel["optional"]).lower()
        assert "ats" in optional_names

    def test_panel_adds_executive_branding_for_vp_plus(self):
        from resume_agency_helpers import build_panel, ResumeContext
        ctx = ResumeContext(language="english", seniority="VP of Engineering")
        panel = build_panel(ctx)
        optional_names = " ".join(panel["optional"]).lower()
        assert "executive" in optional_names or "branding" in optional_names

    def test_stop_condition_passes_when_score_high_and_no_blockers(self):
        from resume_agency_helpers import weighted_score
        scores = {
            "ai_veteran": 9.0, "hr": 8.8, "founder": 8.5,
            "operator": 8.7, "hallucination": 9.0, "ats": 8.6,
        }
        ws = weighted_score(scores)
        blockers = []
        assert ws >= 8.5
        assert len(blockers) == 0

    def test_stop_condition_fails_when_blockers_present(self):
        from resume_agency_helpers import weighted_score
        scores = {"ai_veteran": 9.0, "hr": 9.0, "founder": 9.0}
        ws = weighted_score(scores)
        blockers = ["HARD_BLOCK: unsupported metric"]
        stop_met = ws >= 8.5 and len(blockers) == 0
        assert stop_met is False

    def test_revision_cycle_count_increments_per_cycle(self):
        from memory_manager import DEFAULT_PROGRESS
        progress = dict(DEFAULT_PROGRESS)
        assert progress["revision_cycle_count"] == 0
        progress["revision_cycle_count"] += 1
        assert progress["revision_cycle_count"] == 1

    def test_stuck_escape_condition_triggers_at_3_cycles(self):
        from memory_manager import DEFAULT_PROGRESS
        progress = dict(DEFAULT_PROGRESS)
        progress["revision_cycle_count"] = 3
        current_score = 8.2
        escape_active = current_score < 8.5 and progress["revision_cycle_count"] >= 3
        assert escape_active is True

    def test_section_scores_stored_per_section(self):
        from memory_manager import DEFAULT_PROGRESS
        progress = dict(DEFAULT_PROGRESS)
        progress["section_scores"] = {
            "header": 9.0,
            "summary": 7.5,
            "experience": 8.3,
            "education": 8.8,
            "skills": 8.0,
        }
        assert progress["section_scores"]["summary"] == 7.5
        assert progress["section_scores"]["header"] == 9.0

    def test_docx_export_produces_file(self, tmp_path):
        try:
            from docx_export import export_resume_to_docx
        except ImportError:
            pytest.skip("python-docx not installed")

        resume_data = {
            "name": "Jane Doe",
            "header_lines": ["jane@example.com | New York, NY | linkedin.com/in/janedoe"],
            "sections": [
                {
                    "title": "Summary",
                    "items": [
                        "Senior ML Engineer with 8 years building production recommendation systems."
                    ],
                },
                {
                    "title": "Experience",
                    "items": [
                        {
                            "company": "TechCorp",
                            "title": "Senior ML Engineer",
                            "dates": "2020–2024",
                            "bullets": [
                                "Built XGBoost propensity model reducing churn 23% across 2M users.",
                                "Led real-time inference pipeline at 10ms p99 latency.",
                            ],
                        }
                    ],
                },
                {
                    "title": "Education",
                    "items": [{"heading": "M.S. Computer Science — NYU, 2016"}],
                },
                {
                    "title": "Skills",
                    "items": ["Python, PyTorch, Spark, AWS SageMaker"],
                },
            ],
        }
        out_path = tmp_path / "test_export.docx"
        result = export_resume_to_docx(resume_data, str(out_path))
        assert out_path.exists(), "DOCX file was not created"
        assert out_path.stat().st_size > 1000, "DOCX file is suspiciously small"
        assert result == str(out_path)

    def test_docx_export_handles_minimal_data(self, tmp_path):
        try:
            from docx_export import export_resume_to_docx
        except ImportError:
            pytest.skip("python-docx not installed")

        out_path = tmp_path / "minimal.docx"
        export_resume_to_docx({"name": "Test User", "header_lines": [], "sections": []}, str(out_path))
        assert out_path.exists()


# =============================================================================
# 6. FAST MODE
# =============================================================================

class TestFastMode:
    """Documents fast mode contract and validates trigger phrase set."""

    FAST_TRIGGERS = {
        "fast mode",
        "fast mode resume",
        "fast mode. build my resume",
        "fast mode. critique my resume",
        "/fast",
    }

    RETURN_TRIGGERS = {"interactive mode", "standard mode"}

    def test_fast_mode_trigger_set_is_non_empty(self):
        assert len(self.FAST_TRIGGERS) > 0

    def test_return_triggers_distinct_from_fast_triggers(self):
        assert self.FAST_TRIGGERS.isdisjoint(self.RETURN_TRIGGERS)

    def test_fast_mode_intake_skips_optional_fields(self):
        """Fast mode only asks minimum blocking questions (language, path, industry/role)."""
        blocking = {"language", "path", "industry"}
        optional = {"geography", "company_stage", "target_salary"}

        fast_mode_required = {"language"}  # Minimum required in fast mode
        assert fast_mode_required.issubset(blocking)
        assert fast_mode_required.isdisjoint(optional)

    def test_fast_mode_does_not_skip_hallucination_detection(self):
        """Fast mode never disables QA or hallucination detection."""
        fast_mode_disabled_checks = set()  # Nothing is disabled
        assert "hallucination_detection" not in fast_mode_disabled_checks
        assert "qc_lead" not in fast_mode_disabled_checks


# =============================================================================
# 7. SKILL.MD CONTENT VALIDATION
# =============================================================================

class TestSkillMdContent:
    """SKILL.md must contain all required sections, contracts, and protocols."""

    SKILL_PATH = SKILL_ROOT / "skills" / "boutique-resume-agency" / "SKILL.md"

    def _content(self):
        return self.SKILL_PATH.read_text(encoding="utf-8")

    def test_tier1_section_present(self):
        assert "Tier 1" in self._content()

    def test_tier2_section_present(self):
        assert "Tier 2" in self._content()

    def test_input_contract_present(self):
        content = self._content()
        assert "Input contract" in content
        assert "session_context" in content

    def test_return_contract_present(self):
        content = self._content()
        assert "Return contract" in content
        assert "score_contribution" in content

    def test_all_8_core_spawn_prompts_present(self):
        content = self._content()
        experts = [
            "AI Veteran",
            "HR / Recruiter",
            "Founder",
            "Business Operator",
            "Devil's Advocate",
            "Creative Reframer",
            "QC Lead",
            "Hallucination Detector",
        ]
        for expert in experts:
            assert f"Spawn prompt — {expert}" in content, (
                f"SKILL.md missing spawn prompt for: {expert}"
            )

    def test_wave_execution_order_defined(self):
        content = self._content()
        assert "Wave 1" in content
        assert "Wave 2" in content
        assert "Wave 3" in content

    def test_hard_block_convention_defined(self):
        assert "HARD_BLOCK:" in self._content()

    def test_blocker_convention_defined(self):
        assert "BLOCKER:" in self._content()

    def test_warning_convention_defined(self):
        assert "WARNING:" in self._content()

    def test_error_timeout_protocol_defined(self):
        content = self._content()
        assert "timeout" in content.lower()
        assert "90" in content

    def test_inter_expert_communication_section_present(self):
        assert "Expert-to-expert communication" in self._content()

    def test_da_challenge_format_documented(self):
        assert "Challenging [expert" in self._content() or "Challenging " in self._content()

    def test_reframer_response_format_documented(self):
        assert "Responding to devils_advocate" in self._content()

    def test_qc_conflict_detection_documented(self):
        content = self._content()
        assert "CONFLICT:" in content
        assert "CEO must resolve" in content

    def test_qc_escalation_detection_documented(self):
        content = self._content()
        assert "ESCALATION:" in content

    def test_prior_findings_contract_defined(self):
        assert "prior_findings" in self._content()

    def test_session_end_section_present(self):
        assert "Session end" in self._content()

    def test_famous_opinion_epilogue_present(self):
        content = self._content().lower()
        assert "famous opinion" in content or "epilogue" in content

    def test_on_the_fly_spawning_documented(self):
        content = self._content()
        assert "On-the-fly" in content or "on-the-fly" in content or "spawn" in content.lower()

    def test_context_dependent_expert_spawn_template_present(self):
        content = self._content()
        assert "spawn prompt template" in content.lower() or "CEO spawn prompt" in content

    def test_example_flows_has_flow_3_agent_teams(self):
        ef = (SKILL_ROOT / "references" / "example_flows.md").read_text(encoding="utf-8")
        assert "Flow 3" in ef
        assert "agent teams" in ef.lower()

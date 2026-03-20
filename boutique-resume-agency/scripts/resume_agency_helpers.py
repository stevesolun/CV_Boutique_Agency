from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional
from pathlib import Path
import json

# Default scoring weights used by weighted_score().
# Keys match the expert names used in score dicts throughout the skill.
DEFAULT_WEIGHTS: Dict[str, float] = {
    "ai_veteran":   0.20,
    "hr":           0.20,
    "founder":      0.15,
    "operator":     0.15,
    "domain":       0.15,
    "hallucination":0.10,
    "ats":          0.05,
}

@dataclass
class PanelContext:
    """Context used to build the expert panel.

    Example::

        ctx = PanelContext(
            language="english",
            industry="fintech",
            role="VP Engineering",
            seniority="vp",
            geography="us",
            company_stage="series-c",
        )
        panel = build_panel(ctx)
    """
    language: str
    industry: Optional[str] = None
    role: Optional[str] = None
    seniority: Optional[str] = None
    geography: Optional[str] = None
    company_stage: Optional[str] = None
    job_description: Optional[str] = None


def build_panel(context: PanelContext) -> Dict[str, Any]:
    """Return core and optional expert lists for the given context.

    Always returns the 8 mandatory core experts.
    Optional experts are added based on context fields.
    """
    core = [
        "AI veteran",
        "HR / recruiter specialist",
        "Founder / entrepreneur",
        "Business leader / operator",
        "Devil's advocate",
        "Brainstorm / creative reframer",
        "Quality-control lead",
        "Hallucination detector",
    ]
    optional = []
    if context.industry:
        optional += ["Domain expert", "Industry-specific reviewer"]
    if context.language and context.language.lower() != "english":
        optional.append("Language / localization expert")
    optional += ["ATS specialist", "Executive branding expert"]
    return {"core": core, "optional": optional}


def weighted_score(
    scores: Dict[str, float],
    weights: Optional[Dict[str, float]] = None,
) -> float:
    """Compute weighted average score across active experts.

    Args:
        scores:  Dict of expert_key -> float score (0–10).
        weights: Dict of expert_key -> float weight. Defaults to
                 DEFAULT_WEIGHTS if not provided. Only keys present
                 in both scores and weights contribute to the result.

    Example::

        score = weighted_score({
            "ai_veteran": 8.9, "hr": 8.5, "founder": 9.1,
            "operator": 8.7, "domain": 9.0, "hallucination": 9.2, "ats": 8.6,
        })
        # Uses DEFAULT_WEIGHTS; returns ~8.93
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS
    used = {k: v for k, v in scores.items() if k in weights}
    if not used:
        return 0.0
    total_weight = sum(weights[k] for k in used)
    return sum(scores[k] * weights[k] for k in used) / total_weight


def save_json(path: str | Path, data: Dict[str, Any]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def load_json(path: str | Path) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def check_resume_length_best_practice(
    industry: str,
    seniority: str,
    geography: Optional[str] = None,
) -> Dict[str, Any]:
    """Return length guidance for the given context.

    Returns recommended_default_pages=None for academic/research roles
    (CVs in those fields follow different conventions and require
    external validation). Returns 2 for all other contexts.
    """
    academic_industries = {"academia", "academic", "research", "university", "education"}
    is_academic = industry.lower() in academic_industries

    return {
        "industry": industry,
        "seniority": seniority,
        "geography": geography,
        "recommended_default_pages": None if is_academic else 2,
        "allow_3_pages_only_if": (
            "academic/research CV — length determined by field convention"
            if is_academic
            else "validated current best practice supports it"
        ),
        "needs_external_validation": True,
        "note": (
            "Academic CVs have no standard page limit — validate against field norms."
            if is_academic
            else "Default is 2 pages for most industries. Validate before recommending 3+."
        ),
    }

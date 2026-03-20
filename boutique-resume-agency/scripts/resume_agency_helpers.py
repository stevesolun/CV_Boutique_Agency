from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional
from pathlib import Path
import json

@dataclass
class PanelContext:
    language: str
    industry: Optional[str] = None
    role: Optional[str] = None
    seniority: Optional[str] = None
    geography: Optional[str] = None
    company_stage: Optional[str] = None
    job_description: Optional[str] = None

def build_panel(context: PanelContext) -> Dict[str, Any]:
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

def weighted_score(scores: Dict[str, float], weights: Dict[str, float]) -> float:
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

def check_resume_length_best_practice(industry: str, seniority: str, geography: Optional[str] = None) -> Dict[str, Any]:
    return {
        "industry": industry,
        "seniority": seniority,
        "geography": geography,
        "recommended_default_pages": 2,
        "allow_3_pages_only_if": "validated current best practice supports it",
        "needs_external_validation": True,
    }

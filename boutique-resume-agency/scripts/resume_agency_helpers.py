from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional
from pathlib import Path
import json
import re

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
    """Return 2025-2026 resume length guidance with leverage points and a search query.

    The returned dict is designed to be used in two steps by the skill:
    1. Use the built-in data as a starting point and baseline recommendation.
    2. Run a web search using ``source_search_query`` to get live, cited sources
       that validate (or update) the recommendation before presenting it to the user.

    Fields
    ------
    recommended_range : str or None
        Human-readable page range, e.g. "2–3". None for academia (no fixed limit).
    min_pages / max_pages : int or None
        Numeric bounds. max_pages is None for academia.
    is_cv_format : bool
        True for academic/research roles — these use CV format, not resume format.
    rationale : str
        Why this range applies to this industry/seniority combination.
    leverage_points : list[str]
        Data-backed arguments to use if the user resists the recommendation.
    source_search_query : str
        Ready-to-use web search query to retrieve current validated sources.
    ats_note : str
        ATS-specific length consideration.
    key_rules : list[str]
        Universal rules that apply regardless of length.
    needs_external_validation : bool
        Always True — skill must run a live search before citing best practice.
    """

    ind = industry.lower().strip()
    sen = seniority.lower().strip()
    geo = (geography or "").lower().strip()

    # ------------------------------------------------------------------ #
    # Industry lookup table — 2025-2026 standards                         #
    # ------------------------------------------------------------------ #
    INDUSTRY_DATA: Dict[str, Dict] = {
        # Keys are match strings (checked with 'in' against ind)
        "tech": {
            "labels": ["tech", "software", "engineering", "it ", "data", "ai", "ml",
                       "developer", "devops", "cloud", "product", "saas"],
            "range": "2–3",
            "min": 2, "max": 3,
            "rationale": (
                "Technical roles require documenting specific tools, languages, frameworks, "
                "and project outcomes. Two pages is the strong default; three is acceptable "
                "for senior engineers or PMs with large portfolios."
            ),
            "leverage": [
                "Most FAANG and top-tier tech recruiters expect 2 pages for senior engineers — "
                "a single page signals under-qualified at staff+ level.",
                "ATS systems (Greenhouse, Lever, Workday) parse 2-page resumes more effectively "
                "for keyword density than single-page resumes.",
                "A third page is only justified if every bullet is a different role, project, or "
                "technical domain — padding kills credibility faster than length.",
            ],
            "search": "software engineer resume length best practices 2025 2026",
            "ats": (
                "2-page resumes score higher keyword density in ATS systems used by tech companies. "
                "3 pages is acceptable for staff/principal/VP roles with distinct project breadth."
            ),
        },
        "healthcare": {
            "labels": ["healthcare", "health", "medicine", "medical", "nursing", "clinical",
                       "biotech", "pharma", "pharmaceutical", "science", "biology", "chemistry",
                       "lab", "research scientist"],
            "range": "2–3",
            "min": 2, "max": 3,
            "rationale": (
                "Healthcare resumes require detailed documentation of licenses, certifications, "
                "clinical rotations, and continuing education. Two to three pages is standard."
            ),
            "leverage": [
                "Licensing bodies and hospital credentialing departments expect complete records — "
                "truncating certifications or clinical history is a compliance risk.",
                "Two pages is the minimum for anyone past residency or a junior lab role.",
            ],
            "search": "healthcare medical resume length best practices 2025 2026",
            "ats": (
                "Healthcare ATS systems expect full certification and license details — "
                "trimming these to fit one page actively harms ATS scoring."
            ),
        },
        "finance": {
            "labels": ["finance", "banking", "investment", "hedge", "private equity", "vc ",
                       "venture capital", "accounting", "cfo", "cpa", "audit", "financial"],
            "range": "1–2",
            "min": 1, "max": 2,
            "rationale": (
                "Finance and banking cultures value concision and signal density. "
                "One page is preferred for analysts and associates; two pages is acceptable "
                "for senior roles with extensive deal history or certifications (CFA, CPA, etc.)."
            ),
            "leverage": [
                "Goldman Sachs, JPMorgan, and most bulge-bracket banks filter for 1-page resumes "
                "at analyst and associate level — a 2-page resume from a 3-year analyst is a red flag.",
                "Private equity and VC firms receive hundreds of applications; two-page resumes "
                "at junior level signal inability to prioritise, which is itself a disqualifier.",
                "Senior finance roles (VP, MD, CFO) can justify 2 pages when certifications and "
                "deal tombstones require the space — anything beyond 2 is actively penalised.",
            ],
            "search": "finance banking resume length best practices 2025 2026",
            "ats": (
                "Most finance ATS and manual processes are optimised for 1-page parsing. "
                "Dense 2-page resumes are accepted at senior level."
            ),
        },
        "legal": {
            "labels": ["legal", "law", "attorney", "lawyer", "counsel", "solicitor",
                       "barrister", "paralegal", "compliance"],
            "range": "1–2",
            "min": 1, "max": 2,
            "rationale": (
                "Legal resumes follow similar conventions to finance — concise and high-signal. "
                "Partners and senior counsel with extensive matters may extend to 2 pages."
            ),
            "leverage": [
                "Law firm hiring partners read dozens of resumes in sequence — a 2-page junior "
                "resume signals poor judgment about what matters.",
                "One page is the expectation for associates with fewer than 7 years experience.",
            ],
            "search": "lawyer attorney resume length best practices 2025 2026",
            "ats": "Legal ATS systems are optimised for 1-page parsing at associate level.",
        },
        "creative": {
            "labels": ["creative", "design", "designer", "marketing", "brand", "advertising",
                       "copywriter", "content", "ux", "ui", "media", "film", "fashion"],
            "range": "1 page + portfolio link",
            "min": 1, "max": 1,
            "rationale": (
                "Creative roles treat the resume as a gateway to the portfolio. "
                "One tight page + a portfolio link is the industry standard — the portfolio "
                "does the heavy lifting on craft, taste, and execution."
            ),
            "leverage": [
                "Creative directors at agencies receive 200+ applications per role — "
                "a 2-page resume without a portfolio link gets binned; a 1-page with a strong "
                "portfolio link gets clicked.",
                "A 1-page resume forces you to surface only your best work, which itself "
                "signals editorial judgment — the very skill you're selling.",
                "The portfolio URL is more valuable than any bullet point — prioritise it over length.",
            ],
            "search": "creative designer marketing resume length portfolio 2025 2026",
            "ats": (
                "Most creative roles use portfolio-first review rather than ATS keyword scoring. "
                "The resume primarily needs to pass a 7-second human scan, not an algorithm."
            ),
        },
        "government": {
            "labels": ["government", "federal", "public sector", "civil service", "military",
                       "defence", "defense", "nsa", "cia", "fbi", "dod", "usajobs"],
            "range": "3–7",
            "min": 3, "max": 7,
            "rationale": (
                "US federal resumes (USAJOBS) require in-depth work histories including hours "
                "worked per week, supervisor names, and full salary history. "
                "3–5 pages is typical; complex senior roles can reach 7."
            ),
            "leverage": [
                "USAJOBS applications are reviewed against a vacancy announcement point by point — "
                "an incomplete federal resume that omits hours worked or GS-level equivalencies "
                "is automatically disqualified, regardless of how strong the experience is.",
                "State and local government roles also typically require 2–3 pages minimum "
                "to satisfy HR documentation requirements.",
            ],
            "search": "federal government resume USAJOBS length requirements 2025 2026",
            "ats": (
                "USAJOBS has its own structured data entry system. The uploaded resume "
                "supplements structured fields rather than replacing them."
            ),
        },
        "academia": {
            "labels": ["academia", "academic", "university", "college", "research", "phd",
                       "professor", "lecturer", "postdoc", "faculty", "scholar", "science"],
            "range": "5–15+ (CV format)",
            "min": 5, "max": None,
            "is_cv_format": True,
            "rationale": (
                "Academic positions use CV format, not resume format. "
                "Full publication lists, grant histories, teaching experience, conference "
                "presentations, and service records are expected. "
                "5 pages is a minimum for a junior faculty application; "
                "senior professors often have 15–30 page CVs."
            ),
            "leverage": [
                "A truncated academic CV signals a thin publication or grant record — "
                "search committees will assume what you've omitted is weak.",
                "Academic hiring committees read CVs cover-to-cover for shortlisted candidates; "
                "brevity is not a virtue in this context.",
            ],
            "search": "academic CV length best practices faculty application 2025",
            "ats": (
                "Academic ATS systems (Interfolio, Workday for universities) are configured "
                "to accept multi-page CVs. Length is not penalised."
            ),
        },
        "consulting": {
            "labels": ["consulting", "consultant", "strategy", "mckinsey", "bcg", "bain",
                       "deloitte", "kpmg", "pwc", "ernst", "ey ", "advisory"],
            "range": "1–2",
            "min": 1, "max": 2,
            "rationale": (
                "Consulting resumes are expected to be intensely structured and concise. "
                "MBB firms expect 1 page for most candidates; 2 pages is acceptable for "
                "experienced industry hires or senior manager+ level."
            ),
            "leverage": [
                "McKinsey, BCG, and Bain all publish explicit guidance preferring 1-page resumes "
                "for MBA and experienced hire applications.",
                "A consulting resume is itself a demonstration of your ability to structure "
                "complex information into a concise, high-impact document — "
                "failing to do that is failing the test before the interview.",
            ],
            "search": "consulting strategy resume length McKinsey BCG Bain best practices 2025",
            "ats": "Most consulting firms use human review for initial screen, not ATS.",
        },
    }

    # ------------------------------------------------------------------ #
    # Match industry to lookup table                                      #
    # Use word-boundary regex so short labels like "ai" don't match      #
    # substrings (e.g. "retail" contains the letters "ai").              #
    # ------------------------------------------------------------------ #
    def _matches(label: str, text: str) -> bool:
        pattern = r"\b" + re.escape(label.strip()) + r"\b"
        return bool(re.search(pattern, text, re.IGNORECASE))

    matched: Optional[Dict] = None
    for _key, data in INDUSTRY_DATA.items():
        if any(_matches(label, ind) for label in data["labels"]):
            matched = data
            break

    # ------------------------------------------------------------------ #
    # Experience-level page range (fallback when no industry match)       #
    # ------------------------------------------------------------------ #
    SENIORITY_DEFAULTS = {
        "entry": {"range": "1", "min": 1, "max": 1,
                  "rationale": "Entry-level candidates (0–5 years) should target 1 page. "
                               "Recruiters expect brevity; a second page signals padding."},
        "mid":   {"range": "1–2", "min": 1, "max": 2,
                  "rationale": "Mid-level candidates (5–15 years) typically fill 1–2 pages comfortably."},
        "senior": {"range": "2–3", "min": 2, "max": 3,
                   "rationale": "Senior candidates (15+ years) can justify 2–3 pages with distinct roles."},
        "exec":  {"range": "2–3", "min": 2, "max": 3,
                  "rationale": "Executive roles (C-suite, VP+) typically require 2–3 pages to cover "
                               "board, advisory, and strategic leadership scope."},
    }

    seniority_bucket = "mid"
    for bucket in ["entry", "mid", "senior", "exec"]:
        if bucket in sen:
            seniority_bucket = bucket
            break
    if any(kw in sen for kw in ["junior", "graduate", "intern", "0-", "1-", "2-", "fresh"]):
        seniority_bucket = "entry"
    elif any(kw in sen for kw in ["director", "vp", "chief", "c-suite", "cto", "ceo", "cfo", "partner"]):
        seniority_bucket = "exec"
    elif any(kw in sen for kw in ["staff", "principal", "architect", "lead", "head of", "15", "20"]):
        seniority_bucket = "senior"

    if matched is None:
        sen_data = SENIORITY_DEFAULTS[seniority_bucket]
        matched = {
            "range": sen_data["range"],
            "min": sen_data["min"],
            "max": sen_data["max"],
            "rationale": sen_data["rationale"],
            "leverage": [
                "Research consistently shows recruiters spend ~7 seconds on initial scan — "
                "pages beyond the recommended range are rarely read.",
                "ATS keyword density is optimised when content is concentrated, not spread thin.",
            ],
            "search": f"resume length best practices {seniority_bucket} level 2025 2026",
            "ats": "Focus keyword density on pages 1–2; additional pages dilute ATS scoring.",
        }

    return {
        "industry": industry,
        "seniority": seniority,
        "geography": geography,
        "recommended_range": matched["range"],
        "min_pages": matched["min"],
        "max_pages": matched["max"],
        "is_cv_format": matched.get("is_cv_format", False),
        "rationale": matched["rationale"],
        "leverage_points": matched["leverage"],
        "source_search_query": matched["search"],
        "ats_note": matched.get("ats", ""),
        "key_rules": [
            "Relevance over length — a tight shorter resume beats a padded longer one.",
            "Avoid 1.5 pages — the second page must be at least one-third full.",
            "Apply the 10-year rule — focus on the last 10–15 years; earlier roles get one line or nothing.",
            "ATS consideration — two-page resumes often score higher keyword density than single-page.",
        ],
        "needs_external_validation": True,
    }

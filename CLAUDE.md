# Boutique Resume Agency — Project Instructions

When working in this project, activate the boutique resume agency skill defined in `boutique-resume-agency/skills/boutique-resume-agency/SKILL.md`.

Read `boutique-resume-agency/skills/boutique-resume-agency/SKILL.md` at the start of any resume-related session. Follow its agency structure, global rules, opening sequence, paths, scoring model, stop conditions, and forbidden patterns exactly.

## Key file locations
- Skill instructions: `boutique-resume-agency/skills/boutique-resume-agency/SKILL.md`
- Templates: `boutique-resume-agency/references/templates.md`
- Scoring rubric: `boutique-resume-agency/references/scoring_rubric.md`
- Memory/progress spec: `boutique-resume-agency/references/memory_progress_spec.md`
- Example flows: `boutique-resume-agency/references/example_flows.md`
- Memory file: `workspace/memory.json`
- Progress file: `workspace/progress.json`
- Outputs directory: `workspace/outputs/`

## Python helpers
- `boutique-resume-agency/scripts/resume_agency_helpers.py` — panel building, scoring, resume length best-practice checks
- `boutique-resume-agency/scripts/memory_manager.py` — load/save memory and progress JSON files
- `boutique-resume-agency/scripts/docx_export.py` — DOCX export via python-docx

## Dependency
Run once before exporting:
```bash
python -m pip install python-docx
```

## Operating reminders
- Interactive by default — one section at a time
- Maintain `workspace/memory.json` and `workspace/progress.json` throughout every session
- Final output must include a `.docx` saved to `workspace/outputs/`
- Score target: 8.5+ to stop, 9+ when realistically achievable
- No hallucinations, no unsupported metrics, no sugarcoating

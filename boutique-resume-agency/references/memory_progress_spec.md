# Memory and Progress Spec

## Files
- `memory.json`
- `progress.json`

## memory.json schema
```json
{
  "user_profile": {},
  "target_context": {},
  "positioning_choices": [],
  "resolved_issues": [],
  "repeated_issues": [],
  "approved_sections": {},
  "forbidden_claims": [],
  "open_questions": [],
  "final_constraints": [],
  "language": "",
  "intentional_transition": false
}
```

`final_constraints` is an array. Append constraint objects — e.g.:
```json
{"type": "page_length", "agreed_range": "2–3", "user_override": false}
```

`language` — ISO language tag or plain name (e.g. `"english"`, `"fr"`, `"spanish"`). Set during intake. Used to determine whether a Language / localization expert is needed.

`intentional_transition` — boolean. Set to `true` when the user confirms a cross-industry career move in Path B (Tailor to JD sub-path). Suppresses the `industry_mismatch` blocker and routes the gap to the creative reframer as a positioning challenge.

## progress.json schema
```json
{
  "current_stage": "",
  "stage_history": [],
  "scores_by_stage": [],
  "section_scores": {},
  "critical_blockers": [],
  "current_plan": [],
  "next_actions": [],
  "user_decisions": [],
  "revision_cycle_count": 0
}
```

`revision_cycle_count` — integer. Incremented by 1 each time a full revision cycle completes (all active experts score + `weighted_score()` called). Used to evaluate the stuck-below-8.5 escape condition (≥ 3 cycles).

## Expert key mapping (for weighted_score())

| Expert name | DEFAULT_WEIGHTS key |
|-------------|---------------------|
| AI veteran | `ai_veteran` |
| HR / recruiter specialist | `hr` |
| Founder / entrepreneur | `founder` |
| Business leader / operator | `operator` |
| Domain expert | `domain` |
| Hallucination detector | `hallucination` |
| ATS specialist | `ats` |
| Devil's advocate | qualitative only — not in DEFAULT_WEIGHTS |
| Brainstorm / creative reframer | qualitative only — not in DEFAULT_WEIGHTS |
| Quality-control lead | qualitative only — not in DEFAULT_WEIGHTS |

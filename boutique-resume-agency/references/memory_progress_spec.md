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
  "final_constraints": []
}
```

`final_constraints` is an array. Append constraint objects — e.g.:
```json
{"type": "page_length", "agreed_range": "2–3", "user_override": false}
```

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
  "user_decisions": []
}
```

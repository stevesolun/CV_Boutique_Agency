from __future__ import annotations
from pathlib import Path
from typing import Dict, Any
import json
from _file_utils import atomic_write_json

DEFAULT_MEMORY = {
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
    "intentional_transition": False,
}

DEFAULT_PROGRESS = {
    "current_stage": "",
    "stage_history": [],
    "scores_by_stage": [],
    "section_scores": {},
    "critical_blockers": [],
    "current_plan": [],
    "next_actions": [],
    "user_decisions": [],
    "revision_cycle_count": 0,
}

def _load(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    if not path.exists():
        return json.loads(json.dumps(default))
    return json.loads(path.read_text(encoding="utf-8"))

def _save(path: Path, data: Dict[str, Any]) -> None:
    atomic_write_json(path, data)

def load_memory(path: str) -> Dict[str, Any]:
    return _load(Path(path), DEFAULT_MEMORY)

def load_progress(path: str) -> Dict[str, Any]:
    return _load(Path(path), DEFAULT_PROGRESS)

def update_memory(path: str, key: str, value: Any, append: bool = False) -> Dict[str, Any]:
    data = load_memory(path)
    if append:
        data.setdefault(key, [])
        data[key].append(value)
    else:
        data[key] = value
    _save(Path(path), data)
    return data

def update_progress(path: str, key: str, value: Any, append: bool = False) -> Dict[str, Any]:
    data = load_progress(path)
    if append:
        data.setdefault(key, [])
        data[key].append(value)
    else:
        data[key] = value
    _save(Path(path), data)
    return data

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict
import json


def atomic_write_json(path: str | Path, data: Dict[str, Any]) -> None:
    """Write *data* as JSON to *path* atomically (temp-file + rename).

    A trailing newline is appended so the file is a well-formed POSIX text
    file. Any stale .tmp left by a previous crashed run is removed first.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.unlink(missing_ok=True)  # clean up stale tmp from previous crash
    try:
        tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        tmp.replace(p)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise

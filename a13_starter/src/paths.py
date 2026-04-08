from __future__ import annotations

import os
from pathlib import Path


def resolve_project_root(anchor_file: str, levels_up: int) -> Path:
    override = os.getenv("A13_PROJECT_ROOT")
    if override:
        return Path(override).expanduser().resolve()
    return Path(anchor_file).resolve().parents[levels_up]


def resolve_runtime_root(project_root: Path) -> Path:
    override = os.getenv("A13_RUNTIME_DIR")
    if override:
        runtime_root = Path(override).expanduser().resolve()
    else:
        runtime_root = project_root
    runtime_root.mkdir(parents=True, exist_ok=True)
    return runtime_root

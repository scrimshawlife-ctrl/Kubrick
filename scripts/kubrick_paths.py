"""Shared immutable-package and mutable-state paths for Kubrick."""

from __future__ import annotations

import os
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parent.parent
PATTERNS_DIR = SKILL_ROOT / "references" / "patterns"
INDEX_PATH = SKILL_ROOT / "references" / "corpus-index.yaml"


def state_root() -> Path:
    configured = os.environ.get("KUBRICK_STATE_DIR", "").strip()
    if configured:
        return Path(configured).expanduser().resolve()
    return (Path.home() / ".openclaw" / "state" / "kubrick").resolve()


def state_paths() -> dict[str, Path]:
    root = state_root()
    return {
        "root": root,
        "cache": root / "cache",
        "registry_cache": root / "cache-registry",
        "receipts": root / "receipts",
        "outcomes": root / "outcomes",
        "evolution": root / "evolution",
        "patterns": root / "patterns",
        "ranking": root / "ranking.json",
    }


def ensure_state_dirs() -> dict[str, Path]:
    paths = state_paths()
    for key in (
        "root",
        "cache",
        "registry_cache",
        "receipts",
        "outcomes",
        "evolution",
        "patterns",
    ):
        paths[key].mkdir(parents=True, exist_ok=True)
    return paths

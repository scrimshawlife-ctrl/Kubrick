#!/usr/bin/env python3
"""Read-only installation and corpus checks for Kubrick."""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

from kubrick_paths import INDEX_PATH, PATTERNS_DIR, SKILL_ROOT, state_root
from retrieve_symbolic_patterns import build_receipt, load_all_patterns, rank_patterns


def check(condition: bool, message: str, failures: list[str]) -> None:
    print(f"{'ok' if condition else 'FAIL'}: {message}")
    if not condition:
        failures.append(message)


def main() -> None:
    failures: list[str] = []
    check(sys.version_info >= (3, 9), "Python 3.9 or newer", failures)
    check((SKILL_ROOT / "SKILL.md").is_file(), "SKILL.md present", failures)
    check(INDEX_PATH.is_file(), "corpus index present", failures)
    patterns = load_all_patterns()
    check(len(patterns) >= 9, "at least nine pattern sidecars load", failures)

    for path in sorted((SKILL_ROOT / "schemas").glob("*.json")):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            failures.append(f"invalid JSON schema: {path.name}")
    check(
        not any(item.startswith("invalid JSON schema") for item in failures),
        "JSON schemas parse",
        failures,
    )

    brief = {
        "dramatic_problem": "identity dissolution and breakdown",
        "genre": "drama",
        "format": "feature",
        "cultural_context": "contemporary",
        "prohibited_patterns": ["broken mirror"],
    }
    ranked, rejected = rank_patterns(brief, patterns)
    receipt = build_receipt(brief, ranked, rejected)["retrieval_receipt"]
    check(receipt["status"] == "SELECTED", "retrieval fixture selects a pattern", failures)
    check(bool(receipt["selected_primary_grammar"]), "primary grammar returned", failures)

    with tempfile.TemporaryDirectory() as directory:
        probe = Path(directory) / "state"
        probe.mkdir()
        check(probe.is_dir(), "temporary state path is writable", failures)
    print(f"configured state: {state_root()}")
    print(f"python3: {shutil.which('python3') or 'not found'}")

    if failures:
        print(json.dumps({"ok": False, "failures": failures}, indent=2))
        raise SystemExit(1)
    print(json.dumps({"ok": True, "patterns": len(patterns)}, indent=2))


if __name__ == "__main__":
    main()

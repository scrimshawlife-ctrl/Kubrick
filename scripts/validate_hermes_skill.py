#!/usr/bin/env python3
"""Validate Kubrick as a portable, self-contained Hermes skill.

Uses only the Python standard library. Run from any working directory:
    python scripts/validate_hermes_skill.py
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
SKILL_FILE = SKILL_ROOT / "SKILL.md"

REQUIRED_FRONTMATTER = {"name", "description", "version", "author"}
REQUIRED_PATHS = [
    "SKILL.md",
    "QUICKSTART.md",
    "references/hermes-runtime-contract.md",
    "references/corpus-index.yaml",
    "references/patterns",
    "schemas/motif-structure-graph.schema.yaml",
    "scripts/retrieve_symbolic_patterns.py",
    "scripts/build_motif_graph.py",
    "scripts/evolve_from_use.py",
    "evals",
]

FORBIDDEN_REPOSITORY_ASSUMPTIONS = [
    re.compile(r"pip install -e"),
    re.compile(r"/Users/"),
    re.compile(r"[A-Za-z]:\\\\Users\\\\"),
    re.compile(r"continuity-forge installed and in PATH", re.IGNORECASE),
]


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must begin with YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("SKILL.md frontmatter is not closed")
    fields: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line or line[0].isspace() or ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"')
    return fields


def referenced_relative_paths(text: str) -> set[str]:
    candidates: set[str] = set()
    for match in re.finditer(r"`((?:references|schemas|scripts|evals|docs)/[^`\n]+)`", text):
        value = match.group(1)
        if " " not in value and not value.startswith("/"):
            candidates.add(value.rstrip(".,;:"))
    return candidates


def validate_python(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError, UnicodeError) as exc:
        errors.append(f"Python compile failure: {path.relative_to(SKILL_ROOT)}: {exc}")
    return errors


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    if not SKILL_FILE.is_file():
        print("FAIL: SKILL.md missing", file=sys.stderr)
        return 1

    skill_text = SKILL_FILE.read_text(encoding="utf-8")

    try:
        frontmatter = parse_frontmatter(skill_text)
    except ValueError as exc:
        errors.append(str(exc))
        frontmatter = {}

    missing_fields = sorted(REQUIRED_FRONTMATTER - set(frontmatter))
    if missing_fields:
        errors.append(f"Missing frontmatter fields: {', '.join(missing_fields)}")
    if frontmatter.get("name") != "kubrick":
        errors.append("Frontmatter name must be 'kubrick'")
    if frontmatter.get("author") != "Hermes":
        errors.append("Frontmatter author must be 'Hermes'")

    for relative in REQUIRED_PATHS:
        path = SKILL_ROOT / relative
        if not path.exists():
            errors.append(f"Required path missing: {relative}")

    for relative in sorted(referenced_relative_paths(skill_text)):
        path = SKILL_ROOT / relative
        if not path.exists():
            warnings.append(f"Referenced path not resolved literally: {relative}")

    for pattern in FORBIDDEN_REPOSITORY_ASSUMPTIONS:
        if pattern.search(skill_text):
            errors.append(f"Repository-only assumption found in SKILL.md: {pattern.pattern}")

    for path in sorted((SKILL_ROOT / "scripts").glob("*.py")):
        errors.extend(validate_python(path))

    runtime_text = (SKILL_ROOT / "references/hermes-runtime-contract.md").read_text(encoding="utf-8")
    if "Continuity Forge" not in runtime_text or "optional" not in runtime_text.lower():
        errors.append("Runtime contract must explicitly keep Continuity Forge optional")
    if "NOT_COMPUTABLE" not in skill_text:
        errors.append("SKILL.md must retain fail-closed NOT_COMPUTABLE behavior")
    if "standalone Hermes skill" not in skill_text:
        errors.append("SKILL.md must explicitly identify Kubrick as a standalone Hermes skill")

    print("Kubrick Hermes Skill Validation")
    print(f"skill_root: {SKILL_ROOT}")
    print(f"version: {frontmatter.get('version', 'UNKNOWN')}")
    print(f"python_scripts_checked: {len(list((SKILL_ROOT / 'scripts').glob('*.py')))}")

    for warning in warnings:
        print(f"WARN: {warning}")
    for error in errors:
        print(f"FAIL: {error}", file=sys.stderr)

    if errors:
        print(f"status: FAIL ({len(errors)} errors, {len(warnings)} warnings)", file=sys.stderr)
        return 1

    print(f"status: PASS ({len(warnings)} warnings)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

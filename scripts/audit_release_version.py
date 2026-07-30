#!/usr/bin/env python3
"""Audit Kubrick release-version declarations against the VERSION manifest."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGETS = {
    "SKILL.md": re.compile(r"^version:\s*([^\s]+)", re.MULTILINE),
    "README.md": re.compile(r"\b(0\.\d+\.\d+)\b"),
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    expected = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    declarations = {}
    mismatches = []
    for relative, pattern in TARGETS.items():
        text = (ROOT / relative).read_text(encoding="utf-8")
        match = pattern.search(text)
        observed = match.group(1) if match else None
        declarations[relative] = observed
        if observed != expected:
            mismatches.append({"file": relative, "expected": expected, "observed": observed})

    report = {
        "status": "READY" if not mismatches else "NOT_READY",
        "expected_version": expected,
        "declarations": declarations,
        "mismatches": mismatches,
        "tag_allowed": not mismatches,
    }
    rendered = json.dumps(report, indent=2)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    print(rendered)
    raise SystemExit(1 if args.strict and mismatches else 0)


if __name__ == "__main__":
    main()

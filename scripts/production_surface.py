#!/usr/bin/env python3
"""Shared deterministic runtime for Kubrick first-class production surfaces.

This bounded v0.15 foundation provides stable argument handling, evidence labels,
authority classes, artifact identities, and fail-closed diagnostics for design,
script, image, and video commands. Domain-specific compilers can replace the
payload builders without changing the public command contract.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VALID_SURFACES = {"design", "script", "image", "video"}
VALID_AUTHORITY = {"PROPOSED", "OBSERVATION", "NOT_COMPUTABLE"}


def _read_text(path: str | None) -> str | None:
    if not path:
        return None
    return Path(path).read_text(encoding="utf-8")


def _stable_id(surface: str, action: str, inputs: dict[str, Any]) -> str:
    canonical = json.dumps(
        {"surface": surface, "action": action, "inputs": inputs},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]
    return f"kubrick-{surface}-{action}-{digest}"


def _required_input(surface: str, action: str) -> bool:
    return action not in {"create", "build"} or surface in {"image", "video"}


def build_artifact(surface: str, action: str, args: argparse.Namespace) -> dict[str, Any]:
    source_text = _read_text(args.input)
    evidence_text = _read_text(args.evidence)
    brief = args.brief

    if _required_input(surface, action) and not any((source_text, evidence_text, brief)):
        return {
            "status": "NOT_COMPUTABLE",
            "authority": "NOT_COMPUTABLE",
            "surface": surface,
            "action": action,
            "diagnostic": {
                "code": "INSUFFICIENT_EVIDENCE",
                "message": "Provide --input, --evidence, or --brief for this action.",
            },
        }

    inputs = {
        "brief": brief,
        "input": source_text,
        "evidence": evidence_text,
        "provider": args.provider,
        "project_id": args.project_id,
    }
    artifact_id = _stable_id(surface, action, inputs)

    artifact: dict[str, Any] = {
        "schema_version": "0.15-foundation",
        "artifact_id": artifact_id,
        "surface": surface,
        "action": action,
        "status": "PROPOSED",
        "authority": "PROPOSED",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project_id": args.project_id,
        "provenance": {
            "observed": [key for key, value in inputs.items() if value],
            "inferred": [],
            "speculative": [],
        },
        "shared_invariants": {
            "preserve_identity": True,
            "preserve_locked_facts": True,
            "preserve_ownership": True,
            "preserve_chronology": True,
            "preserve_geometry": True,
            "preserve_material_state": True,
            "preserve_residue": True,
        },
        "request": {
            "brief": brief,
            "provider": args.provider,
            "has_input": source_text is not None,
            "has_evidence": evidence_text is not None,
        },
        "result": {
            "implementation_state": "FOUNDATION",
            "message": (
                f"First-class {surface}:{action} contract resolved. "
                "Domain compiler expansion is tracked by issue #33."
            ),
        },
    }

    if surface == "design":
        artifact["result"]["contract"] = "section-aware design.md lifecycle"
    elif surface == "script":
        artifact["result"]["contract"] = "causality and continuity-safe script lifecycle"
    elif surface == "image":
        artifact["result"]["contract"] = "neutral still prompt plus provider-preservation layer"
    elif surface == "video":
        artifact["result"]["contract"] = {
            "required_temporal_fields": [
                "start_state", "action", "subject_movement", "camera", "duration",
                "physical_behavior", "forbidden_motion", "end_state",
                "continuity_invariants", "negative_constraints",
            ]
        }
    return artifact


def run(surface: str, actions: set[str]) -> int:
    if surface not in VALID_SURFACES:
        raise ValueError(f"unknown surface: {surface}")

    parser = argparse.ArgumentParser(prog=f"kubrick do {surface}")
    parser.add_argument("--surface-action", choices=sorted(actions), required=True)
    parser.add_argument("--brief")
    parser.add_argument("--input")
    parser.add_argument("--evidence")
    parser.add_argument("--provider", default="generic")
    parser.add_argument("--project-id", default="local-project")
    parser.add_argument("--output")
    args = parser.parse_args()

    artifact = build_artifact(surface, args.surface_action, args)
    encoded = json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.output:
        target = Path(args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")
    return 4 if artifact["status"] == "NOT_COMPUTABLE" else 0

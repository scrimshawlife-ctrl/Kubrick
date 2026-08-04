#!/usr/bin/env python3
"""Claim-level provenance labels and collision taxonomy for Kubrick.

Shared by retrieval, production surfaces, and learn/evolve receipts so collision
and provenance vocabulary stays stable across the operator surface.
"""
from __future__ import annotations

from typing import Any, Iterable

# Stable collision taxonomy (extend only with regression coverage).
COLLISION_TYPES = frozenset(
    {
        "REDUNDANT",
        "CONTRADICTORY",
        "CULTURALLY_INCOMPATIBLE",
        "RHYTHMICALLY_OVERLAPPING",
        "PAYOFF_COMPETITION",
        "OWNERSHIP_CONFLICT",
        "GEOMETRY_RESET",
        "RESIDUE_ERASURE",
        "AUTHORITY_PROMOTION",
        "PROVIDER_SEMANTIC_DROP",
    }
)

HARD_FAIL_COLLISIONS = frozenset(
    {
        "CONTRADICTORY",
        "CULTURALLY_INCOMPATIBLE",
        "OWNERSHIP_CONFLICT",
        "AUTHORITY_PROMOTION",
        "PROVIDER_SEMANTIC_DROP",
    }
)

PROVENANCE_LABELS = frozenset({"observed", "inferred", "speculative", "external_authoritative"})


def normalize_collision(entry: dict[str, Any]) -> dict[str, Any] | None:
    if not isinstance(entry, dict):
        return None
    kind = str(entry.get("type", "")).upper()
    if kind not in COLLISION_TYPES:
        return None
    payload = {
        "type": kind,
        "with": entry.get("with"),
        "patterns": list(entry.get("patterns") or []),
        "claim_ids": list(entry.get("claim_ids") or []),
        "severity": kind in HARD_FAIL_COLLISIONS,
    }
    return payload


def classify_collisions(entries: Iterable[Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for entry in entries:
        if isinstance(entry, dict):
            normalized = normalize_collision(entry)
            if normalized:
                out.append(normalized)
    return out


def provenance_bucket(
    *,
    observed: list[str] | None = None,
    inferred: list[str] | None = None,
    speculative: list[str] | None = None,
    external_authoritative: list[str] | None = None,
) -> dict[str, list[str]]:
    return {
        "observed": list(observed or []),
        "inferred": list(inferred or []),
        "speculative": list(speculative or []),
        "external_authoritative": list(external_authoritative or []),
    }


def claim(
    claim_id: str,
    text: str,
    *,
    label: str = "observed",
    evidence_refs: list[str] | None = None,
) -> dict[str, Any]:
    if label not in PROVENANCE_LABELS:
        raise ValueError(f"unknown provenance label: {label}")
    return {
        "claim_id": claim_id,
        "text": text,
        "label": label,
        "evidence_refs": list(evidence_refs or []),
    }

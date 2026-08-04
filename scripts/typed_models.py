#!/usr/bin/env python3
"""Frozen typed shapes for high-risk Kubrick artifacts (stdlib TypedDict).

These are structural contracts for tests and adapters. They intentionally stay
lightweight — full JSON Schema validation remains in schemas/.
"""
from __future__ import annotations

from typing import Any, TypedDict


class CompileReceipt(TypedDict, total=False):
    schema_version: str
    status: str
    authority: str
    identities: dict[str, str]
    provider: str
    mode: str
    artifacts: list[str]
    diagnostic: dict[str, Any]


class MotifStructureGraph(TypedDict, total=False):
    schema_version: str
    graph_id: str
    nodes: list[dict[str, Any]]
    edges: list[dict[str, Any]]
    layers: dict[str, Any]
    surface_output: dict[str, Any]
    convergence_sites: list[dict[str, Any]]


class StoryboardSymbolicState(TypedDict, total=False):
    schema_version: str
    frames: list[dict[str, Any]]
    transitions: list[dict[str, Any]]
    locked_invariants: list[str]


class ModelAdapterPacket(TypedDict, total=False):
    schema_version: str
    provider: str
    graph_identity: str
    frames: list[dict[str, Any]]
    shared_constraints: dict[str, Any]
    negative_constraints: list[str]


class ProductionSurfaceArtifact(TypedDict, total=False):
    schema_version: str
    artifact_id: str
    surface: str
    action: str
    status: str
    authority: str
    provenance: dict[str, list[str]]
    shared_invariants: dict[str, bool]
    result: dict[str, Any]


REQUIRED_KEYS: dict[str, tuple[str, ...]] = {
    "compile-receipt": ("status",),
    "motif-structure-graph": ("nodes", "edges"),
    "storyboard-symbolic-state": ("frames",),
    "model-adapter-packet": ("frames", "shared_constraints"),
    "production-surface": ("artifact_id", "surface", "action", "status", "authority"),
}


def validate_required(kind: str, payload: dict[str, Any]) -> list[str]:
    missing = [key for key in REQUIRED_KEYS.get(kind, ()) if key not in payload]
    return [f"missing required key {key!r} for {kind}" for key in missing]

#!/usr/bin/env python3
"""Deterministic symbolic-pattern retrieval for Kubrick."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from kubrick_paths import PATTERNS_DIR, ensure_state_dirs, state_paths

try:
    import yaml
except ImportError:  # JSON remains available without PyYAML.
    yaml = None


DEFAULT_WEIGHTS = {
    "dramatic_fit": 0.25,
    "character_fit": 0.15,
    "cultural_fit": 0.15,
    "cinematic_fit": 0.15,
    "source_quality": 0.10,
    "mutation_potential": 0.10,
    "continuity_compatibility": 0.10,
}
THRESHOLD = 0.55
MAX_SUPPORTING = 2
CORPUS_VERSION = "0.9.0"


def load_document(path: Path | None) -> Dict[str, Any]:
    if path is None:
        text = sys.stdin.read()
        suffix = ""
    else:
        text = path.read_text(encoding="utf-8")
        suffix = path.suffix.lower()
    if suffix == ".json":
        result = json.loads(text)
    elif yaml is not None:
        result = yaml.safe_load(text)
    else:
        try:
            result = json.loads(text)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "PyYAML is required for YAML briefs; install requirements.txt "
                "or provide JSON"
            ) from exc
    if not isinstance(result, dict):
        raise RuntimeError("brief must decode to an object")
    return result


def load_json_files(root: Path) -> Dict[str, Dict[str, Any]]:
    patterns: Dict[str, Dict[str, Any]] = {}
    if not root.exists():
        return patterns
    for path in sorted(root.rglob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        pattern_id = data.get("pattern_id")
        if pattern_id:
            patterns[str(pattern_id)] = data
    return patterns


def load_all_patterns() -> Dict[str, Dict[str, Any]]:
    patterns = load_json_files(PATTERNS_DIR)
    overlays = load_json_files(state_paths()["patterns"])
    for pattern_id, overlay in overlays.items():
        if pattern_id in patterns:
            patterns[pattern_id] = {**patterns[pattern_id], **overlay}
    return patterns


def words(value: Any) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", str(value).lower())
        if len(token) >= 3
    }


def any_overlap(needles: Iterable[Any], haystack: Any) -> bool:
    target = words(haystack)
    return any(words(value) & target for value in needles)


def compute_score(
    pattern: Dict[str, Any],
    brief: Dict[str, Any],
    weights: Dict[str, float] | None = None,
) -> Dict[str, Any]:
    weights = weights or DEFAULT_WEIGHTS
    operations = pattern.get("dramatic_operations") or []
    dramatic = 0.95 if any_overlap(operations, brief.get("dramatic_problem", "")) else 0.7

    genres = [str(item).lower() for item in (pattern.get("applicable_genres") or [])]
    formats = [str(item).lower() for item in (pattern.get("applicable_formats") or [])]
    cinematic = 0.6
    if str(brief.get("genre", "")).lower() in genres:
        cinematic = 0.9
    if str(brief.get("format", "")).lower() in formats:
        cinematic += 0.05

    scopes = pattern.get("cultural_scope") or []
    cultural = 0.85 if any_overlap(scopes, brief.get("cultural_context", "")) else 0.5
    tier = str(pattern.get("source_tier", "POPULAR")).upper()
    tier_score = {
        "PRIMARY": 0.95,
        "SCHOLARLY": 0.85,
        "PRACTITIONER": 0.75,
    }.get(tier, 0.5)
    mutation = bool((pattern.get("mutation_requirements") or {}).get("required"))

    active = [str(item).lower() for item in brief.get("active_project_motifs", [])]
    serialized = json.dumps(pattern, sort_keys=True).lower()
    compatibility = 0.6 if any(item in serialized for item in active) else 0.8

    components = {
        "dramatic_fit": dramatic,
        "cinematic_fit": min(cinematic, 1.0),
        "cultural_fit": cultural,
        "source_quality": tier_score,
        "mutation_potential": 0.9 if mutation else 0.6,
        "continuity_compatibility": compatibility,
        "character_fit": 0.7,
        "cliché_risk": 0.3,
    }
    total = sum(components.get(key, 0.5) * weight for key, weight in weights.items())
    total -= components["cliché_risk"] * 0.20
    return {
        "total_score": round(max(0.0, min(1.0, total)), 4),
        "score_components": {
            key: round(value, 4) for key, value in components.items()
        },
    }


def apply_exclusions(
    patterns: Iterable[Dict[str, Any]], brief: Dict[str, Any]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
    prohibited = [str(item).lower() for item in brief.get("prohibited_patterns", [])]
    accepted = []
    rejected = []
    for pattern in patterns:
        pattern_id = str(pattern["pattern_id"])
        searchable = f"{pattern_id} {pattern.get('title', '')}".lower()
        match = next((item for item in prohibited if item in searchable), None)
        if match:
            rejected.append(
                {"pattern_id": pattern_id, "reason": f"prohibited pattern: {match}"}
            )
        else:
            accepted.append(pattern)
    return accepted, rejected


def evolution_order() -> Dict[str, float]:
    path = state_paths()["ranking"]
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return {
            str(key): float(value)
            for key, value in (data.get("pattern_scores") or {}).items()
        }
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return {}


def rank_patterns(
    brief: Dict[str, Any], patterns_db: Dict[str, Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
    candidates, rejected = apply_exclusions(patterns_db.values(), brief)
    observed = evolution_order()
    ranked = []
    for pattern in candidates:
        score = compute_score(pattern, brief)
        if score["total_score"] < 0.3:
            continue
        pattern_id = str(pattern["pattern_id"])
        ranked.append(
            {
                "pattern_id": pattern_id,
                "total_score": score["total_score"],
                "score_components": score["score_components"],
                "pattern_confidence": float(pattern.get("confidence", 0.7)),
                "evolution_score": observed.get(pattern_id, 0.0),
                "provenance_refs": pattern.get("source_refs") or [],
                "mutation_requirements": pattern.get("mutation_requirements") or {},
                "production_cost": pattern.get("production_cost") or {},
                "selection_reason": (
                    "Dramatic and cinematic fit after exclusions; "
                    "evidence ranking used only as a tie-break"
                ),
            }
        )
    ranked.sort(
        key=lambda item: (
            item["total_score"],
            item["evolution_score"],
            item["pattern_confidence"],
            item["pattern_id"],
        ),
        reverse=True,
    )
    return ranked, rejected


def build_receipt(
    brief: Dict[str, Any],
    ranked: List[Dict[str, Any]],
    rejected: List[Dict[str, str]],
) -> Dict[str, Any]:
    request_hash = hashlib.sha256(
        json.dumps(brief, sort_keys=True).encode("utf-8")
    ).hexdigest()[:16]
    primary = ranked[0] if ranked else None
    supporting = ranked[1 : 1 + MAX_SUPPORTING]
    selected = bool(primary and primary["total_score"] >= THRESHOLD)
    return {
        "retrieval_receipt": {
            "request_hash": request_hash,
            "corpus_version": CORPUS_VERSION,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "selected_primary_grammar": primary["pattern_id"] if selected else None,
            "selected_supporting_grammars": (
                [item["pattern_id"] for item in supporting] if selected else []
            ),
            "ranked_patterns": ranked[:5] if selected else [],
            "rejected_patterns": rejected,
            "confidence": primary["total_score"] if primary else 0.0,
            "status": "SELECTED" if selected else "NOT_COMPUTABLE",
            "brief": brief,
        }
    }


def log_receipt(receipt: Dict[str, Any]) -> Path:
    paths = ensure_state_dirs()
    request_hash = receipt["retrieval_receipt"]["request_hash"]
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
    path = paths["receipts"] / f"receipt-{request_hash}-{timestamp}.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return path


def output_document(receipt: Dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(receipt, indent=2))
    elif yaml is not None:
        print(yaml.safe_dump(receipt, sort_keys=False, default_flow_style=False))
    else:
        raise RuntimeError("PyYAML is required for YAML output; use --format json")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--brief", type=Path, help="Path to a JSON or YAML brief")
    parser.add_argument("--format", choices=("json", "yaml"), default="yaml")
    parser.add_argument("--no-log", action="store_true")
    args = parser.parse_args()
    try:
        brief = load_document(args.brief)
        patterns = load_all_patterns()
        if not patterns:
            raise RuntimeError(f"no pattern sidecars found under {PATTERNS_DIR}")
        ranked, rejected = rank_patterns(brief, patterns)
        receipt = build_receipt(brief, ranked, rejected)
        if not args.no_log:
            receipt["retrieval_receipt"]["logged_to"] = str(log_receipt(receipt))
        output_document(receipt, args.format)
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(f"kubrick retrieval failed: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    if receipt["retrieval_receipt"]["status"] == "NOT_COMPUTABLE":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

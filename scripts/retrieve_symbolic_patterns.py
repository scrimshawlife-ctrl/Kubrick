#!/usr/bin/env python3
"""Kubrick deterministic symbolic retrieval.

Ledger-aware, collision-aware, cacheable, and fail-closed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    import yaml
except ImportError:
    print("pyyaml required. pip install pyyaml", file=sys.stderr)
    raise SystemExit(1)

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
PATTERNS_DIR = SKILL_ROOT / "references" / "patterns"
CACHE_DIR = SKILL_ROOT / "references" / "usage" / "cache"
RECEIPT_DIR = SKILL_ROOT / "references" / "usage" / "receipts"
THRESHOLD = 0.55
MAX_SUPPORTING = 2

WEIGHTS = {
    "dramatic_fit": 0.24,
    "character_fit": 0.10,
    "cinematic_fit": 0.12,
    "cultural_fit": 0.10,
    "source_quality": 0.10,
    "mutation_potential": 0.14,
    "continuity_compatibility": 0.10,
    "payoff_compatibility": 0.10,
}

COLLISION_TYPES = {
    "REDUNDANT",
    "CONTRADICTORY",
    "CULTURALLY_INCOMPATIBLE",
    "RHYTHMICALLY_OVERLAPPING",
    "PAYOFF_COMPETITION",
}


def _tokens(value: Any) -> set[str]:
    if isinstance(value, (list, tuple, set)):
        value = " ".join(str(item) for item in value)
    return set(re.findall(r"[a-z0-9_]+", str(value).lower().replace("-", "_")))


def _overlap(query: Any, candidate: Any) -> float:
    q = _tokens(query)
    c = _tokens(candidate)
    if not q or not c:
        return 0.0
    return len(q & c) / max(1, len(q))


def _load(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        if path.suffix == ".json":
            return json.load(handle)
        return yaml.safe_load(handle) or {}


def load_all_patterns() -> Dict[str, Dict[str, Any]]:
    patterns: Dict[str, Dict[str, Any]] = {}
    for path in PATTERNS_DIR.rglob("*.json"):
        pattern = _load(path)
        pattern_id = pattern.get("pattern_id")
        if pattern_id:
            patterns[pattern_id] = pattern
    return patterns


def ledger_snapshot(brief: Dict[str, Any]) -> Dict[str, Any]:
    ledger = brief.get("symbolic_ledger") or {}
    return {
        "active": sorted(set(ledger.get("active_motifs", brief.get("active_project_motifs", [])))),
        "retired": sorted(set(ledger.get("retired_motifs", []))),
        "prohibited": sorted(set(ledger.get("prohibited_motifs", brief.get("prohibited_patterns", [])))),
        "unresolved_payoffs": sorted(set(ledger.get("unresolved_payoffs", []))),
        "saturation_score": float(ledger.get("saturation_score", 0.0)),
        "symbolic_debt": float(ledger.get("symbolic_debt", 0.0)),
        "collisions": ledger.get("collisions", []),
        "prohibited_cultural_scopes": ledger.get("prohibited_cultural_scopes", []),
    }


def cache_key(brief: Dict[str, Any], ledger: Dict[str, Any]) -> str:
    payload = json.dumps({"brief": brief, "ledger": ledger}, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]


def production_cost(pattern: Dict[str, Any]) -> float:
    values = [
        float(value)
        for value in (pattern.get("production_cost") or {}).values()
        if isinstance(value, (int, float))
    ]
    return sum(values) / len(values) if values else 0.5


def detect_collisions(pattern: Dict[str, Any], ledger: Dict[str, Any]) -> List[Dict[str, str]]:
    collisions: List[Dict[str, str]] = []
    text = json.dumps(pattern, sort_keys=True).lower()
    pattern_id = pattern.get("pattern_id", "")

    for active in ledger["active"]:
        if active.lower() in text or active.lower() == pattern_id.lower():
            collisions.append({"type": "REDUNDANT", "with": active})

    for collision in ledger["collisions"]:
        if not isinstance(collision, dict):
            continue
        collision_type = collision.get("type")
        participants = set(collision.get("patterns", []))
        if collision_type in COLLISION_TYPES and pattern_id in participants:
            collisions.append({"type": collision_type, "with": ",".join(sorted(participants - {pattern_id}))})

    pattern_scope = _tokens(pattern.get("cultural_scope", []))
    prohibited_scope = _tokens(ledger.get("prohibited_cultural_scopes", []))
    if pattern_scope & prohibited_scope:
        collisions.append({"type": "CULTURALLY_INCOMPATIBLE", "with": "prohibited cultural scope"})

    return collisions


def score_pattern(pattern: Dict[str, Any], brief: Dict[str, Any], ledger: Dict[str, Any]) -> Dict[str, Any]:
    dramatic_query = [
        brief.get("dramatic_problem", ""),
        brief.get("desired_state_change", ""),
        brief.get("symbolic_intent", ""),
    ]
    dramatic_candidate = (
        pattern.get("dramatic_operations", [])
        + pattern.get("transformation_grammars", [])
        + [pattern.get("transferable_structure", "")]
    )
    dramatic_fit = _overlap(dramatic_query, dramatic_candidate)
    character_fit = _overlap(
        [brief.get("character_state", ""), brief.get("character_pressure", "")], dramatic_candidate
    )
    cinematic_fit = max(
        _overlap(brief.get("preferred_encoding_vectors", []), pattern.get("cinematic_affordances", [])),
        0.8 if brief.get("format") in pattern.get("applicable_formats", []) else 0.0,
        0.8 if brief.get("genre", "").lower() in [g.lower() for g in pattern.get("applicable_genres", [])] else 0.0,
    )
    cultural_fit = _overlap(brief.get("cultural_context", ""), pattern.get("cultural_scope", []))
    if not brief.get("cultural_context"):
        cultural_fit = 0.65

    source_quality = {
        "PRIMARY": 0.95,
        "SCHOLARLY": 0.85,
        "PRACTITIONER": 0.75,
        "COMPARATIVE": 0.65,
    }.get(pattern.get("source_tier", "POPULAR"), 0.5)

    mutation = pattern.get("mutation_requirements", {})
    mutation_potential = 0.95 if mutation.get("required") and mutation.get("variables") else 0.35

    active_text = " ".join(ledger["active"]).lower()
    redundant = any(token in active_text for token in _tokens(pattern.get("title", "")))
    continuity_compatibility = max(
        0.0,
        0.9
        - (0.35 if redundant else 0.0)
        - min(0.5, ledger["saturation_score"] * 0.35)
        - min(0.4, ledger["symbolic_debt"] * 0.25),
    )

    unresolved = ledger["unresolved_payoffs"]
    payoff_compatibility = 0.75 if not unresolved else min(1.0, 0.4 + _overlap(unresolved, dramatic_candidate))

    components = {
        "dramatic_fit": dramatic_fit,
        "character_fit": character_fit,
        "cinematic_fit": cinematic_fit,
        "cultural_fit": cultural_fit,
        "source_quality": source_quality,
        "mutation_potential": mutation_potential,
        "continuity_compatibility": continuity_compatibility,
        "payoff_compatibility": payoff_compatibility,
    }
    total = sum(components[key] * weight for key, weight in WEIGHTS.items())

    budget = brief.get("production_cost_ceiling")
    cost = production_cost(pattern)
    if isinstance(budget, (int, float)) and cost > float(budget):
        total -= min(0.35, cost - float(budget))

    collisions = detect_collisions(pattern, ledger)
    hard_collision = any(item["type"] in {"CONTRADICTORY", "CULTURALLY_INCOMPATIBLE"} for item in collisions)
    if hard_collision:
        total = 0.0
    else:
        total -= min(0.3, 0.08 * len(collisions))

    return {
        "pattern_id": pattern["pattern_id"],
        "total_score": round(max(0.0, min(1.0, total)), 4),
        "score_components": {key: round(value, 4) for key, value in components.items()},
        "collisions": collisions,
        "production_cost_score": round(cost, 4),
        "provenance_refs": pattern.get("source_refs", []),
        "mutation_requirements": mutation,
        "lexicon_links": pattern.get("lexicon_links", []),
    }


def reason_vector(ranked: List[Dict[str, Any]], ledger: Dict[str, Any]) -> List[str]:
    if not ranked:
        return ["NO_EXECUTABLE_PATTERNS"]
    top = ranked[0]
    reasons: List[str] = []
    components = top["score_components"]
    if components["dramatic_fit"] <= 0:
        reasons.append("LOW_DRAMATIC_FIT")
    if components["mutation_potential"] < 0.6:
        reasons.append("LOW_MUTATION_POTENTIAL")
    if components["continuity_compatibility"] < 0.5:
        reasons.append("SATURATION_OR_SYMBOLIC_DEBT")
    if components["cultural_fit"] < 0.25:
        reasons.append("LOW_CULTURAL_FIT")
    if top["production_cost_score"] > 0.8:
        reasons.append("HIGH_PRODUCTION_COST")
    reasons.extend(sorted({item["type"] for item in top["collisions"]}))
    if ledger["saturation_score"] >= 0.85:
        reasons.append("SYMBOLIC_OVERLOAD")
    return reasons or ["BELOW_CONFIDENCE_THRESHOLD"]


def gap_report(brief: Dict[str, Any], ranked: List[Dict[str, Any]]) -> Dict[str, Any]:
    top = ranked[0] if ranked else None
    if not top:
        weak_dimensions = ["dramatic", "character", "cinematic", "cultural", "mutation"]
    else:
        weak_dimensions = [
            key.replace("_fit", "").replace("_potential", "")
            for key, value in top["score_components"].items()
            if value < 0.35
        ]
    problem_tokens = _tokens(brief.get("dramatic_problem", ""))
    recommended = set(brief.get("requested_domains", []))
    if "sound" in problem_tokens:
        recommended.add("sound")
    if "threshold" in problem_tokens:
        recommended.add("ritual-liminal")
    return {
        "dramatic_problem": brief.get("dramatic_problem"),
        "coverage_strength": round(top["total_score"], 4) if top else 0.0,
        "weak_dimensions": weak_dimensions,
        "recommended_pattern_domains": sorted(recommended),
    }


def build_receipt(brief: Dict[str, Any], ranked: List[Dict[str, Any]], ledger: Dict[str, Any]) -> Dict[str, Any]:
    eligible = [item for item in ranked if item["total_score"] >= THRESHOLD]
    primary = eligible[0] if eligible else None
    supporting = eligible[1 : 1 + MAX_SUPPORTING]
    status = "SELECTED" if primary else "NOT_COMPUTABLE"
    key = cache_key(brief, ledger)
    return {
        "retrieval_receipt": {
            "request_hash": key,
            "corpus_version": "0.11.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "selected_primary_grammar": primary["pattern_id"] if primary else None,
            "selected_supporting_grammars": [item["pattern_id"] for item in supporting],
            "ranked_patterns": ranked[:8] if primary else [],
            "confidence": primary["total_score"] if primary else 0.0,
            "status": status,
            "reason_vector": [] if primary else reason_vector(ranked, ledger),
            "pattern_gap_report": gap_report(brief, ranked),
            "ledger_snapshot": ledger,
            "brief": brief,
        }
    }


def load_cached(key: str) -> Dict[str, Any] | None:
    path = CACHE_DIR / f"{key}.json"
    return _load(path) if path.exists() else None


def persist(receipt: Dict[str, Any]) -> Tuple[Path, Path]:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    key = receipt["retrieval_receipt"]["request_hash"]
    cache_path = CACHE_DIR / f"{key}.json"
    receipt_path = RECEIPT_DIR / f"receipt-{key}-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.json"
    for path in (cache_path, receipt_path):
        with path.open("w", encoding="utf-8") as handle:
            json.dump(receipt, handle, indent=2)
    return cache_path, receipt_path


def read_brief(path: str | None) -> Dict[str, Any]:
    if not path:
        return yaml.safe_load(sys.stdin) or {}
    return _load(Path(path))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--brief")
    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument("--gap-report-only", action="store_true")
    args = parser.parse_args()

    brief = read_brief(args.brief)
    ledger = ledger_snapshot(brief)
    key = cache_key(brief, ledger)
    if not args.no_cache:
        cached = load_cached(key)
        if cached:
            cached["retrieval_receipt"]["cache_hit"] = True
            print(yaml.safe_dump(cached, sort_keys=False))
            raise SystemExit(0 if cached["retrieval_receipt"]["status"] == "SELECTED" else 1)

    patterns = load_all_patterns()
    ranked = sorted(
        (score_pattern(pattern, brief, ledger) for pattern in patterns.values()),
        key=lambda item: (-item["total_score"], item["pattern_id"]),
    )
    receipt = build_receipt(brief, ranked, ledger)
    receipt["retrieval_receipt"]["cache_hit"] = False

    if args.gap_report_only:
        print(yaml.safe_dump(receipt["retrieval_receipt"]["pattern_gap_report"], sort_keys=False))
        return

    cache_path, receipt_path = persist(receipt)
    receipt["retrieval_receipt"]["cached_to"] = str(cache_path)
    receipt["retrieval_receipt"]["logged_to"] = str(receipt_path)
    print(yaml.safe_dump(receipt, sort_keys=False))
    raise SystemExit(0 if receipt["retrieval_receipt"]["status"] == "SELECTED" else 1)


if __name__ == "__main__":
    main()

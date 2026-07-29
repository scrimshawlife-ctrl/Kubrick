#!/usr/bin/env python3
"""Registry-aware Kubrick retrieval for the standalone Hermes skill.

Extends the stable ledger-aware scorer with consolidated route metadata from
references/executable-corpus-registry.yaml and references/corpus-index.yaml.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

try:
    import yaml
except ImportError:
    print("pyyaml required. pip install pyyaml", file=sys.stderr)
    raise SystemExit(1)

import retrieve_symbolic_patterns as base

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
REGISTRY_PATH = SKILL_ROOT / "references" / "executable-corpus-registry.yaml"
INDEX_PATH = SKILL_ROOT / "references" / "corpus-index.yaml"
CACHE_DIR = SKILL_ROOT / "references" / "usage" / "cache-registry"
RECEIPT_DIR = SKILL_ROOT / "references" / "usage" / "receipts"
CORPUS_VERSION = "0.11.5"
ROUTE_MATCH_BONUS = 0.08
STRONG_DEFAULT_BONUS = 0.03


def load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def route_registry() -> tuple[dict[str, set[str]], set[str]]:
    registry = load_yaml(REGISTRY_PATH)
    routes: dict[str, set[str]] = {}
    for route, pattern_ids in (registry.get("default_routes") or {}).items():
        routes[str(route)] = {str(item) for item in pattern_ids or []}
    strong_defaults = {str(item) for item in registry.get("strong_defaults", [])}
    return routes, strong_defaults


def route_query(brief: Dict[str, Any]) -> set[str]:
    values = [
        brief.get("dramatic_problem", ""),
        brief.get("desired_state_change", ""),
        brief.get("symbolic_intent", ""),
        brief.get("requested_domains", []),
        brief.get("preferred_encoding_vectors", []),
    ]
    return base._tokens(values)


def route_matches(brief: Dict[str, Any], routes: dict[str, set[str]]) -> list[str]:
    tokens = route_query(brief)
    matches = []
    for route in routes:
        route_tokens = base._tokens(route)
        if route_tokens and route_tokens & tokens:
            matches.append(route)
    return sorted(matches)


def cache_key(brief: Dict[str, Any], ledger: Dict[str, Any]) -> str:
    payload = json.dumps(
        {"algorithm": CORPUS_VERSION, "brief": brief, "ledger": ledger},
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]


def score_with_registry(
    pattern: Dict[str, Any],
    brief: Dict[str, Any],
    ledger: Dict[str, Any],
    routes: dict[str, set[str]],
    matched_routes: list[str],
    strong_defaults: set[str],
) -> Dict[str, Any]:
    scored = base.score_pattern(pattern, brief, ledger)
    pattern_id = scored["pattern_id"]
    direct_routes = sorted(route for route in matched_routes if pattern_id in routes.get(route, set()))
    bonus = 0.0
    if direct_routes:
        bonus += ROUTE_MATCH_BONUS
    if pattern_id in strong_defaults:
        bonus += STRONG_DEFAULT_BONUS
    scored["base_score"] = scored["total_score"]
    scored["route_matches"] = direct_routes
    scored["route_bonus"] = round(bonus, 4)
    scored["strong_default"] = pattern_id in strong_defaults
    scored["total_score"] = round(min(1.0, scored["total_score"] + bonus), 4)
    return scored


def gap_report(
    brief: Dict[str, Any],
    ranked: list[Dict[str, Any]],
    matched_routes: list[str],
    routes: dict[str, set[str]],
) -> Dict[str, Any]:
    report = base.gap_report(brief, ranked)
    report["matched_registry_routes"] = matched_routes
    report["route_candidate_counts"] = {
        route: len(routes.get(route, set())) for route in matched_routes
    }
    if not matched_routes:
        report.setdefault("weak_dimensions", []).append("registry_route")
    return report


def build_receipt(
    brief: Dict[str, Any],
    ranked: list[Dict[str, Any]],
    ledger: Dict[str, Any],
    matched_routes: list[str],
    routes: dict[str, set[str]],
) -> Dict[str, Any]:
    eligible = [item for item in ranked if item["total_score"] >= base.THRESHOLD]
    primary = eligible[0] if eligible else None
    supporting = eligible[1 : 1 + base.MAX_SUPPORTING]
    status = "SELECTED" if primary else "NOT_COMPUTABLE"
    key = cache_key(brief, ledger)
    return {
        "retrieval_receipt": {
            "request_hash": key,
            "algorithm": "registry-aware-v1",
            "corpus_version": CORPUS_VERSION,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "selected_primary_grammar": primary["pattern_id"] if primary else None,
            "selected_supporting_grammars": [item["pattern_id"] for item in supporting],
            "ranked_patterns": ranked[:8] if primary else [],
            "confidence": primary["total_score"] if primary else 0.0,
            "status": status,
            "reason_vector": [] if primary else base.reason_vector(ranked, ledger),
            "pattern_gap_report": gap_report(brief, ranked, matched_routes, routes),
            "matched_registry_routes": matched_routes,
            "ledger_snapshot": ledger,
            "brief": brief,
        }
    }


def load_cached(key: str) -> Dict[str, Any] | None:
    path = CACHE_DIR / f"{key}.json"
    return base._load(path) if path.exists() else None


def persist(receipt: Dict[str, Any]) -> tuple[Path, Path]:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    key = receipt["retrieval_receipt"]["request_hash"]
    cache_path = CACHE_DIR / f"{key}.json"
    receipt_path = RECEIPT_DIR / (
        f"receipt-registry-{key}-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.json"
    )
    for path in (cache_path, receipt_path):
        path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return cache_path, receipt_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--brief")
    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument("--gap-report-only", action="store_true")
    parser.add_argument("--show-routes", action="store_true")
    args = parser.parse_args()

    brief = base.read_brief(args.brief)
    ledger = base.ledger_snapshot(brief)
    routes, strong_defaults = route_registry()
    matched_routes = route_matches(brief, routes)

    if args.show_routes:
        print(yaml.safe_dump({"matched_routes": matched_routes}, sort_keys=False))
        return

    key = cache_key(brief, ledger)
    if not args.no_cache:
        cached = load_cached(key)
        if cached:
            cached["retrieval_receipt"]["cache_hit"] = True
            print(yaml.safe_dump(cached, sort_keys=False))
            raise SystemExit(0 if cached["retrieval_receipt"]["status"] == "SELECTED" else 1)

    patterns = base.load_all_patterns()
    ranked = sorted(
        (
            score_with_registry(
                pattern, brief, ledger, routes, matched_routes, strong_defaults
            )
            for pattern in patterns.values()
        ),
        key=lambda item: (-item["total_score"], item["pattern_id"]),
    )
    receipt = build_receipt(brief, ranked, ledger, matched_routes, routes)
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

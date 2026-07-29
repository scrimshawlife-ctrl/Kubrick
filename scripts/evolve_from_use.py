#!/usr/bin/env python3
"""Evidence-based Kubrick evolution using external, reversible overlays."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from kubrick_paths import PATTERNS_DIR, ensure_state_dirs

try:
    import yaml
except ImportError:
    yaml = None


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def load_patterns(root: Path) -> Dict[str, Dict[str, Any]]:
    patterns = {}
    if not root.exists():
        return patterns
    for path in sorted(root.rglob("*.json")):
        data = load_json(path)
        if data.get("pattern_id"):
            patterns[str(data["pattern_id"])] = data
    return patterns


def load_receipt(path: Path) -> Dict[str, Any] | None:
    try:
        if path.suffix == ".json":
            return load_json(path)
        if path.suffix in {".yaml", ".yml"} and yaml is not None:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else None
    except (OSError, ValueError, json.JSONDecodeError):
        return None
    return None


def aggregate_usage(receipts_dir: Path, outcomes_dir: Path) -> Dict[str, Dict[str, Any]]:
    usage: Dict[str, Dict[str, Any]] = defaultdict(
        lambda: {
            "uses": 0,
            "total_score": 0.0,
            "success_signals": 0,
            "failure_signals": 0,
            "projects": [],
        }
    )
    for path in sorted(receipts_dir.glob("*")):
        receipt = load_receipt(path)
        if not receipt:
            continue
        record = receipt.get("retrieval_receipt", receipt)
        for item in record.get("ranked_patterns", [])[:3]:
            pattern_id = item.get("pattern_id")
            if pattern_id:
                usage[pattern_id]["uses"] += 1
                usage[pattern_id]["total_score"] += float(
                    item.get("total_score", 0.5)
                )
                usage[pattern_id]["projects"].append(
                    record.get("request_hash", "unknown")
                )
    for path in sorted(outcomes_dir.glob("*.json")):
        try:
            outcome = load_json(path)
        except (OSError, ValueError, json.JSONDecodeError):
            continue
        pattern_id = outcome.get("pattern_id")
        if not pattern_id:
            continue
        signal = outcome.get("outcome", "neutral")
        if signal == "success":
            usage[pattern_id]["success_signals"] += 1
        elif signal in {"failure", "debt", "collision", "revision_broken"}:
            usage[pattern_id]["failure_signals"] += 1
        usage[pattern_id]["projects"].append(outcome.get("project", "unknown"))
    return usage


def evolve_pattern(
    pattern: Dict[str, Any], stats: Dict[str, Any]
) -> Dict[str, Any] | None:
    uses = int(stats.get("uses", 0))
    if uses == 0:
        return None
    average = float(stats["total_score"]) / uses
    success = int(stats.get("success_signals", 0))
    failure = int(stats.get("failure_signals", 0))
    signals = success + failure
    success_rate = success / signals if signals else 0.5
    before = float(pattern.get("confidence", 0.7))
    delta = 0.0
    if uses >= 3:
        delta += (average - 0.6) * 0.15
        delta += (success_rate - 0.5) * 0.25
    if failure > success and uses >= 2:
        delta -= 0.1
    after = max(0.3, min(0.98, round(before + delta, 4)))
    history = list(pattern.get("usage_history") or [])
    history.append(
        {
            "date": datetime.now(timezone.utc).isoformat(),
            "uses_in_window": uses,
            "average_retrieval_score": round(average, 4),
            "success_rate": round(success_rate, 4),
            "confidence_before": before,
            "confidence_after": after,
            "delta": round(delta, 4),
            "source_projects": sorted(set(stats.get("projects", [])))[:5],
        }
    )
    return {
        "pattern_id": pattern["pattern_id"],
        "confidence": after,
        "last_evolved": datetime.now(timezone.utc).isoformat(),
        "usage_history": history,
    }


def main() -> None:
    paths = ensure_state_dirs()
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipts-dir", type=Path, default=paths["receipts"])
    parser.add_argument("--outcomes-dir", type=Path, default=paths["outcomes"])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    base_patterns = load_patterns(PATTERNS_DIR)
    existing_overlays = load_patterns(paths["patterns"])
    usage = aggregate_usage(args.receipts_dir, args.outcomes_dir)
    evolved = {}
    scores = {}
    for pattern_id, pattern in base_patterns.items():
        if pattern_id in existing_overlays:
            pattern = {**pattern, **existing_overlays[pattern_id]}
        stats = usage.get(pattern_id, {})
        overlay = evolve_pattern(pattern, stats)
        if not overlay:
            continue
        evolved[pattern_id] = overlay
        scores[pattern_id] = round(
            stats.get("success_signals", 0)
            - stats.get("failure_signals", 0)
            + overlay["confidence"] * 2,
            4,
        )
        if not args.dry_run:
            save_json(paths["patterns"] / f"{pattern_id}.json", overlay)

    receipt = {
        "evolution_receipt": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dry_run": args.dry_run,
            "patterns_evolved": sorted(evolved),
            "bundled_corpus_mutated": False,
            "usage_window": {
                "receipts_scanned": len(list(args.receipts_dir.glob("*"))),
                "outcomes_scanned": len(list(args.outcomes_dir.glob("*"))),
            },
        }
    }
    if not args.dry_run:
        save_json(
            paths["ranking"],
            {"updated_at": receipt["evolution_receipt"]["timestamp"], "pattern_scores": scores},
        )
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
        save_json(paths["evolution"] / f"evolution-{stamp}.json", receipt)
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()

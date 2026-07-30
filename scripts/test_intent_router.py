# scripts/test_intent_router.py
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import intent_router as ir

EXPECTED_INTENTS = {
    "compile", "retrieve", "ledger", "design", "storyboard", "adapt",
    "visual", "learn", "check", "operate", "mcp", "bundle",
}

# From design spec — must stay complete
EXPECTED_LEGACY = {
    "compile", "retrieve", "ledger", "design-build",
    "storyboard-propagate", "storyboard-compare",
    "adapter-build", "adapt-provider", "adapt-grok", "adapt-flux",
    "adapt-sd3", "adapt-midjourney",
    "visual-normalize", "visual-compare", "visual-correct",
    "correction-govern", "closed-loop-qa",
    "outcome-record", "evolution-propose", "forge-signals",
    "validate-skill", "validate-corpus", "coverage",
    "artifact-validate", "repeatability", "eval",
    "operator", "mcp-server", "grok-review-bundle",
}


def test_intent_count_and_names():
    assert set(ir.INTENT_REGISTRY) == EXPECTED_INTENTS


def test_every_legacy_maps_exactly_once():
    assert set(ir.ALIAS_TABLE) == EXPECTED_LEGACY
    for name, alias in ir.ALIAS_TABLE.items():
        assert alias.intent in ir.INTENT_REGISTRY, name
        actions = ir.INTENT_REGISTRY[alias.intent].actions
        assert alias.action in actions or alias.passthrough_action, name


def main():
    test_intent_count_and_names()
    test_every_legacy_maps_exactly_once()
    print("intent_router unit: registry PASS")


if __name__ == "__main__":
    main()

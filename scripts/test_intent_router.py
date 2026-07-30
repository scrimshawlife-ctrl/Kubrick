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


def test_resolve_do_adapt_provider():
    call = ir.resolve([
        "do", "adapt", "--action", "provider",
        "--provider", "flux", "--packet", "p.yaml", "--output", "o.yaml",
    ])
    assert call.intent == "adapt"
    assert call.action == "provider"
    assert call.script.name == "adapt_provider.py"
    assert call.argv == ["--provider", "flux", "--packet", "p.yaml", "--output", "o.yaml"]
    assert call.legacy_name is None


def test_resolve_alias_adapt_flux():
    call = ir.resolve(["adapt-flux", "--packet", "p.yaml", "--output", "o.yaml"])
    assert call.intent == "adapt"
    assert call.action == "provider"
    assert call.script.name == "adapt_provider.py"
    assert "--provider" in call.argv and "flux" in call.argv
    assert call.legacy_name == "adapt-flux"


def test_resolve_unknown_intent():
    try:
        ir.resolve(["do", "nope"])
        raise AssertionError("expected RouterError")
    except ir.RouterError as e:
        assert e.exit_code == 2
        assert "compile" in e.message or "valid" in e.message.lower()


def test_ledger_passthrough_action():
    call = ir.resolve(["ledger", "audit", "--ledger", "L.yaml"])
    assert call.intent == "ledger"
    assert call.action == "audit"
    assert call.script.name == "symbolic_ledger.py"
    assert call.argv[0] == "audit"


def test_top_level_help_lists_intents_not_all_aliases():
    text = ir.format_top_level_help()
    assert "adapt" in text and "visual" in text and "learn" in text
    assert "adapt-flux" not in text  # aliases not first-class
    assert "do <intent>" in text or "kubrick do" in text


def test_recipe_storyboard_example():
    argv = ir.resolve_recipe("storyboard-example")
    call = ir.resolve(argv)
    assert call.intent == "compile"
    assert call.script.name == "kubrick_compile.py"


def test_alias_do_parity_matrix():
    cases = [
        (["validate-skill"], ["do", "check", "--action", "skill"]),
        (["closed-loop-qa", "--expected", "e", "--observation-input", "o",
          "--source-graph-id", "g", "--frame-id", "f1", "--out", "out/x"],
         ["do", "visual", "--action", "closed-loop", "--expected", "e",
          "--observation-input", "o", "--source-graph-id", "g",
          "--frame-id", "f1", "--out", "out/x"]),
        (["forge-signals", "--project-id", "p", "--input", "i.yaml", "--output", "o.yaml"],
         ["do", "learn", "--action", "forge-signals", "--project-id", "p",
          "--input", "i.yaml", "--output", "o.yaml"]),
    ]
    for legacy, modern in cases:
        a, b = ir.resolve(legacy), ir.resolve(modern)
        assert a.script == b.script, (legacy, modern, a.script, b.script)
        assert a.argv == b.argv, (legacy, modern, a.argv, b.argv)


def main():
    test_intent_count_and_names()
    test_every_legacy_maps_exactly_once()
    test_resolve_do_adapt_provider()
    test_resolve_alias_adapt_flux()
    test_resolve_unknown_intent()
    test_ledger_passthrough_action()
    test_top_level_help_lists_intents_not_all_aliases()
    test_recipe_storyboard_example()
    test_alias_do_parity_matrix()
    print("intent_router unit: registry + resolve + help/recipe + alias/do parity PASS")


if __name__ == "__main__":
    main()

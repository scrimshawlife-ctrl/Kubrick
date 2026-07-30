# scripts/intent_router.py
"""Operator intent registry and legacy alias tables for Kubrick CLI routing."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent


@dataclass(frozen=True)
class IntentCall:
    intent: str
    action: str
    script: Path
    argv: list[str]
    legacy_name: str | None = None


@dataclass(frozen=True)
class AliasSpec:
    intent: str
    action: str
    # When True, first remainder token may be treated as action (ledger, operator)
    passthrough_action: bool = False
    fixed_flags: tuple[str, ...] = ()


@dataclass(frozen=True)
class IntentSpec:
    description: str
    actions: dict[str, str]  # action -> script filename
    default_action: str | None = None
    # Optional specialized argv builder name keys later


INTENT_REGISTRY: dict[str, IntentSpec] = {
    "compile": IntentSpec(
        "Full brief-to-packet compile",
        {"run": "kubrick_compile.py"},
        "run",
    ),
    "retrieve": IntentSpec(
        "Registry-aware pattern retrieval",
        {"retrieve": "retrieve_symbolic_patterns_registry.py"},
        "retrieve",
    ),
    "ledger": IntentSpec(
        "Project symbolic ledger",
        {
            "init": "symbolic_ledger.py",
            "audit": "symbolic_ledger.py",
            "mutate": "symbolic_ledger.py",
            "rehydrate": "symbolic_ledger.py",
            "apply-forge": "symbolic_ledger.py",
            "export-retrieval": "symbolic_ledger.py",
            "record-pattern": "symbolic_ledger.py",
        },
        None,
    ),
    "design": IntentSpec(
        "Design-specification compilation",
        {"build": "generate_design_spec.py"},
        "build",
    ),
    "storyboard": IntentSpec(
        "Multi-frame state",
        {
            "propagate": "propagate_graph_state.py",
            "compare": "compare_frame_state.py",
        },
        None,
    ),
    "adapt": IntentSpec(
        "Neutral packet and provider adaptation",
        {
            "build": "build_model_adapter_packet.py",
            "provider": "adapt_provider.py",
        },
        "build",
    ),
    "visual": IntentSpec(
        "Visual QA loop",
        {
            "normalize": "normalize_visual_observation.py",
            "compare": "compare_visual_observation.py",
            "correct": "build_visual_correction_packet.py",
            "govern": "govern_correction_iteration.py",
            "closed-loop": "closed_loop_visual_qa.py",
        },
        None,
    ),
    "learn": IntentSpec(
        "Outcomes and multi-signal evolution",
        {
            "outcome": "record_pattern_outcome.py",
            "evolve": "propose_pattern_evolution.py",
            "forge-signals": "extract_forge_signals.py",
        },
        None,
    ),
    "check": IntentSpec(
        "Validation and regression",
        {
            "skill": "validate_hermes_skill.py",
            "corpus": "validate_pattern_corpus.py",
            "coverage": "audit_corpus_coverage.py",
            "artifact": "validate_artifact.py",
            "repeatability": "check_repeatability.py",
            "eval": "run_hermes_evals.py",
            # smoke is composite (skill + corpus); script is primary entry for registry
            "smoke": "validate_hermes_skill.py",
        },
        "smoke",
    ),
    "operate": IntentSpec(
        "Graph/ledger operators",
        {
            "saturation-score": "graph_operators.py",
            "counterpoint": "graph_operators.py",
            "convergence-lock": "graph_operators.py",
            "surface-occult-audit": "graph_operators.py",
            "symbolic-architecture-export": "graph_operators.py",
            "motif-mutation": "graph_operators.py",
        },
        None,
    ),
    "mcp": IntentSpec(
        "Optional MCP server",
        {"serve": "mcp_kubrick_server.py"},
        "serve",
    ),
    "bundle": IntentSpec(
        "Grok review bundle",
        {"build": "build_grok_review_bundle.py"},
        "build",
    ),
}


ALIAS_TABLE: dict[str, AliasSpec] = {
    "compile": AliasSpec("compile", "run"),
    "retrieve": AliasSpec("retrieve", "retrieve"),
    "ledger": AliasSpec("ledger", "init", passthrough_action=True),
    "design-build": AliasSpec("design", "build"),
    "storyboard-propagate": AliasSpec("storyboard", "propagate"),
    "storyboard-compare": AliasSpec("storyboard", "compare"),
    "adapter-build": AliasSpec("adapt", "build"),
    "adapt-provider": AliasSpec("adapt", "provider"),
    "adapt-grok": AliasSpec(
        "adapt", "provider", fixed_flags=("--provider", "grok-imagine")
    ),
    "adapt-flux": AliasSpec("adapt", "provider", fixed_flags=("--provider", "flux")),
    "adapt-sd3": AliasSpec("adapt", "provider", fixed_flags=("--provider", "sd3")),
    "adapt-midjourney": AliasSpec(
        "adapt", "provider", fixed_flags=("--provider", "midjourney")
    ),
    "visual-normalize": AliasSpec("visual", "normalize"),
    "visual-compare": AliasSpec("visual", "compare"),
    "visual-correct": AliasSpec("visual", "correct"),
    "correction-govern": AliasSpec("visual", "govern"),
    "closed-loop-qa": AliasSpec("visual", "closed-loop"),
    "outcome-record": AliasSpec("learn", "outcome"),
    "evolution-propose": AliasSpec("learn", "evolve"),
    "forge-signals": AliasSpec("learn", "forge-signals"),
    "validate-skill": AliasSpec("check", "skill"),
    "validate-corpus": AliasSpec("check", "corpus"),
    "coverage": AliasSpec("check", "coverage"),
    "artifact-validate": AliasSpec("check", "artifact"),
    "repeatability": AliasSpec("check", "repeatability"),
    "eval": AliasSpec("check", "eval"),
    "operator": AliasSpec("operate", "saturation-score", passthrough_action=True),
    "mcp-server": AliasSpec("mcp", "serve"),
    "grok-review-bundle": AliasSpec("bundle", "build"),
}


def all_legacy_commands() -> set[str]:
    """Return the set of legacy top-level command names."""
    return set(ALIAS_TABLE)

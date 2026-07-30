#!/usr/bin/env python3
"""Unified Hermes-native CLI for Kubrick's deterministic tools."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable

COMMANDS = {
    "validate-skill": "validate_hermes_skill.py",
    "validate-corpus": "validate_pattern_corpus.py",
    "coverage": "audit_corpus_coverage.py",
    "compile": "kubrick_compile.py",
    "retrieve": "retrieve_symbolic_patterns_registry.py",
    "ledger": "symbolic_ledger.py",
    "design-build": "generate_design_spec.py",
    "storyboard-propagate": "propagate_graph_state.py",
    "storyboard-compare": "compare_frame_state.py",
    "adapter-build": "build_model_adapter_packet.py",
    "adapt-grok": "adapt_grok_imagine.py",
    "adapt-flux": "adapt_flux.py",
    "adapt-sd3": "adapt_sd3.py",
    "adapt-midjourney": "adapt_midjourney.py",
    "adapt-provider": "adapt_provider.py",
    "visual-normalize": "normalize_visual_observation.py",
    "visual-compare": "compare_visual_observation.py",
    "visual-correct": "build_visual_correction_packet.py",
    "correction-govern": "govern_correction_iteration.py",
    "closed-loop-qa": "closed_loop_visual_qa.py",
    "outcome-record": "record_pattern_outcome.py",
    "evolution-propose": "propose_pattern_evolution.py",
    "forge-signals": "extract_forge_signals.py",
    "operator": "graph_operators.py",
    "mcp-server": "mcp_kubrick_server.py",
    "grok-review-bundle": "build_grok_review_bundle.py",
    "artifact-validate": "validate_artifact.py",
    "repeatability": "check_repeatability.py",
    "eval": "run_hermes_evals.py",
}


def main() -> None:
    parser = argparse.ArgumentParser(prog="kubrick", description="Kubrick standalone Hermes operator CLI")
    parser.add_argument("command", choices=sorted(COMMANDS))
    parser.add_argument("args", nargs=argparse.REMAINDER)
    ns = parser.parse_args()
    # argparse remainder keeps a leading -- sometimes; strip a lone separator
    args = ns.args
    if args and args[0] == "--":
        args = args[1:]
    result = subprocess.run([PY, str(ROOT / "scripts" / COMMANDS[ns.command]), *args], cwd=ROOT)
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()

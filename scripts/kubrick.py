#!/usr/bin/env python3
"""Unified Hermes-native CLI for Kubrick's existing deterministic tools."""
from __future__ import annotations
import argparse, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
PY=sys.executable

COMMANDS={
    "validate-skill":"validate_hermes_skill.py",
    "validate-corpus":"validate_pattern_corpus.py",
    "coverage":"audit_corpus_coverage.py",
    "compile":"kubrick_compile.py",
    "retrieve":"retrieve_symbolic_patterns_registry.py",
    "ledger":"symbolic_ledger.py",
    "storyboard-propagate":"propagate_graph_state.py",
    "storyboard-compare":"compare_frame_state.py",
    "adapter-build":"build_model_adapter_packet.py",
    "adapt-grok":"adapt_grok_imagine.py",
    "visual-compare":"compare_visual_observation.py",
    "visual-correct":"build_visual_correction_packet.py",
    "artifact-validate":"validate_artifact.py",
    "eval":"run_hermes_evals.py",
}

def main() -> None:
    parser=argparse.ArgumentParser(prog="kubrick",description="Kubrick standalone Hermes operator CLI")
    parser.add_argument("command",choices=sorted(COMMANDS))
    parser.add_argument("args",nargs=argparse.REMAINDER)
    ns=parser.parse_args()
    script=ROOT/"scripts"/COMMANDS[ns.command]
    result=subprocess.run([PY,str(script),*ns.args],cwd=ROOT)
    raise SystemExit(result.returncode)

if __name__=="__main__": main()

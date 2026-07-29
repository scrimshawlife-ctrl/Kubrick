#!/usr/bin/env python3
"""Compile a Kubrick brief into deterministic private and audience artifacts."""
from __future__ import annotations
import argparse, hashlib, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
try:
    import yaml
except ImportError:
    raise SystemExit("pyyaml required")

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable


def read(path):
    p = Path(path)
    return json.loads(p.read_text(encoding="utf-8")) if p.suffix == ".json" else yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def run(cmd):
    return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)


def fail(out, stage, reasons, diagnostic=None):
    final = {"status": "NOT_COMPUTABLE", "stage": stage, "reason_vector": reasons}
    if diagnostic:
        final["diagnostic"] = diagnostic[-1500:]
    (out / "compile-receipt.json").write_text(json.dumps(final, indent=2), encoding="utf-8")
    print(json.dumps(final, indent=2))
    raise SystemExit(1)


def build_structured_packet(brief, graph, selected):
    channels = brief.get("symbolic_channels") or {
        "diegetic": brief.get("diegetic_channel", []),
        "dramaturgical": brief.get("dramaturgical_channel", []),
        "cinematic": brief.get("cinematic_channel", []),
    }
    motifs = brief.get("motifs", [])
    if not motifs:
        motifs = [{
            "motif_id": selected,
            "dramatic_function": brief.get("dramatic_problem", "transform pressure"),
            "observed_form": node.get("observed_form", ""),
            "recurrences": [{
                "state": node.get("initial_state", "present"),
                "mutation": node.get("target_state", "transformed"),
                "consequence": edge.get("transformation", "") if graph.get("edges") else "state changes",
            }],
        } for node, edge in zip(graph.get("nodes", []), graph.get("edges", []) + [{}])]
    cultural = brief.get("cultural_sources", [])
    if not cultural and brief.get("cultural_context"):
        cultural = [{"source": brief["cultural_context"], "boundary": brief.get("cultural_boundary", "project-specific transfer only; no universal equivalence")}]
    return {
        "dramatic_function": brief.get("dramatic_problem", "transform pressure"),
        "causal_actions": brief.get("causal_actions") or [edge.get("transformation", "") for edge in graph.get("edges", []) if edge.get("transformation")],
        "motifs": motifs,
        "channels": channels,
        "convergence_sites": [{"site_id": site.get("site_id"), "functions": site.get("functions") or [site.get("observable_effect", ""), brief.get("desired_state_change", "transformed")]} for site in graph.get("convergence_sites", [])],
        "cultural_sources": cultural,
        "interpretation_claims": brief.get("interpretation_claims", []),
        "production_constraints": brief.get("production_constraints", []),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--brief", required=True)
    parser.add_argument("--ledger")
    parser.add_argument("--mode", choices=["single-frame", "scene", "storyboard", "diagnostic"], default="single-frame")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    brief = read(args.brief)
    if args.ledger:
        brief["symbolic_ledger"] = read(args.ledger)
    normalized = out / "brief.normalized.yaml"
    write(normalized, brief)

    retrieval = run([PY, str(ROOT / "scripts/retrieve_symbolic_patterns_registry.py"), "--brief", str(normalized), "--no-cache"])
    try:
        receipt = yaml.safe_load(retrieval.stdout) or {}
    except Exception:
        receipt = {}
    write(out / "retrieval-receipt.yaml", receipt)
    selected = (receipt.get("retrieval_receipt") or {}).get("selected_primary_grammar")
    if retrieval.returncode != 0 or not selected:
        fail(out, "retrieval", (receipt.get("retrieval_receipt") or {}).get("reason_vector", ["RETRIEVAL_FAILED"]))

    forms = brief.get("observed_forms") or []
    if len(forms) < 2:
        evidence = brief.get("observable_evidence") or []
        forms = [{"id": f"observed_{i+1}", "kind": "motif", "observed_form": str(value), "initial_state": "present", "target_state": brief.get("desired_state_change", "mutated"), "provenance_label": "OBSERVED", "pattern_links": [selected]} for i, value in enumerate(evidence[:3])]
    if len(forms) < 2:
        fail(out, "graph", ["INSUFFICIENT_OBSERVED_FORMS"])

    relations = brief.get("relations") or [{"source": forms[0].get("id", "observed_1"), "target": forms[1].get("id", "observed_2"), "relation": "opposes", "pressure": 0.7, "transformation": brief.get("desired_state_change", "relation changes")}]
    graph_spec = {
        "graph_id": hashlib.sha256(json.dumps(brief, sort_keys=True).encode()).hexdigest()[:16],
        "symbolic_intent": {"dramatic_function": brief.get("dramatic_problem", "transform pressure"), "emotional_force": brief.get("character_pressure", "pressure"), "desired_state_change": brief.get("desired_state_change", "transformed")},
        "observed_forms": forms,
        "relations": relations,
        "layers": brief.get("layers", {"layout_geometry": brief.get("geometry", []), "semantics_function": [brief.get("dramatic_problem", "")], "attributes_states": brief.get("state_differentials", [])}),
        "convergence_sites": brief.get("convergence_sites", [{"site_id": "primary", "node_ids": [forms[0].get("id"), forms[1].get("id")], "edge_ids": [0], "observable_effect": brief.get("convergence_effect", "relation becomes materially visible"), "mask_priority": 0.9}]),
        "residue": brief.get("residue", []),
        "surface_output": brief.get("surface_output", {}),
    }
    spec_path = out / "graph-input.yaml"
    write(spec_path, graph_spec)
    graph_run = run([PY, str(ROOT / "scripts/build_motif_graph.py"), "--input", str(spec_path), "--output", str(out / "motif-graph.private.yaml")])
    if graph_run.returncode != 0:
        fail(out, "graph", ["GRAPH_INVALID"], graph_run.stderr or graph_run.stdout)

    graph = read(out / "motif-graph.private.yaml")
    structured_packet = build_structured_packet(brief, graph, selected)
    structured_path = out / "structured-symbolic-packet.yaml"
    write(structured_path, structured_packet)
    structured_audit = run([PY, str(ROOT / "scripts/audit_symbolic_structure.py"), "--input", str(structured_path), "--output", str(out / "structured-anti-slop-report.json")])
    if structured_audit.returncode != 0:
        fail(out, "structured-audit", ["STRUCTURED_ANTI_SLOP_FAILED"], structured_audit.stdout)

    translate = run([PY, str(ROOT / "scripts/translate_motif_graph.py"), "--graph", str(out / "motif-graph.private.yaml"), "--mode", args.mode])
    try:
        audience = yaml.safe_load(translate.stdout) or {}
    except Exception:
        audience = {}
    write(out / "audience-constraints.yaml", audience)
    text_audit = run([PY, str(ROOT / "scripts/audit_anti_slop.py"), "--text", yaml.safe_dump(audience), "--json"])
    try:
        text_audit_data = json.loads(text_audit.stdout)
    except Exception:
        text_audit_data = {"status": "FAIL", "violations": [{"gate": "UNKNOWN", "repair": "inspect audit output"}]}
    (out / "text-anti-slop-report.json").write_text(json.dumps(text_audit_data, indent=2), encoding="utf-8")

    status = "COMPILED" if translate.returncode == 0 and text_audit.returncode == 0 else "NOT_COMPUTABLE"
    final = {
        "status": status,
        "compiler_version": "0.2.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": args.mode,
        "selected_primary": selected,
        "artifacts": {
            "retrieval": "retrieval-receipt.yaml",
            "private_graph": "motif-graph.private.yaml",
            "structured_packet": "structured-symbolic-packet.yaml",
            "structured_audit": "structured-anti-slop-report.json",
            "audience": "audience-constraints.yaml",
            "text_audit": "text-anti-slop-report.json",
        },
        "reason_vector": [] if status == "COMPILED" else ["TRANSLATION_OR_TEXT_AUDIT_FAILED"],
    }
    (out / "compile-receipt.json").write_text(json.dumps(final, indent=2), encoding="utf-8")
    print(json.dumps(final, indent=2))
    raise SystemExit(0 if status == "COMPILED" else 1)


if __name__ == "__main__":
    main()

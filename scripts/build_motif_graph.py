#!/usr/bin/env python3
"""Build and validate Kubrick's latent motif/structure graph IR."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

try:
    import yaml
except ImportError:
    print("pyyaml required. pip install pyyaml", file=sys.stderr)
    raise SystemExit(1)

LAYER_KEYS = ("layout_geometry", "semantics_function", "attributes_states")
NAMED_ESOTERICA = {
    "nigredo", "albedo", "rubedo", "athanor", "rebis", "ouroboros", "sephirot",
    "tarot", "qabalah", "kabbalah", "hermetic", "alchemy", "alchemical",
}


def load(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle) if path.suffix == ".json" else yaml.safe_load(handle) or {}


def tokens(value: Any) -> set[str]:
    return set(re.findall(r"[a-z0-9_]+", json.dumps(value).lower()))


def validate(graph: Dict[str, Any]) -> Dict[str, Any]:
    errors: List[str] = []
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    sites = graph.get("convergence_sites", [])
    layers = graph.get("layers", {})

    node_ids = {node.get("id") for node in nodes}
    for index, edge in enumerate(edges):
        if edge.get("source") not in node_ids or edge.get("target") not in node_ids:
            errors.append(f"edge[{index}] references unknown node")

    if not 1 <= len(sites) <= 2:
        errors.append("exactly one or two convergence sites are required")

    for site in sites:
        if len(site.get("node_ids", [])) < 2 or len(site.get("edge_ids", [])) < 1:
            errors.append(f"convergence site {site.get('site_id')} lacks relational density")

    leakage: List[str] = []
    layer_tokens = {key: tokens(layers.get(key, [])) for key in LAYER_KEYS}
    for left_index, left in enumerate(LAYER_KEYS):
        for right in LAYER_KEYS[left_index + 1 :]:
            shared = layer_tokens[left] & layer_tokens[right]
            for token in sorted(shared - {"light", "object", "state", "space", "character"}):
                leakage.append(f"{token}:{left}<->{right}")
    if leakage:
        errors.append("attribute leakage detected across disentangled layers")

    surface = graph.get("observable_prompt", "")
    named = sorted(tokens(surface) & NAMED_ESOTERICA)
    if named:
        errors.append("named esoterica leaked into observable output")

    density = round(len(edges) / max(1, len(nodes)), 4)
    graph["validation"] = {
        "attribute_leakage": leakage,
        "convergence_density": density,
        "named_esoterica_surface": named,
        "status": "VALID" if not errors else "INVALID",
        "errors": errors,
    }
    return graph


def build(spec: Dict[str, Any]) -> Dict[str, Any]:
    intent = spec.get("symbolic_intent", {})
    observed = spec.get("observed_forms", [])
    nodes = []
    for index, item in enumerate(observed):
        nodes.append({
            "id": item.get("id", f"node_{index + 1}"),
            "kind": item.get("kind", "motif"),
            "observed_form": item.get("observed_form", item.get("form", "")),
            "initial_state": item.get("initial_state", "unresolved"),
            "target_state": item.get("target_state", intent.get("desired_state_change", "transformed")),
            "provenance_label": item.get("provenance_label", "OBSERVED"),
            "lexicon_links": item.get("lexicon_links", []),
            "pattern_links": item.get("pattern_links", []),
        })

    edges = []
    relations = spec.get("relations", [])
    for relation in relations:
        edges.append({
            "source": relation["source"],
            "target": relation["target"],
            "relation": relation.get("relation", "opposes"),
            "pressure": float(relation.get("pressure", 0.5)),
            "transformation": relation.get("transformation", "relation changes under pressure"),
        })

    graph = {
        "schema_version": "1.0.0",
        "graph_id": spec.get("graph_id", "kubrick-graph"),
        "intent": {
            "dramatic_function": intent.get("dramatic_function", "transform"),
            "emotional_force": intent.get("emotional_force", "pressure"),
            "desired_state_change": intent.get("desired_state_change", "transformed"),
        },
        "nodes": nodes,
        "edges": edges,
        "layers": spec.get("layers", {key: [] for key in LAYER_KEYS}),
        "convergence_sites": spec.get("convergence_sites", []),
        "residue": spec.get("residue", []),
        "observable_prompt": spec.get("observable_prompt", ""),
        "validation": {},
    }
    return validate(graph)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    graph = build(load(Path(args.input)))
    output = yaml.safe_dump(graph, sort_keys=False)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        print(output)
    raise SystemExit(0 if graph["validation"]["status"] == "VALID" else 1)


if __name__ == "__main__":
    main()

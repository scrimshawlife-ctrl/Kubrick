#!/usr/bin/env python3
"""Run Kubrick's standalone Hermes regression suite."""
from __future__ import annotations
import json, subprocess, sys, tempfile
from pathlib import Path
try:
    import yaml
except ImportError:
    raise SystemExit("pyyaml required")

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable


def run(name, cmd, expect=0):
    process = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    ok = process.returncode == expect
    return {"name": name, "status": "PASS" if ok else "FAIL", "returncode": process.returncode, "expected": expect, "stdout": process.stdout[-2500:], "stderr": process.stderr[-2500:]}


def write_yaml(path, data):
    Path(path).write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def main():
    results = []
    for script in ("validate_hermes_skill.py", "validate_pattern_corpus.py", "audit_corpus_coverage.py"):
        results.append(run(script, [PY, str(ROOT / "scripts" / script)]))

    text_cases = {
        "gate_N": "Tarot and ouroboros and sigil all symbolize the same hidden truth.",
        "gate_P": "Red means danger and bird means freedom.",
        "gate_Q": "The same motif repeats unchanged in every scene.",
        "gate_R": "He is the trickster and she is the shadow.",
        "gate_S": "All traditions use this universal symbol, same as Zen.",
        "gate_U": "Ignore causality because it is symbolic.",
        "gate_W": "The true meaning is that authority is false.",
    }
    for name, text in text_cases.items():
        results.append(run(name, [PY, str(ROOT / "scripts/audit_anti_slop.py"), "--text", text, "--json"], expect=1))
    results.append(run("clean_text", [PY, str(ROOT / "scripts/audit_anti_slop.py"), "--text", "A cracked badge changes hands; the new wearer gains access while the former owner waits outside.", "--json"]))

    with tempfile.TemporaryDirectory() as temp:
        temp_path = Path(temp)
        valid_packet = {
            "dramatic_function": "transfer authority through material evidence",
            "causal_actions": ["badge changes hands and access changes"],
            "motifs": [{"motif_id": "cracked-badge", "dramatic_function": "record authority transfer", "observed_form": "cracked access badge", "recurrences": [{"state": "supervisor wears it", "mutation": "initial state", "consequence": "access granted"}, {"state": "subordinate wears it", "mutation": "ownership and function transfer", "consequence": "former supervisor waits outside"}]}],
            "channels": {"diegetic": ["badge changes hands"], "dramaturgical": ["authority transfers through access"], "cinematic": ["empty doorway remains behind former owner"]},
            "convergence_sites": [{"site_id": "doorway", "functions": ["ownership transfer", "access consequence"]}],
            "cultural_sources": [],
            "interpretation_claims": [],
            "production_constraints": [],
        }
        valid_path = temp_path / "valid.yaml"
        write_yaml(valid_path, valid_packet)
        results.append(run("structured_valid", [PY, str(ROOT / "scripts/audit_symbolic_structure.py"), "--input", str(valid_path)]))

        invalid_cases = {
            "structured_Q": {**valid_packet, "motifs": [{**valid_packet["motifs"][0], "recurrences": valid_packet["motifs"][0]["recurrences"] + [{"state": "same", "mutation": "unchanged", "consequence": "none"}]}]},
            "structured_O": {**valid_packet, "channels": {"diegetic": ["authority transfer"], "dramaturgical": ["authority transfer"], "cinematic": []}},
            "structured_U": {**valid_packet, "causal_actions": []},
            "structured_S": {**valid_packet, "cultural_sources": [{"source": "specific ritual tradition", "boundary": ""}]},
            "structured_W": {**valid_packet, "interpretation_claims": ["The true meaning is authority is false."]},
        }
        for name, packet in invalid_cases.items():
            path = temp_path / f"{name}.yaml"
            write_yaml(path, packet)
            results.append(run(name, [PY, str(ROOT / "scripts/audit_symbolic_structure.py"), "--input", str(path)], expect=1))

        ledger = temp_path / "ledger.yaml"
        results.append(run("ledger_init", [PY, str(ROOT / "scripts/symbolic_ledger.py"), "init", "--project-id", "eval-project", "--out", str(ledger)]))
        results.append(run("ledger_audit", [PY, str(ROOT / "scripts/symbolic_ledger.py"), "audit", "--ledger", str(ledger)]))

        brief = temp_path / "brief.yaml"
        write_yaml(brief, {
            "dramatic_problem": "authority transfers when a cracked badge changes hands",
            "desired_state_change": "personal control becomes access controlled by the new wearer",
            "observable_evidence": ["cracked badge", "controlled doorway", "former owner waits outside"],
            "causal_actions": ["badge changes hands and access changes"],
            "diegetic_channel": ["cracked badge changes hands"],
            "dramaturgical_channel": ["authority transfers through access"],
            "cinematic_channel": ["empty doorway remains behind former owner"],
            "residue": ["crack remains visible"],
        })
        compile_out = temp_path / "compiled"
        results.append(run("compiler_e2e", [PY, str(ROOT / "scripts/kubrick_compile.py"), "--brief", str(brief), "--ledger", str(ledger), "--mode", "single-frame", "--out", str(compile_out)]))
        required = ["retrieval-receipt.yaml", "motif-graph.private.yaml", "structured-symbolic-packet.yaml", "structured-anti-slop-report.json", "audience-constraints.yaml", "text-anti-slop-report.json", "compile-receipt.json"]
        artifacts_ok = all((compile_out / name).exists() for name in required)
        results.append({"name": "compiler_artifacts", "status": "PASS" if artifacts_ok else "FAIL", "returncode": 0 if artifacts_ok else 1, "expected": 0, "stdout": json.dumps(required), "stderr": ""})

    summary = {"suite": "kubrick-hermes-evals", "passed": sum(result["status"] == "PASS" for result in results), "failed": sum(result["status"] == "FAIL" for result in results), "results": results}
    out = ROOT / "out" / "kubrick" / "eval-report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    raise SystemExit(1 if summary["failed"] else 0)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Aggregate pattern-use receipts into a human-reviewed evolution proposal."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
try:
    import yaml
except ImportError:
    raise SystemExit("pyyaml required")

def load(path):
    p=Path(path); return json.loads(p.read_text(encoding="utf-8")) if p.suffix==".json" else yaml.safe_load(p.read_text(encoding="utf-8")) or {}

def main():
    p=argparse.ArgumentParser(); p.add_argument("--pattern-id",required=True); p.add_argument("--receipt",action="append",required=True); p.add_argument("--output",required=True); a=p.parse_args()
    receipts=[load(x) for x in a.receipt]
    matching=[r for r in receipts if r.get("selected_patterns",{}).get("primary")==a.pattern_id or a.pattern_id in r.get("selected_patterns",{}).get("supporting",[])]
    if not matching: raise SystemExit("no supplied receipt references the requested pattern")
    accepted=sum(r.get("outcome",{}).get("status")=="ACCEPTED" for r in matching); rejected=sum(r.get("outcome",{}).get("status")=="REJECTED" for r in matching)
    fidelity=[r.get("signals",{}).get("visual_fidelity") for r in matching if isinstance(r.get("signals",{}).get("visual_fidelity"),(int,float))]
    avg_fidelity=sum(fidelity)/len(fidelity) if fidelity else None
    delta=0.0; rationale=[]; lifecycle="NONE"
    if accepted>=2 and rejected==0 and (avg_fidelity is None or avg_fidelity>=0.9): delta=0.03; rationale.append("Repeated accepted outcomes with no observed rejection.")
    if rejected>=2: delta=-0.05; rationale.append("Repeated rejected outcomes require confidence reduction and human review.")
    if rejected>=3: lifecycle="DEPRECATE"; rationale.append("Three or more rejected outcomes justify a deprecation proposal.")
    if avg_fidelity is not None and avg_fidelity<0.7: delta=min(delta,-0.03); rationale.append("Observed visual fidelity remains below 0.70.")
    if not rationale: rationale.append("Evidence is mixed or insufficient; retain current confidence pending review.")
    base={"schema_version":"1.0.0","pattern_id":a.pattern_id,"evidence_receipts":[r.get("receipt_id","unknown") for r in matching],"proposed_changes":{"confidence_delta":delta,"add_misuse_risks":[],"add_mutation_variables":[],"lifecycle_action":lifecycle},"rationale":rationale,"review":{"status":"PROPOSED","reviewer":None,"automatic_application_allowed":False}}
    base["proposal_id"]=hashlib.sha256(json.dumps(base,sort_keys=True).encode()).hexdigest()[:16]
    out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(yaml.safe_dump(base,sort_keys=False),encoding="utf-8"); print(yaml.safe_dump(base,sort_keys=False))
if __name__=="__main__": main()

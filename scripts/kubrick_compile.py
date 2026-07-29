#!/usr/bin/env python3
"""Compile a Kubrick brief into deterministic private and audience artifacts."""
from __future__ import annotations
import argparse, hashlib, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
try:
    import yaml
except ImportError:
    raise SystemExit('pyyaml required')
ROOT=Path(__file__).resolve().parent.parent; PY=sys.executable

def read(path):
    p=Path(path); return json.loads(p.read_text()) if p.suffix=='.json' else yaml.safe_load(p.read_text()) or {}
def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(yaml.safe_dump(data,sort_keys=False),encoding='utf-8')
def run(cmd):
    p=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True); return p

def main():
    a=argparse.ArgumentParser(); a.add_argument('--brief',required=True); a.add_argument('--ledger'); a.add_argument('--mode',choices=['single-frame','scene','storyboard','diagnostic'],default='single-frame'); a.add_argument('--out',required=True); args=a.parse_args()
    out=Path(args.out); out.mkdir(parents=True,exist_ok=True); brief=read(args.brief)
    if args.ledger: brief['symbolic_ledger']=read(args.ledger)
    normalized=out/'brief.normalized.yaml'; write(normalized,brief)
    retrieval=run([PY,str(ROOT/'scripts/retrieve_symbolic_patterns_registry.py'),'--brief',str(normalized),'--no-cache'])
    try: receipt=yaml.safe_load(retrieval.stdout) or {}
    except Exception: receipt={}
    write(out/'retrieval-receipt.yaml',receipt)
    selected=(receipt.get('retrieval_receipt') or {}).get('selected_primary_grammar')
    if retrieval.returncode!=0 or not selected:
        final={'status':'NOT_COMPUTABLE','reason_vector':(receipt.get('retrieval_receipt') or {}).get('reason_vector',['RETRIEVAL_FAILED']),'stage':'retrieval'}
        (out/'compile-receipt.json').write_text(json.dumps(final,indent=2)); print(json.dumps(final,indent=2)); raise SystemExit(1)
    forms=brief.get('observed_forms') or []
    if len(forms)<2:
        evidence=brief.get('observable_evidence') or []
        forms=[{'id':f'observed_{i+1}','kind':'motif','observed_form':str(v),'initial_state':'present','target_state':brief.get('desired_state_change','mutated'),'provenance_label':'OBSERVED','pattern_links':[selected]} for i,v in enumerate(evidence[:3])]
    if len(forms)<2:
        final={'status':'NOT_COMPUTABLE','reason_vector':['INSUFFICIENT_OBSERVED_FORMS'],'stage':'graph'}; (out/'compile-receipt.json').write_text(json.dumps(final,indent=2)); print(json.dumps(final,indent=2)); raise SystemExit(1)
    relations=brief.get('relations') or [{'source':forms[0].get('id','observed_1'),'target':forms[1].get('id','observed_2'),'relation':'opposes','pressure':0.7,'transformation':brief.get('desired_state_change','relation changes')}]
    graph_spec={'graph_id':hashlib.sha256(json.dumps(brief,sort_keys=True).encode()).hexdigest()[:16],'symbolic_intent':{'dramatic_function':brief.get('dramatic_problem','transform pressure'),'emotional_force':brief.get('character_pressure','pressure'),'desired_state_change':brief.get('desired_state_change','transformed')},'observed_forms':forms,'relations':relations,'layers':brief.get('layers',{'layout_geometry':brief.get('geometry',[]),'semantics_function':[brief.get('dramatic_problem','')],'attributes_states':brief.get('state_differentials',[])}),'convergence_sites':brief.get('convergence_sites',[{'site_id':'primary','node_ids':[forms[0].get('id'),forms[1].get('id')],'edge_ids':[0],'observable_effect':brief.get('convergence_effect','relation becomes materially visible'),'mask_priority':0.9}]),'residue':brief.get('residue',[]),'surface_output':brief.get('surface_output',{})}
    spec_path=out/'graph-input.yaml'; write(spec_path,graph_spec)
    graph_run=run([PY,str(ROOT/'scripts/build_motif_graph.py'),'--input',str(spec_path),'--output',str(out/'motif-graph.private.yaml')])
    if graph_run.returncode!=0:
        final={'status':'NOT_COMPUTABLE','reason_vector':['GRAPH_INVALID'],'stage':'graph','diagnostic':graph_run.stderr[-1000:]}; (out/'compile-receipt.json').write_text(json.dumps(final,indent=2)); print(json.dumps(final,indent=2)); raise SystemExit(1)
    translate=run([PY,str(ROOT/'scripts/translate_motif_graph.py'),'--graph',str(out/'motif-graph.private.yaml'),'--mode',args.mode])
    try: audience=yaml.safe_load(translate.stdout) or {}
    except Exception: audience={}
    write(out/'audience-constraints.yaml',audience)
    audit=run([PY,str(ROOT/'scripts/audit_anti_slop.py'),'--text',yaml.safe_dump(audience),'--json'])
    try: audit_data=json.loads(audit.stdout)
    except Exception: audit_data={'status':'FAIL','violations':[{'gate':'UNKNOWN','repair':'inspect audit output'}]}
    (out/'anti-slop-report.json').write_text(json.dumps(audit_data,indent=2))
    status='COMPILED' if translate.returncode==0 and audit.returncode==0 else 'NOT_COMPUTABLE'
    final={'status':status,'compiler_version':'0.1.0','timestamp':datetime.now(timezone.utc).isoformat(),'mode':args.mode,'selected_primary':selected,'artifacts':{'retrieval':'retrieval-receipt.yaml','private_graph':'motif-graph.private.yaml','audience':'audience-constraints.yaml','anti_slop':'anti-slop-report.json'},'reason_vector':[] if status=='COMPILED' else ['TRANSLATION_OR_ANTI_SLOP_FAILED']}
    (out/'compile-receipt.json').write_text(json.dumps(final,indent=2)); print(json.dumps(final,indent=2)); raise SystemExit(0 if status=='COMPILED' else 1)
if __name__=='__main__': main()

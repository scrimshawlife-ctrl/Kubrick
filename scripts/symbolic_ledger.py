#!/usr/bin/env python3
"""Initialize, update, and audit Kubrick project symbolic ledgers."""
from __future__ import annotations
import argparse, json
from datetime import datetime, timezone
from pathlib import Path
try:
    import yaml
except ImportError:
    raise SystemExit("pyyaml required")

def load(path: Path):
    if not path.exists(): return {}
    return json.loads(path.read_text()) if path.suffix=='.json' else yaml.safe_load(path.read_text()) or {}

def dump(data, path: Path|None=None):
    text=yaml.safe_dump(data,sort_keys=False)
    if path: path.parent.mkdir(parents=True,exist_ok=True); path.write_text(text)
    else: print(text)

def init(project_id):
    return {'schema_version':'1.0.0','project_id':project_id,'governing_grammar':None,'supporting_grammars':[],'active_motifs':[],'retired_motifs':[],'prohibited_motifs':[],'unresolved_payoffs':[],'completed_payoffs':[],'collisions':[],'cultural_boundaries':[],'symbolic_debt':0.0,'saturation_score':0.0,'revision':0,'updated_at':datetime.now(timezone.utc).isoformat()}

def audit(d):
    errors=[]
    if d.get('schema_version')!='1.0.0': errors.append('unsupported schema_version')
    if not d.get('project_id'): errors.append('project_id required')
    if len(d.get('supporting_grammars',[]))>2: errors.append('supporting_grammars exceeds 2')
    ids=[m.get('motif_id') for m in d.get('active_motifs',[]) if isinstance(m,dict)]
    if len(ids)!=len(set(ids)): errors.append('duplicate active motif ids')
    if not 0<=float(d.get('saturation_score',0))<=1: errors.append('saturation_score outside 0..1')
    return {'status':'VALID' if not errors else 'INVALID','errors':errors,'active_motif_count':len(ids),'revision':d.get('revision',0)}

def main():
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest='cmd',required=True)
    a=sub.add_parser('init'); a.add_argument('--project-id',required=True); a.add_argument('--out',required=True)
    a=sub.add_parser('audit'); a.add_argument('--ledger',required=True)
    a=sub.add_parser('mutate'); a.add_argument('--ledger',required=True); a.add_argument('--motif-id',required=True); a.add_argument('--observed-form',required=True); a.add_argument('--state',required=True); a.add_argument('--mutation',required=True)
    args=p.parse_args()
    if args.cmd=='init': dump(init(args.project_id),Path(args.out)); return
    path=Path(args.ledger); d=load(path)
    if args.cmd=='audit': r=audit(d); print(json.dumps(r,indent=2)); raise SystemExit(0 if r['status']=='VALID' else 1)
    motifs=d.setdefault('active_motifs',[]); existing=next((m for m in motifs if m.get('motif_id')==args.motif_id),None)
    if existing:
        existing['current_state']=args.state; existing['last_mutation']=args.mutation; existing['recurrence_count']=int(existing.get('recurrence_count',0))+1
    else:
        motifs.append({'motif_id':args.motif_id,'observed_form':args.observed_form,'current_state':args.state,'recurrence_count':1,'last_mutation':args.mutation,'ownership':None,'pattern_links':[],'convergence_sites':[]})
    d['revision']=int(d.get('revision',0))+1; d['updated_at']=datetime.now(timezone.utc).isoformat(); dump(d,path)
if __name__=='__main__': main()

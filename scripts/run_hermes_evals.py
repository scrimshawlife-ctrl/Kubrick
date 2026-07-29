#!/usr/bin/env python3
"""Run Kubrick's standalone Hermes regression suite."""
from __future__ import annotations
import json, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent; PY=sys.executable

def run(name,cmd,expect=0):
    p=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
    return {'name':name,'status':'PASS' if p.returncode==expect else 'FAIL','returncode':p.returncode,'expected':expect,'stdout':p.stdout[-2000:],'stderr':p.stderr[-2000:]}

def main():
    results=[]
    for script in ('validate_hermes_skill.py','validate_pattern_corpus.py','audit_corpus_coverage.py'):
        results.append(run(script,[PY,str(ROOT/'scripts'/script)]))
    cases={'gate_N':'Tarot and ouroboros and sigil all symbolize the same hidden truth.','gate_P':'Red means danger and bird means freedom.','gate_Q':'The same motif repeats unchanged in every scene.','gate_R':'He is the trickster and she is the shadow.','gate_S':'All traditions use this universal symbol, same as Zen.','gate_U':'Ignore causality because it is symbolic.','gate_W':'The true meaning is that authority is false.'}
    for name,text in cases.items(): results.append(run(name,[PY,str(ROOT/'scripts/audit_anti_slop.py'),'--text',text,'--json'],expect=1))
    results.append(run('clean_text',[PY,str(ROOT/'scripts/audit_anti_slop.py'),'--text','A cracked badge changes hands; the new wearer gains access while the former owner waits outside.','--json']))
    with tempfile.TemporaryDirectory() as td:
        td=Path(td); ledger=td/'ledger.yaml'; brief=td/'brief.yaml'; compiled=td/'compiled'
        results.append(run('ledger_init',[PY,str(ROOT/'scripts/symbolic_ledger.py'),'init','--project-id','eval-project','--out',str(ledger)]))
        results.append(run('ledger_audit',[PY,str(ROOT/'scripts/symbolic_ledger.py'),'audit','--ledger',str(ledger)]))
        brief.write_text('''dramatic_problem: authority remains active after the leader exits because access and geometry preserve the system
desired_state_change: personal command becomes institutional pressure
format: single-frame
observable_evidence:
  - empty command chair
  - controlled doorway
  - repeated work cells
geometry:
  - repeated cells organized around an empty center
state_differentials:
  - occupied authority becomes operative vacancy
residue:
  - workers continue orienting toward the empty position
''',encoding='utf-8')
        results.append(run('compiler_end_to_end',[PY,str(ROOT/'scripts/kubrick_compile.py'),'--brief',str(brief),'--ledger',str(ledger),'--mode','single-frame','--out',str(compiled)]))
        required=['retrieval-receipt.yaml','motif-graph.private.yaml','audience-constraints.yaml','anti-slop-report.json','compile-receipt.json']
        present=all((compiled/name).exists() for name in required)
        results.append({'name':'compiler_artifact_set','status':'PASS' if present else 'FAIL','returncode':0 if present else 1,'expected':0,'stdout':','.join(required),'stderr':''})
    summary={'suite':'kubrick-hermes-evals','passed':sum(r['status']=='PASS' for r in results),'failed':sum(r['status']=='FAIL' for r in results),'results':results}
    out=ROOT/'out'/'kubrick'/'eval-report.json'; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2)); raise SystemExit(1 if summary['failed'] else 0)
if __name__=='__main__': main()

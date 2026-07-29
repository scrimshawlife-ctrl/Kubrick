#!/usr/bin/env python3
"""Run Kubrick's standalone Hermes regression suite."""
from __future__ import annotations
import json, subprocess, sys, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
PY=sys.executable

def run(name,cmd,expect=0):
    p=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
    ok=p.returncode==expect
    return {"name":name,"status":"PASS" if ok else "FAIL","returncode":p.returncode,"expected":expect,"stdout":p.stdout[-2000:],"stderr":p.stderr[-2000:]}

def main():
    results=[]
    for script in ("validate_hermes_skill.py","validate_pattern_corpus.py","audit_corpus_coverage.py"):
        results.append(run(script,[PY,str(ROOT/"scripts"/script)]))
    cases={
      "gate_N":"Tarot and ouroboros and sigil all symbolize the same hidden truth.",
      "gate_P":"Red means danger and bird means freedom.",
      "gate_Q":"The same motif repeats unchanged in every scene.",
      "gate_R":"He is the trickster and she is the shadow.",
      "gate_S":"All traditions use this universal symbol, same as Zen.",
      "gate_U":"Ignore causality because it is symbolic.",
      "gate_W":"The true meaning is that authority is false.",
    }
    for name,text in cases.items():
        results.append(run(name,[PY,str(ROOT/"scripts/audit_anti_slop.py"),"--text",text,"--json"],expect=1))
    results.append(run("clean_text",[PY,str(ROOT/"scripts/audit_anti_slop.py"),"--text","A cracked badge changes hands; the new wearer gains access while the former owner waits outside.","--json"],expect=0))
    summary={"suite":"kubrick-hermes-evals","passed":sum(r["status"]=="PASS" for r in results),"failed":sum(r["status"]=="FAIL" for r in results),"results":results}
    out=ROOT/"out"/"kubrick"/"eval-report.json"; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print(json.dumps(summary,indent=2)); raise SystemExit(1 if summary["failed"] else 0)
if __name__=="__main__": main()

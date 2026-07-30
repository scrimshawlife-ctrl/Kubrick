# Kubrick Quickstart

Kubrick is a **standalone Hermes skill**. Continuity Forge, MCP servers, model APIs, and external generation providers remain optional.

## 1. Install

```bash
./install.sh
# or: cp -R . ~/.hermes/skills/kubrick
```

Install runtime validation dependencies when working from the repository:

```bash
python -m pip install pyyaml jsonschema
```

## 2. Unified CLI

The default operator surface is:

```bash
python scripts/kubrick.py <command> [arguments]
```

Core commands:

```text
validate-skill          validate Hermes skill structure
validate-corpus         validate executable patterns
coverage                audit corpus and registry coverage
compile                 run the unified compiler
retrieve                run registry-aware retrieval
ledger                  initialize, audit, or mutate project state
storyboard-propagate    propagate graph state across frames
storyboard-compare      inspect adjacent-frame continuity
adapter-build           build a neutral provider packet
adapt-grok              emit Grok Imagine prompt packets
adapt-flux / adapt-sd3 / adapt-midjourney
closed-loop-qa          observation → differential score → correction
forge-signals           extract multi-signal Forge observations
evolution-propose       multi-signal proposal-only evolution
operator                saturation, counterpoint, lock, audit, export
mcp-server              optional stdio MCP wrapper
artifact-validate       validate YAML/JSON against a repository schema
eval                    run the regression suite
```

## 3. Compile a single frame

```bash
python scripts/kubrick.py compile \
  --brief project/brief.yaml \
  --ledger project/symbolic-ledger.yaml \
  --mode single-frame \
  --out project/out/kubrick
```

## 4. Compile a storyboard for a provider

```bash
python scripts/kubrick.py compile \
  --brief project/brief.yaml \
  --ledger project/symbolic-ledger.yaml \
  --mode storyboard \
  --storyboard-plan project/storyboard-plan.yaml \
  --provider grok-imagine \
  --out project/out/kubrick
```

Providers: `none`, `generic`, `grok-imagine`, `flux`, `sd3`, `midjourney`.

This orchestrates:

```text
retrieval
→ private graph
→ schema validation
→ structured symbolic audit
→ audience translation
→ storyboard propagation
→ transition comparison
→ neutral adapter packet
→ provider prompt packet
→ compile receipt
```

## 5. Forge feedback and multi-signal evolution

```bash
python scripts/kubrick.py forge-signals \
  --project-id myfilm \
  --input path/to/forge-ledger-diff.yaml \
  --output out/forge-bundle.yaml

python scripts/kubrick.py evolution-propose \
  --pattern-id interface_badge_authority_transfer \
  --receipt out/use-receipt.yaml \
  --forge-bundle out/forge-bundle.yaml \
  --output out/evolution-proposal.yaml
```

## 6. Closed-loop visual QA

```bash
python scripts/kubrick.py closed-loop-qa \
  --expected out/storyboard-symbolic-state.yaml \
  --observation-input observations/frame-001.json \
  --source-graph-id <graph-id> \
  --frame-id frame-001 \
  --out out/qa/frame-001
```

## 7. Operators

```bash
python scripts/kubrick.py operator saturation-score --ledger project/symbolic-ledger.yaml
python scripts/kubrick.py operator convergence-lock --graph out/motif-graph.private.yaml
python scripts/kubrick.py operator surface-occult-audit --input out/audience-constraints.yaml
python scripts/kubrick.py operator symbolic-architecture-export \
  --graph out/motif-graph.private.yaml \
  --ledger project/symbolic-ledger.yaml \
  --output out/symbolic-architecture-export.yaml
```

A successful storyboard run emits:

```text
brief.normalized.yaml
retrieval-receipt.yaml
graph-input.yaml
motif-graph.private.yaml
structured-symbolic-packet.yaml
structured-anti-slop-report.json
audience-constraints.yaml
text-anti-slop-report.json
storyboard-symbolic-state.yaml
storyboard-transition-report.json
model-adapter-packet.yaml
grok-imagine-prompt-packet.yaml
schema-graph.json
schema-storyboard.json
schema-adapter.json
compile-receipt.json
```

Weak retrieval, invalid graph state, schema drift, anti-slop failure, storyboard reset, residue loss, or adapter failure returns `NOT_COMPUTABLE` and exits nonzero.

## 5. Project ledger

```bash
python scripts/kubrick.py ledger init \
  --project-id my-film \
  --out project/symbolic-ledger.yaml

python scripts/kubrick.py ledger audit \
  --ledger project/symbolic-ledger.yaml

python scripts/kubrick.py ledger mutate \
  --ledger project/symbolic-ledger.yaml \
  --motif-id cracked-badge \
  --observed-form "a cracked access badge" \
  --state "worn by the former subordinate" \
  --mutation "ownership and access function transferred"
```

Local ledger state remains `PROPOSED` unless explicitly ingested by an external canonical system.

## 6. Validate an artifact

```bash
python scripts/kubrick.py artifact-validate \
  --artifact out/kubrick/motif-graph.private.yaml \
  --schema schemas/motif-structure-graph.schema.yaml
```

Validation errors include exact artifact paths.

## 7. Canonical example

```bash
python scripts/kubrick.py compile \
  --brief examples/authority-transfer-storyboard/brief.yaml \
  --ledger examples/authority-transfer-storyboard/symbolic-ledger.yaml \
  --mode storyboard \
  --storyboard-plan examples/authority-transfer-storyboard/storyboard-plan.yaml \
  --provider grok-imagine \
  --out out/kubrick/authority-transfer
```

## Runtime rules

- observed form before interpretation,
- dramatic function before symbolism,
- mandatory mutation or justified stagnation,
- one governing grammar and at most two supporting patterns,
- one or two convergence sites,
- private pattern and lexicon links never enter audience output,
- adapters may translate syntax but may not rewrite graph identity,
- local output is `PROPOSED`,
- weak evidence returns `NOT_COMPUTABLE`,
- Continuity Forge remains optional.

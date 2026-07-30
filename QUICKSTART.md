# Kubrick Quickstart

Kubrick is a **standalone Hermes skill** (v0.13.0). Continuity Forge, MCP servers, model APIs, and external generation providers remain optional.

## 1. Install

```bash
./install.sh
# or: cp -R . ~/.hermes/skills/kubrick
```

Install runtime validation dependencies when working from the repository:

```bash
python -m pip install pyyaml jsonschema
```

Validate:

```bash
python scripts/kubrick.py validate-skill
```

## 2. Unified CLI

```bash
python scripts/kubrick.py <command> [arguments]
```

### Core commands

```text
validate-skill          validate Hermes skill structure
validate-corpus         validate executable patterns
coverage                audit corpus and registry coverage
compile                 run the unified compiler
retrieve                run registry-aware retrieval
ledger                  init / audit / mutate / rehydrate / apply-forge
design-build            compile a governed design specification
storyboard-propagate    propagate graph state across frames
storyboard-compare      inspect adjacent-frame continuity
adapter-build           build a neutral provider packet
adapt-grok              emit Grok Imagine prompt packets
adapt-flux              emit Flux prompt packets
adapt-sd3               emit SD3 prompt packets
adapt-midjourney        emit Midjourney prompt packets
adapt-provider          syntax-only translation for any supported provider
visual-normalize        normalize human or optional model observations
visual-compare          compare expected and observed visual state
visual-correct          build targeted regeneration instructions
correction-govern       stop, continue, or escalate correction iterations
closed-loop-qa          observation → differential score → correction
outcome-record          record production-use evidence
evolution-propose       multi-signal proposal-only evolution
forge-signals           extract multi-signal Forge observations
operator                saturation, counterpoint, lock, audit, export, mutate
mcp-server              optional stdio MCP wrapper
grok-review-bundle      package the complete Grok review workflow
artifact-validate       validate YAML/JSON against a repository schema
repeatability           compare stable hashes across clean compiles
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

**Providers:** `none` · `generic` · `grok-imagine` · `flux` · `sd3` · `midjourney`

Pipeline:

```text
retrieval
→ private graph
→ schema validation
→ structured symbolic audit
→ audience translation
→ storyboard propagation
→ transition comparison
→ neutral adapter packet
→ provider prompt packet (syntax only)
→ compile receipt
```

### Canonical example

```bash
python scripts/kubrick.py compile \
  --brief examples/authority-transfer-storyboard/brief.yaml \
  --ledger examples/authority-transfer-storyboard/symbolic-ledger.yaml \
  --mode storyboard \
  --storyboard-plan examples/authority-transfer-storyboard/storyboard-plan.yaml \
  --provider grok-imagine \
  --out out/kubrick/authority-transfer
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
<provider>-prompt-packet.yaml
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
  --mutation "ownership and access function transferred" \
  --pattern-link interface_badge_authority_transfer

python scripts/kubrick.py ledger export-retrieval \
  --ledger project/symbolic-ledger.yaml \
  --out project/ledger-retrieval-snapshot.yaml
```

Local ledger state remains `PROPOSED` unless explicitly ingested by Continuity Forge or another authorized canonical system.

## 6. Forge feedback and multi-signal evolution

```bash
python scripts/kubrick.py forge-signals \
  --project-id myfilm \
  --input path/to/forge-ledger-diff.yaml \
  --output out/forge-bundle.yaml

# Example fixture:
# references/examples/forge-signals/ledger-before-after.yaml

python scripts/kubrick.py ledger apply-forge \
  --ledger project/symbolic-ledger.yaml \
  --forge-bundle out/forge-bundle.yaml

python scripts/kubrick.py evolution-propose \
  --pattern-id interface_badge_authority_transfer \
  --receipt out/use-receipt.yaml \
  --forge-bundle out/forge-bundle.yaml \
  --output out/evolution-proposal.yaml \
  --receipt-output out/evolution-proposal.multi-signal.yaml
```

Rules:

- Forge signal bundles are `OBSERVATION` only (`forge_canonical: true`).
- Every evolution event emits a deterministic multi-signal receipt.
- Large confidence deltas and structural/lifecycle mutations require human review.
- `automatic_application_allowed` is always `false`.

## 7. Closed-loop visual QA

```bash
python scripts/kubrick.py closed-loop-qa \
  --expected out/storyboard-symbolic-state.yaml \
  --observation-input observations/frame-001.json \
  --source-graph-id <graph-id> \
  --frame-id frame-001 \
  --out out/qa/frame-001
```

Produces:

```text
visual-observation.yaml
visual-fidelity-report.json
visual-correction-packet.yaml
closed-loop-qa-receipt.yaml
```

The receipt reports **geometry**, **state**, **residue**, and **convergence** fidelity separately. Graph identity mismatch fails closed (`NOT_COMPUTABLE`).

## 8. Multi-provider adapters

```bash
python scripts/kubrick.py adapter-build \
  --graph out/motif-graph.private.yaml \
  --storyboard out/storyboard-symbolic-state.yaml \
  --provider generic \
  --output out/model-adapter-packet.yaml

python scripts/kubrick.py adapt-provider \
  --packet out/model-adapter-packet.yaml \
  --provider flux \
  --output out/flux-prompt-packet.yaml

python scripts/kubrick.py adapt-provider \
  --packet out/model-adapter-packet.yaml \
  --provider sd3 \
  --output out/sd3-prompt-packet.yaml

python scripts/kubrick.py adapt-provider \
  --packet out/model-adapter-packet.yaml \
  --provider midjourney \
  --output out/midjourney-prompt-packet.yaml
```

Adapters change syntax only. They do not call external APIs, require credentials, or rewrite graph identity / private pattern links.

## 9. Operators and optional MCP

```bash
python scripts/kubrick.py operator saturation-score \
  --ledger project/symbolic-ledger.yaml

python scripts/kubrick.py operator counterpoint \
  --packet out/structured-symbolic-packet.yaml

python scripts/kubrick.py operator convergence-lock \
  --graph out/motif-graph.private.yaml

python scripts/kubrick.py operator surface-occult-audit \
  --input out/audience-constraints.yaml

python scripts/kubrick.py operator symbolic-architecture-export \
  --graph out/motif-graph.private.yaml \
  --ledger project/symbolic-ledger.yaml \
  --output out/symbolic-architecture-export.yaml

# Optional MCP surface — same CLI tools, never authoritative
python scripts/kubrick.py mcp-server
```

Every operator emits an auditable receipt and fails closed on weak evidence.

## 10. Design specification

```bash
python scripts/kubrick.py design-build --help
```

Use when consolidating design intent into a schema-valid specification (`schemas/design-specification.schema.yaml`). See:

- `references/design-specification-compiler.md`
- `templates/design-specification.yaml`

## 11. Validate an artifact

```bash
python scripts/kubrick.py artifact-validate \
  --artifact out/kubrick/motif-graph.private.yaml \
  --schema schemas/motif-structure-graph.schema.yaml
```

Validation errors include exact artifact paths.

## 12. Full verification

```bash
python scripts/kubrick.py validate-skill
python scripts/kubrick.py validate-corpus
python scripts/kubrick.py coverage
python scripts/kubrick.py eval
python scripts/test_outcome_governance.py
python scripts/test_wave2_wave3.py
python scripts/test_design_specification.py
python scripts/kubrick.py repeatability --output out/kubrick/repeatability-report.json
python scripts/audit_release_version.py --strict
```

## Runtime rules

- observed form before interpretation
- dramatic function before symbolism
- mandatory mutation or justified stagnation
- one governing grammar and at most two supporting patterns
- one or two convergence sites
- private pattern and lexicon links never enter audience output
- adapters may translate syntax but may not rewrite graph identity
- local output is `PROPOSED` / `OBSERVATION` / `PROPOSAL`
- evolution never applies automatically
- large confidence or structural changes require human review
- weak evidence returns `NOT_COMPUTABLE`
- Continuity Forge remains optional and canonical when connected
- MCP remains optional and never authoritative

## Further reading

| Doc | Purpose |
|---|---|
| `README.md` | Public overview and architecture |
| `SKILL.md` | Hermes operating contract |
| `docs/ROADMAP-v0.13.md` | Current roadmap |
| `docs/RELEASE-NOTES-v0.13.md` | What shipped in 0.13 |
| `docs/README.md` | Full docs index |
| `references/continuity-forge-integration.md` | Forge handoff + feedback |
| `references/hermes-model-adapters.md` | Adapter invariants |
| `references/hermes-visual-qa.md` | Visual QA contract |

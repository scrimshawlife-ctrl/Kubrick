# Kubrick Quickstart

Kubrick is a **standalone Hermes skill**. Continuity Forge, MCP servers, model APIs, and Python packaging are optional extensions.

## 1. Install

```bash
./install.sh
# or: cp -R . ~/.hermes/skills/kubrick
```

Restart Hermes after installation.

## 2. Validate

```bash
python scripts/validate_hermes_skill.py
python scripts/validate_pattern_corpus.py
python scripts/audit_corpus_coverage.py
python scripts/run_hermes_evals.py
```

## 3. Compile a symbolic packet

The default operator surface is the one-command compiler:

```bash
python scripts/kubrick_compile.py \
  --brief project/brief.yaml \
  --ledger project/symbolic-ledger.yaml \
  --mode single-frame \
  --out project/out/kubrick
```

Modes: `single-frame`, `scene`, `storyboard`, `diagnostic`.

A successful run writes:

```text
project/out/kubrick/
├── brief.normalized.yaml
├── retrieval-receipt.yaml
├── graph-input.yaml
├── motif-graph.private.yaml
├── audience-constraints.yaml
├── anti-slop-report.json
└── compile-receipt.json
```

Weak retrieval, insufficient observed forms, invalid graphs, private-symbol leakage, or anti-slop failure returns `NOT_COMPUTABLE` and exits nonzero.

## 4. Initialize and maintain a project ledger

```bash
python scripts/symbolic_ledger.py init \
  --project-id my-film \
  --out project/symbolic-ledger.yaml

python scripts/symbolic_ledger.py audit \
  --ledger project/symbolic-ledger.yaml

python scripts/symbolic_ledger.py mutate \
  --ledger project/symbolic-ledger.yaml \
  --motif-id cracked-badge \
  --observed-form "a cracked access badge" \
  --state "worn by the former subordinate" \
  --mutation "ownership and access function transferred"
```

The ledger remains local and `PROPOSED` unless an external canonical system explicitly ingests it.

## 5. Hermes prompts

### Vague premise

```text
Load kubrick. Develop this premise using observed form, dramatic pressure,
character transformation, and a restrained motif lifecycle.
```

### Existing scene

```text
Load kubrick. Diagnose this scene for causality, agency, motif mutation,
symbolic overload, and Gates A–W. Preserve approved facts.
```

### Single frame

```text
Load kubrick. Build and validate a private motif graph, then emit only
observable geometry, light, material, state differential, convergence, and residue.
```

### Ledger-aware revision

```text
Load kubrick. Revise this sequence against the supplied project symbolic ledger.
Emit the state delta and flag contradictions rather than overwriting prior state.
```

## 6. Lower-level deterministic tools

Registry-aware retrieval:

```bash
python scripts/retrieve_symbolic_patterns_registry.py --brief project/brief.yaml
```

Graph construction and translation:

```bash
python scripts/build_motif_graph.py --input graph-input.yaml --output motif-graph.private.yaml
python scripts/translate_motif_graph.py --graph motif-graph.private.yaml --mode single-frame
```

Anti-slop audit:

```bash
python scripts/audit_anti_slop.py --input audience-constraints.yaml --json
```

## 7. Runtime rules

- observed form before interpretation,
- dramatic function before symbolism,
- mandatory mutation or justified stagnation,
- one governing grammar and at most two supporting patterns,
- one or two convergence sites,
- private pattern and lexicon links never enter audience output,
- local output is `PROPOSED`,
- weak evidence returns `NOT_COMPUTABLE`,
- Continuity Forge remains optional.

## References

- `SKILL.md` — Hermes operating contract
- `schemas/project-symbolic-ledger.schema.yaml` — project persistence contract
- `schemas/motif-structure-graph.schema.yaml` — private graph IR
- `references/executable-corpus-registry.yaml` — default routes and guards
- `references/hermes-graph-operators.md` — graph operator contracts
- `evals/` — regression and adversarial fixtures

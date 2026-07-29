# Kubrick Quickstart

Kubrick is a **standalone Hermes skill**. Hermes loads the directory directly from `~/.hermes/skills/`; Continuity Forge, MCP servers, model APIs, and Python packaging are optional extensions.

## 1. Install for Hermes

```bash
# From the Kubrick repository root
./install.sh
```

Default destination:

```text
~/.hermes/skills/kubrick
```

Alternative categorized installation:

```bash
./install.sh creative
# → ~/.hermes/skills/creative/kubrick
```

Manual installation:

```bash
mkdir -p ~/.hermes/skills
cp -R . ~/.hermes/skills/kubrick
```

Restart Hermes after copying or updating the skill.

## 2. Validate the Installed Skill

The validator uses only the Python standard library and may be run from any working directory:

```bash
python ~/.hermes/skills/kubrick/scripts/validate_hermes_skill.py
```

It checks:

- Hermes frontmatter,
- required references and schemas,
- Python syntax,
- relative-path portability,
- repository-only assumptions,
- optional Continuity Forge status,
- fail-closed `NOT_COMPUTABLE` policy.

## 3. Choose the Hermes Entry Point

### Vague premise or concept

```text
Load kubrick. Develop this premise using observed form, dramatic pressure,
character transformation, and a restrained motif lifecycle.
```

### Existing scene or script

```text
Load kubrick. Diagnose this scene for causality, character agency,
motif mutation, symbolic overload, and Gates A–W. Preserve approved facts.
```

### Single-frame image prompt

```text
Load kubrick. Build a latent motif graph for this image, keep the hidden
architecture private, and output only observable geometry, light, material,
state differential, convergence, and residue constraints.
```

### Motif mutation

```text
Load kubrick. Apply RUNE.MUTATE to this motif under the new pressure.
Preserve identity lineage and change at least one observable variable.
```

### Continuity-aware revision

```text
Load kubrick. Revise this sequence against the supplied project ledger.
Emit the revision delta and flag contradictions rather than overwriting canon.
```

### Optional Continuity Forge handoff

```text
Load kubrick and hermes-continuity-forge. Prepare the approved symbolic
architecture and scene contracts for canonical ingestion. Surface all receipts.
```

Kubrick must continue locally when the companion skill is absent.

## 4. Deterministic Retrieval

Use retrieval when concrete pattern candidates improve the task—not for every request.

```bash
python scripts/retrieve_symbolic_patterns.py --brief path/to/brief.yaml
```

The retriever consumes project ledger state when supplied and emits:

- ranked patterns,
- score decomposition,
- collision and exclusion results,
- production-cost pressure,
- `NOT_COMPUTABLE` reason vectors,
- pattern-gap reporting,
- a receipt cache key based on brief and ledger snapshot.

Runtime receipts should be written to a project output directory, not treated as corpus source files.

## 5. Motif Graph Construction

For dense symbolic work or single-frame generation:

```bash
python scripts/build_motif_graph.py \
  --input path/to/graph-input.yaml \
  --out out/kubrick/motif-graph.yaml
```

The graph keeps these layers separate until convergence:

1. layout / geometry,
2. semantics / function,
3. attributes / states.

Validation flags excessive convergence sites, weak edge density, unknown references, layer leakage, and audience-facing named esoterica.

## 6. Explicit Maintenance Only

Evolution is not part of ordinary creative generation.

```bash
python scripts/evolve_from_use.py --dry-run
python scripts/evolve_from_use.py
```

Use it only after retrieval receipts and project outcomes provide evidence. Structural changes and large confidence shifts require human review.

## 7. Core Runtime Rules

- observed form before interpretation,
- dramatic function before symbolism,
- mandatory mutation or explicit justified stagnation,
- one governing grammar and at most two supporting patterns by default,
- one or two convergence sites,
- hidden symbolic architecture remains latent,
- local output is `PROPOSED`,
- weak evidence returns `NOT_COMPUTABLE`,
- Continuity Forge is optional.

## References

- `SKILL.md` — Hermes operating contract
- `references/hermes-runtime-contract.md` — dependency, path, artifact, and canon policy
- `docs/ROADMAP-v0.11.md` — production-hardening roadmap
- `references/patterns/` — executable pattern sidecars
- `schemas/motif-structure-graph.schema.yaml` — graph intermediate representation
- `evals/` — regression and adversarial fixtures

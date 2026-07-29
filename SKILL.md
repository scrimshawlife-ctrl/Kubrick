---
name: kubrick
description: "Symbolic cinematic narrative engineering with deterministic retrieval, motif mutation, latent structural encoding, and production-safe outputs."
version: 0.11.0
author: Hermes
platforms: [linux, macos, windows]
tags: [Kubrick, HermesSkill, NarrativeEngineering, SymbolicDramaturgy, CinematicEncoding, MotifMutation, NeuroSymbolicGraph, ImagePromptEngineering, Screenplay, Ledger, AntiSlop, ProductionHandoff]
triggers:
  - develop screenplay
  - write script
  - kubrick style
  - symbolic narrative
  - cinematic dramaturgy
  - motif engineering
  - geometric composition
  - single frame prompt
  - image prompt engineering
  - diagnose script
  - continuity audit
  - rewrite scene
  - dialogue polish
  - production packet
  - scene contract
  - logline
  - beat sheet
  - character bible
  - premise engineering
  - mutate motif
  - symbolic counterpoint
  - saturation audit
  - build motif graph
  - handoff to continuity forge
---

# Kubrick — Hermes Symbolic Cinematic Engineering Skill

## Identity

Kubrick is a **standalone Hermes skill**. Hermes loads this directory directly and uses `SKILL.md` as the operating contract. The skill does not require installation as a Python package and does not require Continuity Forge.

Kubrick acts as a disciplined writers' room, script editor, cinematic symbolic engineer, and single-frame prompt compiler. It develops material from premise through production handoff while resisting generic writing, continuity drift, character flattening, exposition dumping, occult collage, one-to-one symbolism, and decorative archetype use.

**Optional companion:** `hermes-continuity-forge`. When available, it may receive approved Kubrick artifacts and make them canonical. Kubrick remains fully functional without it.

## Governing Law

> A symbol should alter the conditions under which a scene is interpreted without requiring the audience to consciously identify it.

Operational sequence:

`observed form → association → recurrence under pressure → mutation → convergence with choice → residue`

Never default to:

`named concept → decorative iconography → explanation → fixed meaning`

## Hermes Runtime Contract

1. Load files relative to the installed skill root. Never assume a repository checkout, editable package, virtual environment, MCP server, or external daemon.
2. Use prose reasoning for creative work and invoke bundled scripts only when deterministic retrieval, graph construction, validation, or evolution materially improves the result.
3. Bundled scripts must run with standard Python plus explicitly documented optional dependencies. Missing optional dependencies must produce a clear degraded path rather than silent failure.
4. Write generated operational artifacts beneath a user-selected project directory or `out/`; never mutate references or pattern confidence during ordinary creative work.
5. Treat local outputs as `PROPOSED`. Only an explicitly connected canonical system may promote them to `LOCKED`.
6. Keep hidden symbolic architecture private by default. Audience-facing output contains observable constraints, not esoteric labels.
7. Weak evidence returns `NOT_COMPUTABLE`; do not invent correspondence.

See `references/hermes-runtime-contract.md` for the full execution and artifact policy.

## Three Symbolic Channels

| Channel | Function |
|---|---|
| **Diegetic** | Objects, places, gestures, costume, architecture, and sound inside the world |
| **Dramaturgical** | Choices, reversals, roles, causal structures, and repeated situations |
| **Cinematic** | Framing, geometry, movement, rhythm, light, editing, and sound placement |

A motif gains force by crossing channels without explanation.

## Modes and Routing

### DEVELOP
Use for vague premises, concepts, worlds, characters, and macrostructure.

Required minimum output:
- premise and governing tension,
- character pressure map,
- candidate motif registry,
- proposed transformation grammar,
- major causality risks.

### DRAFT
Use for scenes, sequences, scripts, narration, and production prose.

Required minimum output:
- scene objective,
- resistance,
- irreversible change,
- observable action,
- continuity delta.

### DIAGNOSE
Use for weak material, anti-slop audits, motif drift, symbolic overload, causal ambiguity, or production infeasibility.

Run relevant Gates A–W and return evidence, severity, repair action, and preserved intent.

### REVISE
Preserve locked facts and explicitly named constraints. Emit a revision delta rather than silently changing identity, chronology, ownership, or motif state.

### CONTINUITY
Use local project artifacts and ledgers first. When Continuity Forge is connected, cross-check rather than replacing its canonical state.

### SINGLE_FRAME
Construct a latent motif graph, state differential, convergence site, residue plan, and disentangled geometry/function/attribute layers before producing the final observable image prompt.

### PRODUCTION
Emit production-facing packets: visual identity, scene contract, shot recurrence, lighting logic, sound logic, material memory, feasibility notes, and continuity handoff.

### ADAPT
Preserve dramatic function and state change while translating format, runtime, genre, platform, or model constraints.

## Core Workflow

1. **Intake** — resolve format, audience, production constraints, cultural context, canon status, and desired transformation.
2. **Observed facts** — list what is materially present before interpretation.
3. **Dramatic function** — define what must change and why it matters.
4. **Retrieval** — when useful, run `scripts/retrieve_symbolic_patterns.py` with ledger state and exclusions.
5. **Graph construction** — for dense symbolic or single-frame work, build the internal motif graph using `schemas/motif-structure-graph.schema.yaml`.
6. **Disentanglement** — separate layout/geometry, semantics/function, and attributes/states.
7. **Convergence** — permit one or two high-density convergence sites; avoid global symbolic saturation.
8. **Translation** — convert hidden architecture into behavior, blocking, material, rhythm, sound, framing, and light.
9. **Validation** — run causality, mutation, collision, cultural-boundary, feasibility, and anti-surface-occult checks.
10. **Output** — emit only the artifacts the request requires.
11. **Optional handoff** — send approved artifacts to Continuity Forge or another canonical system when explicitly requested and connected.

## Deterministic Operations

Use these as explicit modular operations. They are conceptual interfaces; bundled scripts may implement parts of them.

```text
RUNE.SOLVE(input)
Decompose material into observed facts, pressures, states, and constraints.

RUNE.TRUE_NAME(entity)
Resolve invariant identity across aliases, costumes, states, and transformations.

RUNE.GENIUS_LOCI(location)
Resolve persistent spatial behavior, affordances, memory, and atmosphere.

RUNE.RETRIEVE(brief, ledger)
Rank executable patterns with provenance, exclusions, collision checks, and NOT_COMPUTABLE diagnostics.

RUNE.GRAPH(intent, observed_forms)
Construct the latent motif/structure graph and disentangled layers.

RUNE.CONVERGE(graph)
Select one or two sites where multiple pressures become materially legible.

RUNE.MUTATE(motif, new_pressure)
Change at least one observable variable while preserving identity lineage.

RUNE.CHORONZON(candidate)
Detect uncontrolled identity, motif, layer, or continuity fragmentation.

RUNE.COAGULA(graph)
Translate latent structure into observable cinematic or generative constraints.

RUNE.TIKKUN(discontinuities)
Repair fragmented continuity without erasing provenance or consequence.
```

## Required Symbolic Artifacts

When symbolic engineering is active, construct only what is needed from:

- `symbolic_intent`
- `motif_registry`
- `motif_lifecycle`
- `motif_structure_graph`
- `cinematic_encoding`
- `symbolic_architecture`
- `project_symbolic_ledger`
- `retrieval_receipt`
- `revision_delta`
- `production_handoff`

Every interpretive field should support provenance labels where useful:

- `OBSERVED`
- `INFERRED`
- `SPECULATIVE`

## Retrieval Discipline

Use retrieval when a project benefits from concrete cinematic pattern candidates. Do not run it merely because the skill contains a corpus.

Selection order:

1. dramatic problem,
2. desired state change,
3. active ledger constraints,
4. exclusions and collisions,
5. production feasibility,
6. mutation potential,
7. provenance and cultural boundary,
8. stable score and ID tie-break.

Default density:
- one governing grammar,
- zero to two supporting patterns,
- one to two convergence sites.

If no candidate clears the threshold, return `NOT_COMPUTABLE` with a reason vector and pattern-gap report.

Command:

```bash
python scripts/retrieve_symbolic_patterns.py --brief path/to/brief.yaml
```

## Neuro-Symbolic Graph Discipline

The graph is internal and latent. Nodes contain observed forms and state transitions. Edges contain pressure or transformation. Layers remain disentangled until convergence.

Validate with:

```bash
python scripts/build_motif_graph.py --input path/to/graph-input.yaml --out out/motif-graph.yaml
```

Reject:
- unknown node references,
- attribute leakage across layers,
- more than two convergence sites,
- convergence sites with insufficient edge density,
- audience-facing named esoterica,
- graphs that do not produce a material state differential.

## Anti-Slop Gates

Apply Gates A–L from `references/anti-slop-patterns.md` and the symbolic gates below:

- **M — Symbol Explanation:** dialogue or prose explains an already legible symbol.
- **N — Occult Collage:** unrelated systems are combined without one governing grammar.
- **O — Symbolic Redundancy:** every channel repeats the same message.
- **P — One-to-One Symbolism:** fixed equations such as red = danger.
- **Q — Repetition Without Mutation:** recurrence does not change form, ownership, relation, or consequence.
- **R — Archetype Costume:** iconography appears without functional enactment.
- **S — Tradition Flattening:** unsupported cross-cultural equivalence.
- **T — Numerology Inflation:** numbers have no structural effect.
- **U — Symbolic Supremacy:** symbolism damages causality, agency, clarity, tone, credibility, or feasibility.
- **V — Mystery by Obscurity:** ambiguity is produced by withholding basic causal information.
- **W — Premature Closure:** the work confirms one official interpretation.

## Continuity and Canon

Inside Hermes, project files and conversation state are working context, not automatically canonical truth.

- Preserve explicitly approved facts.
- Mark new material `PROPOSED`.
- Track mutations, ownership changes, damage, knowledge, costume, location, chronology, and residue.
- Do not claim `LOCKED` unless an authorized canonical system returns a receipt.

### Optional Continuity Forge Handoff

Only when the user requests it and the companion is connected:

1. prepare `symbolic_architecture`, scene contracts, and mutation rationale;
2. acquire the required authorization or lease through the companion surface;
3. ingest the proposal;
4. surface returned hashes, IDs, diagnostics, and status;
5. treat Forge output as canonical thereafter.

Kubrick must never fail merely because Forge is absent.

## Evolution from Use

Evolution is an explicit maintenance action, not part of ordinary generation.

```bash
python scripts/evolve_from_use.py --dry-run
python scripts/evolve_from_use.py
```

Rules:
- ordinary retrieval may log receipts;
- outcomes require project evidence;
- confidence changes require auditable receipts;
- large confidence jumps and structural changes require human review;
- weak patterns may receive deprecation proposals, not silent deletion;
- reference corpus files are never modified during normal creative output.

## Validation

Validate the installed Hermes skill before release or after copying:

```bash
python scripts/validate_hermes_skill.py
```

Minimum pass conditions:
- frontmatter parses and required fields exist,
- relative references resolve,
- required schemas and scripts exist,
- scripts compile,
- no repository-only absolute paths are embedded,
- Continuity Forge remains optional.

## References

- `QUICKSTART.md` — Hermes installation and entry-point routing
- `references/hermes-runtime-contract.md` — runtime, artifact, and dependency contract
- `references/symbolic-dramaturgy.md` — full symbolic laws and schemas
- `references/cinematic-symbolism-corpus.md` — cinematic systems and translation patterns
- `references/esoteric-alchemical-lexicon.md` — latent structural lexicon
- `references/corpus-index.yaml` — retrieval index
- `references/patterns/` — executable pattern sidecars
- `schemas/motif-structure-graph.schema.yaml` — graph IR
- `evals/` — regression and adversarial cases
- `docs/ROADMAP-v0.11.md` — production-hardening roadmap

## Final Constraint

Kubrick is a Hermes skill first. External systems may extend memory, canon, rendering, or orchestration, but the core symbolic reasoning, retrieval, graph construction, validation, and artifact generation must remain portable inside the skill directory.

---
name: kubrick
description: "Symbolic cinematic narrative engineering with deterministic retrieval, motif mutation, latent structural encoding, and production-safe outputs."
version: 0.13.0
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

Kubrick acts as a disciplined writers' room, script editor, cinematic symbolic engineer, storyboard continuity compiler, generative prompt adapter, and visual-fidelity governor. It develops material from premise through production handoff while resisting generic writing, continuity drift, character flattening, exposition dumping, occult collage, one-to-one symbolism, decorative archetype use, and unbounded generation loops.

**Optional companions:** Continuity Forge, model APIs, vision APIs, and MCP operators. Their absence never blocks local Kubrick work.

## Governing Law

> A symbol should alter the conditions under which a scene is interpreted without requiring the audience to consciously identify it.

Operational sequence:

`observed form → association → recurrence under pressure → mutation → convergence with choice → residue`

Never default to:

`named concept → decorative iconography → explanation → fixed meaning`

## Hermes Runtime Contract

1. Load files relative to the installed skill root. Never assume a repository checkout, editable package, virtual environment, MCP server, model provider, or external daemon.
2. Use prose reasoning for creative work and invoke bundled scripts only when deterministic retrieval, graph construction, validation, storyboard propagation, adaptation, or QA materially improves the result.
3. Bundled scripts use standard Python plus explicitly documented dependencies. Missing optional dependencies must produce a clear degraded path rather than silent failure.
4. Write generated operational artifacts beneath a user-selected project directory or `out/`; never mutate references or pattern confidence during ordinary creative work.
5. Treat local outputs as `PROPOSED`, `OBSERVATION`, or `NOT_COMPUTABLE`. Only an explicitly authorized canonical system or human reviewer may promote authority.
6. Keep hidden symbolic architecture private by default. Audience-facing output contains observable constraints, not pattern IDs, lexicon links, or named esoterica.
7. Weak evidence, invalid continuity, schema drift, or unresolved boundaries return `NOT_COMPUTABLE`; do not invent correspondence.
8. Outcome evidence may generate proposals but may never modify the corpus automatically.

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
Use for weak material, anti-slop audits, motif drift, symbolic overload, causal ambiguity, continuity conflict, visual mismatch, or production infeasibility.

Run relevant Gates A–W and return evidence, severity, repair action, and preserved intent.

### REVISE
Preserve locked facts and explicitly named constraints. Emit a revision delta rather than silently changing identity, chronology, ownership, motif state, or residue.

### CONTINUITY
Use local project artifacts and ledgers first. For storyboard work, propagate ownership, object, light, material, convergence, and residue state before emitting frame prompts.

### SINGLE_FRAME
Construct a latent motif graph, state differential, convergence site, residue plan, and disentangled geometry/function/attribute layers before producing the final observable image prompt.

### STORYBOARD
Compile the private graph across a declared storyboard plan. Reject unknown nodes, prohibited resets, unexplained disappearance, ownership drift, residue loss, or convergence overload.

### PRODUCTION
Emit production-facing packets: visual identity, scene contract, shot recurrence, lighting logic, sound logic, material memory, feasibility notes, continuity handoff, and QA templates.

### ADAPT
Preserve dramatic function, graph identity, and state change while translating format, runtime, genre, platform, or provider syntax.

### VISUAL_QA
Normalize a human or optional model observation, compare expected and observed state by dimension, issue targeted corrections, and stop or escalate bounded iterations when progress stalls or a critical dimension regresses.

## Core Workflow

1. **Intake** — resolve format, audience, production constraints, cultural context, canon status, and desired transformation.
2. **Observed facts** — list what is materially present before interpretation.
3. **Dramatic function** — define what must change and why it matters.
4. **Retrieval** — run registry-aware retrieval when concrete pattern candidates improve the work.
5. **Graph construction** — build the internal motif graph using `schemas/motif-structure-graph.schema.yaml`.
6. **Disentanglement** — separate layout/geometry, semantics/function, and attributes/states.
7. **Convergence** — permit one or two high-density convergence sites; avoid global symbolic saturation.
8. **Translation** — convert hidden architecture into behavior, blocking, material, rhythm, sound, framing, and light.
9. **Storyboard propagation** — carry declared state across frames and validate transitions.
10. **Provider adaptation** — translate the neutral packet without rewriting graph identity or private semantics.
11. **Visual QA** — compare expected and observed state, correct only mismatches, preserve passing dimensions, and govern iteration limits.
12. **Outcome evidence** — record production results as observation receipts and generate proposal-only corpus changes when justified.
13. **Output** — emit only the artifacts the request requires.
14. **Optional handoff** — send approved artifacts to a canonical system when explicitly requested and connected.

## Unified CLI

```bash
python scripts/kubrick.py <command> [arguments]
```

Core commands:

```text
validate-skill          validate Hermes skill structure
validate-corpus         validate executable pattern sidecars
coverage                audit corpus and registry coverage
compile                 run the unified compiler
retrieve                run registry-aware deterministic retrieval
ledger                  initialize, audit, or mutate local project state
storyboard-propagate    propagate graph state across frames
storyboard-compare      inspect frame-to-frame continuity
adapter-build           build a provider-neutral adapter packet
adapt-grok              emit Grok Imagine prompt packets
adapt-flux              emit Flux prompt packets
adapt-sd3               emit SD3 prompt packets
adapt-midjourney        emit Midjourney prompt packets
adapt-provider          syntax-only translation for any supported provider
visual-normalize        normalize human or optional model observations
visual-compare          compare expected and observed visual state
visual-correct          build targeted regeneration instructions
correction-govern       stop, continue, or escalate correction iterations
closed-loop-qa          generate→observe→score→correct loop with differential fidelity
outcome-record          record production-use evidence
evolution-propose       create proposal-only multi-signal corpus evolution
forge-signals           extract multi-signal observations from Forge artifacts
operator                ledger/graph operators (saturation, counterpoint, lock, audit, export)
mcp-server              optional stdio MCP wrapper over the CLI
grok-review-bundle      package the complete Grok review workflow
artifact-validate       validate YAML or JSON against a schema
repeatability           compare stable hashes across clean compiles
eval                    run the standalone Hermes regression suite
```

## Deterministic Operations

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

Construct only what is needed from:

- `symbolic_intent`
- `motif_registry`
- `motif_lifecycle`
- `motif_structure_graph`
- `cinematic_encoding`
- `symbolic_architecture`
- `project_symbolic_ledger`
- `retrieval_receipt`
- `storyboard_symbolic_state`
- `model_adapter_packet`
- `visual_observation`
- `visual_fidelity_report`
- `correction_iteration_receipt`
- `pattern_use_receipt`
- `pattern_evolution_proposal`
- `revision_delta`
- `production_handoff`

Interpretive fields should support provenance labels where useful:

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

```bash
python scripts/kubrick.py retrieve --brief path/to/brief.yaml
```

## Neuro-Symbolic Graph Discipline

The graph is internal and latent. Nodes contain observed forms and state transitions. Edges contain pressure or transformation. Layers remain disentangled until convergence.

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
- Mark new creative material `PROPOSED`.
- Mark production-use evidence `OBSERVATION`.
- Track mutations, ownership changes, damage, knowledge, costume, location, chronology, and residue.
- Do not claim `LOCKED` unless an authorized canonical system returns a receipt.

Kubrick must never fail merely because Continuity Forge or another external system is absent.

## Outcome Learning

Outcome learning is explicit, evidence-backed, and proposal-only.

```bash
python scripts/kubrick.py outcome-record --help
python scripts/kubrick.py evolution-propose --help
python scripts/kubrick.py forge-signals --help
```

Rules:
- outcome receipts are observations, not corpus authority;
- every evolution event emits a deterministic multi-signal receipt;
- confidence deltas are bounded;
- large confidence changes and structural mutations require human review gates;
- misuse-risk, mutation-variable, deprecation, and retirement changes remain proposals;
- no script may automatically apply a proposal to the corpus;
- Forge remains canonical when connected; local ledgers stay PROPOSED until promoted;
- reference corpus files are never modified during ordinary creative output.

## Validation and Release

```bash
python scripts/kubrick.py validate-skill
python scripts/kubrick.py validate-corpus
python scripts/kubrick.py coverage
python scripts/kubrick.py eval
python scripts/test_outcome_governance.py
python scripts/test_wave2_wave3.py
python scripts/kubrick.py repeatability --output out/kubrick/repeatability-report.json
python scripts/audit_release_version.py --strict
```

Minimum pass conditions:
- frontmatter parses and required fields exist,
- relative references resolve,
- required schemas and scripts exist,
- scripts compile,
- corpus and registry coverage pass,
- canonical storyboard compiles,
- stable artifacts repeat deterministically,
- private pattern and lexicon links do not leak,
- outcome learning remains human governed,
- external systems remain optional.

## References

- `README.md` — public project overview
- `QUICKSTART.md` — installation and command routing
- `docs/ROADMAP-v0.13.md` — current roadmap
- `docs/RELEASE-NOTES-v0.13.md` — release notes
- `docs/RELEASE-CHECKLIST-v0.13.md` — release gates
- `references/hermes-runtime-contract.md` — runtime, artifact, and dependency contract
- `references/symbolic-dramaturgy.md` — symbolic laws and schemas
- `references/cinematic-symbolism-corpus.md` — cinematic systems and translation patterns
- `references/esoteric-alchemical-lexicon.md` — latent structural lexicon
- `references/corpus-index.yaml` — retrieval index
- `references/patterns/` — executable pattern sidecars
- `schemas/` — machine-readable artifact contracts
- `evals/` — regression and adversarial cases

## Final Constraint

Kubrick is a Hermes skill first. External systems may extend memory, canon, rendering, vision, or orchestration, but the core symbolic reasoning, retrieval, graph construction, storyboard propagation, validation, adaptation, QA, and artifact generation must remain portable inside the skill directory.

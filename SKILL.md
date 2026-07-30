---
name: "kubrick"
description: "OpenClaw-native cinematic engineering, deterministic symbolism, storyboard continuity, provider adaptation, visual QA, and governed learning."
license: MIT
metadata:
  kubrick_version: "0.13.0"
  openclaw:
    requires:
      bins:
        - python3
    envVars:
      - name: KUBRICK_STATE_DIR
        required: false
        description: Optional writable directory for retrieval caches, receipts, outcomes, and reversible evolution overlays.
    emoji: "🎬"
    homepage: https://github.com/scrimshawlife-ctrl/Kubrick/tree/openclaw
---

# Kubrick for OpenClaw

Kubrick is a standalone OpenClaw Agent Skill for symbolic cinematic narrative engineering. Use it as a disciplined writers' room, script editor, motif system, storyboard continuity engine, provider-prompt compiler, and visual-fidelity reviewer.

It converts dramatic intent into observable cinematic structure while preserving causality, character agency, continuity, provenance, production feasibility, and a strict boundary between private symbolic reasoning and audience-facing output.

Continuity Forge is optional. It becomes canonical only after an explicit, verified handoff.

## Governing law

A symbol should alter how a scene is interpreted without requiring the audience to consciously identify it.

Use this sequence:

`observed form → contextual association → recurrence under new pressure → formal mutation → convergence with character choice → retrospective legibility`

Reject this sequence:

`symbol appears → symbol is explained → meaning is delivered`

## When to use

Use Kubrick when the request involves one or more of:

- screenplay, pilot, short, video, podcast, scene, logline, beat sheet, or character-bible development;
- narrative or scene diagnosis, revision, continuity, blocking, dialogue, motif mutation, or production feasibility;
- motif architecture across diegetic, dramaturgical, and cinematic channels;
- private motif graphs, symbolic ledgers, storyboards, design specifications, provider prompt packets, or visual QA;
- governed use receipts and proposal-only pattern evolution;
- an explicit Continuity Forge handoff.

Do not use Kubrick for generic prose that does not benefit from cinematic or dramatic structure. Do not imitate a living creator's exact style; translate requested qualities into high-level formal constraints.

## OpenClaw runtime contract

Treat the installed skill directory as immutable.

- Resolve repository paths relative to this `SKILL.md`, never from the caller's current working directory.
- Store retrieval caches, receipts, outcomes, and reversible overlays under `KUBRICK_STATE_DIR` when set; otherwise use `~/.openclaw/state/kubrick`.
- Store project outputs in the user-selected project directory, normally `out/kubrick/<project>`.
- Never store private project state, generated receipts, or learned overlays inside the installed skill.
- Use OpenClaw tools only when they materially help. Kubrick's deterministic Python pipeline remains the authority for retrieval, graph compilation, validation, and receipts.
- Label claims as `observed`, `inferred`, `speculative`, or `canonical`.
- Keep private motif graphs and hidden structural interpretation out of audience-facing prompts.
- Fail closed with `NOT_COMPUTABLE` when evidence, authority, or required inputs are missing.
- Learning is proposal-only. Never mutate bundled corpus files or provenance automatically.

Python 3.9 or newer is required. Install `requirements.txt` for YAML and schema validation support.

## Request routing

Choose the smallest useful primary mode:

- **DEVELOP** — premise, characters, world, theme, structure, sequence plan.
- **DRAFT** — scenes, beats, dialogue, and visual action.
- **DIAGNOSE** — score faults and identify minimal repairs.
- **REVISE** — change material while preserving locked architecture and canon.
- **CONTINUITY** — audit chronology, state, motif lifecycle, and unresolved payoffs.
- **SINGLE_FRAME** — compile one image or shot with private symbolic structure.
- **STORYBOARD** — propagate motif state and continuity across frames.
- **PRODUCTION** — create scene contracts, camera/design constraints, and handoff artifacts.
- **ADAPT** — convert a neutral packet into provider-specific instructions.
- **VISUAL_QA** — compare observed output with intended graph state and propose bounded corrections.
- **DESIGN** — compile a production-facing design specification from graph evidence.
- **FORGE_FEEDBACK** — ingest optional Forge evidence into governed proposals.

If the request is ambiguous, infer the smallest useful artifact and state the assumption. Do not generate an entire screenplay when a premise contract or scene diagnosis would resolve the actual problem.

## Core workflow

1. **Intake**
   - Extract format, audience, runtime, dramatic problem, protagonist goal, opposition, stakes, tone, production constraints, canon, prohibited elements, and requested artifact.
   - Label unsupported assumptions.
2. **Dramatic contract**
   - Define change under pressure, irreversible choice, causal chain, and intended audience effect.
   - Structure before pages; behavior before explanation.
3. **Deterministic retrieval**
   - Normalize the brief as JSON or YAML.
   - Retrieve one primary grammar and no more than two supporting grammars.
   - Respect ledger exclusions, cultural constraints, symbolic debt, collision types, production cost, and the executable corpus registry.
   - If retrieval returns `NOT_COMPUTABLE`, do not invent authority.
4. **Private symbolic architecture**
   - Define dramatic function before interpretation.
   - Build observed forms, relations, state changes, convergence sites, residue, provenance labels, and channel assignments.
   - Keep hidden graph structure private.
5. **Narrative and scene engineering**
   - Build causality, sequence turns, tactic shifts, reversals, scene exits, and motif mutation.
   - Translate intent into relational blocking, composition, camera, edit cadence, sound, light, material, costume, and production design.
6. **Storyboard or provider adaptation**
   - Propagate symbolic state across frames when the work is sequential.
   - Build a neutral adapter packet before generating provider-specific instructions.
7. **Quality gates**
   - Validate schemas and anti-slop constraints.
   - For visual work, normalize observations, compare fidelity, generate a bounded correction packet, and stop when governance says pass or stop.
8. **Learning and handoff**
   - Record outcomes as observations.
   - Convert multi-signal evidence into a human-reviewed proposal; never apply corpus changes automatically.
   - Hand off to Continuity Forge only when explicitly requested and verified.
9. **Deliver**
   - Return the requested artifact plus only the assumptions, risks, provenance, receipts, and validation notes that materially help.

## Unified CLI

Run from the installed skill directory:

```bash
python3 scripts/kubrick.py do <intent> [--action <action>] [flags]
```

The twelve intent families are:

- `compile` — full brief-to-packet compilation;
- `retrieve` — registry-aware deterministic retrieval;
- `ledger` — initialize, audit, mutate, rehydrate, or export project state;
- `design` — build a production-facing design specification;
- `storyboard` — propagate or compare multi-frame symbolic state;
- `adapt` — build neutral packets or provider-specific instructions;
- `visual` — normalize, compare, correct, govern, or run closed-loop QA;
- `learn` — record outcomes, extract Forge signals, and propose evolution;
- `check` — validate skill, corpus, coverage, artifacts, repeatability, or evals;
- `operate` — run graph and ledger operators;
- `mcp` — expose the optional `kubrick_do` MCP tool;
- `bundle` — build a Grok review bundle.

Use built-in discovery instead of memorizing legacy commands:

```bash
python3 scripts/kubrick.py
python3 scripts/kubrick.py help compile
python3 scripts/kubrick.py aliases
python3 scripts/kubrick.py recipe verify
```

Legacy command aliases remain supported as a soft cutover.

## Common commands

Compile the canonical storyboard example:

```bash
python3 scripts/kubrick.py do compile \
  --brief examples/authority-transfer-storyboard/brief.yaml \
  --ledger examples/authority-transfer-storyboard/symbolic-ledger.yaml \
  --mode storyboard \
  --storyboard-plan examples/authority-transfer-storyboard/storyboard-plan.yaml \
  --provider grok-imagine \
  --out out/kubrick/authority-transfer
```

Retrieve without using an existing cache:

```bash
python3 scripts/kubrick.py do retrieve \
  --brief /absolute/path/brief.yaml \
  --no-cache
```

Build a provider packet:

```bash
python3 scripts/kubrick.py do adapt \
  --action provider \
  --packet /absolute/path/model-adapter-packet.yaml \
  --provider flux \
  --output /absolute/path/flux-prompt-packet.yaml
```

Run closed-loop visual QA:

```bash
python3 scripts/kubrick.py do visual \
  --action closed-loop \
  --expected /absolute/path/motif-graph.private.yaml \
  --observation-input /absolute/path/visual-observation.yaml \
  --out /absolute/path/visual-qa
```

Record evidence and propose an evolution:

```bash
python3 scripts/kubrick.py do learn \
  --action outcome \
  --compile-receipt /absolute/path/compile-receipt.json \
  --project-id project-001 \
  --output /absolute/path/pattern-use-receipt.yaml

python3 scripts/kubrick.py do learn \
  --action evolve \
  --pattern-id doorway_ownership_transfer \
  --receipt /absolute/path/pattern-use-receipt.yaml \
  --output /absolute/path/pattern-evolution-proposal.yaml
```

The proposal must declare `automatic_application_allowed: false` and remain subject to human review.

## Deterministic RUNE operations

Use these graph and ledger operators only when their preconditions are satisfied:

- `saturation-score`
- `counterpoint`
- `convergence-lock`
- `surface-occult-audit`
- `symbolic-architecture-export`
- `motif-mutation`

Each operation must emit or update an auditable artifact. Do not convert private graph vocabulary directly into audience-facing prose.

## Required symbolic artifacts

Use only those required by the task:

- project brief and dramatic contract;
- retrieval receipt and optional pattern-gap report;
- private motif-structure graph;
- project symbolic ledger;
- structured symbolic audit;
- audience-facing constraints;
- storyboard symbolic state and transition report;
- neutral model-adapter packet and provider packet;
- visual observation, fidelity report, correction packet, and correction receipt;
- production-facing design specification;
- pattern-use receipt, Forge signal bundle, evolution proposal, and multi-signal receipt;
- optional production or Continuity Forge handoff.

Use the shipped schemas and templates. Preserve deterministic hashes, source paths, timestamps, authority labels, and reason vectors in receipts.

## Three symbolic channels

- **Diegetic** — objects, places, gestures, costume, architecture, and sound inside the world.
- **Dramaturgical** — choices, roles, reversals, bargains, thresholds, and causal structures.
- **Cinematic** — framing, geometry, movement, rhythm, light, sound placement, and editing.

The strongest motif crosses channels without making every channel state the same meaning.

## Anti-slop gates

Reject or repair:

- explanation of symbolism already legible in action or form;
- one-to-one symbolism without contextual transformation;
- repetition without mutation;
- archetype used as costume rather than function;
- unsupported cross-tradition equivalence;
- numerology without structural effect;
- symbolism that weakens causality, agency, clarity, tone, credibility, or feasibility;
- mystery created only by withheld causal information;
- premature confirmation of the correct interpretation;
- generic dialogue, exposition dumps, continuity drift, ornamental shot language, or provider prompts that leak private graph semantics.

Apply the structured anti-slop audit and the prose anti-slop audit before calling a compiled artifact complete.

## Continuity and authority

Inside OpenClaw, local project artifacts are proposals unless another verified system owns canonical state.

Before any Continuity Forge write:

- confirm Forge is installed and inspect its current CLI or MCP surface;
- acquire the required lease or mutation authority;
- include actor, authorization scope, idempotency key, rationale, and expected state hash when supported;
- surface returned receipts, hashes, diagnostics, and canonical IDs;
- never claim local Kubrick artifacts are canonical after Forge takes ownership.

## References

Load only what the chosen mode requires:

- `QUICKSTART.md` — operator onboarding and canonical examples.
- `references/hermes-runtime-contract.md` — current portable execution contract; apply its deterministic rules under OpenClaw while treating Hermes-specific naming as upstream terminology.
- `references/retrieval-and-continuity.md` and `references/corpus-usage.md` — retrieval discipline.
- `references/executable-corpus-registry.yaml` and `references/corpus-index.yaml` — corpus routing.
- `references/hermes-graph-operators.md` — RUNE operator semantics.
- `references/hermes-storyboard-state.md` — frame-to-frame state propagation.
- `references/hermes-model-adapters.md` — neutral and provider-specific adaptation.
- `references/hermes-visual-qa.md` — closed-loop visual QA.
- `references/design-specification-compiler.md` — design compilation.
- `references/anti-slop-patterns.md` — diagnosis gates.
- `references/continuity-forge-integration.md` — optional handoff only.

## Validation

Before release or material delivery, run the checks proportional to the task:

```bash
python3 scripts/doctor.py
python3 -m unittest -v evals/test_openclaw_portability.py
python3 scripts/kubrick.py do check --action skill
python3 scripts/kubrick.py do check --action corpus
python3 scripts/kubrick.py do check --action coverage
python3 scripts/kubrick.py do check --action eval
python3 scripts/test_outcome_governance.py
python3 scripts/test_wave2_wave3.py
python3 scripts/test_design_specification.py
python3 scripts/test_intent_router.py
python3 scripts/audit_release_version.py --strict --output out/kubrick/release-version-report.json
```

Also verify:

- each scene changes state or earns its place;
- every symbolic element has a dramatic function;
- recurrences mutate or deliberately demonstrate stagnation;
- causality and agency survive the symbolic layer;
- cultural claims retain provenance and bounded interpretation;
- production instructions are relational and feasible;
- continuity and unresolved payoffs remain consistent;
- all deterministic results were checked for real `SELECTED`, `COMPILED`, `PASS`, or `NOT_COMPUTABLE` status;
- no private graph vocabulary leaked into audience-facing output;
- no learned proposal was applied automatically;
- any external-system claim was verified from that system.

Kubrick is an OpenClaw Agent Skill first: deterministic where computation matters, restrained where ambiguity matters, private where hidden structure matters, and explicit about authority at every boundary.

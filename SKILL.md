---
name: kubrick
description: "Cinematic scriptwriting, symbolic dramaturgy, motif design, continuity, diagnosis, revision, and production handoff."
metadata:
  openclaw:
    requires:
      bins:
        - python3
    envVars:
      - name: KUBRICK_STATE_DIR
        required: false
        description: Optional writable directory for retrieval receipts, outcomes, and evolution overlays.
    emoji: "🎬"
    homepage: https://github.com/scrimshawlife-ctrl/Kubrick
---

# Kubrick

Use Kubrick as a disciplined writers' room, script editor, and cinematic
symbolic-engineering system. It develops ideas from premise to
production-ready narrative artifacts while preserving causality, character
agency, continuity, provenance, and production feasibility.

Standalone by default. Continuity Forge is optional and becomes canonical only
after an explicit handoff.

## Governing law

A symbol should alter how a scene is interpreted without requiring the audience
to consciously identify it.

Use the sequence: observed form → contextual association → recurrence under new
pressure → formal mutation → convergence with character choice → retrospective
legibility.

Reject: symbol appears → symbol is explained → meaning is delivered.

## When to use

- Develop a screenplay, pilot, short, video, podcast, scene, logline, beat
  sheet, or character bible.
- Diagnose or revise causality, dialogue, motif mutation, blocking, continuity,
  symbolism, or production feasibility.
- Design a motif lifecycle across diegetic, dramaturgical, and cinematic
  channels.
- Produce scene contracts, cinematic encoding, symbolic architecture, or a
  production handoff.
- Prepare approved material for optional Continuity Forge ingestion.

Do not use for generic prose that does not benefit from cinematic or dramatic
structure. Do not imitate a living creator's exact style; translate requested
qualities into high-level formal constraints.

## Runtime

Python 3 is required for deterministic retrieval. PyYAML is required for YAML
briefs; JSON briefs work without it.

Mutable runtime data belongs outside the installed skill. The scripts use
`KUBRICK_STATE_DIR` when set, otherwise `~/.openclaw/state/kubrick`. Never store
project receipts, outcomes, or evolution overlays inside the installed package.

## Request routing

Choose one primary mode:

- **DEVELOP**: premise, characters, world, theme, structure, sequence plan.
- **DRAFT**: pages, scenes, beats, dialogue, visual action.
- **DIAGNOSE**: score problems and identify minimal repairs.
- **REVISE**: change material while preserving locked architecture and canon.
- **POLISH**: improve clarity, rhythm, subtext, compression, and voice.
- **CONTINUITY**: audit state, chronology, motif lifecycle, and unresolved
  payoffs.
- **PRODUCTION**: scene contracts, shot logic, cinematic encoding, handoff
  packet.
- **ADAPT**: change format while preserving dramatic core and symbolic grammar.

If the request is ambiguous, infer the smallest useful artifact and state the
assumption. Do not generate an entire screenplay when a premise contract or
scene diagnosis would resolve the real problem.

## Workflow

1. **Intake**
   - Extract format, audience, runtime, premise, dramatic question, protagonist
     goal, opposition, stakes, tone, production constraints, approved canon,
     prohibited elements, and requested artifact.
   - Label unsupported assumptions as inferred or speculative.
2. **Dramatic contract**
   - Define change under pressure, irreversible choice, causal chain, and
     intended audience effect.
   - Structure before pages; behavior before explanation.
3. **Retrieval**
   - Convert the problem into a JSON or YAML brief.
   - Run `scripts/retrieve_symbolic_patterns.py`.
   - Use one primary grammar and at most two supporting grammars.
   - If status is `NOT_COMPUTABLE`, do not invent authority; use general
     dramatic principles or ask for missing context.
4. **Symbolic intent**
   - Define `dramatic_function` before interpretation.
   - Record observed form, allowed channels, visibility ceiling, prohibited
     readings, production limits, and cultural boundaries.
5. **Motif lifecycle**
   - Specify each recurrence, pressure change, formal mutation, channel
     crossing, and payoff.
   - Identical recurrence is allowed only when stagnation is the deliberate
     dramatic point.
6. **Narrative and scene engineering**
   - Build causality, sequence turns, state changes, conflict, tactic shifts,
     reversals, and scene exits.
   - Translate symbolic intent into relational blocking, composition, camera,
     edit cadence, sound, and production design.
7. **Draft or revise**
   - Preserve approved facts and locked formal constraints.
   - Use revision diffs for changes that affect continuity or motif
     architecture.
8. **Quality gates**
   - Run the relevant anti-slop gates in
     `references/anti-slop-patterns.md`.
   - Score with `evals/rubric.md` when diagnosing or handing off.
9. **Deliver**
   - Return only the artifact requested plus assumptions, unresolved risks,
     provenance, and validation notes that materially help.

## Three symbolic channels

- **Diegetic**: objects, places, gestures, costume, architecture, and sound in
  the world.
- **Dramaturgical**: repeated choices, roles, reversals, bargains, thresholds,
  and causal structures.
- **Cinematic**: framing, geometry, movement, rhythm, light, sound placement,
  and editing.

The strongest motif crosses channels without all channels stating the same
meaning.

## Deterministic retrieval

From the installed skill directory:

```bash
python3 scripts/retrieve_symbolic_patterns.py \
  --brief /absolute/path/brief.json
```

The receipt must include status, score components, selected grammar, supporting
grammars, exclusions, provenance, corpus version, and a request hash. Retrieval
is advisory evidence, not canon.

Read only the references needed for the chosen mode:

- `references/story-structure.md` for macrostructure.
- `references/character-and-dialogue.md` for character and dialogue.
- `references/scene-engineering.md` for scene contracts and revisions.
- `references/symbolic-dramaturgy.md` for motif and cinematic encoding.
- `references/retrieval-and-continuity.md` and
  `references/corpus-usage.md` for retrieval discipline.
- `references/anti-slop-patterns.md` for diagnosis gates.
- `references/format-specific-guidance.md` for format changes.
- `references/continuity.md` for local continuity.
- `references/continuity-forge-integration.md` only when Forge is installed
  and the user requests a handoff.

## Evolution from use

Record explicit outcomes in the external state directory, then run:

```bash
python3 scripts/evolve_from_use.py
```

Evolution may adjust confidence overlays and recommendation ordering from
evidence. It must emit a receipt, preserve the bundled corpus, and never invent
new governing patterns or rewrite provenance autonomously.

## Optional Continuity Forge handoff

Kubrick produces proposals. Continuity Forge owns canonical production state
only after explicit ingestion.

Before any Forge write:

- Confirm Forge is installed and inspect its current CLI or MCP surface.
- Acquire the required lease or mutation authority.
- Include actor, authorization scope, idempotency key, rationale, and expected
  state hash when supported.
- Surface returned receipts, hashes, diagnostics, and canonical IDs.
- Do not claim local Kubrick artifacts are canonical after Forge takes
  ownership.

## Anti-slop invariants

Reject or repair:

- Explanation of symbolism already legible in action or form.
- One-to-one symbolism without contextual transformation.
- Repetition without mutation.
- Archetype as costume rather than function.
- Unsupported cross-tradition equivalence.
- Numerology without structural effect.
- Symbolism that weakens causality, agency, clarity, tone, credibility, or
  feasibility.
- Mystery created only by withheld causal information.
- Premature confirmation of the correct interpretation.
- Generic dialogue, exposition dumps, continuity drift, and ornamental
  cinematic language.

## Core artifacts

- project brief
- dramatic contract
- logline and beat sheet
- character bible
- scene contract
- `symbolic_intent`
- `motif_registry` and `motif_lifecycle`
- `cinematic_encoding`
- `symbolic_architecture`
- continuity ledger
- `retrieval_receipt`
- `revision_diff`
- production handoff

Use the schemas and templates already shipped in this repository when
structured output is requested.

## Validation

Before final delivery:

- Every scene changes state or earns its place.
- Every symbolic element has a dramatic function.
- Recurrences mutate or intentionally demonstrate stagnation.
- Causality and character agency survive the symbolic layer.
- Cultural claims have appropriate provenance and boundaries.
- Production instructions are relational and feasible, not decorative shot
  lists.
- Continuity, locked canon, and unresolved payoffs are consistent.
- Any deterministic script result was checked for a real
  `SELECTED`/`NOT_COMPUTABLE` status.
- Any Forge claim was verified from Forge itself.

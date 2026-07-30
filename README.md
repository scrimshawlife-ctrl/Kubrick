<p align="center">
  <img src="assets/hero.jpg" alt="Kubrick — Symbolic Cinematic Narrative Engineering" width="100%">
</p>

<h1 align="center">Kubrick</h1>

<p align="center">
  <strong>Hermes-Native Symbolic Cinematic Engineering</strong><br>
  <em>0.13.0 — Forge Feedback • Multi-Provider Adapters • Operator Surface</em>
</p>

<p align="center">
  <a href="https://github.com/scrimshawlife-ctrl/Kubrick/releases"><img src="https://img.shields.io/github/v/release/scrimshawlife-ctrl/Kubrick?color=5a6a8a&style=flat-square" alt="Latest Release"></a>
  <a href="https://github.com/scrimshawlife-ctrl/Kubrick"><img src="https://img.shields.io/github/stars/scrimshawlife-ctrl/Kubrick?style=flat-square" alt="GitHub Stars"></a>
  <a href="https://github.com/scrimshawlife-ctrl/Kubrick/issues"><img src="https://img.shields.io/github/issues/scrimshawlife-ctrl/Kubrick?style=flat-square" alt="Issues"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-1a1f2e?style=flat-square" alt="License"></a>
  <a href="#installation"><img src="https://img.shields.io/badge/Hermes-Standalone_Skill-8b5cf6?style=flat-square" alt="Hermes Standalone Skill"></a>
</p>

<p align="center">
  <strong>Observed form first. Dramatic function first. Hidden architecture made executable.</strong>
</p>

---

**Kubrick** is a self-contained Hermes skill for screenplay development, scene diagnosis, motif engineering, cinematic encoding, storyboard continuity, generative prompt construction, closed-loop visual QA, multi-signal outcome learning, and governed design-specification compilation.

It converts dramatic pressure into observable geometry, behavior, rhythm, material state, light, sound, convergence, and residue. Esoteric and archetypal source systems remain latent by default: audience-facing packets expose enforceable cinematic constraints rather than named occult concepts.

## 0.13.0 Highlights

Wave 2 and Wave 3 of the production-hardening roadmap are **shipped on `main`** ([#3](https://github.com/scrimshawlife-ctrl/Kubrick/issues/3), [#4](https://github.com/scrimshawlife-ctrl/Kubrick/issues/4), [PR #24](https://github.com/scrimshawlife-ctrl/Kubrick/pull/24)).

| Area | What landed |
|---|---|
| **Forge multi-signal feedback** | Ledger diffs, revisions, saturation, collisions, ingestion, and payoff outcomes → deterministic observation bundles |
| **Multi-signal evolution** | Confidence, mutation success, feasibility, anti-slop, cultural boundaries, payoff → proposal-only evolution with human review gates |
| **First-class project ledgers** | Persistent motif state, pattern history, rehydrate/apply-forge, retrieval snapshots; Forge remains canonical |
| **Multi-provider adapters** | Grok Imagine, Flux, SD3, Midjourney share one latent graph; adapters change **syntax only** |
| **Closed-loop visual QA** | Observe → normalize → differential score → correct; geometry / state / residue / convergence reported separately |
| **CLI + optional MCP operators** | Saturation, counterpoint, convergence lock, surface-occult audit, motif mutation, symbolic-architecture export |
| **Cultural-signal packs** | Time-sensitive contemporary memetic patterns with provenance and validity windows |
| **Design specification compiler** | Heterogeneous evidence → schema-valid `design.md` candidate without silent authority promotion |
| **Fail-closed governance** | Weak evidence → `NOT_COMPUTABLE`; no structural change applies automatically |

## Core Philosophy

- **Observed first, meaning second** — every motif begins as concrete form, behavior, relation, or material state.
- **Dramatic function before symbolism** — symbolic design must change pressure, agency, causality, or interpretation.
- **Mandatory mutation** — recurrence changes scale, ownership, orientation, material, rhythm, framing, context, or consequence.
- **Three-channel symbolism** — diegetic, dramaturgical, and cinematic channels cross without explanatory dialogue.
- **Constraint over citation** — source traditions become geometry, rhythm, threshold, role persistence, transformation, and residue.
- **Fail closed** — weak evidence or unresolved boundaries return `NOT_COMPUTABLE`.
- **Human-governed evolution** — local outputs remain observations or proposals until explicitly approved.
- **Forge-canonical when connected** — Continuity Forge owns committed project state; Kubrick never auto-promotes authority.

## Installation

```bash
git clone https://github.com/scrimshawlife-ctrl/Kubrick.git
cd Kubrick
./install.sh
```

Default destination:

```text
~/.hermes/skills/kubrick
```

Install repository validation dependencies when developing locally:

```bash
python -m pip install pyyaml jsonschema
```

Validate the installed skill:

```bash
python ~/.hermes/skills/kubrick/scripts/kubrick.py validate-skill
```

Continuity Forge, MCP servers, generation APIs, and vision APIs remain optional.

## Unified Pipeline

```bash
python scripts/kubrick.py compile \
  --brief examples/authority-transfer-storyboard/brief.yaml \
  --ledger examples/authority-transfer-storyboard/symbolic-ledger.yaml \
  --mode storyboard \
  --storyboard-plan examples/authority-transfer-storyboard/storyboard-plan.yaml \
  --provider grok-imagine \
  --out out/kubrick/authority-transfer
```

Providers: `none` · `generic` · `grok-imagine` · `flux` · `sd3` · `midjourney`

```text
brief
→ registry-aware retrieval
→ private motif graph
→ structural and anti-slop audit
→ audience constraints
→ storyboard state propagation
→ transition comparison
→ neutral model-adapter packet
→ provider prompt packet (syntax-only)
→ schema receipts
→ compile receipt
```

## Operator Commands

```text
validate-skill          validate Hermes skill structure
validate-corpus         validate executable pattern sidecars
coverage                audit corpus and registry coverage
compile                 run the unified symbolic compiler
retrieve                registry-aware deterministic retrieval
ledger                  init / audit / mutate / rehydrate / apply-forge
design-build            compile a governed design specification
storyboard-propagate    propagate graph state across frames
storyboard-compare      inspect frame-to-frame continuity
adapter-build           build a provider-neutral adapter packet
adapt-grok              emit Grok Imagine prompt packets
adapt-flux              emit Flux prompt packets
adapt-sd3               emit SD3 prompt packets
adapt-midjourney        emit Midjourney prompt packets
adapt-provider          syntax-only translation for any supported provider
visual-normalize        normalize human or optional vision observations
visual-compare          compare expected and observed frame state
visual-correct          build targeted regeneration instructions
correction-govern       stop, continue, or escalate correction iterations
closed-loop-qa          observe → score → correct with differential fidelity
outcome-record          record production-use evidence (OBSERVATION)
evolution-propose       multi-signal proposal-only corpus evolution
forge-signals           extract multi-signal Forge observations
operator                saturation, counterpoint, lock, audit, export, mutate
mcp-server              optional stdio MCP wrapper (never authoritative)
grok-review-bundle      package the complete Grok review workflow
artifact-validate       validate YAML or JSON against a repository schema
repeatability           compare stable hashes across two clean compiles
eval                    run the standalone Hermes regression suite
```

## Common Workflows

### Multi-provider adaptation

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
```

Adapters preserve `source_graph_id` and never rewrite canonical symbolic intent.

### Forge feedback → evolution proposal

```bash
python scripts/kubrick.py forge-signals \
  --project-id myfilm \
  --input references/examples/forge-signals/ledger-before-after.yaml \
  --output out/forge-bundle.yaml

python scripts/kubrick.py ledger apply-forge \
  --ledger project/symbolic-ledger.yaml \
  --forge-bundle out/forge-bundle.yaml

python scripts/kubrick.py evolution-propose \
  --pattern-id interface_badge_authority_transfer \
  --forge-bundle out/forge-bundle.yaml \
  --output out/evolution-proposal.yaml
```

Every evolution event emits a multi-signal receipt. Structural changes and large confidence deltas require human review. Nothing applies automatically.

### Closed-loop visual QA

```bash
python scripts/kubrick.py closed-loop-qa \
  --expected out/storyboard-symbolic-state.yaml \
  --observation-input observations/frame-001.json \
  --source-graph-id <graph-id> \
  --frame-id frame-001 \
  --out out/qa/frame-001
```

### Operators and optional MCP

```bash
python scripts/kubrick.py operator saturation-score --ledger project/symbolic-ledger.yaml
python scripts/kubrick.py operator surface-occult-audit --input out/audience-constraints.yaml
python scripts/kubrick.py operator symbolic-architecture-export \
  --graph out/motif-graph.private.yaml \
  --ledger project/symbolic-ledger.yaml \
  --output out/symbolic-architecture-export.yaml

# Optional — tools wrap the same CLI; fail closed on weak evidence
python scripts/kubrick.py mcp-server
```

### Design specification

```bash
python scripts/kubrick.py design-build --help
```

See `references/design-specification-compiler.md` and `templates/design-specification.yaml`.

## Verification

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

CI (`.github/workflows/hermes-evals.yml`) runs Hermes evals, outcome governance, Wave 2/3 smoke tests, multi-provider storyboard compiles, repeatability, and strict release-version audit.

## Documentation

| File | Purpose |
|---|---|
| [`SKILL.md`](SKILL.md) | Canonical Hermes operating contract |
| [`QUICKSTART.md`](QUICKSTART.md) | Installation and command routing |
| [`CHANGELOG.md`](CHANGELOG.md) | Release history |
| [`docs/ROADMAP-v0.13.md`](docs/ROADMAP-v0.13.md) | Current roadmap and next priorities |
| [`docs/RELEASE-NOTES-v0.13.md`](docs/RELEASE-NOTES-v0.13.md) | v0.13 release notes |
| [`docs/RELEASE-CHECKLIST-v0.13.md`](docs/RELEASE-CHECKLIST-v0.13.md) | Release gates and procedure |
| [`docs/README.md`](docs/README.md) | Docs index |
| [`references/hermes-runtime-contract.md`](references/hermes-runtime-contract.md) | Runtime, dependency, artifact, and canon policy |
| [`references/hermes-model-adapters.md`](references/hermes-model-adapters.md) | Provider adapter contract |
| [`references/hermes-visual-qa.md`](references/hermes-visual-qa.md) | Visual QA contract |
| [`references/continuity-forge-integration.md`](references/continuity-forge-integration.md) | Forge handoff and feedback |
| [`references/design-specification-compiler.md`](references/design-specification-compiler.md) | Design-spec compiler |
| [`references/patterns/`](references/patterns/) | Executable pattern sidecars |
| [`schemas/`](schemas/) | Machine-readable artifact contracts |
| [`evals/`](evals/) | Regression and adversarial specifications |

## Architecture (v0.13)

```text
                    ┌─────────────────────┐
                    │  Project brief +    │
                    │  symbolic ledger    │
                    └──────────┬──────────┘
                               │
              retrieve → graph → audit → audience
                               │
                    storyboard propagate / compare
                               │
              neutral adapter packet (shared latent graph)
                               │
            ┌──────────────────┼──────────────────┐
            ▼                  ▼                  ▼
      grok-imagine           flux / sd3        midjourney
      (syntax only)        (syntax only)     (syntax only)
                               │
                    closed-loop visual QA
                    (geometry · state · residue · convergence)
                               │
              outcome receipt → multi-signal evolution proposal
                               │
                    human review gate (never auto-apply)
                               │
              optional Forge signals ←── Continuity Forge (canonical)
```

## Version

**0.13.0 — Forge Feedback, Multi-Provider Adapters, and Operator Surface**

Shipped on `main` via [PR #24](https://github.com/scrimshawlife-ctrl/Kubrick/pull/24). Issues [#3](https://github.com/scrimshawlife-ctrl/Kubrick/issues/3) and [#4](https://github.com/scrimshawlife-ctrl/Kubrick/issues/4) are closed.

See [CHANGELOG.md](CHANGELOG.md) for full release history.

---

<p align="center">
  <em>Symbolism should alter the conditions under which a scene is interpreted—without requiring the audience to consciously identify it.</em>
</p>

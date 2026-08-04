# OpenClaw alignment checklist (v0.16)

Track issue: https://github.com/scrimshawlife-ctrl/Kubrick/issues/32

Bring the permanent `openclaw` branch to Hermes `main` / v0.16 contracts without
erasing OpenClaw packaging, external state (`KUBRICK_STATE_DIR`), doctor, or overlays.

Local parity branch: `cursor/openclaw-v016-parity-44a4`

## Port these from Hermes main (v0.16)

1. `kubrick.manifest.yaml` intents (15) + recipes + schema registry (`host: openclaw`)
2. `scripts/intent_router.py` + `scripts/kubrick.py` surface sugar (`qa`, `validate`, `receipts`)
3. `scripts/io_safety.py`, MCP allowlist, diagnostics, receipt identities
4. Canonical engine: `scripts/production_engine.py`
5. Domain compilers + surfaces (`surface_compilers.py`, `*_surface.py`, `production_surface.py`)
6. Provider capabilities, cinematic project state helper, golden fixtures
7. Atomic installer invariants (validate → swap → receipt → rollback)
8. Hub packaging story (or OpenClaw-equivalent export without nested drift)

## Keep OpenClaw-specific

- Install under `~/.openclaw/skills/kubrick`
- Mutable state outside the skill package (`kubrick_paths` / `KUBRICK_STATE_DIR`)
- Native `scripts/retrieve_symbolic_patterns.py` (prohibited-pattern doctor checks)
- `doctor` / portability tests
- Agent Skill packaging frontmatter required by OpenClaw
- `.clawhubignore` / ClawHub packaging

## Acceptance

- `do check --action smoke` passes on OpenClaw edition
- `python scripts/doctor.py` — prohibited patterns excluded
- `python scripts/test_v016_phased_acceptance.py` PASS
- `python scripts/test_golden_v016.py` PASS
- `pytest evals/test_openclaw_portability.py` PASS
- No silent authority promotion; `NOT_COMPUTABLE` preserved
- Retrieve/state paths remain outside the skill package

# OpenClaw alignment checklist (v0.15)

Track issue: https://github.com/scrimshawlife-ctrl/Kubrick/issues/32

Bring the permanent `openclaw` branch to Hermes `main` contracts without erasing
OpenClaw packaging, external state (`KUBRICK_STATE_DIR`), doctor, or overlays.

## Port these from Hermes main

1. `kubrick.manifest.yaml` intents (15) + recipes + schema registry
2. `scripts/intent_router.py` + `scripts/kubrick.py` action forwarding for surfaces
3. `scripts/io_safety.py`, MCP allowlist, diagnostics, receipt identities
4. Production surface scripts (`production_surface.py`, `*_surface.py`)
5. Atomic installer invariants (validate → swap → receipt → rollback)
6. Hub packaging story (or OpenClaw-equivalent export without nested drift)

## Keep OpenClaw-specific

- Install under `~/.openclaw/skills/kubrick`
- Mutable state outside the skill package
- `doctor` / portability tests
- Agent Skill packaging frontmatter required by OpenClaw

## Acceptance

- `do check --action smoke` passes on OpenClaw edition
- `kubrick_do` MCP policy matches main
- Storyboard example recipe compiles
- No silent authority promotion; `NOT_COMPUTABLE` preserved

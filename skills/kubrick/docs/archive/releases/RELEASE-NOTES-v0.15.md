# Kubrick v0.15.0 Release Notes

v0.15.0 promotes first-class `design` / `script` / `image` / `video` production
surfaces (foundation runtime) and hardens the Hermes operator boundary.

## Highlights

- Peer production-surface intents with fail-closed evidence gates
- MCP and filesystem path policy (`io_safety`)
- Complete schema registry; hub sync gate
- Provenance/collision taxonomy shared across retrieval and surfaces
- Windows `install.ps1`; `SECURITY.md`
- Task aliases `create`, `revise`, `inspect`, `validate`

## Upgrade notes

- Set `KUBRICK_PROJECT_DIR` in agent/CI environments that write outside cwd.
- Re-run `bash scripts/sync_hub_skill.sh` after local edits before committing.
- OpenClaw edition still tracks separately; see `docs/OPENCLAW-ALIGNMENT.md`.

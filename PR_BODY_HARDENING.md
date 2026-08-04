## Summary

Ships **Kubrick v0.15.0** on Hermes `main`:

1. **Hardening** — MCP allowlist, path/intake policy (`io_safety`), complete schema registry, hub sync gate, SECURITY.md, `install.ps1`, provenance taxonomy, typed models, adversarial evals, pinned CI.
2. **First-class production surfaces** — domain compilers for `design` / `script` / `image` / `video` (`surface_compilers.py`), schemas, and `examples/production-surfaces/`.
3. Companion OpenClaw branch: `cursor/openclaw-v015-parity-44a4` (base `openclaw`) ports the same contracts while preserving OpenClaw install/state/doctor.

Tracks #33 / #32.

## Test plan

- [x] `python scripts/kubrick.py do check --action smoke`
- [x] `python scripts/check_hub_sync.py`
- [x] `python scripts/test_io_safety.py`
- [x] `python scripts/test_surface_compilers.py`
- [x] `python scripts/test_intent_router.py`
- [x] `python scripts/audit_release_version.py --strict`
- [x] design/video example path from `examples/production-surfaces/README.md`

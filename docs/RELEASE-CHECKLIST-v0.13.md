# Kubrick v0.13 Release Checklist

## Required gates

- [ ] `python scripts/kubrick.py validate-skill`
- [ ] `python scripts/kubrick.py validate-corpus`
- [ ] `python scripts/kubrick.py coverage`
- [ ] `python scripts/kubrick.py eval`
- [ ] `python scripts/test_outcome_governance.py`
- [ ] `python scripts/test_wave2_wave3.py`
- [ ] `python scripts/kubrick.py repeatability --output out/kubrick/repeatability-report.json`
- [ ] Canonical authority-transfer storyboard compiles with `status: COMPILED`.
- [ ] Multi-provider adapters (flux/sd3/midjourney) preserve `source_graph_id`.
- [ ] Multi-signal evolution receipts validate and never set `automatic_application_allowed: true`.
- [ ] Forge signal bundles remain `OBSERVATION` with `forge_canonical: true`.
- [ ] Closed-loop QA reports geometry/state/residue/convergence separately.
- [ ] Surface-occult audit fails closed on named esoterica.
- [ ] No audience-facing packet exposes private pattern or lexicon links.
- [ ] README and QUICKSTART commands execute in CI.

## Release procedure

1. Confirm the default branch is green.
2. Review `CHANGELOG.md` and version declarations.
3. Confirm no generated output or usage receipt is unintentionally committed.
4. Create the `v0.13.0` tag from the verified main commit.
5. Publish release notes from the `0.13.0` changelog section.
6. Reinstall into a clean Hermes skill directory and run `validate-skill`.

## Non-goals

- External model APIs are not required.
- Continuity Forge and MCP remain optional.
- Evolution proposals do not modify corpus authority automatically.

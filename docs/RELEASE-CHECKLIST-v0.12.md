# Kubrick v0.12 Release Checklist

## Required gates

- [ ] `python scripts/kubrick.py validate-skill`
- [ ] `python scripts/kubrick.py validate-corpus`
- [ ] `python scripts/kubrick.py coverage`
- [ ] `python scripts/kubrick.py eval`
- [ ] `python scripts/test_outcome_governance.py`
- [ ] `python scripts/kubrick.py repeatability --output out/kubrick/repeatability-report.json`
- [ ] Canonical authority-transfer storyboard compiles with `status: COMPILED`.
- [ ] Graph, storyboard, and adapter schema receipts pass.
- [ ] Stable artifacts match across two clean runs after volatile timestamps and receipt locations are excluded.
- [ ] No audience-facing packet exposes private pattern or lexicon links.
- [ ] Outcome receipts remain `OBSERVATION` and evolution remains `PROPOSED`.
- [ ] README and QUICKSTART commands execute in CI.

## Release procedure

1. Confirm the default branch is green.
2. Review `CHANGELOG.md` and version declarations.
3. Confirm no generated output or usage receipt is unintentionally committed.
4. Create the `v0.12.0` tag from the verified main commit.
5. Publish release notes from the `0.12.0` changelog section.
6. Reinstall into a clean Hermes skill directory and run `validate-skill`.

## Non-goals

- External model APIs are not required.
- Continuity Forge and MCP remain optional.
- Evolution proposals do not modify corpus authority automatically.

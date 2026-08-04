# Push instructions (agent environment has no GitHub credentials)

## Hermes PR (`main`)

```bash
git fetch origin
git checkout cursor/hardening-upgrades-44a4   # or apply /tmp/kubrick-hermes-v015.patch
git push -u origin cursor/hardening-upgrades-44a4
gh pr create --base main --head cursor/hardening-upgrades-44a4 \
  --title "feat: v0.15 production surfaces + operator hardening" \
  --body-file PR_BODY_HARDENING.md
```

## OpenClaw PR (`openclaw`)

```bash
git checkout cursor/openclaw-v015-parity-44a4  # or apply /tmp/kubrick-openclaw-v015.patch
git push -u origin cursor/openclaw-v015-parity-44a4
gh pr create --base openclaw --head cursor/openclaw-v015-parity-44a4 \
  --title "feat(openclaw): v0.15 surfaces and operator hardening parity" \
  --body "Ports Hermes v0.15 production surfaces + hardening while preserving OpenClaw install/state/doctor. Fixes doctor prohibited-pattern exclusion. Tracks #32."
```

## Local verification

```bash
python scripts/kubrick.py do check --action smoke
python scripts/test_cross_surface.py
# OpenClaw only:
python scripts/doctor.py
```


## Current tips (local only until push)

- Hermes `cursor/hardening-upgrades-44a4`: run `git rev-parse --short HEAD` (provider capabilities + video prompt)
- OpenClaw `cursor/openclaw-v015-parity-44a4`: `0ff78b7` (provider capabilities + video prompt)

Handoff artifacts:

- `/tmp/kubrick-hermes-v015.patch` / `.bundle`
- `/tmp/kubrick-openclaw-v015.patch` / `.bundle`

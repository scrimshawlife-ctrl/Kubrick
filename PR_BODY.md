## Summary

Adds `kubrick` **v0.16.0**, an optional creative-production skill for cinematic
composition, screenplay/scene engineering, visual continuity, symbolic encoding,
storyboard state propagation, multi-provider image-prompt adaptation, first-class
`design` / `script` / `image` / `video` production surfaces, and production-design QA.

Path:

```text
optional-skills/creative/kubrick/
```

## Why it belongs in optional-skills

The workflow is broadly useful to filmmakers, designers, game narrative teams, image-generation pipelines, and generative-video systems, but it is specialized enough that it should not ship as a default bundled skill.

It complements existing creative skills (diagrams, pixel art, meme generation, creative ideation) by covering **screen/film continuity and production handoff**, not general ideation or raster meme templates.

## What the skill provides

- Deterministic operator surface: `python3 ${HERMES_SKILL_DIR}/scripts/kubrick.py do <intent> …`
- Shared production engine with validate→compile→receipt lifecycle
- Surface sugar: `kubrick design|script|image|video|qa|receipts|validate`
- Motif/structure graph, project symbolic ledger, storyboard state propagation
- Anti-slop / symbolic quality gates with fail-closed `NOT_COMPUTABLE` behavior
- Multi-provider adapters (generic, Flux, SD3, Midjourney, Grok Imagine)
- Optional Continuity Forge feedback path (never required)
- Stdlib-first helpers; optional `pyyaml` / `jsonschema` with explicit degraded paths
- Eval fixtures (`evals/golden/v016/`) and release validation scripts

## Validation

- [x] Confirmed local Hermes detection under `~/.hermes/skills/kubrick` (trust: local)
- [x] `python3 scripts/kubrick.py do check --action skill` → PASS
- [x] `python3 scripts/kubrick.py do check --action smoke` → PASS
- [x] `python3 scripts/audit_release_version.py --strict` → READY (v0.16.0)
- [x] `python3 scripts/test_v016_phased_acceptance.py` → PASS
- [x] `python3 scripts/test_golden_v016.py` → PASS
- [ ] Positive activation: cinematic visual-system / screenplay prompt loads Kubrick
- [ ] Negative activation: unrelated checksum/devops prompt does **not** load Kubrick
- [x] Script paths documented via `${HERMES_SKILL_DIR}`
- [x] No credentials, private filesystem paths, or machine-specific assumptions in skill content
- [x] MIT license present (`LICENSE` + frontmatter `license: MIT`)

## Dependencies

**None required** for prose creative work.

Optional:

| Dependency | Purpose | Failure mode |
|---|---|---|
| Python 3 | Deterministic helpers | Use prose-only path |
| `pyyaml`, `jsonschema` | Stronger schema validation | Explicit missing-package message + degraded path |
| Continuity Forge | Canonical ledger handoff | Local PROPOSED artifacts only |
| Model / vision APIs | Provider render + visual observation | Provider-neutral packets only |

## License and provenance

- **License:** MIT — Copyright (c) 2026 Daniel Meyer / Applied Alchemy Labs
- **Author frontmatter:** `Daniel Meyer / Applied Alchemy Labs`
- **Provenance:** Pattern sidecars are original operational encodings of publicly discussed cinematic grammar; not film clips or copyrighted scripts. Esoteric lexicon is latent structural vocabulary only.
- **Related edition:** OpenClaw packaging lives on branch `openclaw` (community packaging credit: Prabu / @prabu-openclaw). This PR ships the Hermes edition only.

## Install (after merge)

```bash
hermes skills install official/creative/kubrick
```

## Community fallback (already available)

```bash
hermes skills tap add scrimshawlife-ctrl/Kubrick
# or
hermes skills publish /path/to/Kubrick --to github --repo scrimshawlife-ctrl/Kubrick
```

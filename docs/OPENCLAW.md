# Kubrick on OpenClaw

This repository maintains **two runtime editions** of the same creative skill.

| Edition | Git ref | Primary install target | Status |
|---|---|---|---|
| **Hermes** (canonical upstream) | [`main`](https://github.com/scrimshawlife-ctrl/Kubrick/tree/main) | `~/.hermes/skills/kubrick` | Active development |
| **OpenClaw Agent Skill** | permanent branch [`openclaw`](https://github.com/scrimshawlife-ctrl/Kubrick/tree/openclaw) | `~/.openclaw/skills/kubrick` | v0.13.0 port maintained with work by **Prabu** ([@prabu-openclaw](https://github.com/prabu-openclaw)) |

The **symbolic corpus, laws, schemas, and narrative intent** are shared in spirit. Packaging, installer behavior, state location, and skill frontmatter differ so each runtime stays native.

## Credit and history

OpenClaw support was contributed by **Prabu** (`prabu@openclaw.ai` / [@prabu-openclaw](https://github.com/prabu-openclaw)):

| Item | Reference |
|---|---|
| Feature work | Commit [`77fa721`](https://github.com/scrimshawlife-ctrl/Kubrick/commit/77fa721b8a308fe82fb75da88dbf7556bb703aed) — *feat: add OpenClaw skill support* |
| Onboarding docs fix | Commit [`15defae`](https://github.com/scrimshawlife-ctrl/Kubrick/commit/15defaec662f886c822107bb4123078278afbc3b) — *docs: fix OpenClaw branch onboarding* |
| Pull request (closed; lives on branch) | [PR #1](https://github.com/scrimshawlife-ctrl/Kubrick/pull/1) — *feat: add OpenClaw Agent Skill support* |
| Permanent branch | [`openclaw`](https://github.com/scrimshawlife-ctrl/Kubrick/tree/openclaw) |

PR #1 was closed in favor of keeping OpenClaw packaging on the dedicated **`openclaw`** branch rather than merging into Hermes `main`. That is intentional dual-track maintenance, not a rejection of the port.

## What the OpenClaw edition changes

Relative to a Hermes-centric skill layout, Prabu’s adaptation focuses on:

1. **OpenClaw Agent Skill frontmatter and SKILL.md** — triggerable workflow for OpenClaw, still usable as a skill document.
2. **OpenClaw-first install** — `install.sh` targets `~/.openclaw/skills/kubrick`; ClawHub-oriented packaging (e.g. `.clawhubignore`).
3. **External mutable state** — receipts, outcomes, evolution overlays, and ranking data under `KUBRICK_STATE_DIR` or `~/.openclaw/state/kubrick` so skill updates do not rewrite the packaged corpus.
4. **Overlay-based evolution** — reversible, auditable learning instead of mutating bundled pattern sidecars in place.
5. **Hardened retrieval** — external caches, safer scoring, explicit exclusion receipts, and fail-closed results.
6. **Portability tooling** — `scripts/doctor.py`, `evals/test_openclaw_portability.py`, and CI on the OpenClaw branch.
7. **v0.13 operator surface** — unified intent router, storyboard compiler, multi-provider adapters, visual QA, design compiler, graph operators, optional MCP, and proposal-only multi-signal learning.

The OpenClaw edition is aligned with upstream **v0.13.0** as of this port. Future mainline work may still require deliberate follow-up ports; the branches are not silently merged.

## Install (OpenClaw)

Prefer the permanent branch:

```bash
openclaw skills install git:scrimshawlife-ctrl/Kubrick@openclaw --global
```

Or a single-branch clone:

```bash
git clone --branch openclaw --single-branch \
  https://github.com/scrimshawlife-ctrl/Kubrick.git
cd Kubrick
python3 -m pip install -r requirements.txt
./install.sh
```

Verify (on the OpenClaw edition):

```bash
python3 ~/.openclaw/skills/kubrick/scripts/doctor.py
openclaw skills list
```

## Install (Hermes — upstream `main`)

```bash
git clone --branch main --single-branch \
  https://github.com/scrimshawlife-ctrl/Kubrick.git
cd Kubrick
./install.sh   # → ~/.hermes/skills/kubrick
```

See root [`README.md`](../README.md) and [`QUICKSTART.md`](../QUICKSTART.md).

## Which edition should I use?

| If you… | Use |
|---|---|
| Run **Hermes** as the agent host | **`main`** |
| Run **OpenClaw** as the agent host | **`openclaw`** branch |
| Need the v0.13 compiler / intent-router / multi-provider pipeline on OpenClaw | **`openclaw`** |
| Need OpenClaw packaging, external state dir, doctor, ClawHub metadata | **`openclaw`** |

## For maintainers

- Do **not** assume a silent merge of `openclaw` into `main` (or the reverse). Port features deliberately.
- When adding Hermes-only tools on `main`, note in this file or the changelog if OpenClaw users need a follow-up.
- When improving OpenClaw packaging on `openclaw`, link PRs/commits here.

## Related links

- Branch tree: https://github.com/scrimshawlife-ctrl/Kubrick/tree/openclaw
- PR #1: https://github.com/scrimshawlife-ctrl/Kubrick/pull/1
- Upstream runtime contract terminology: [`../references/hermes-runtime-contract.md`](../references/hermes-runtime-contract.md)

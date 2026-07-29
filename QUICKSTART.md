# Kubrick Quickstart

Kubrick is a standalone OpenClaw Agent Skill for cinematic writing, symbolic
dramaturgy, motif engineering, diagnosis, revision, and production handoff. It
works without Continuity Forge and remains compatible with Hermes.

## 1. Install

Install the merged repository as a shared managed skill:

```bash
openclaw skills install git:scrimshawlife-ctrl/Kubrick --global
```

Or install a checkout manually:

```bash
git clone https://github.com/scrimshawlife-ctrl/Kubrick.git
cd Kubrick
python3 -m pip install -r requirements.txt
./install.sh
```

The manual installer targets `~/.openclaw/skills/kubrick`.

Hermes compatibility:

```bash
./install.sh --hermes
```

The manual installer moves an existing installation to a timestamped backup
instead of deleting it. It deliberately does not create an external symlink,
because OpenClaw skips symlinks that resolve outside an untrusted skill root.

## 2. Verify

```bash
python3 ~/.openclaw/skills/kubrick/scripts/doctor.py
openclaw skills list
```

The doctor checks Python, the corpus, schemas, deterministic retrieval, and
writable state without changing a project.

## 3. Use in OpenClaw

Try:

```text
Develop this short-film premise into a dramatic contract, motif lifecycle,
sequence outline, and three scene contracts. Keep the production to two actors
and one apartment.
```

```text
Diagnose this scene for causality, exposition, motif repetition, and geometric
drift. Quote the weak passages and propose the smallest repairs.
```

```text
Rewrite this sequence while preserving the locked broken-circle motif, but
mutate its function under the protagonist's new choice.
```

## 4. Deterministic retrieval

JSON requires only Python:

```bash
python3 scripts/retrieve_symbolic_patterns.py \
  --brief /absolute/path/brief.json \
  --format json
```

YAML briefs and output require PyYAML from `requirements.txt`:

```bash
python3 scripts/retrieve_symbolic_patterns.py \
  --brief evals/retrieval/inputs/sample_melodrama_lowbudget.yaml
```

Retrieval emits a receipt with ranked patterns, scores, exclusions, provenance,
and a `SELECTED` or `NOT_COMPUTABLE` status.

## 5. Runtime state and evolution

Live data defaults to:

```text
~/.openclaw/state/kubrick/
├── receipts/
├── outcomes/
├── patterns/
├── evolution/
└── ranking.json
```

Set `KUBRICK_STATE_DIR` to use another writable location.

After recording explicit project outcomes, run:

```bash
python3 scripts/evolve_from_use.py
```

Evolution writes reversible overlays and receipts. It never modifies the
installed corpus.

## 6. Validate a checkout

```bash
python3 -m py_compile scripts/*.py evals/test_openclaw_portability.py
python3 -m unittest -v evals/test_openclaw_portability.py
python3 scripts/doctor.py
bash -n install.sh
```

Read `SKILL.md` for the complete workflow and `README.md` for architecture,
design boundaries, and artifact definitions.

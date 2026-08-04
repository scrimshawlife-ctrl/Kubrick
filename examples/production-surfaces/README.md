# Production surfaces example

End-to-end v0.15 path: brief → design.md → script → image prompt → video shot → drift.

## Quick demo

```bash
bash examples/production-surfaces/run_demo.sh
# artifacts land in out/surfaces-demo/
```

## Workflow recipes

### 1) Existing project → improve `design.md`

```bash
python scripts/kubrick.py do design --action improve \
  --input path/to/design.md \
  --evidence examples/authority-transfer-storyboard/brief.yaml \
  --output out/surfaces/design-improved.md
```

Placeholder sections are filled from evidenced YAML. `[LOCKED]` claims are preserved.

### 2) Premise → design → screenplay → image sequence

```bash
python scripts/kubrick.py do design --action create \
  --brief examples/authority-transfer-storyboard/brief.yaml \
  --project-id authority-transfer \
  --output out/surfaces/design.md

python scripts/kubrick.py do script --action create \
  --brief examples/authority-transfer-storyboard/brief.yaml \
  --design out/surfaces/design.md \
  --format fountain \
  --output out/surfaces/script.fountain

python scripts/kubrick.py do image --action sequence \
  --brief examples/authority-transfer-storyboard/brief.yaml \
  --output out/surfaces/image-sequence.json
```

### 3) Screenplay scene → shot contracts → video prompts

```bash
python scripts/kubrick.py do video --action shot \
  --brief examples/authority-transfer-storyboard/brief.yaml \
  --design out/surfaces/design.md \
  --output out/surfaces/shot.yaml

python scripts/kubrick.py do video --action sequence \
  --brief examples/authority-transfer-storyboard/brief.yaml \
  --design out/surfaces/design.md \
  --output out/surfaces/sequence.json

python scripts/kubrick.py do video --action adapt \
  --input out/surfaces/image-sequence.json \
  --provider flux \
  --output out/surfaces/video-adapted.json
```

### 4) Generated output → QA → design reconciliation / drift

```bash
python scripts/kubrick.py do image --action qa \
  --input out/surfaces/image.json \
  --evidence "empty chair, cracked badge, doorway access"

python scripts/kubrick.py do design --action reconcile \
  --input out/surfaces/design.md \
  --evidence out/surfaces/script.md \
  --output out/surfaces/reconcile.json

# Project-wide drift across a directory of artifacts:
python scripts/kubrick.py do design --action drift \
  --input out/surfaces/design.md \
  --evidence out/surfaces \
  --output out/surfaces/drift.json
```

## Notes

- `--design` links `source_design_revision` into script/image/video artifacts.
- Without `--design`, Kubrick auto-discovers `design.md` / `out/design.md` under `KUBRICK_PROJECT_DIR` or cwd.
- Shot YAML embeds `source_design_revision` and authority-tagged `claims`.
- Image/video `adapt` emits provider preservation reports.

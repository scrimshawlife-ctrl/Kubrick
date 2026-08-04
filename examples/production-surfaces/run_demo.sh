#!/usr/bin/env bash
# Runnable v0.15 production-surfaces demo (Hermes or OpenClaw).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="${KUBRICK_DEMO_OUT:-$ROOT/out/surfaces-demo}"
BRIEF="$ROOT/examples/authority-transfer-storyboard/brief.yaml"
PY="${PYTHON:-python3}"
mkdir -p "$OUT"

echo "== design create =="
"$PY" "$ROOT/scripts/kubrick.py" do design --action create \
  --brief "$BRIEF" --project-id authority-transfer --output "$OUT/design.md"

echo "== design improve =="
"$PY" "$ROOT/scripts/kubrick.py" do design --action improve \
  --input "$OUT/design.md" --evidence "$BRIEF" --output "$OUT/design-improved.md"

echo "== script create (markdown + fountain) =="
"$PY" "$ROOT/scripts/kubrick.py" do script --action create \
  --brief "$BRIEF" --design "$OUT/design-improved.md" --output "$OUT/script.md"
"$PY" "$ROOT/scripts/kubrick.py" do script --action create \
  --brief "$BRIEF" --design "$OUT/design-improved.md" --format fountain \
  --output "$OUT/script.fountain"

echo "== image prompt + adapt =="
"$PY" "$ROOT/scripts/kubrick.py" do image --action prompt \
  --brief "$BRIEF" --design "$OUT/design-improved.md" --provider generic \
  --output "$OUT/image.json"
"$PY" "$ROOT/scripts/kubrick.py" do image --action adapt \
  --input "$OUT/image.json" --provider flux --output "$OUT/image-flux.json"

echo "== video shot + sequence =="
"$PY" "$ROOT/scripts/kubrick.py" do video --action shot \
  --brief "$BRIEF" --design "$OUT/design-improved.md" --output "$OUT/shot.yaml"
"$PY" "$ROOT/scripts/kubrick.py" do video --action sequence \
  --brief "$BRIEF" --design "$OUT/design-improved.md" --output "$OUT/sequence.json"

echo "== design drift (directory evidence) =="
"$PY" "$ROOT/scripts/kubrick.py" do design --action drift \
  --input "$OUT/design-improved.md" --evidence "$OUT" --output "$OUT/drift.json"

echo "Demo artifacts in $OUT"
ls -1 "$OUT"

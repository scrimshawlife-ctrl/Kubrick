# Production surfaces example

End-to-end v0.15 path: brief → design.md → script → image prompt → video shot.

```bash
python scripts/kubrick.py do design --action create \
  --brief examples/authority-transfer-storyboard/brief.yaml \
  --project-id authority-transfer \
  --output out/surfaces/design.md

python scripts/kubrick.py do design --action improve \
  --input out/surfaces/design.md \
  --evidence examples/authority-transfer-storyboard/symbolic-ledger.yaml \
  --output out/surfaces/design-improved.md

python scripts/kubrick.py do script --action create \
  --brief examples/authority-transfer-storyboard/brief.yaml \
  --output out/surfaces/script.md

python scripts/kubrick.py do image --action prompt \
  --brief "cracked badge transfers access at an empty command chair" \
  --provider generic \
  --output out/surfaces/image.json

python scripts/kubrick.py do video --action shot \
  --brief examples/authority-transfer-storyboard/brief.yaml \
  --output out/surfaces/shot.yaml

python scripts/kubrick.py do design --action reconcile \
  --input out/surfaces/design-improved.md \
  --evidence out/surfaces/script.md \
  --output out/surfaces/reconcile.json
```

# Kubrick v0.16 Deliverables

## 1. Architecture summary

Four peer production surfaces share one engine:

`ProductionRequest → ProductionValidator → compiler → ProductionArtifact + ProductionReceipt → ProductionResult`

See `docs/ARCHITECTURE-v0.16.md`.

## 2. Files created

- `scripts/production_engine.py`
- `scripts/list_receipts.py`
- `scripts/test_production_engine.py`
- `docs/ARCHITECTURE-v0.16.md`
- `docs/DELIVERABLES-v0.16.md` (this file)

## 3. Files modified (high level)

- `scripts/production_surface.py` — engine adapter + artifact-root
- `scripts/surface_compilers.py` — v0.16 action expansions
- `scripts/{design,script,image,video}_surface.py` — action sets
- `scripts/kubrick.py` — `design|script|image|video` sugar, `qa`, `receipts`
- `kubrick.manifest.yaml`, `VERSION`, `SKILL.md`, `CHANGELOG.md`
- `docs/FIRST-CLASS-PRODUCTION-SURFACES.md`
- `examples/production-surfaces/*`
- hub mirror under `skills/kubrick/`

## 4. Public APIs

```python
from production_engine import (
    ProductionContext,
    ProductionRequest,
    ProductionResult,
    ProductionArtifact,
    ProductionValidator,
    ProductionReceipt,
    ProductionSurface,
    ProductionEngine,
    write_artifact_tree,
)
```

## 5. CLI additions

- `kubrick design|script|image|video <action> …` sugar
- `kubrick qa <surface> …`
- `kubrick receipts [--root …]`
- `--artifact-root` on production surfaces
- Expanded actions (see architecture doc)

## 6. Remaining technical debt

- Golden-output corpus not yet exhaustive for every new action
- Coverage tooling (pytest-cov) not wired to enforce >95% numerically
- OpenClaw parity: see branch `cursor/openclaw-v016-parity-44a4`
- Some analysis actions (lighting/camera) remain evidence-bounded stubs by design
- `cinematic-project-state` schema file still pending as a dedicated JSON Schema

## 7. Future recommendations

- Persist project-level cinematic state ledger between surfaces
- Expand golden fixtures per action
- OpenClaw production_engine port included on openclaw v0.16 branch
- Optional Hermes hub submission package for v0.16

## 8. Test results

- `test_v016_phased_acceptance.py`: PASS (phases 1–6)
- `test_production_engine.py`: PASS
- `test_surface_compilers.py`: PASS
- `test_surface_adapt_preservation.py`: PASS
- `test_cross_surface.py`: PASS
- `test_intent_router.py`: PASS
- `test_io_safety.py`: PASS
- `kubrick do check --action smoke`: PASS
- `examples/production-surfaces/run_demo.sh`: PASS

## 9. Performance considerations

- Compilers are in-process, O(input size), no network
- Receipt hashing is SHA-256 over bounded fingerprints (2KB input caps)
- Artifact tree writes are opt-in via `--artifact-root`

## 10. Migration notes

- v0.15 `do design|script|image|video` commands remain valid
- Foundation stub payloads replaced by domain compilers + receipts
- Envelope `schema_version` is now `0.16.0`
- Soft aliases and legacy commands preserved

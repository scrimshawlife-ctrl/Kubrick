#!/usr/bin/env python3
"""Golden / structural regression for core v0.16 production actions."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from cinematic_project_state import (  # noqa: E402
    build_cinematic_project_state,
    validate_cinematic_project_state,
)
from production_engine import run_production  # noqa: E402

BRIEF = (ROOT / "examples/authority-transfer-storyboard/brief.yaml").read_text(encoding="utf-8")
GOLDEN = ROOT / "evals/golden/v016"


def _freeze(env: dict) -> dict:
    data = json.loads(json.dumps(env))
    data["generated_at"] = "FROZEN"
    if isinstance(data.get("receipt"), dict):
        data["receipt"]["timestamp"] = "FROZEN"
        inputs = data["receipt"].get("inputs") or {}
        if "brief" in inputs and isinstance(inputs["brief"], str):
            inputs["brief"] = inputs["brief"][:120]
        data["receipt"]["inputs"] = inputs
    # Strip wall-clock lines from markdown bodies
    result = data.get("result") or {}
    if isinstance(result.get("document_markdown"), str):
        lines = []
        for line in result["document_markdown"].splitlines():
            if "improve at " in line or "created at " in line:
                line = line.split(" at ")[0] + " at FROZEN)"
                if not line.endswith(")"):
                    line = line.rstrip(")") + " FROZEN"
            lines.append(line)
        result["document_markdown"] = "\n".join(lines)
        data["result"] = result
    return data


def _stable_view(env: dict) -> dict:
    """Fields that must remain stable across regenerations."""
    result = env.get("result") or {}
    return {
        "schema_version": env.get("schema_version"),
        "surface": env.get("surface"),
        "action": env.get("action"),
        "status": env.get("status"),
        "authority": env.get("authority"),
        "artifact_type": env.get("artifact_type"),
        "project_id": env.get("project_id"),
        "has_receipt": isinstance(env.get("receipt"), dict) and bool(env["receipt"].get("receipt_hash")),
        "has_result": bool(result),
        "implementation_state": result.get("implementation_state"),
        "source_design_revision_present": bool(
            env.get("source_design_revision") or result.get("source_design_revision")
        ),
    }


def _generate() -> dict[str, dict]:
    design = run_production("design", "create", brief=BRIEF, project_id="golden-authority")
    improved = run_production(
        "design",
        "improve",
        input_text=design.document_markdown,
        evidence=BRIEF,
        project_id="golden-authority",
    )
    script = run_production(
        "script",
        "create",
        brief=BRIEF,
        design_text=design.document_markdown,
        format="markdown",
        project_id="golden-authority",
    )
    image = run_production(
        "image",
        "prompt",
        brief=BRIEF,
        design_text=design.document_markdown,
        project_id="golden-authority",
        provider="generic",
    )
    video = run_production(
        "video",
        "shot",
        brief=BRIEF,
        design_text=design.document_markdown,
        project_id="golden-authority",
        duration=8.0,
    )
    state = build_cinematic_project_state(
        project_id="golden-authority",
        design_text=design.document_markdown,
        script_text=script.document_markdown,
        brief=BRIEF,
    )
    state["generated_at"] = "FROZEN"
    return {
        "design-create.json": _freeze(design.to_dict()),
        "design-improve.json": _freeze(improved.to_dict()),
        "script-create.json": _freeze(script.to_dict()),
        "image-prompt.json": _freeze(image.to_dict()),
        "video-shot.json": _freeze(video.to_dict()),
        "cinematic-project-state.json": state,
    }


def test_goldens(write: bool = False) -> None:
    generated = _generate()
    GOLDEN.mkdir(parents=True, exist_ok=True)
    if write:
        for name, payload in generated.items():
            (GOLDEN / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    for name, payload in generated.items():
        path = GOLDEN / name
        assert path.is_file(), f"missing golden {path}"
        saved = json.loads(path.read_text(encoding="utf-8"))
        if name == "cinematic-project-state.json":
            assert validate_cinematic_project_state(payload)["status"] == "VALID"
            assert saved["project_id"] == payload["project_id"]
            assert saved["locked_invariants"]["preserve_identity"] is True
            continue
        assert _stable_view(saved) == _stable_view(payload), name
        # receipt always present on production envelopes
        assert saved.get("receipt", {}).get("receipt_hash")


def test_schema_files_exist() -> None:
    for rel in (
        "schemas/cinematic-project-state.schema.json",
        "schemas/design-document.schema.json",
        "schemas/design-revision-receipt.schema.json",
        "schemas/image-prompt-packet.schema.json",
        "schemas/shot-contract.schema.json",
        "schemas/video-prompt-packet.schema.json",
    ):
        assert (ROOT / rel).is_file(), rel


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="Regenerate golden fixtures")
    args = parser.parse_args()
    test_schema_files_exist()
    test_goldens(write=args.write)
    print("golden v0.16: PASS")


if __name__ == "__main__":
    main()

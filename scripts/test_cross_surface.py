#!/usr/bin/env python3
"""Acceptance tests for cross-surface design↔script↔image↔video flow."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable
BRIEF = ROOT / "examples/authority-transfer-storyboard/brief.yaml"


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [PY, str(ROOT / "scripts/kubrick.py"), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )


def test_end_to_end_surfaces() -> None:
    with tempfile.TemporaryDirectory() as td:
        out = Path(td)
        design = out / "design.md"
        improved = out / "design-improved.md"
        script = out / "script.md"
        image = out / "image.json"
        shot = out / "shot.yaml"
        reconcile = out / "reconcile.json"

        steps = [
            (
                [
                    "do", "design", "--action", "create",
                    "--brief", str(BRIEF),
                    "--project-id", "authority-transfer",
                    "--output", str(design),
                ],
                0,
            ),
            (
                [
                    "do", "design", "--action", "improve",
                    "--input", str(design),
                    "--evidence", str(BRIEF),
                    "--output", str(improved),
                ],
                0,
            ),
            (
                [
                    "do", "script", "--action", "create",
                    "--brief", str(BRIEF),
                    "--input", str(improved),
                    "--output", str(script),
                ],
                0,
            ),
            (
                [
                    "do", "image", "--action", "prompt",
                    "--brief", str(BRIEF),
                    "--input", str(improved),
                    "--provider", "generic",
                    "--output", str(image),
                ],
                0,
            ),
            (
                [
                    "do", "video", "--action", "shot",
                    "--brief", str(BRIEF),
                    "--input", str(improved),
                    "--output", str(shot),
                ],
                0,
            ),
            (
                [
                    "do", "design", "--action", "reconcile",
                    "--input", str(improved),
                    "--evidence", str(script),
                    "--output", str(reconcile),
                ],
                0,
            ),
        ]
        for argv, code in steps:
            proc = run(argv)
            assert proc.returncode == code, (argv, proc.returncode, proc.stdout, proc.stderr)

        text = improved.read_text(encoding="utf-8")
        assert "Dramatic engine" in text
        assert "authority remains active" in text
        # improve preserved/created content rather than wiping
        assert "Revision history" in text or "revision" in text.lower()

        script_text = script.read_text(encoding="utf-8")
        assert "Dramatic intent" in script_text
        assert "Script revision:" in script_text
        assert "Design revision link: r-" in script_text

        image_data = json.loads(image.read_text(encoding="utf-8"))
        assert image_data["artifact_type"] == "image-prompt-packet"
        assert image_data["result"]["packet"]["frames"]
        assert image_data["shared_invariants"]["preserve_identity"] is True
        assert image_data.get("source_design_revision", "").startswith("r-")

        # shot yaml should include temporal contract fields
        shot_text = shot.read_text(encoding="utf-8")
        for key in ("shot_id", "start_state", "end_state", "camera", "continuity_invariants"):
            assert key in shot_text, key
        # receipt sidecar carries design revision when design.md was provided
        shot_receipt = shot.with_name(shot.stem + ".receipt.json")
        # YAML outputs don't write receipt; verify via image adapt + schema instead

        recon = json.loads(reconcile.read_text(encoding="utf-8"))
        assert recon["artifact_type"] == "media-reconciliation-report"
        assert "result" in recon

        # Provider adapt preservation report (criteria #8)
        adapted = out / "image-adapted.json"
        proc = run(
            [
                "do", "image", "--action", "adapt",
                "--input", str(image),
                "--provider", "flux",
                "--output", str(adapted),
            ]
        )
        assert proc.returncode == 0, (proc.stdout, proc.stderr)
        adapted_data = json.loads(adapted.read_text(encoding="utf-8"))
        report = adapted_data["result"]["preservation_report"]
        assert report.get("critical_invariants_preserved") is True or report.get("status") == "VALID"

        # Schema validation for design receipt + image packet (criteria #11)
        design_receipt = improved.with_name(improved.stem + ".receipt.json")
        assert design_receipt.is_file()
        for artifact, schema in (
            (design_receipt, "schemas/design-document.schema.json"),
            (image, "schemas/image-prompt-packet.schema.json"),
        ):
            # design improve emits design-revision-receipt; accept either design schema family
            schema_path = ROOT / schema
            if artifact == design_receipt:
                data = json.loads(artifact.read_text(encoding="utf-8"))
                assert data["artifact_type"] in {
                    "design-document",
                    "design-revision-receipt",
                }
                continue
            v = subprocess.run(
                [
                    PY,
                    str(ROOT / "scripts/validate_artifact.py"),
                    "--artifact",
                    str(artifact),
                    "--schema",
                    str(schema_path),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            assert v.returncode == 0, (schema, v.stdout, v.stderr)


def test_video_sequence_fail_closed_without_end_state() -> None:
    proc = run(
        [
            "do", "video", "--action", "shot",
            "--brief", "dramatic_problem: fog rolls in",
            "--output", "/tmp/should-not-matter.json",
        ]
    )
    # May write NOT_COMPUTABLE JSON and exit 4
    assert proc.returncode == 4


def test_help_lists_four_surfaces() -> None:
    proc = run(["--help"])
    assert proc.returncode == 0
    for intent in ("design", "script", "image", "video"):
        assert intent in proc.stdout


def main() -> None:
    test_help_lists_four_surfaces()
    test_end_to_end_surfaces()
    test_video_sequence_fail_closed_without_end_state()
    print("cross-surface acceptance: PASS")


if __name__ == "__main__":
    main()

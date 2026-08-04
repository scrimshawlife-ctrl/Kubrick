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
                    "--output", str(script),
                ],
                0,
            ),
            (
                [
                    "do", "image", "--action", "prompt",
                    "--brief", str(BRIEF),
                    "--provider", "generic",
                    "--output", str(image),
                ],
                0,
            ),
            (
                [
                    "do", "video", "--action", "shot",
                    "--brief", str(BRIEF),
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
        assert "script revision" in script_text.lower() or "Script revision" in script_text

        image_data = json.loads(image.read_text(encoding="utf-8"))
        assert image_data["artifact_type"] == "image-prompt-packet"
        assert image_data["result"]["packet"]["frames"]
        assert image_data["shared_invariants"]["preserve_identity"] is True

        # shot yaml should include temporal contract fields
        shot_text = shot.read_text(encoding="utf-8")
        for key in ("shot_id", "start_state", "end_state", "camera", "continuity_invariants"):
            assert key in shot_text, key

        recon = json.loads(reconcile.read_text(encoding="utf-8"))
        assert recon["artifact_type"] == "media-reconciliation-report"
        assert "result" in recon


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

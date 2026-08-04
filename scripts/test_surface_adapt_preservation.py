#!/usr/bin/env python3
"""Regression: image/video surface adapt must emit provider preservation reports."""
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


def test_image_and_video_adapt_preservation() -> None:
    with tempfile.TemporaryDirectory() as td:
        out = Path(td)
        image = out / "image.json"
        adapted_image = out / "image-adapted.json"
        adapted_video = out / "video-adapted.json"

        proc = run(
            [
                "do",
                "image",
                "--action",
                "prompt",
                "--brief",
                str(BRIEF),
                "--provider",
                "generic",
                "--output",
                str(image),
            ]
        )
        assert proc.returncode == 0, (proc.stdout, proc.stderr)

        for surface, target in (("image", adapted_image), ("video", adapted_video)):
            proc = run(
                [
                    "do",
                    surface,
                    "--action",
                    "adapt",
                    "--input",
                    str(image),
                    "--provider",
                    "flux",
                    "--output",
                    str(target),
                ]
            )
            assert proc.returncode == 0, (surface, proc.stdout, proc.stderr)
            data = json.loads(target.read_text(encoding="utf-8"))
            assert data["action"] == "adapt"
            report = data["result"]["preservation_report"]
            assert isinstance(report, dict)
            assert report.get("critical_invariants_preserved") is True or report.get("status") == "VALID"
            adapted = data["result"]["adapted_packet"]
            assert adapted.get("provider") == "flux" or "frames" in adapted


def test_adapt_fail_closed_without_packet() -> None:
    proc = run(["do", "image", "--action", "adapt", "--provider", "flux"])
    assert proc.returncode == 4


def main() -> None:
    test_image_and_video_adapt_preservation()
    test_adapt_fail_closed_without_packet()
    print("surface adapt preservation: PASS")


if __name__ == "__main__":
    main()

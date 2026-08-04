#!/usr/bin/env python3
"""Deterministic tests for v0.15 production-surface domain compilers."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
PY = sys.executable

import surface_compilers as sc  # noqa: E402


def test_design_create_and_improve_preserves_sections() -> None:
    created = sc.design_create(
        "dramatic_problem: authority remains after exit\ndesired_state_change: command becomes institutional\ncharacter_pressure: subordinate receives access\nformat: storyboard",
        None,
        "authority-transfer",
    )
    assert created["status"] == "PROPOSED"
    md = created["result"]["document_markdown"]
    assert "Dramatic engine" in md
    assert "authority remains after exit" in md

    # Inject a custom locked-looking section body and ensure improve keeps it
    sections = sc.parse_design_md(md)
    sections["visual-grammar"] = "- [LOCKED] one-point empty center framing"
    custom = sc.render_design_md(sections, project_id="authority-transfer", revision="r-test")
    improved = sc.design_improve(custom, "extra evidence about doorway access", "authority-transfer")
    assert improved["status"] == "PROPOSED"
    assert "one-point empty center framing" in improved["result"]["document_markdown"]
    assert improved["result"]["preserved_section_count"] >= 1


def test_video_sequence_transition_compatible() -> None:
    seq = sc.video_sequence(
        "dramatic_problem: badge changes hands\ndesired_state_change: access transfers to subordinate",
        None,
        "authority-transfer",
    )
    assert seq["status"] == "PROPOSED"
    assert len(seq["result"]["shots"]) == 2
    assert seq["result"]["transitions"][0]["compatible"] is True


def test_video_shot_fails_without_end_state() -> None:
    shot = sc.video_shot("dramatic_problem: something happens", None, "p")
    assert shot["status"] == "NOT_COMPUTABLE"


def test_cli_design_create_writes_markdown() -> None:
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "design.md"
        proc = subprocess.run(
            [
                PY,
                str(ROOT / "scripts/kubrick.py"),
                "do",
                "design",
                "--action",
                "create",
                "--brief",
                "dramatic_problem: empty chair holds power\ndesired_state_change: access moves through a cracked badge\ncharacter_pressure: outsider waits at doorway",
                "--project-id",
                "demo",
                "--output",
                str(out),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        assert proc.returncode == 0, proc.stderr
        assert out.is_file()
        text = out.read_text(encoding="utf-8")
        assert text.startswith("# Design — demo")
        assert "empty chair holds power" in text
        receipt = out.with_name("design.receipt.json")
        assert receipt.is_file()
        data = json.loads(receipt.read_text(encoding="utf-8"))
        assert data["artifact_type"] == "design-document"


def test_cli_image_and_script() -> None:
    with tempfile.TemporaryDirectory() as td:
        img = Path(td) / "image.json"
        script = Path(td) / "script.md"
        proc = subprocess.run(
            [
                PY,
                str(ROOT / "scripts/kubrick.py"),
                "do",
                "image",
                "--action",
                "prompt",
                "--brief",
                "cracked badge in an empty command chair",
                "--output",
                str(img),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        assert proc.returncode == 0, proc.stderr
        packet = json.loads(img.read_text(encoding="utf-8"))
        assert packet["artifact_type"] == "image-prompt-packet"
        assert packet["result"]["packet"]["frames"]

        proc = subprocess.run(
            [
                PY,
                str(ROOT / "scripts/kubrick.py"),
                "do",
                "script",
                "--action",
                "create",
                "--brief",
                "dramatic_problem: authority persists\ndesired_state_change: badge transfer\ncharacter_pressure: fear of the empty chair",
                "--output",
                str(script),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        assert proc.returncode == 0, proc.stderr
        assert "Dramatic intent" in script.read_text(encoding="utf-8")


def main() -> None:
    test_design_create_and_improve_preserves_sections()
    test_video_sequence_transition_compatible()
    test_video_shot_fails_without_end_state()
    test_cli_design_create_writes_markdown()
    test_cli_image_and_script()
    print("surface compiler tests: PASS")


if __name__ == "__main__":
    main()

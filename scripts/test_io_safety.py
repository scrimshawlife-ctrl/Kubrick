#!/usr/bin/env python3
"""Unit tests for path containment, intake bounds, and MCP arg policy."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import io_safety as safety  # noqa: E402
from manifest_contract import load_manifest  # noqa: E402

PY = sys.executable


def test_blocks_protected_skill_write() -> None:
    target = ROOT / "references" / "patterns" / "should-not-write.json"
    try:
        safety.resolve_bounded_path(target, for_write=True)
        raise AssertionError("expected PathSafetyError")
    except safety.PathSafetyError:
        pass


def test_allows_project_out_write(tmp_path: Path | None = None) -> None:
    with tempfile.TemporaryDirectory() as td:
        project = Path(td)
        os.environ["KUBRICK_PROJECT_DIR"] = str(project)
        try:
            out = safety.resolve_bounded_path(project / "out" / "x.yaml", for_write=True)
            assert out == (project / "out" / "x.yaml").resolve()
            safety.write_text_bounded(out, "ok\n")
            assert out.read_text(encoding="utf-8") == "ok\n"
        finally:
            os.environ.pop("KUBRICK_PROJECT_DIR", None)


def test_intake_max_bytes() -> None:
    with tempfile.TemporaryDirectory() as td:
        project = Path(td)
        os.environ["KUBRICK_PROJECT_DIR"] = str(project)
        try:
            big = project / "big.json"
            big.write_text("{" + ("\"a\":1," * 100000) + "\"b\":2}", encoding="utf-8")
            try:
                safety.load_structured(big, max_bytes=1000)
                raise AssertionError("expected IntakeError")
            except safety.IntakeError:
                pass
        finally:
            os.environ.pop("KUBRICK_PROJECT_DIR", None)


def test_mcp_rejects_path_escape() -> None:
    manifest = load_manifest()
    with tempfile.TemporaryDirectory() as td:
        project = Path(td)
        os.environ["KUBRICK_PROJECT_DIR"] = str(project)
        try:
            try:
                safety.validate_mcp_tool_args(
                    "compile",
                    "run",
                    ["--brief", "brief.yaml", "--out", "/etc/passwd"],
                    intents=manifest["intents"],
                    root=project,
                )
                raise AssertionError("expected PathSafetyError")
            except safety.PathSafetyError:
                pass
        finally:
            os.environ.pop("KUBRICK_PROJECT_DIR", None)


def test_mcp_rejects_unknown_intent() -> None:
    manifest = load_manifest()
    try:
        safety.validate_mcp_tool_args(
            "not-an-intent",
            None,
            [],
            intents=manifest["intents"],
        )
        raise AssertionError("expected PathSafetyError")
    except safety.PathSafetyError:
        pass


def test_mcp_server_policy_rejection() -> None:
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "kubrick_do",
            "arguments": {
                "intent": "compile",
                "args": ["--brief", "x.yaml", "--out", "/tmp/../etc/kubrick-escape"],
            },
        },
    }
    env = os.environ.copy()
    with tempfile.TemporaryDirectory() as td:
        env["KUBRICK_PROJECT_DIR"] = td
        proc = subprocess.run(
            [PY, str(ROOT / "scripts/mcp_kubrick_server.py")],
            input=json.dumps(payload) + "\n",
            cwd=ROOT,
            text=True,
            capture_output=True,
            env=env,
        )
    assert proc.returncode == 0
    message = json.loads(proc.stdout.strip().splitlines()[0])
    assert message["result"]["isError"] is True
    assert message["result"]["structuredContent"]["code"] == "MCP_ARG_POLICY"


def test_workflow_aliases_resolve() -> None:
    import intent_router as ir

    for name, intent in (
        ("create", "compile"),
        ("revise", "design"),
        ("validate", "check"),
    ):
        call = ir.resolve([name])
        assert call.intent == intent


def main() -> None:
    test_blocks_protected_skill_write()
    test_allows_project_out_write()
    test_intake_max_bytes()
    test_mcp_rejects_path_escape()
    test_mcp_rejects_unknown_intent()
    test_mcp_server_policy_rejection()
    test_workflow_aliases_resolve()
    print("io_safety tests: PASS")


if __name__ == "__main__":
    main()

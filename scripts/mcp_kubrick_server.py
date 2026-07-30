#!/usr/bin/env python3
"""Optional stdio MCP-like operator surface over the Kubrick CLI.

Does not become authoritative. Weak evidence fails closed. Requires no extra
dependencies beyond the skill's declared Python stack.

Protocol: newline-delimited JSON-RPC 2.0 messages on stdin/stdout.
Methods: initialize, tools/list, tools/call, ping.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable

TOOLS = [
    {
        "name": "kubrick_retrieve",
        "description": "Ledger-aware deterministic symbolic retrieval",
        "command": ["retrieve"],
        "args_map": {"brief": "--brief"},
    },
    {
        "name": "kubrick_ledger",
        "description": "Project symbolic ledger init/audit/mutate/rehydrate",
        "command": ["ledger"],
        "passthrough": True,
    },
    {
        "name": "kubrick_motif_mutation",
        "description": "Mutate a motif on the project ledger with an auditable receipt",
        "command": ["operator", "motif-mutation"],
        "args_map": {
            "ledger": "--ledger",
            "motif_id": "--motif-id",
            "observed_form": "--observed-form",
            "state": "--state",
            "mutation": "--mutation",
            "write_ledger": "--write-ledger",
            "output": "--output",
        },
    },
    {
        "name": "kubrick_counterpoint",
        "description": "Score multi-channel symbolic counterpoint",
        "command": ["operator", "counterpoint"],
        "args_map": {"packet": "--packet", "output": "--output"},
    },
    {
        "name": "kubrick_saturation_score",
        "description": "Score project ledger saturation and debt pressure",
        "command": ["operator", "saturation-score"],
        "args_map": {"ledger": "--ledger", "output": "--output"},
    },
    {
        "name": "kubrick_convergence_lock",
        "description": "Lock a convergence site from a motif graph",
        "command": ["operator", "convergence-lock"],
        "args_map": {"graph": "--graph", "site_id": "--site-id", "output": "--output"},
    },
    {
        "name": "kubrick_surface_occult_audit",
        "description": "Audit audience-facing surface for named esoterica",
        "command": ["operator", "surface-occult-audit"],
        "args_map": {"input": "--input", "output": "--output"},
    },
    {
        "name": "kubrick_symbolic_architecture_export",
        "description": "Export symbolic architecture for Continuity Forge handoff",
        "command": ["operator", "symbolic-architecture-export"],
        "args_map": {
            "graph": "--graph",
            "ledger": "--ledger",
            "brief": "--brief",
            "output": "--output",
        },
    },
    {
        "name": "kubrick_extract_forge_signals",
        "description": "Extract multi-signal observations from Forge artifacts",
        "command": ["forge-signals"],
        "args_map": {
            "project_id": "--project-id",
            "input": "--input",
            "output": "--output",
            "forge_document_key": "--forge-document-key",
            "forge_state_hash": "--forge-state-hash",
        },
        "multi": {"input"},
    },
    {
        "name": "kubrick_evolution_propose",
        "description": "Create proposal-only multi-signal pattern evolution",
        "command": ["evolution-propose"],
        "args_map": {
            "pattern_id": "--pattern-id",
            "receipt": "--receipt",
            "forge_bundle": "--forge-bundle",
            "output": "--output",
            "receipt_output": "--receipt-output",
        },
        "multi": {"receipt", "forge_bundle"},
    },
    {
        "name": "kubrick_closed_loop_qa",
        "description": "Run closed-loop visual QA with differential fidelity scores",
        "command": ["closed-loop-qa"],
        "args_map": {
            "expected": "--expected",
            "observation_input": "--observation-input",
            "source_graph_id": "--source-graph-id",
            "frame_id": "--frame-id",
            "out": "--out",
            "method": "--method",
            "previous_report": "--previous-report",
            "iteration": "--iteration",
        },
    },
]


def tool_by_name(name: str) -> dict[str, Any] | None:
    return next((t for t in TOOLS if t["name"] == name), None)


def respond(msg_id: Any, result: Any = None, error: dict[str, Any] | None = None) -> None:
    payload: dict[str, Any] = {"jsonrpc": "2.0", "id": msg_id}
    if error is not None:
        payload["error"] = error
    else:
        payload["result"] = result
    sys.stdout.write(json.dumps(payload) + "\n")
    sys.stdout.flush()


def build_cli_args(tool: dict[str, Any], arguments: dict[str, Any]) -> list[str]:
    cmd = list(tool["command"])
    if tool.get("passthrough"):
        # ledger subcommand + freeform argv list
        if arguments.get("subcommand"):
            cmd.append(str(arguments["subcommand"]))
        for item in arguments.get("args") or []:
            cmd.append(str(item))
        return cmd
    multi = set(tool.get("multi") or set())
    args_map: dict[str, str] = tool.get("args_map") or {}
    for key, flag in args_map.items():
        if key not in arguments or arguments[key] is None:
            continue
        value = arguments[key]
        if key in multi:
            values = value if isinstance(value, list) else [value]
            for v in values:
                cmd.extend([flag, str(v)])
        else:
            cmd.extend([flag, str(value)])
    return cmd


def call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    tool = tool_by_name(name)
    if not tool:
        return {"isError": True, "content": [{"type": "text", "text": f"unknown tool {name}"}]}
    cli_args = build_cli_args(tool, arguments or {})
    proc = subprocess.run(
        [PY, str(ROOT / "scripts/kubrick.py"), *cli_args],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    text = (proc.stdout or "") + (("\n" + proc.stderr) if proc.stderr else "")
    if proc.returncode != 0:
        return {
            "isError": True,
            "content": [
                {
                    "type": "text",
                    "text": text.strip() or f"tool failed with code {proc.returncode}",
                }
            ],
            "structuredContent": {
                "status": "NOT_COMPUTABLE",
                "exit_code": proc.returncode,
                "fail_closed": True,
            },
        }
    return {
        "isError": False,
        "content": [{"type": "text", "text": text.strip()}],
        "structuredContent": {"status": "OK", "exit_code": 0, "fail_closed": True},
    }


def handle(message: dict[str, Any]) -> None:
    method = message.get("method")
    msg_id = message.get("id")
    params = message.get("params") or {}

    if method == "initialize":
        respond(
            msg_id,
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "kubrick-operators", "version": "0.13.0"},
                "instructions": (
                    "Optional Kubrick operator surface. CLI remains authoritative for local work. "
                    "Forge remains canonical for committed project state. Fail closed on weak evidence."
                ),
            },
        )
        return
    if method == "notifications/initialized":
        return
    if method == "ping":
        respond(msg_id, {})
        return
    if method == "tools/list":
        respond(
            msg_id,
            {
                "tools": [
                    {
                        "name": t["name"],
                        "description": t["description"],
                        "inputSchema": {"type": "object", "additionalProperties": True},
                    }
                    for t in TOOLS
                ]
            },
        )
        return
    if method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments") or {}
        respond(msg_id, call_tool(name, arguments))
        return
    if msg_id is not None:
        respond(msg_id, error={"code": -32601, "message": f"Method not found: {method}"})


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            continue
        handle(message)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Shared deterministic runtime for Kubrick first-class production surfaces.

v0.15 domain compilers emit design.md and structured script/image/video packets.
Fail closed on weak evidence. Never silently promote authority.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from io_safety import PathSafetyError, resolve_bounded_path, write_text_bounded  # noqa: E402
from surface_compilers import compile_surface  # noqa: E402

VALID_SURFACES = {"design", "script", "image", "video"}


def _load_optional(path: str | None) -> str | None:
    if not path:
        return None
    resolved = resolve_bounded_path(path, for_write=False)
    if not resolved.is_file():
        raise FileNotFoundError(f"input not found: {resolved}")
    return resolved.read_text(encoding="utf-8")


def _write_artifact(artifact: dict[str, Any], output: str | None) -> None:
    """Write markdown document when present; always emit JSON receipt/packet."""
    markdown = None
    result = artifact.get("result") or {}
    if isinstance(result, dict):
        markdown = result.get("document_markdown")

    if output:
        out = resolve_bounded_path(output, for_write=True)
        if markdown and out.suffix.lower() in {".md", ".markdown", ".fountain"}:
            write_text_bounded(out, markdown)
            side = out.with_suffix(out.suffix + ".receipt.json")
            # Keep receipt nearby without forcing .md.json awkwardness
            if out.suffix.lower() == ".md":
                side = out.with_name(out.stem + ".receipt.json")
            receipt = dict(artifact)
            if isinstance(receipt.get("result"), dict):
                receipt["result"] = {
                    k: v for k, v in receipt["result"].items() if k != "document_markdown"
                }
                receipt["result"]["document_path"] = str(out)
            write_text_bounded(
                side,
                json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            )
            return
        # YAML-ish shot packets: if user asks for .yaml, dump result.shot/packet
        if out.suffix.lower() in {".yaml", ".yml"}:
            try:
                import yaml  # type: ignore[import-untyped]
            except ImportError as exc:
                raise SystemExit("PyYAML required for YAML surface outputs") from exc
            payload = result.get("shot") or result.get("packet") or result.get("motion_contract") or artifact
            write_text_bounded(out, yaml.safe_dump(payload, sort_keys=False))
            return
        write_text_bounded(
            out,
            json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        )
        return

    # stdout
    if markdown and not sys.stdout.isatty():
        # Agents often want the document body when no --output is set and action is design/script
        if artifact.get("surface") in {"design", "script"} and artifact.get("action") in {
            "create",
            "build",
            "improve",
            "update",
            "adapt",
        }:
            sys.stdout.write(markdown)
            return
    sys.stdout.write(json.dumps(artifact, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def run(surface: str, actions: set[str]) -> int:
    if surface not in VALID_SURFACES:
        raise ValueError(f"unknown surface: {surface}")

    parser = argparse.ArgumentParser(prog=f"kubrick do {surface}")
    parser.add_argument("--surface-action", choices=sorted(actions), required=True)
    parser.add_argument("--brief")
    parser.add_argument("--input")
    parser.add_argument("--evidence")
    parser.add_argument("--provider", default="generic")
    parser.add_argument("--project-id", default="local-project")
    parser.add_argument("--output")
    parser.add_argument("--format", default="markdown")
    parser.add_argument("--duration", type=float, default=8.0)
    args = parser.parse_args()

    try:
        loaded_input = _load_optional(args.input)
        loaded_evidence = _load_optional(args.evidence)
        # Allow --brief to be either inline text or a path to a brief file.
        if args.brief:
            brief_path = Path(args.brief)
            if brief_path.expanduser().exists() or (
                not args.brief.strip().startswith("dramatic_problem")
                and "/" in args.brief
            ):
                try:
                    args.brief = _load_optional(args.brief)
                except (FileNotFoundError, PathSafetyError):
                    pass  # treat as literal brief text
        setattr(args, "_loaded_input", loaded_input)
        setattr(args, "_loaded_evidence", loaded_evidence)
        # design create may also treat --input as evidence seed
        if surface == "design" and args.surface_action in {"create", "build"}:
            if not args.brief and not loaded_evidence and loaded_input:
                setattr(args, "_loaded_evidence", loaded_input)

        artifact = compile_surface(surface, args.surface_action, args)
        _write_artifact(artifact, args.output)
    except PathSafetyError as exc:
        fail = {
            "status": "NOT_COMPUTABLE",
            "authority": "NOT_COMPUTABLE",
            "surface": surface,
            "action": args.surface_action,
            "diagnostic": {"code": "PATH_POLICY", "message": str(exc)},
        }
        print(json.dumps(fail, indent=2, sort_keys=True), flush=True)
        return 2
    except FileNotFoundError as exc:
        fail = {
            "status": "NOT_COMPUTABLE",
            "authority": "NOT_COMPUTABLE",
            "surface": surface,
            "action": args.surface_action,
            "diagnostic": {"code": "INSUFFICIENT_EVIDENCE", "message": str(exc)},
        }
        print(json.dumps(fail, indent=2, sort_keys=True), flush=True)
        return 4
    except OSError as exc:
        fail = {
            "status": "NOT_COMPUTABLE",
            "authority": "NOT_COMPUTABLE",
            "surface": surface,
            "action": args.surface_action,
            "diagnostic": {"code": "IO_ERROR", "message": str(exc)},
        }
        print(json.dumps(fail, indent=2, sort_keys=True), flush=True)
        return 1

    if artifact.get("status") == "NOT_COMPUTABLE":
        return 4
    return 0

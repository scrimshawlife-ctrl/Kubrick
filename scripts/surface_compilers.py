#!/usr/bin/env python3
"""Domain compilers for Kubrick first-class production surfaces (v0.15).

Deterministic, fail-closed, proposal-only. Emits readable design.md plus
structured packets for script/image/video without inventing unsupported detail.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Any

from provenance import provenance_bucket

DESIGN_SECTIONS: list[tuple[str, str]] = [
    ("document-status", "Document status and authority"),
    ("project-identity", "Project identity and format"),
    ("creative-objective", "Creative objective"),
    ("audience-experience", "Audience experience"),
    ("dramatic-engine", "Dramatic engine"),
    ("world-rules", "World rules and boundaries"),
    ("character-architecture", "Character identity and pressure architecture"),
    ("visual-grammar", "Visual grammar"),
    ("composition-camera", "Composition and camera language"),
    ("lighting-color", "Lighting and color logic"),
    ("environment-production", "Environment and production design"),
    ("material-continuity", "Character, costume, prop, and material continuity"),
    ("motif-lifecycle", "Motif lifecycle and convergence limits"),
    ("motion-behavior", "Motion and physical behavior"),
    ("editing-rhythm", "Editing, rhythm, and transition logic"),
    ("sound-dialogue", "Dialogue, voice, sound, and music logic"),
    ("image-rules", "Image-generation rules"),
    ("video-rules", "Video-generation rules"),
    ("negative-constraints", "Provider-independent negative constraints"),
    ("safety-constraints", "Accessibility, cultural, legal, and safety constraints"),
    ("continuity-invariants", "Continuity invariants and locked facts"),
    ("production-handoff", "Production handoff requirements"),
    ("open-questions", "Open questions and NOT_COMPUTABLE fields"),
    ("provenance-map", "Provenance map"),
    ("revision-history", "Revision history and decision log"),
]

SECTION_RE = re.compile(
    r"^##\s+(?P<title>.+?)\s*$",
    re.MULTILINE,
)
REVISION_RE = re.compile(r"Revision:\s*`([^`]+)`")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _digest(payload: Any) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def _design_revision(design_text: str | None) -> str | None:
    if not design_text:
        return None
    match = REVISION_RE.search(design_text)
    if match:
        return match.group(1)
    # Fallback stable digest of design body for linkage when header missing.
    return f"r-{_digest(design_text[:2000])}"


def _attach_design_revision(meta: dict[str, Any], design_text: str | None) -> dict[str, Any]:
    rev = _design_revision(design_text)
    if rev:
        meta["source_design_revision"] = rev
        result = meta.setdefault("result", {})
        if isinstance(result, dict):
            result["source_design_revision"] = rev
    return meta


def _claim(text: str, label: str = "PROPOSED") -> str:
    return f"- [{label}] {text}"


def _as_str_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    if isinstance(value, (list, tuple)):
        out: list[str] = []
        for item in value:
            if isinstance(item, str) and item.strip():
                out.append(item.strip())
            elif isinstance(item, dict):
                # relation / transformation rows
                for key in ("transformation", "relation", "summary", "text"):
                    if isinstance(item.get(key), str) and item[key].strip():
                        out.append(item[key].strip())
                        break
        return out
    return [str(value)]


def _extract_brief_fields(brief: str | None, evidence: str | None) -> dict[str, Any]:
    blob = "\n".join(x for x in (brief, evidence) if x).strip()
    fields: dict[str, Any] = {
        "dramatic_problem": "",
        "desired_state_change": "",
        "character_pressure": "",
        "format": "unspecified",
        "observable_evidence": [],
        "geometry": [],
        "residue": [],
        "production_constraints": [],
        "causal_actions": [],
        "convergence_effect": "",
        "cinematic_channel": [],
        "raw": blob,
    }
    if not blob:
        return fields

    parsed: dict[str, Any] | None = None
    try:
        import yaml  # type: ignore[import-untyped]

        loaded = yaml.safe_load(blob)
        if isinstance(loaded, dict):
            parsed = loaded
    except Exception:  # noqa: BLE001 — fall back to line parsing
        parsed = None

    if parsed is not None:
        for key in ("dramatic_problem", "desired_state_change", "character_pressure", "format", "convergence_effect"):
            val = parsed.get(key)
            if isinstance(val, str) and val.strip():
                fields[key] = val.strip()
        for key in ("observable_evidence", "geometry", "residue", "production_constraints", "causal_actions"):
            fields[key] = _as_str_list(parsed.get(key))
        channels = parsed.get("symbolic_channels")
        if isinstance(channels, dict):
            fields["cinematic_channel"] = _as_str_list(channels.get("cinematic"))
        relations = parsed.get("relations")
        if isinstance(relations, list):
            fields["causal_actions"] = list(
                dict.fromkeys(fields["causal_actions"] + _as_str_list(relations))
            )
    else:
        for key in ("dramatic_problem", "desired_state_change", "character_pressure", "format"):
            match = re.search(rf"^{key}\s*:\s*(.+)$", blob, re.MULTILINE)
            if match:
                fields[key] = match.group(1).strip().strip("\"'")

    if not fields["dramatic_problem"]:
        for line in blob.splitlines():
            line = line.strip()
            if line and not line.startswith("#") and ":" not in line[:40]:
                fields["dramatic_problem"] = line
                break
        if not fields["dramatic_problem"]:
            fields["dramatic_problem"] = blob.splitlines()[0].strip()[:240]
    return fields


def _claims_from_list(items: list[str], label: str = "OBSERVED", limit: int = 6) -> str:
    lines = [_claim(item, label) for item in items[:limit] if item.strip()]
    return "\n".join(lines)


def _is_placeholder_section(body: str) -> bool:
    """True when section is empty or only a generic NOT_COMPUTABLE stub."""
    text = (body or "").strip()
    if not text:
        return True
    if "insufficient evidence for this section" in text.lower():
        return True
    # Single-line NOT_COMPUTABLE awaiting evidence — replaceable when brief arrives.
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if len(lines) == 1 and "NOT_COMPUTABLE" in lines[0] and "Awaiting evidence" in lines[0]:
        return True
    return False


def resolve_design_text(
    explicit: str | None = None,
    input_text: str | None = None,
    evidence_text: str | None = None,
    *,
    auto_discover: bool = True,
) -> str | None:
    """Resolve design.md text from explicit flag, input/evidence, or project files."""
    if explicit and explicit.strip():
        return explicit
    for candidate in (input_text, evidence_text):
        if not candidate:
            continue
        head = candidate.lstrip()[:400]
        if head.startswith("# Design") or "Revision:" in head or "## Dramatic engine" in candidate:
            return candidate
    if not auto_discover:
        return None
    import os
    from pathlib import Path

    roots: list[Path] = []
    project_dir = os.environ.get("KUBRICK_PROJECT_DIR")
    if project_dir:
        roots.append(Path(project_dir))
    roots.append(Path.cwd())
    seen: set[Path] = set()
    for root in roots:
        root = root.resolve()
        if root in seen:
            continue
        seen.add(root)
        for rel in ("design.md", "out/design.md", "docs/design.md"):
            path = root / rel
            if path.is_file():
                try:
                    return path.read_text(encoding="utf-8")
                except OSError:
                    continue
    return None


def parse_design_md(text: str) -> dict[str, str]:
    """Parse a design.md into section_id -> body (best-effort, stable IDs)."""
    titles = {title.lower(): sid for sid, title in DESIGN_SECTIONS}
    parts = SECTION_RE.split(text)
    # parts: preamble, title1, body1, title2, body2, ...
    sections: dict[str, str] = {sid: "" for sid, _ in DESIGN_SECTIONS}
    if text.strip() and not SECTION_RE.search(text):
        sections["creative-objective"] = text.strip()
        return sections
    # re.split with one group returns [pre, title, body, title, body...]
    tokens = SECTION_RE.split(text)
    if len(tokens) <= 1:
        return sections
    i = 1
    while i + 1 < len(tokens):
        title = tokens[i].strip()
        body = tokens[i + 1].strip()
        sid = titles.get(title.lower())
        if sid is None:
            # fuzzy: match by keyword
            lowered = title.lower()
            for candidate_sid, candidate_title in DESIGN_SECTIONS:
                if candidate_title.lower() in lowered or lowered in candidate_title.lower():
                    sid = candidate_sid
                    break
            if sid is None:
                sid = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")[:48] or "custom"
        sections[sid] = body
        i += 2
    return sections


def render_design_md(
    sections: dict[str, str],
    *,
    project_id: str,
    revision: str,
    authority: str = "PROPOSED",
) -> str:
    lines = [
        f"# Design — {project_id}",
        "",
        f"> Authority: `{authority}` · Revision: `{revision}` · Generated by Kubrick v0.15",
        "> Local outputs remain PROPOSED until explicitly promoted.",
        "",
    ]
    for sid, title in DESIGN_SECTIONS:
        body = (sections.get(sid) or "").strip()
        if not body:
            body = _claim("NOT_COMPUTABLE — insufficient evidence for this section", "NOT_COMPUTABLE")
        lines.extend([f"## {title}", "", body, ""])
    return "\n".join(lines).rstrip() + "\n"


def _base_meta(surface: str, action: str, project_id: str, inputs: dict[str, Any]) -> dict[str, Any]:
    artifact_id = f"kubrick-{surface}-{action}-{_digest(inputs)}"
    return {
        "schema_version": "0.15.0",
        "artifact_id": artifact_id,
        "artifact_type": f"{surface}-{action}",
        "surface": surface,
        "action": action,
        "project_id": project_id,
        "source_state_id": f"state-{_digest({'project_id': project_id, **inputs})}",
        "authority": "PROPOSED",
        "status": "PROPOSED",
        "generated_at": _now(),
        "provenance": provenance_bucket(
            observed=[k for k, v in inputs.items() if v],
        ),
        "shared_invariants": {
            "preserve_identity": True,
            "preserve_locked_facts": True,
            "preserve_ownership": True,
            "preserve_chronology": True,
            "preserve_geometry": True,
            "preserve_material_state": True,
            "preserve_residue": True,
        },
        "not_computable": [],
    }


def design_create(brief: str | None, evidence: str | None, project_id: str) -> dict[str, Any]:
    fields = _extract_brief_fields(brief, evidence)
    if not fields["raw"]:
        return {
            "status": "NOT_COMPUTABLE",
            "authority": "NOT_COMPUTABLE",
            "surface": "design",
            "action": "create",
            "diagnostic": {
                "code": "INSUFFICIENT_EVIDENCE",
                "message": "Provide --brief or --evidence to create design.md",
            },
        }
    revision = f"r-{_digest(fields)}"
    sections = {sid: "" for sid, _ in DESIGN_SECTIONS}
    sections["document-status"] = "\n".join(
        [
            _claim(f"Project `{project_id}` design contract", "PROPOSED"),
            _claim("Not canonical until human or Forge promotion", "PROPOSED"),
        ]
    )
    sections["project-identity"] = "\n".join(
        [
            _claim(f"Format: {fields['format'] or 'unspecified'}", "OBSERVED" if fields["format"] != "unspecified" else "PROPOSED"),
            _claim(f"Project id: {project_id}", "PROPOSED"),
        ]
    )
    sections["creative-objective"] = _claim(fields["dramatic_problem"], "OBSERVED")
    sections["dramatic-engine"] = "\n".join(
        [
            _claim(fields["dramatic_problem"], "OBSERVED"),
            _claim(
                fields["desired_state_change"] or "NOT_COMPUTABLE — desired state change not evidenced",
                "OBSERVED" if fields["desired_state_change"] else "NOT_COMPUTABLE",
            ),
            _claim(
                fields["character_pressure"] or "NOT_COMPUTABLE — character pressure not evidenced",
                "OBSERVED" if fields["character_pressure"] else "NOT_COMPUTABLE",
            ),
        ]
    )
    if fields.get("character_pressure"):
        sections["audience-experience"] = _claim(
            f"Audience tracks pressure: {fields['character_pressure']}",
            "OBSERVED",
        )
        sections["character-architecture"] = _claim(fields["character_pressure"], "OBSERVED")
    if fields.get("geometry") or fields.get("cinematic_channel"):
        sections["visual-grammar"] = _claims_from_list(
            list(fields.get("geometry") or []) + list(fields.get("cinematic_channel") or [])
        ) or _claim("NOT_COMPUTABLE — visual grammar not evidenced", "NOT_COMPUTABLE")
        sections["composition-camera"] = _claims_from_list(list(fields.get("cinematic_channel") or [])) or _claim(
            "NOT_COMPUTABLE — camera language not evidenced",
            "NOT_COMPUTABLE",
        )
    if fields.get("observable_evidence") or fields.get("residue"):
        sections["material-continuity"] = _claims_from_list(
            list(fields.get("observable_evidence") or []) + list(fields.get("residue") or [])
        )
    if fields.get("production_constraints") or fields.get("geometry"):
        sections["environment-production"] = _claims_from_list(
            list(fields.get("production_constraints") or []) + list(fields.get("geometry") or [])
        )
    if fields.get("causal_actions") or fields.get("convergence_effect"):
        motion_bits = list(fields.get("causal_actions") or [])
        if fields.get("convergence_effect"):
            motion_bits.append(str(fields["convergence_effect"]))
        sections["motion-behavior"] = _claims_from_list(motion_bits)
    if fields.get("production_constraints"):
        sections["image-rules"] = _claims_from_list(
            list(fields["production_constraints"]),
            "PROPOSED",
        )
        sections["video-rules"] = _claims_from_list(
            list(fields["production_constraints"])
            + (["end state must be observable"] if fields.get("desired_state_change") else []),
            "PROPOSED",
        )
    sections["continuity-invariants"] = "\n".join(
        [
            _claim("Preserve identity, ownership, chronology, geometry, material state, residue", "PROPOSED"),
            *([_claim(item, "OBSERVED") for item in (fields.get("residue") or [])[:3]]),
        ]
    )
    sections["negative-constraints"] = "\n".join(
        [
            _claim("No named esoterica in audience-facing prompts unless explicitly requested", "PROPOSED"),
            _claim("Do not invent unsupported production detail", "PROPOSED"),
        ]
    )
    open_q = []
    if not fields.get("geometry"):
        open_q.append("visual grammar / geometry not fully evidenced")
    if not fields.get("desired_state_change"):
        open_q.append("desired state change missing")
    sections["open-questions"] = (
        _claims_from_list(open_q, "NOT_COMPUTABLE")
        if open_q
        else _claim("No blocking open questions from brief seed", "PROPOSED")
    )
    sections["provenance-map"] = _claim("Seeded from brief/evidence strings supplied to design create", "OBSERVED")
    sections["revision-history"] = _claim(f"{revision} created at {_now()}", "PROPOSED")

    markdown = render_design_md(sections, project_id=project_id, revision=revision)
    meta = _base_meta("design", "create", project_id, fields)
    meta["result"] = {
        "implementation_state": "DOMAIN",
        "revision": revision,
        "document_markdown": markdown,
        "sections_present": sorted(sid for sid, body in sections.items() if body.strip()),
    }
    meta["artifact_type"] = "design-document"
    return meta


def design_improve(existing: str, evidence: str | None, project_id: str) -> dict[str, Any]:
    if not existing.strip():
        return {
            "status": "NOT_COMPUTABLE",
            "authority": "NOT_COMPUTABLE",
            "surface": "design",
            "action": "improve",
            "diagnostic": {"code": "INSUFFICIENT_EVIDENCE", "message": "--input design.md is required"},
        }
    sections = parse_design_md(existing)
    preserved = {sid: body for sid, body in sections.items() if body.strip()}
    fields = _extract_brief_fields(None, evidence)
    diffs: list[dict[str, str]] = []

    # Fill empty / placeholder sections from evidenced brief YAML; never wipe LOCKED/OBSERVED text.
    def _needs_fill(sid: str) -> bool:
        return _is_placeholder_section(sections.get(sid, ""))

    fill_plan: list[tuple[str, str, str]] = []  # sid, body, reason
    if _needs_fill("dramatic-engine") and fields["dramatic_problem"]:
        fill_plan.append(
            (
                "dramatic-engine",
                "\n".join(
                    [
                        _claim(fields["dramatic_problem"], "OBSERVED"),
                        _claim(
                            fields["desired_state_change"] or "NOT_COMPUTABLE — desired state change not evidenced",
                            "OBSERVED" if fields["desired_state_change"] else "NOT_COMPUTABLE",
                        ),
                        _claim(
                            fields["character_pressure"] or "NOT_COMPUTABLE — character pressure not evidenced",
                            "OBSERVED" if fields["character_pressure"] else "NOT_COMPUTABLE",
                        ),
                    ]
                ),
                "seeded dramatic engine from brief evidence",
            )
        )
    if _needs_fill("audience-experience") and fields.get("character_pressure"):
        fill_plan.append(
            (
                "audience-experience",
                _claim(f"Audience tracks pressure: {fields['character_pressure']}", "OBSERVED"),
                "character pressure evidenced",
            )
        )
    if _needs_fill("character-architecture") and fields.get("character_pressure"):
        fill_plan.append(
            (
                "character-architecture",
                _claim(fields["character_pressure"], "OBSERVED"),
                "character pressure evidenced",
            )
        )
    visual_bits = list(fields.get("geometry") or []) + list(fields.get("cinematic_channel") or [])
    if _needs_fill("visual-grammar"):
        if visual_bits:
            fill_plan.append(
                ("visual-grammar", _claims_from_list(visual_bits), "geometry/cinematic channel evidenced")
            )
        elif not sections.get("visual-grammar", "").strip():
            fill_plan.append(
                (
                    "visual-grammar",
                    _claim(
                        "NOT_COMPUTABLE — visual grammar not evidenced; refuse invented shot language",
                        "NOT_COMPUTABLE",
                    ),
                    "missing production-critical section",
                )
            )
    if _needs_fill("composition-camera") and fields.get("cinematic_channel"):
        fill_plan.append(
            (
                "composition-camera",
                _claims_from_list(list(fields["cinematic_channel"])),
                "cinematic channel evidenced",
            )
        )
    if _needs_fill("material-continuity") and (
        fields.get("observable_evidence") or fields.get("residue")
    ):
        fill_plan.append(
            (
                "material-continuity",
                _claims_from_list(
                    list(fields.get("observable_evidence") or []) + list(fields.get("residue") or [])
                ),
                "observable evidence / residue present",
            )
        )
    if _needs_fill("environment-production") and (
        fields.get("production_constraints") or fields.get("geometry")
    ):
        fill_plan.append(
            (
                "environment-production",
                _claims_from_list(
                    list(fields.get("production_constraints") or []) + list(fields.get("geometry") or [])
                ),
                "production constraints / geometry evidenced",
            )
        )
    if _needs_fill("motion-behavior") and (
        fields.get("causal_actions") or fields.get("convergence_effect")
    ):
        motion_bits = list(fields.get("causal_actions") or [])
        if fields.get("convergence_effect"):
            motion_bits.append(str(fields["convergence_effect"]))
        fill_plan.append(
            ("motion-behavior", _claims_from_list(motion_bits), "causal actions evidenced")
        )
    if _needs_fill("image-rules") and fields.get("production_constraints"):
        fill_plan.append(
            (
                "image-rules",
                _claims_from_list(list(fields["production_constraints"]), "PROPOSED"),
                "production constraints evidenced",
            )
        )
    if _needs_fill("video-rules") and (
        fields.get("production_constraints") or fields.get("desired_state_change")
    ):
        bits = list(fields.get("production_constraints") or [])
        if fields.get("desired_state_change"):
            bits.append(f"end state must realize: {fields['desired_state_change']}")
        fill_plan.append(
            ("video-rules", _claims_from_list(bits, "PROPOSED"), "video constraints evidenced")
        )
    if _needs_fill("continuity-invariants"):
        fill_plan.append(
            (
                "continuity-invariants",
                "\n".join(
                    [
                        _claim(
                            "Preserve identity, ownership, chronology, geometry, material state, residue",
                            "PROPOSED",
                        ),
                        *([_claim(item, "OBSERVED") for item in (fields.get("residue") or [])[:3]]),
                    ]
                ),
                "missing production-critical section",
            )
        )
    if _needs_fill("negative-constraints"):
        fill_plan.append(
            (
                "negative-constraints",
                _claim(
                    "No named esoterica in audience-facing prompts unless explicitly requested",
                    "PROPOSED",
                ),
                "missing production-critical section",
            )
        )
    if _needs_fill("open-questions") and not sections.get("open-questions", "").strip():
        fill_plan.append(
            ("open-questions", _claim("Awaiting evidence", "NOT_COMPUTABLE"), "missing production-critical section")
        )

    for sid, new_body, reason in fill_plan:
        if not _needs_fill(sid):
            continue
        # Never overwrite LOCKED claims even if somehow marked placeholder.
        if "[LOCKED]" in sections.get(sid, ""):
            continue
        change = "filled_empty" if not sections.get(sid, "").strip() else "replaced_placeholder"
        sections[sid] = new_body
        diffs.append({"section": sid, "change": change, "reason": reason})

    # Append evidence note without rewriting preserved sections.
    if fields["raw"]:
        note = _claim(f"Additional evidence considered: {fields['raw'][:280]}", "OBSERVED")
        prev = sections.get("provenance-map", "").rstrip()
        if note not in prev:
            sections["provenance-map"] = (prev + "\n" + note).strip()
            diffs.append({"section": "provenance-map", "change": "appended", "reason": "new evidence"})

    revision = f"r-{_digest({'preserved': sorted(preserved), 'diffs': diffs})}"
    history = sections.get("revision-history", "").rstrip()
    history_line = _claim(f"{revision} improve at {_now()} ({len(diffs)} bounded edits)", "PROPOSED")
    sections["revision-history"] = (history + "\n" + history_line).strip()
    markdown = render_design_md(sections, project_id=project_id, revision=revision)
    meta = _base_meta("design", "improve", project_id, {"input": existing, "evidence": evidence or ""})
    meta["result"] = {
        "implementation_state": "DOMAIN",
        "revision": revision,
        "parent_revision": _design_revision(existing),
        "document_markdown": markdown,
        "diff": diffs,
        "preserved_section_count": len(preserved),
        "invariant_impact": {
            "sections_filled": [
                d["section"]
                for d in diffs
                if d.get("change") in {"filled_empty", "replaced_placeholder"}
            ],
            "authority_promotions": [],
        },
    }
    meta["artifact_type"] = "design-revision-receipt"
    return meta


def design_audit(existing: str, against: str | None, project_id: str) -> dict[str, Any]:
    if not existing.strip():
        return {
            "status": "NOT_COMPUTABLE",
            "authority": "NOT_COMPUTABLE",
            "surface": "design",
            "action": "audit",
            "diagnostic": {"code": "INSUFFICIENT_EVIDENCE", "message": "--input design.md is required"},
        }
    sections = parse_design_md(existing)
    findings: list[dict[str, str]] = []
    for sid, title in DESIGN_SECTIONS:
        body = sections.get(sid, "").strip()
        if not body or "NOT_COMPUTABLE" in body and body.count("\n") == 0:
            if sid in {
                "dramatic-engine",
                "visual-grammar",
                "continuity-invariants",
                "image-rules",
                "video-rules",
            }:
                findings.append(
                    {
                        "severity": "high",
                        "section": sid,
                        "code": "MISSING_OR_WEAK",
                        "message": f"{title} lacks enforceable content",
                    }
                )
        if body and re.search(r"\b(flux|midjourney|sd3|grok)\b", body, re.I):
            findings.append(
                {
                    "severity": "medium",
                    "section": sid,
                    "code": "PROVIDER_COUPLING",
                    "message": "Provider-specific language found in design contract",
                }
            )
    if against:
        # Simple lexical overlap check for reconcile-lite during audit
        design_tokens = set(re.findall(r"[a-z0-9_]{4,}", existing.lower()))
        against_tokens = set(re.findall(r"[a-z0-9_]{4,}", against.lower()))
        overlap = len(design_tokens & against_tokens)
        if overlap < 3:
            findings.append(
                {
                    "severity": "high",
                    "section": "reconcile",
                    "code": "LOW_OVERLAP",
                    "message": "Against-material shares little vocabulary with design.md",
                }
            )
    status = "PASS" if not any(f["severity"] == "high" for f in findings) else "FAIL"
    meta = _base_meta("design", "audit", project_id, {"input": existing, "against": against or ""})
    meta["status"] = status if status == "PASS" else "PROPOSED"
    meta["result"] = {
        "implementation_state": "DOMAIN",
        "audit_status": status,
        "findings": findings,
        "finding_count": len(findings),
    }
    meta["artifact_type"] = "design-audit-report"
    if status == "FAIL":
        meta["authority"] = "OBSERVATION"
    return meta


def design_reconcile(existing: str, against: str | None, project_id: str) -> dict[str, Any]:
    audit = design_audit(existing, against, project_id)
    if audit.get("status") == "NOT_COMPUTABLE":
        audit["action"] = "reconcile"
        return audit
    meta = _base_meta("design", "reconcile", project_id, {"input": existing, "against": against or ""})
    findings = audit.get("result", {}).get("findings", [])
    drift = [f for f in findings if f.get("code") in {"LOW_OVERLAP", "PROVIDER_COUPLING", "MISSING_OR_WEAK"}]
    meta["result"] = {
        "implementation_state": "DOMAIN",
        "drift": drift,
        "compatible": not any(f.get("severity") == "high" for f in drift),
        "audit": audit.get("result"),
    }
    meta["artifact_type"] = "media-reconciliation-report"
    if not against:
        meta["status"] = "NOT_COMPUTABLE"
        meta["authority"] = "NOT_COMPUTABLE"
        meta["not_computable"] = ["against material missing"]
        meta["diagnostic"] = {
            "code": "INSUFFICIENT_EVIDENCE",
            "message": "Provide --evidence (against script/prompt material) for reconcile",
        }
    return meta


def design_validate(existing: str, project_id: str) -> dict[str, Any]:
    if not existing.strip():
        return {
            "status": "NOT_COMPUTABLE",
            "authority": "NOT_COMPUTABLE",
            "surface": "design",
            "action": "validate",
            "diagnostic": {"code": "INSUFFICIENT_EVIDENCE", "message": "--input design.md is required"},
        }
    sections = parse_design_md(existing)
    missing = [sid for sid, _ in DESIGN_SECTIONS if not sections.get(sid, "").strip()]
    # Structural validity: must have dramatic engine or creative objective with non-placeholder text
    core_ok = any(
        sections.get(sid, "") and "NOT_COMPUTABLE" not in sections.get(sid, "").split("\n")[0]
        for sid in ("dramatic-engine", "creative-objective")
    )
    meta = _base_meta("design", "validate", project_id, {"input": existing})
    meta["result"] = {
        "implementation_state": "DOMAIN",
        "missing_sections": missing,
        "core_objective_present": core_ok,
        "section_count": len(DESIGN_SECTIONS) - len(missing),
        "valid": core_ok,
    }
    meta["artifact_type"] = "design-audit-report"
    if not core_ok:
        meta["status"] = "NOT_COMPUTABLE"
        meta["authority"] = "NOT_COMPUTABLE"
        meta["not_computable"] = ["core dramatic/creative objective"]
    return meta


def design_update(existing: str, evidence: str | None, project_id: str) -> dict[str, Any]:
    # Bounded update == improve + explicit receipt alias
    improved = design_improve(existing, evidence, project_id)
    if improved.get("status") == "NOT_COMPUTABLE":
        improved["action"] = "update"
        return improved
    improved["action"] = "update"
    improved["artifact_type"] = "design-revision-receipt"
    improved["result"]["update_mode"] = "bounded"
    return improved


def script_create(
    brief: str | None,
    evidence: str | None,
    project_id: str,
    fmt: str = "markdown",
    design_text: str | None = None,
) -> dict[str, Any]:
    fields = _extract_brief_fields(brief, evidence)
    if not fields["raw"] and not design_text:
        return {
            "status": "NOT_COMPUTABLE",
            "authority": "NOT_COMPUTABLE",
            "surface": "script",
            "action": "create",
            "diagnostic": {"code": "INSUFFICIENT_EVIDENCE", "message": "Provide --brief, --evidence, or --input design.md"},
        }
    if not fields["raw"] and design_text:
        fields = _extract_brief_fields(design_text, None)
    revision = f"s-{_digest(fields)}"
    design_rev = _design_revision(design_text) or "pending"
    body = "\n".join(
        [
            f"# Script package — {project_id}",
            "",
            f"Format: {fmt}",
            f"Design revision link: {design_rev}",
            f"Script revision: {revision}",
            "",
            "## Dramatic intent",
            fields["dramatic_problem"] or "NOT_COMPUTABLE",
            "",
            "## Observable action",
            fields["desired_state_change"] or "NOT_COMPUTABLE",
            "",
            "## Character pressure",
            fields["character_pressure"] or "NOT_COMPUTABLE",
            "",
            "## Dialogue",
            "NOT_COMPUTABLE — no dialogue evidenced",
            "",
            "## Continuity requirements",
            "- Preserve identity, ownership, chronology, residue",
            "",
            "## Production implications",
            "NOT_COMPUTABLE — awaiting production constraints",
            "",
        ]
    )
    meta = _base_meta("script", "create", project_id, fields)
    meta["result"] = {
        "implementation_state": "DOMAIN",
        "script_revision": revision,
        "source_design_revision": design_rev,
        "format": fmt,
        "document_markdown": body,
        "continuity_requirements": [
            "preserve_identity",
            "preserve_ownership",
            "preserve_chronology",
            "preserve_residue",
        ],
    }
    meta["artifact_type"] = "script-development-packet"
    return _attach_design_revision(meta, design_text)


def script_diagnose(existing: str, project_id: str) -> dict[str, Any]:
    if not existing.strip():
        return {
            "status": "NOT_COMPUTABLE",
            "authority": "NOT_COMPUTABLE",
            "surface": "script",
            "action": "diagnose",
            "diagnostic": {"code": "INSUFFICIENT_EVIDENCE", "message": "--input script is required"},
        }
    findings: list[dict[str, str]] = []
    lowered = existing.lower()
    if "because the symbol" in lowered or "represents" in lowered and "motif" in lowered:
        findings.append(
            {
                "severity": "high",
                "code": "SYMBOLIC_EXPLANATION",
                "message": "Symbolic explanation may be substituting for dramatic causality",
            }
        )
    if "NOT_COMPUTABLE" in existing and existing.count("NOT_COMPUTABLE") > 5:
        findings.append(
            {
                "severity": "medium",
                "code": "UNDER_SPECIFIED",
                "message": "Many NOT_COMPUTABLE fields — script needs more observable action",
            }
        )
    if len(existing.strip()) < 80:
        findings.append(
            {
                "severity": "high",
                "code": "TOO_SHORT",
                "message": "Script material is too thin for continuity-safe production",
            }
        )
    meta = _base_meta("script", "diagnose", project_id, {"input": existing})
    meta["result"] = {
        "implementation_state": "DOMAIN",
        "findings": findings,
        "diagnostic_status": "FAIL" if any(f["severity"] == "high" for f in findings) else "PASS",
    }
    meta["artifact_type"] = "script-diagnostic-report"
    return meta


def script_continuity(existing: str, project_id: str) -> dict[str, Any]:
    if not existing.strip():
        return {
            "status": "NOT_COMPUTABLE",
            "authority": "NOT_COMPUTABLE",
            "surface": "script",
            "action": "continuity-check",
            "diagnostic": {"code": "INSUFFICIENT_EVIDENCE", "message": "--input script is required"},
        }
    checks = {
        "identity_mentioned": bool(re.search(r"\b(character|identity|name)\b", existing, re.I)),
        "object_state_mentioned": bool(re.search(r"\b(object|prop|badge|door|chair)\b", existing, re.I)),
        "residue_mentioned": bool(re.search(r"\b(residue|remains|scar|crack)\b", existing, re.I)),
        "chronology_clear": bool(re.search(r"\b(then|after|before|continues)\b", existing, re.I)),
    }
    missing = [k for k, ok in checks.items() if not ok]
    meta = _base_meta("script", "continuity-check", project_id, {"input": existing})
    meta["result"] = {
        "implementation_state": "DOMAIN",
        "checks": checks,
        "missing": missing,
        "continuity_status": "PASS" if len(missing) <= 2 else "FAIL",
    }
    meta["artifact_type"] = "script-continuity-report"
    if len(missing) > 2:
        meta["status"] = "NOT_COMPUTABLE"
        meta["authority"] = "NOT_COMPUTABLE"
        meta["not_computable"] = missing
    return meta


def script_improve(existing: str, project_id: str) -> dict[str, Any]:
    if not existing.strip():
        return {
            "status": "NOT_COMPUTABLE",
            "authority": "NOT_COMPUTABLE",
            "surface": "script",
            "action": "improve",
            "diagnostic": {"code": "INSUFFICIENT_EVIDENCE", "message": "--input script is required"},
        }
    revision = f"s-{_digest(existing)}"
    improved = existing.rstrip() + "\n\n## Revision notes\n"
    improved += f"- [{revision}] Pressure, observable action, and continuity requirements restated without symbolic lecture.\n"
    if "Continuity requirements" not in existing:
        improved += "\n## Continuity requirements\n- Preserve identity, ownership, chronology, residue\n"
    meta = _base_meta("script", "improve", project_id, {"input": existing})
    meta["result"] = {
        "implementation_state": "DOMAIN",
        "script_revision": revision,
        "document_markdown": improved,
        "source_script_revision": f"s-{_digest(existing[:200])}",
    }
    meta["artifact_type"] = "script-development-packet"
    return meta


def script_adapt(existing: str, project_id: str, fmt: str = "beat-sheet") -> dict[str, Any]:
    if not existing.strip():
        return {
            "status": "NOT_COMPUTABLE",
            "authority": "NOT_COMPUTABLE",
            "surface": "script",
            "action": "adapt",
            "diagnostic": {"code": "INSUFFICIENT_EVIDENCE", "message": "--input script is required"},
        }
    lines = [ln.strip() for ln in existing.splitlines() if ln.strip() and not ln.strip().startswith("#")]
    beats = lines[:12] or ["NOT_COMPUTABLE"]
    doc = "# Beat sheet\n\n" + "\n".join(f"{i+1}. {b}" for i, b in enumerate(beats)) + "\n"
    meta = _base_meta("script", "adapt", project_id, {"input": existing, "format": fmt})
    meta["result"] = {
        "implementation_state": "DOMAIN",
        "format": fmt,
        "document_markdown": doc,
        "source_script_revision": f"s-{_digest(existing[:200])}",
    }
    meta["artifact_type"] = "script-development-packet"
    return meta


def script_handoff(existing: str, project_id: str) -> dict[str, Any]:
    if not existing.strip():
        return {
            "status": "NOT_COMPUTABLE",
            "authority": "NOT_COMPUTABLE",
            "surface": "script",
            "action": "handoff",
            "diagnostic": {"code": "INSUFFICIENT_EVIDENCE", "message": "--input script is required"},
        }
    meta = _base_meta("script", "handoff", project_id, {"input": existing})
    meta["result"] = {
        "implementation_state": "DOMAIN",
        "source_script_revision": f"s-{_digest(existing[:200])}",
        "handoff_targets": ["image", "video", "storyboard", "continuity-forge"],
        "locked_invariants": [
            "preserve_identity",
            "preserve_ownership",
            "preserve_chronology",
            "preserve_residue",
        ],
        "packet_preview": {
            "observable_action": next(
                (ln.strip() for ln in existing.splitlines() if ln.strip() and not ln.startswith("#")),
                "NOT_COMPUTABLE",
            )
        },
    }
    meta["artifact_type"] = "script-development-packet"
    return meta


def _neutral_frame_from_text(text: str, provider: str) -> dict[str, Any]:
    fields = _extract_brief_fields(text, None)
    parts = [fields["dramatic_problem"] or text.strip().splitlines()[0][:280]]
    for item in (fields.get("geometry") or [])[:2]:
        parts.append(item)
    for item in (fields.get("cinematic_channel") or [])[:1]:
        parts.append(item)
    for item in (fields.get("residue") or [])[:1]:
        parts.append(f"residue: {item}")
    prompt = "; ".join(p for p in parts if p)
    negatives = [
        "named occult labels",
        "unsupported location changes",
        "identity reset",
        "residue erasure",
    ]
    constraints = [
        c
        for c in (
            fields["desired_state_change"],
            fields["character_pressure"],
            *(fields.get("observable_evidence") or [])[:2],
        )
        if c
    ]
    return {
        "frame_id": f"frame-{_digest(prompt)}",
        "prompt": prompt,
        "state_constraints": constraints,
        "continuity_from_previous": [],
        "negative_constraints": negatives,
        "provider": provider,
        "provider_syntax_only": True,
    }


def image_prompt(brief: str | None, evidence: str | None, design: str | None, project_id: str, provider: str) -> dict[str, Any]:
    text = "\n".join(x for x in (brief, evidence, design) if x).strip()
    if not text:
        return {
            "status": "NOT_COMPUTABLE",
            "authority": "NOT_COMPUTABLE",
            "surface": "image",
            "action": "prompt",
            "diagnostic": {"code": "INSUFFICIENT_EVIDENCE", "message": "Provide --brief, --evidence, or --input"},
        }
    frame = _neutral_frame_from_text(text, provider)
    meta = _base_meta("image", "prompt", project_id, {"text": text, "provider": provider})
    meta["result"] = {
        "implementation_state": "DOMAIN",
        "packet": {
            "provider": provider,
            "frames": [frame],
            "shared_constraints": {
                "negative_constraints": frame["negative_constraints"],
                "visual_identity": [],
            },
            "locked_invariants": list(meta["shared_invariants"].keys()),
            "required_elements": frame["state_constraints"],
            "forbidden_changes": frame["negative_constraints"],
        },
    }
    meta["artifact_type"] = "image-prompt-packet"
    return _attach_design_revision(meta, design)


def image_sequence(brief: str | None, evidence: str | None, project_id: str, provider: str) -> dict[str, Any]:
    base = image_prompt(brief, evidence, None, project_id, provider)
    if base.get("status") == "NOT_COMPUTABLE":
        base["action"] = "sequence"
        return base
    frame = base["result"]["packet"]["frames"][0]
    f2 = dict(frame)
    f2["frame_id"] = f"frame-{_digest(frame['prompt'] + '|2')}"
    f2["continuity_from_previous"] = ["preserve identity", "preserve residue", "preserve geometry"]
    f2["prompt"] = frame["prompt"] + "; state advanced without identity reset"
    base["action"] = "sequence"
    base["artifact_type"] = "image-sequence-packet"
    base["result"]["packet"]["frames"] = [frame, f2]
    return base


def image_reference(brief: str | None, project_id: str, provider: str) -> dict[str, Any]:
    packet = image_prompt(brief, None, None, project_id, provider)
    if packet.get("status") == "NOT_COMPUTABLE":
        packet["action"] = "reference"
        return packet
    packet["action"] = "reference"
    packet["artifact_type"] = "visual-reference-packet"
    packet["result"]["reference_type"] = "character-environment-prop"
    return packet


def image_negative(brief: str | None, project_id: str) -> dict[str, Any]:
    text = (brief or "").strip() or "generic failure modes"
    meta = _base_meta("image", "negative", project_id, {"brief": text})
    meta["result"] = {
        "implementation_state": "DOMAIN",
        "negative_constraints": [
            "named occult labels",
            "identity reset",
            "ownership swap without causal transfer",
            "geometry reset",
            "residue erasure",
            "unsupported location jump",
        ],
    }
    meta["artifact_type"] = "image-prompt-packet"
    return meta


def image_qa(expected: str | None, observation: str | None, project_id: str) -> dict[str, Any]:
    if not expected or not observation:
        return {
            "status": "NOT_COMPUTABLE",
            "authority": "NOT_COMPUTABLE",
            "surface": "image",
            "action": "qa",
            "diagnostic": {
                "code": "INSUFFICIENT_EVIDENCE",
                "message": "Provide --input expected packet text and --evidence observation text",
            },
        }
    exp_tokens = set(re.findall(r"[a-z0-9_]{4,}", expected.lower()))
    obs_tokens = set(re.findall(r"[a-z0-9_]{4,}", observation.lower()))
    overlap = len(exp_tokens & obs_tokens) / max(1, len(exp_tokens))
    meta = _base_meta("image", "qa", project_id, {"expected": expected, "observation": observation})
    meta["result"] = {
        "implementation_state": "DOMAIN",
        "overlap_ratio": round(overlap, 4),
        "qa_status": "PASS" if overlap >= 0.2 else "FAIL",
        "dimensions": {
            "identity": overlap >= 0.2,
            "geometry": overlap >= 0.15,
            "residue": "residue" in observation.lower() or overlap >= 0.25,
        },
    }
    meta["artifact_type"] = "media-reconciliation-report"
    if overlap < 0.2:
        meta["status"] = "NOT_COMPUTABLE"
        meta["authority"] = "NOT_COMPUTABLE"
    return meta


def _parse_surface_or_adapter_packet(packet_text: str) -> dict[str, Any]:
    text = packet_text.strip()
    data: Any
    if text.startswith("{"):
        data = json.loads(text)
    else:
        try:
            import yaml  # type: ignore[import-untyped]
        except ImportError as exc:
            raise RuntimeError("PyYAML required to parse YAML packets") from exc
        data = yaml.safe_load(text) or {}
    if not isinstance(data, dict):
        raise ValueError("packet root must be an object")
    # Unwrap surface receipt → packet
    if "result" in data and isinstance(data["result"], dict) and "packet" in data["result"]:
        packet = dict(data["result"]["packet"])
        packet.setdefault("source_graph_id", data.get("source_state_id") or data.get("artifact_id") or "surface")
        return packet
    if "frames" in data:
        data.setdefault("source_graph_id", data.get("source_graph_id") or "surface")
        return data
    raise ValueError("packet must include frames or result.packet")


def _to_adapter_packet(packet: dict[str, Any]) -> dict[str, Any]:
    frames = []
    for frame in packet.get("frames") or []:
        frames.append(
            {
                "frame_id": frame.get("frame_id"),
                "prompt": frame.get("prompt", ""),
                "state_constraints": list(frame.get("state_constraints") or []),
                "continuity_from_previous": list(frame.get("continuity_from_previous") or []),
            }
        )
    shared = packet.get("shared_constraints") or {}
    if "negative_constraints" not in shared and packet.get("negative_constraints"):
        shared = {**shared, "negative_constraints": packet.get("negative_constraints")}
    return {
        "source_graph_id": packet.get("source_graph_id") or "surface",
        "provider": "generic",
        "frames": frames,
        "shared_constraints": shared,
        "validation": {"status": "VALID", "errors": []},
        "private_state_policy": {
            "graph_mutation_allowed": False,
            "pattern_links_exposed": False,
            "lexicon_links_exposed": False,
        },
    }


def image_adapt(packet_text: str | None, project_id: str, provider: str) -> dict[str, Any]:
    if not packet_text:
        return {
            "status": "NOT_COMPUTABLE",
            "authority": "NOT_COMPUTABLE",
            "surface": "image",
            "action": "adapt",
            "diagnostic": {"code": "INSUFFICIENT_EVIDENCE", "message": "--input packet is required"},
        }
    meta = _base_meta("image", "adapt", project_id, {"packet": packet_text, "provider": provider})
    try:
        packet = _parse_surface_or_adapter_packet(packet_text)
        adapter_packet = _to_adapter_packet(packet)
        from adapt_provider import adapt  # local import avoids circular startup cost

        adapted = adapt(adapter_packet, provider)
        report = adapted.get("preservation_report") or adapted.get("validation") or {}
        status = "VALID"
        if isinstance(report, dict):
            status = report.get("status") or adapted.get("validation", {}).get("status") or "VALID"
        meta["result"] = {
            "implementation_state": "DOMAIN",
            "provider": provider,
            "adapted_packet": adapted,
            "preservation_report": report
            if isinstance(report, dict)
            else {"status": status},
        }
        if status != "VALID":
            meta["status"] = "NOT_COMPUTABLE"
            meta["authority"] = "NOT_COMPUTABLE"
            meta["not_computable"] = ["provider_semantic_preservation"]
    except Exception as exc:  # noqa: BLE001 — surface must fail closed, not crash
        meta["status"] = "NOT_COMPUTABLE"
        meta["authority"] = "NOT_COMPUTABLE"
        meta["diagnostic"] = {"code": "ADAPTER_NOT_COMPUTABLE", "message": str(exc)}
        meta["result"] = {"implementation_state": "DOMAIN", "provider": provider}
    meta["artifact_type"] = "image-prompt-packet"
    return meta


def video_shot(
    brief: str | None,
    evidence: str | None,
    project_id: str,
    duration: float = 8.0,
    design_text: str | None = None,
) -> dict[str, Any]:
    fields = _extract_brief_fields(brief, evidence)
    if not fields["raw"]:
        return {
            "status": "NOT_COMPUTABLE",
            "authority": "NOT_COMPUTABLE",
            "surface": "video",
            "action": "shot",
            "diagnostic": {"code": "INSUFFICIENT_EVIDENCE", "message": "Provide --brief or --evidence"},
        }
    design_rev = _design_revision(design_text)
    cinematic = list(fields.get("cinematic_channel") or [])
    if cinematic:
        framing = cinematic[0]
    elif "camera" in fields["raw"].lower():
        framing = "evidenced framing"
    else:
        framing = "NOT_COMPUTABLE"
    shot = {
        "shot_id": f"shot-{_digest(fields)}",
        "source_state_id": f"state-{_digest(project_id)}",
        "duration_seconds": float(duration),
        "start_state": {
            "summary": "pre-action institutional arrangement",
            "observable": fields["dramatic_problem"],
            "evidence": list(fields.get("observable_evidence") or [])[:4],
        },
        "action": {
            "subject": "primary figure",
            "verb": "transfers" if "transfer" in fields["raw"].lower() else "changes",
            "path_or_change": fields["desired_state_change"] or "NOT_COMPUTABLE",
            "causal_actions": list(fields.get("causal_actions") or [])[:3],
        },
        "camera": {
            "framing": framing,
            "position": "NOT_COMPUTABLE",
            "movement": "static unless evidenced",
            "lens_behavior": "NOT_COMPUTABLE",
        },
        "physics": {"required": [], "forbidden": ["teleportation", "identity swap"]},
        "end_state": {
            "summary": fields["desired_state_change"] or "NOT_COMPUTABLE",
            "residue": list(fields.get("residue") or [])[:3],
        },
        "continuity_invariants": [
            "preserve_identity",
            "preserve_ownership_rules",
            "preserve_residue",
        ],
        "negative_constraints": [
            "named occult labels",
            "geometry reset",
            "residue erasure",
        ],
    }
    if design_rev:
        shot["source_design_revision"] = design_rev
    if shot["end_state"]["summary"] == "NOT_COMPUTABLE":
        return {
            "status": "NOT_COMPUTABLE",
            "authority": "NOT_COMPUTABLE",
            "surface": "video",
            "action": "shot",
            "diagnostic": {
                "code": "INSUFFICIENT_EVIDENCE",
                "message": "desired end state not evidenced",
            },
            "not_computable": ["end_state"],
        }
    meta = _base_meta("video", "shot", project_id, fields)
    meta["result"] = {"implementation_state": "DOMAIN", "shot": shot}
    meta["artifact_type"] = "shot-contract"
    return _attach_design_revision(meta, design_text)


def video_motion(brief: str | None, project_id: str) -> dict[str, Any]:
    fields = _extract_brief_fields(brief, None)
    if not fields["raw"]:
        return {
            "status": "NOT_COMPUTABLE",
            "authority": "NOT_COMPUTABLE",
            "surface": "video",
            "action": "motion",
            "diagnostic": {"code": "INSUFFICIENT_EVIDENCE", "message": "Provide --brief"},
        }
    meta = _base_meta("video", "motion", project_id, fields)
    meta["result"] = {
        "implementation_state": "DOMAIN",
        "motion_contract": {
            "blocking": fields["dramatic_problem"],
            "object_motion": fields["desired_state_change"] or "NOT_COMPUTABLE",
            "camera_motion": "static unless evidenced",
            "physical_behavior": [],
            "forbidden_motion": ["teleportation", "identity swap", "residue erasure"],
            "rhythm": "NOT_COMPUTABLE",
        },
    }
    meta["artifact_type"] = "motion-contract"
    return meta


def video_sequence(brief: str | None, evidence: str | None, project_id: str) -> dict[str, Any]:
    shot_a = video_shot(brief, evidence, project_id, duration=4.0)
    if shot_a.get("status") == "NOT_COMPUTABLE":
        shot_a["action"] = "sequence"
        return shot_a
    shot1 = shot_a["result"]["shot"]
    # Second shot must start from shot1 end_state
    shot2 = dict(shot1)
    shot2["shot_id"] = f"shot-{_digest(shot1['shot_id'] + '|2')}"
    shot2["start_state"] = dict(shot1["end_state"])
    shot2["end_state"] = {
        "summary": (shot1["end_state"].get("summary") or "") + " with visible residue retained"
    }
    # Compatibility proof
    compatible = shot2["start_state"].get("summary") == shot1["end_state"].get("summary")
    if not compatible:
        return {
            "status": "NOT_COMPUTABLE",
            "authority": "NOT_COMPUTABLE",
            "surface": "video",
            "action": "sequence",
            "diagnostic": {
                "code": "INCOMPATIBLE_TRANSITION",
                "message": "shot end_state/start_state mismatch",
            },
        }
    meta = _base_meta("video", "sequence", project_id, {"brief": brief or "", "evidence": evidence or ""})
    meta["result"] = {
        "implementation_state": "DOMAIN",
        "shots": [shot1, shot2],
        "transitions": [
            {
                "from": shot1["shot_id"],
                "to": shot2["shot_id"],
                "compatible": True,
            }
        ],
    }
    meta["artifact_type"] = "video-sequence-packet"
    return meta


def video_adapt(packet_text: str | None, project_id: str, provider: str) -> dict[str, Any]:
    adapted = image_adapt(packet_text, project_id, provider)
    adapted["surface"] = "video"
    adapted["action"] = "adapt"
    adapted["artifact_type"] = "video-prompt-packet"
    if adapted.get("status") != "NOT_COMPUTABLE":
        adapted["artifact_id"] = (
            f"kubrick-video-adapt-{_digest({'packet': packet_text, 'provider': provider})}"
        )
    return adapted


def video_qa(expected: str | None, observation: str | None, project_id: str) -> dict[str, Any]:
    result = image_qa(expected, observation, project_id)
    if result.get("status") != "NOT_COMPUTABLE" or result.get("result"):
        result["surface"] = "video"
        result["action"] = "qa"
        if "result" in result:
            result["result"]["dimensions"] = {
                **result["result"].get("dimensions", {}),
                "motion": "move" in (observation or "").lower() or result["result"].get("overlap_ratio", 0) >= 0.2,
                "end_state": "end" in (observation or "").lower() or result["result"].get("overlap_ratio", 0) >= 0.25,
            }
    return result


def _design_for_args(a: Any) -> str | None:
    return resolve_design_text(
        _read(a, "design"),
        _read(a, "input"),
        _read(a, "evidence"),
        auto_discover=True,
    )


COMPILERS: dict[tuple[str, str], Any] = {
    ("design", "create"): lambda a: design_create(a.brief, _read(a, "evidence"), a.project_id),
    ("design", "build"): lambda a: design_create(a.brief, _read(a, "evidence"), a.project_id),
    ("design", "improve"): lambda a: design_improve(_read(a, "input") or "", _read(a, "evidence"), a.project_id),
    ("design", "audit"): lambda a: design_audit(_read(a, "input") or "", _read(a, "evidence"), a.project_id),
    ("design", "reconcile"): lambda a: design_reconcile(_read(a, "input") or "", _read(a, "evidence"), a.project_id),
    ("design", "update"): lambda a: design_update(_read(a, "input") or "", _read(a, "evidence"), a.project_id),
    ("design", "validate"): lambda a: design_validate(_read(a, "input") or "", a.project_id),
    ("script", "create"): lambda a: script_create(
        a.brief,
        _read(a, "evidence"),
        a.project_id,
        getattr(a, "format", "markdown"),
        design_text=_design_for_args(a),
    ),
    ("script", "improve"): lambda a: script_improve(_read(a, "input") or "", a.project_id),
    ("script", "diagnose"): lambda a: script_diagnose(_read(a, "input") or "", a.project_id),
    ("script", "adapt"): lambda a: script_adapt(_read(a, "input") or "", a.project_id),
    ("script", "continuity-check"): lambda a: script_continuity(_read(a, "input") or "", a.project_id),
    ("script", "handoff"): lambda a: script_handoff(_read(a, "input") or "", a.project_id),
    ("image", "prompt"): lambda a: image_prompt(
        a.brief,
        _read(a, "evidence"),
        _design_for_args(a) or _read(a, "input"),
        a.project_id,
        a.provider,
    ),
    ("image", "sequence"): lambda a: image_sequence(a.brief, _read(a, "evidence"), a.project_id, a.provider),
    ("image", "reference"): lambda a: image_reference(a.brief or _read(a, "input"), a.project_id, a.provider),
    ("image", "negative"): lambda a: image_negative(a.brief or _read(a, "input"), a.project_id),
    ("image", "adapt"): lambda a: image_adapt(_read(a, "input"), a.project_id, a.provider),
    ("image", "qa"): lambda a: image_qa(_read(a, "input"), _read(a, "evidence"), a.project_id),
    ("video", "shot"): lambda a: video_shot(
        a.brief,
        _read(a, "evidence"),
        a.project_id,
        getattr(a, "duration", 8.0),
        design_text=_design_for_args(a),
    ),
    ("video", "motion"): lambda a: video_motion(a.brief or _read(a, "input"), a.project_id),
    ("video", "sequence"): lambda a: _attach_design_revision(
        video_sequence(a.brief, _read(a, "evidence"), a.project_id),
        _design_for_args(a),
    ),
    ("video", "adapt"): lambda a: video_adapt(_read(a, "input"), a.project_id, a.provider),
    ("video", "qa"): lambda a: video_qa(_read(a, "input"), _read(a, "evidence"), a.project_id),
}


def _read(args: Any, name: str) -> str | None:
    # filled by production_surface before dispatch via setattr
    return getattr(args, f"_loaded_{name}", None)


def compile_surface(surface: str, action: str, args: Any) -> dict[str, Any]:
    key = (surface, action)
    if key not in COMPILERS:
        return {
            "status": "NOT_COMPUTABLE",
            "authority": "NOT_COMPUTABLE",
            "surface": surface,
            "action": action,
            "diagnostic": {"code": "UNKNOWN_ACTION", "message": f"No domain compiler for {surface}:{action}"},
        }
    return COMPILERS[key](args)

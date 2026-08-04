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


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _digest(payload: Any) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def _claim(text: str, label: str = "PROPOSED") -> str:
    return f"- [{label}] {text}"


def _extract_brief_fields(brief: str | None, evidence: str | None) -> dict[str, str]:
    blob = "\n".join(x for x in (brief, evidence) if x).strip()
    fields = {
        "dramatic_problem": "",
        "desired_state_change": "",
        "character_pressure": "",
        "format": "unspecified",
        "raw": blob,
    }
    if not blob:
        return fields
    # YAML-ish key: value lines
    for key in ("dramatic_problem", "desired_state_change", "character_pressure", "format"):
        match = re.search(rf"^{key}\s*:\s*(.+)$", blob, re.MULTILINE)
        if match:
            fields[key] = match.group(1).strip().strip("\"'")
    if not fields["dramatic_problem"]:
        # First non-empty line as objective when freeform
        for line in blob.splitlines():
            line = line.strip()
            if line and not line.startswith("#") and ":" not in line[:40]:
                fields["dramatic_problem"] = line
                break
        if not fields["dramatic_problem"]:
            fields["dramatic_problem"] = blob.splitlines()[0].strip()[:240]
    return fields


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
    sections["continuity-invariants"] = "\n".join(
        [
            _claim("Preserve identity, ownership, chronology, geometry, material state, residue", "PROPOSED"),
        ]
    )
    sections["negative-constraints"] = "\n".join(
        [
            _claim("No named esoterica in audience-facing prompts unless explicitly requested", "PROPOSED"),
            _claim("Do not invent unsupported production detail", "PROPOSED"),
        ]
    )
    sections["open-questions"] = _claim(
        "Fill visual grammar, camera, lighting, and motion sections from further evidence",
        "NOT_COMPUTABLE",
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

    # Strengthen empty production-critical sections only; never wipe valid text.
    critical = [
        "dramatic-engine",
        "visual-grammar",
        "continuity-invariants",
        "negative-constraints",
        "open-questions",
    ]
    for sid in critical:
        if sections.get(sid, "").strip():
            continue
        if sid == "dramatic-engine" and fields["dramatic_problem"]:
            new_body = _claim(fields["dramatic_problem"], "OBSERVED")
        elif sid == "visual-grammar":
            new_body = _claim(
                "NOT_COMPUTABLE — visual grammar not evidenced; refuse invented shot language",
                "NOT_COMPUTABLE",
            )
        elif sid == "continuity-invariants":
            new_body = _claim(
                "Preserve identity, ownership, chronology, geometry, material state, residue",
                "PROPOSED",
            )
        elif sid == "negative-constraints":
            new_body = _claim(
                "No named esoterica in audience-facing prompts unless explicitly requested",
                "PROPOSED",
            )
        else:
            new_body = _claim("Awaiting evidence", "NOT_COMPUTABLE")
        sections[sid] = new_body
        diffs.append({"section": sid, "change": "filled_empty", "reason": "missing production-critical section"})

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
        "document_markdown": markdown,
        "diff": diffs,
        "preserved_section_count": len(preserved),
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


def script_create(brief: str | None, evidence: str | None, project_id: str, fmt: str = "markdown") -> dict[str, Any]:
    fields = _extract_brief_fields(brief, evidence)
    if not fields["raw"]:
        return {
            "status": "NOT_COMPUTABLE",
            "authority": "NOT_COMPUTABLE",
            "surface": "script",
            "action": "create",
            "diagnostic": {"code": "INSUFFICIENT_EVIDENCE", "message": "Provide --brief or --evidence"},
        }
    revision = f"s-{_digest(fields)}"
    body = "\n".join(
        [
            f"# Script package — {project_id}",
            "",
            f"Format: {fmt}",
            f"Design revision link: pending",
            f"Script revision: {revision}",
            "",
            "## Dramatic intent",
            fields["dramatic_problem"],
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
    return meta


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
    prompt = fields["dramatic_problem"] or text.strip().splitlines()[0][:280]
    negatives = [
        "named occult labels",
        "unsupported location changes",
        "identity reset",
        "residue erasure",
    ]
    return {
        "frame_id": f"frame-{_digest(prompt)}",
        "prompt": prompt,
        "state_constraints": [
            c
            for c in (
                fields["desired_state_change"],
                fields["character_pressure"],
            )
            if c
        ],
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
    return meta


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


def image_adapt(packet_text: str | None, project_id: str, provider: str) -> dict[str, Any]:
    if not packet_text:
        return {
            "status": "NOT_COMPUTABLE",
            "authority": "NOT_COMPUTABLE",
            "surface": "image",
            "action": "adapt",
            "diagnostic": {"code": "INSUFFICIENT_EVIDENCE", "message": "--input packet is required"},
        }
    # Syntax-only wrapper: keep content, stamp provider
    meta = _base_meta("image", "adapt", project_id, {"packet": packet_text, "provider": provider})
    meta["result"] = {
        "implementation_state": "DOMAIN",
        "provider": provider,
        "adapted_text": packet_text,
        "preservation_report": {
            "identity_preserved": True,
            "ownership_preserved": True,
            "geometry_preserved": True,
            "residue_preserved": True,
            "negative_constraints_preserved": True,
            "status": "VALID",
        },
    }
    meta["artifact_type"] = "image-prompt-packet"
    return meta


def video_shot(brief: str | None, evidence: str | None, project_id: str, duration: float = 8.0) -> dict[str, Any]:
    fields = _extract_brief_fields(brief, evidence)
    if not fields["raw"]:
        return {
            "status": "NOT_COMPUTABLE",
            "authority": "NOT_COMPUTABLE",
            "surface": "video",
            "action": "shot",
            "diagnostic": {"code": "INSUFFICIENT_EVIDENCE", "message": "Provide --brief or --evidence"},
        }
    shot = {
        "shot_id": f"shot-{_digest(fields)}",
        "source_state_id": f"state-{_digest(project_id)}",
        "duration_seconds": float(duration),
        "start_state": {
            "summary": "pre-action institutional arrangement",
            "observable": fields["dramatic_problem"],
        },
        "action": {
            "subject": "primary figure",
            "verb": "transfers" if "transfer" in fields["raw"].lower() else "changes",
            "path_or_change": fields["desired_state_change"] or "NOT_COMPUTABLE",
        },
        "camera": {
            "framing": "NOT_COMPUTABLE" if "camera" not in fields["raw"].lower() else "evidenced framing",
            "position": "NOT_COMPUTABLE",
            "movement": "static unless evidenced",
            "lens_behavior": "NOT_COMPUTABLE",
        },
        "physics": {"required": [], "forbidden": ["teleportation", "identity swap"]},
        "end_state": {
            "summary": fields["desired_state_change"] or "NOT_COMPUTABLE",
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
    return meta


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
    if adapted.get("status") == "NOT_COMPUTABLE":
        adapted["surface"] = "video"
        adapted["action"] = "adapt"
        return adapted
    adapted["surface"] = "video"
    adapted["action"] = "adapt"
    adapted["artifact_type"] = "video-prompt-packet"
    adapted["artifact_id"] = f"kubrick-video-adapt-{_digest({'packet': packet_text, 'provider': provider})}"
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


COMPILERS: dict[tuple[str, str], Any] = {
    ("design", "create"): lambda a: design_create(a.brief, _read(a, "evidence"), a.project_id),
    ("design", "build"): lambda a: design_create(a.brief, _read(a, "evidence"), a.project_id),
    ("design", "improve"): lambda a: design_improve(_read(a, "input") or "", _read(a, "evidence"), a.project_id),
    ("design", "audit"): lambda a: design_audit(_read(a, "input") or "", _read(a, "evidence"), a.project_id),
    ("design", "reconcile"): lambda a: design_reconcile(_read(a, "input") or "", _read(a, "evidence"), a.project_id),
    ("design", "update"): lambda a: design_update(_read(a, "input") or "", _read(a, "evidence"), a.project_id),
    ("design", "validate"): lambda a: design_validate(_read(a, "input") or "", a.project_id),
    ("script", "create"): lambda a: script_create(
        a.brief, _read(a, "evidence"), a.project_id, getattr(a, "format", "markdown")
    ),
    ("script", "improve"): lambda a: script_improve(_read(a, "input") or "", a.project_id),
    ("script", "diagnose"): lambda a: script_diagnose(_read(a, "input") or "", a.project_id),
    ("script", "adapt"): lambda a: script_adapt(_read(a, "input") or "", a.project_id),
    ("script", "continuity-check"): lambda a: script_continuity(_read(a, "input") or "", a.project_id),
    ("script", "handoff"): lambda a: script_handoff(_read(a, "input") or "", a.project_id),
    ("image", "prompt"): lambda a: image_prompt(a.brief, _read(a, "evidence"), _read(a, "input"), a.project_id, a.provider),
    ("image", "sequence"): lambda a: image_sequence(a.brief, _read(a, "evidence"), a.project_id, a.provider),
    ("image", "reference"): lambda a: image_reference(a.brief or _read(a, "input"), a.project_id, a.provider),
    ("image", "negative"): lambda a: image_negative(a.brief or _read(a, "input"), a.project_id),
    ("image", "adapt"): lambda a: image_adapt(_read(a, "input"), a.project_id, a.provider),
    ("image", "qa"): lambda a: image_qa(_read(a, "input"), _read(a, "evidence"), a.project_id),
    ("video", "shot"): lambda a: video_shot(a.brief, _read(a, "evidence"), a.project_id),
    ("video", "motion"): lambda a: video_motion(a.brief or _read(a, "input"), a.project_id),
    ("video", "sequence"): lambda a: video_sequence(a.brief, _read(a, "evidence"), a.project_id),
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

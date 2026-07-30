# Kubrick v0.13 Status and Continuation Roadmap

## Current state

**v0.13.0 is shipped on `main`.**

Kubrick closes Wave 2 and Wave 3 from the production-hardening roadmap:

- Forge multi-signal feedback
- First-class project ledgers
- Multi-provider adapters (Grok Imagine, Flux, SD3, Midjourney)
- Closed-loop visual QA with differential fidelity
- Optional MCP/CLI operators
- Time-sensitive contemporary cultural-signal packs

Also on `main` (adjacent capability): deterministic **design specification compiler** (`design-build`).

| Tracking | Status |
|---|---|
| Issue [#3](https://github.com/scrimshawlife-ctrl/Kubrick/issues/3) Wave 2 | **Closed** |
| Issue [#4](https://github.com/scrimshawlife-ctrl/Kubrick/issues/4) Wave 3 | **Closed** |
| [PR #24](https://github.com/scrimshawlife-ctrl/Kubrick/pull/24) | **Merged** |
| CI Hermes Skill Evals | Green on merge |

## Completed in 0.13

### Wave 2 — Forge feedback and evolution

- Forge signal extraction from ledger diffs, revisions, saturation, collisions, ingestion, and payoff records (`forge-signals`).
- Multi-signal evolution receipts: mutation success, production feasibility, anti-slop, cultural-boundary, and payoff signals.
- Human review gates for large confidence changes and structural/lifecycle mutations.
- Retirement and deprecation proposals without automatic corpus mutation.
- Project symbolic ledgers as persistent retrieval/evolution inputs with pattern history, rehydrate, and apply-forge.

### Wave 3 — Adapters, QA, operators

- Syntax-only adapters for Grok Imagine, Flux, SD3, and Midjourney over a shared latent graph.
- Closed-loop visual QA with separate geometry, state, residue, and convergence fidelity scores.
- CLI operators: saturation, counterpoint, convergence locking, surface-occult audit, motif mutation, symbolic-architecture export.
- Optional stdio MCP server wrapping the same CLI (never authoritative).
- Time-sensitive contemporary cultural-signal packs with explicit provenance.

### Adjacent

- Deterministic design specification compiler (`design-build`) with schema validation and fail-closed authority rules.

## Invariants (unchanged)

- Weak evidence returns `NOT_COMPUTABLE`.
- Audience output exposes observables, not private symbolic semantics.
- Local artifacts remain `PROPOSED` / `OBSERVATION` / `PROPOSAL`.
- Evolution proposals never apply automatically.
- Continuity Forge remains canonical authority when connected.
- External providers, MCP, and Forge remain optional.

## Operator surface (authoritative list)

See root `README.md` and `QUICKSTART.md`. Summary:

```text
compile · retrieve · ledger · design-build
adapter-build · adapt-grok · adapt-flux · adapt-sd3 · adapt-midjourney · adapt-provider
closed-loop-qa · forge-signals · evolution-propose · outcome-record
operator · mcp-server
validate-skill · validate-corpus · coverage · eval · repeatability
```

## Next priorities

1. Optional vision-provider normalizers beyond generic JSON and Grok Vision.
2. Video adapters as syntax-only translations over the neutral packet.
3. Privacy-preserving cross-project analytics from **approved** outcome receipts only.
4. Expand executable corpus only with provenance, misuse risks, mutation requirements, production-cost analysis, and regression coverage.
5. Optional Node 24-ready GitHub Actions base images when deprecation pressure requires it.

## Docs map

| Doc | Role |
|---|---|
| `docs/README.md` | Documentation index |
| `docs/RELEASE-NOTES-v0.13.md` | What shipped |
| `docs/RELEASE-CHECKLIST-v0.13.md` | Tag / publish gates |
| `docs/ROADMAP-v0.12.md` | Prior release context |
| `docs/ROADMAP-v0.11.md` | Original Wave 1–3 plan |

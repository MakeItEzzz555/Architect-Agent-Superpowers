# Gridline community progress ledger

Snapshot: **2026-10-23**. Source: public `main` at **`62a7ea4b5dfb36d12bd4ca1ea64de7b123aae29c`**. This ledger explains which parts of each issue have shipped and which acceptance criteria remain unmet. It is **not** a promise of live app integration or architectural certification.

## Shipped foundations (merged)

| Milestone | Evidence | What actually exists |
| --- | --- | --- |
| AEC skills, agent specialization and provider guidance | [PR #3](https://github.com/MakeItEzzz555/Gridline/pull/3) | 30 portable skills, specialist agent descriptions, lifecycle templates, route/activation fixtures, conceptual six-primitive JSON→SVG/DXF engine |
| Packaging / install safeguards | [PR #4](https://github.com/MakeItEzzz555/Gridline/pull/4), [PR #5](https://github.com/MakeItEzzz555/Gridline/pull/5) | Bundled drawing scripts, installed-path tests, ownership-aware replacement, rollback/backup safeguards |
| Specification-derived plan-sheet generation | [PR #6](https://github.com/MakeItEzzz555/Gridline/pull/6) | Structured building JSON→layered DXF, paper-space layouts, title blocks, optional vector PDF and room/door/window/sheet CSVs. Checking covers a *subset* of drafting/tag/schedule invariants, **not** independent full geometry verification |
| Gridline brand migration | [PR #7](https://github.com/MakeItEzzz555/Gridline/pull/7), [PR #8](https://github.com/MakeItEzzz555/Gridline/pull/8) | Public repo branding, logo and installer/plugin naming |
| Partial revision review and local MCP | [PR #9](https://github.com/MakeItEzzz555/Gridline/pull/9) | JSON before/after change analysis for indexed sheets, tighter schedule/title-block comparisons, local read-only stdio MCP tool; no real AutoCAD/Revit connection |
| State safety and native integration research | [PR #17](https://github.com/MakeItEzzz555/Gridline/pull/17), [PR #18](https://github.com/MakeItEzzz555/Gridline/pull/18), [PR #19](https://github.com/MakeItEzzz555/Gridline/pull/19) | Research, acceptance criteria and independent Codex audit; **documentation, not delivered native integration or verifier repairs** |

## Issue-level truth table

| Issue | Shipping progress | Still required to close | Status |
| --- | --- | --- | --- |
| [#10: Cross-sheet consistency](https://github.com/MakeItEzzz555/Gridline/issues/10) | PR #6 creates schedules/plan sheets from one spec; PR #9 reports indexed sheet impacts | Actual independent native DXF/PDF reference extraction, transitive hosted-element dependencies, 40-sheet benchmark with seeded errors and measured recall; scanner uncertainty surfaced | **OPEN — partially implemented** |
| [#11: IFC/IDS validation](https://github.com/MakeItEzzz555/Gridline/issues/11) | `openbim-ifc-coordination` skill documents workflow; research in PRs #18/#19 | Executable local IfcOpenShell/IfcTester schema/IDS gate, defect fixtures and receipts, separately scoped geometry and licensed host roundtrip | **OPEN — researched/guidance only** |
| [#12: Native AEC adapters](https://github.com/MakeItEzzz555/Gridline/issues/12) | Workflow skills for Revit, Rhino/Grasshopper, AutoCAD and openBIM; local Gridline review MCP from PR #9 | Actually installed/versioned adapters, native discovery/readback, permissions and licensed-host tests. No broad agent write capabilities before #15 | **OPEN — no native bridge release** |
| [#13: 2D→editable 3D→openBIM](https://github.com/MakeItEzzz555/Gridline/issues/13) | JSON→2D plan DXF/PDF plus conceptual six-primitives as inputs | Semantic 3D generation, topology/units verification, IFC relationships/GUIDs, repeatable import/export tests and professional review | **OPEN — foundation only** |
| [#14: Scan and markup reconstruction](https://github.com/MakeItEzzz555/Gridline/issues/14) | Investigated and documented uncertainty gates, input provenance and professional review requirements | Scan rectification, annotation separation/OCR, calibration, confidence and ambiguity handling, editable review output and benchmark | **OPEN — not implemented** |
| [#15: Authoritative state/transactions](https://github.com/MakeItEzzz555/Gridline/issues/15) | Pre/post JSON diff and read-only review in PR #9; transaction-oriented research in PRs #18/#19 | Canonical immutable revisions, typed proposals, conflict detection, human-signed approvals, append-only ledger, native transaction/rollback tests | **OPEN — critical write blocker** |
| [#16: Native AutoCAD quality](https://github.com/MakeItEzzz555/Gridline/issues/16) | Layered R2018 DXF, layouts, profiles and basic readback in PR #6/PR #9 | Tested native AutoCAD open/AUDIT/edit/plot, DWG↔DXF fidelity, paper-space measurements, XREF cases and host-specific evidence | **OPEN — not native-verified** |

### Verified unresolved defects and safety boundaries

- The [Codex audit](GRIDLINE_CODEX_AUDIT_AND_DISCUSSION_2026-10-22.md) documents that deleting one opening LINE in generated A-101 can leave the old checker reporting **PASS**. This defect is **not fixed by PR #19**.
- Other documented gaps: missing drawing-relevant input change detection (e.g., grids/units), non-transitive wall→hosted opening→detail impact, mixed-revision artifact publication on interrupted builds, and potentially race-prone file-path validation in the read-only MCP helper.
- A separate **uncommitted** verification worktree observed on the maintainer's Mac is not part of `main` and cannot count as shipped. When a reviewed implementation PR merges, re-audit the issue acceptance criteria and update this ledger and the relevant issue comments.
- A model-agnostic skill is *guidance*, not permission to edit a licensed CAD application; local `ezdxf` checks are not native AutoCAD acceptance; IDS information requirements are not equivalent to geometry, fire, accessibility or permit compliance.

### Community process

Each tracked issue receives an explicit status comment with what shipped, PR evidence, what remains and why it stays open. Close an issue only after all of its stated acceptance criteria have been independently verified and link the implementing PR/tests. Historical closed or merged **PRs** are not open feature issues and are not re-closed.

For the next stages, consult [ROADMAP.md](../ROADMAP.md), [NEXT_AEC_PHASES.md](NEXT_AEC_PHASES.md) and [the Codex audit](GRIDLINE_CODEX_AUDIT_AND_DISCUSSION_2026-10-22.md). Current issue state should always be verified live on GitHub; this document is a dated snapshot.

---
name: construction-documentation
description: "Develop and coordinate architectural construction-document sets: sheet registers, plans, sections, elevations, details, schedules, notes, legends, drawing references, revisions, issue packages and documentation QA. Use for technical design/CD production, permit/tender/issue-set preparation, and drawing-set organization."
---

# Construction Documentation

Turn coordinated design information into a traceable drawing/document package without inventing technical details.

## Preflight

- Project stage, issue purpose, sheet/document numbering standard, units, scales, revision system and consultant deliverables.
- Current architectural model/drawings, room/door/window/finish data, outline specifications and known coordination decisions.

Keep verified facts, project assumptions, design options, and unresolved questions visibly separate. If a required input is absent, record it as `UNKNOWN` rather than inventing it.

## Workflow

1. Build a deliverable/sheet register and responsibility matrix before producing sheets.
2. Develop general arrangements first, then sections/elevations, enlarged plans and details; keep tags/references bidirectional.
3. Generate schedules from authoritative model/data where possible; reconcile IDs and counts against plans.
4. Run cross-sheet, revision, annotation, dimension and consultant-interface QA before issue; freeze the issue snapshot and record transmittal metadata.

## Deliverables

- Sheet/document register
- Coordinated drawing package plan
- Schedules and detail register
- Issue checklist and transmittal metadata

## Verification

- Every callout resolves; room/door/window/detail identifiers reconcile across views and schedules.
- Revision/date/status are consistent and the issue package opens/plots at intended scales.

For file/model changes, compare the result against a pre-change baseline and report changed items, skipped items, failures, and checks actually run.

## Professional boundaries

- Do not invent missing construction assemblies or engineering details.
- Issue status does not equal code compliance or professional approval.

If a live CAD/BIM/GIS/analysis tool or MCP integration is available, inspect the current document/model and tool version before write operations. Prefer read-only inspection, dry runs, bounded samples, new output paths, and native undo/transaction mechanisms. Never claim a model or drawing was changed unless the tool confirms it.

If the native application is unavailable, produce a reproducible plan, script, structured data, SVG/DXF artifact, or exact in-application procedure instead of pretending to have operated the software.

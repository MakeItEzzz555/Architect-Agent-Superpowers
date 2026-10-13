---
name: autocad-dwg-workflow
description: Plan and review safe AutoCAD DWG drawing cleanup, layer and block audits, external-reference repair, layouts, plotting, and issue preparation. Use for AutoCAD-specific DWG workflows, AutoLISP/.NET automation, CTB/STB plot styles, and drawing package handoff.
---

# AutoCAD / DWG Workflow

Use for AutoCAD-specific DWG editing, automation, and drawing issue preparation. Route Revit/pyRevit/Dynamo to `revit-workflow`, Rhino/Grasshopper to `rhino-grasshopper-workflow`, and general IFC/DXF/SVG or cross-platform CAD/BIM data extraction to `cad-bim-automation`.

## Establish the drawing contract

Record AutoCAD product and release, DWG format/version, operating system, available verticals/add-ins, source versus issued status, and intended deliverable. Capture drawing units, insertion scale, UCS/WCS, coordinates, xrefs, layouts, annotation scales, fonts, plot style mode (CTB/STB), page setups, and output paths. Mark uninspected facts `UNKNOWN`; check installed APIs and version-matched documentation before suggesting executable commands.

## Preflight before any edit

1. Work on versioned copies; preserve the original DWG and its dependent files. Inventory model/paper-space entities, layouts, layers, blocks (including attributes and dynamic/annotative behavior), external references, image underlays, fonts, line types, and plot dependencies.
2. Distinguish missing, unloaded, unresolved, nested, and absolute/relative-path xrefs. Do not silently bind, detach, flatten, or replace references; record the dependency impact first.
3. Identify protected geometry and attributes: survey origin, coordinates, units, dimensions, viewports, title blocks, sheet numbers, revision data, layer states, and issued content. Define permitted edits and an exclusion list.
4. For cleanup, identify duplicates, unused definitions, invalid or proxy objects, overlapping annotations, and broken references without assuming that an unused-looking layer or block is safe to delete.
5. For batch scripts, verify the supported execution surface (interactive commands, AutoLISP, .NET API, or approved external automation). Avoid guessed command flags or API signatures.

## Safe execution sequence

**Inventory → dry-run report → bounded sample → reviewed change set → copy-based execution → verification.**

- Preview exact target entity IDs/handles, layer/block names, counts, proposed changes, and skipped items. Require explicit approval before destructive or production-file writes.
- Use application-supported undo/transaction boundaries where verified for the installed version; save to new paths and checkpoint before batch operations. Never treat an undo stack as the only backup.
- Preserve units, insertion points, object transforms, annotative scales, attribute values, and coordinate systems. Test blocks and xrefs on representative samples before full-file changes.
- For plotting, verify model/paper space, page setup, viewport scales and locks, CTB/STB availability, fonts, lineweights, paper sizes, output resolution, and revision/title-block data. Generate proof PDFs before an issue set.
- Never claim compliance, clash freedom, or issue readiness from a successful export alone.

## Acceptance and handoff

Compare before/after counts by layer, block, layout, and xref; sample stable handles and attributes; inspect geometry extents, unit and coordinate invariants, unresolved references, missing fonts, and application warnings. Open the resulting DWG in a compatible AutoCAD environment when available. Visually inspect proof plots for scale, clipping, lineweights, hatches, annotations, and legibility.

Return **Environment / Scope and exclusions / Baseline inventory / Proposed changes / Dry-run evidence / Approval gates / Verification and proof plots / Rollback / Unknowns**. Report unverified checks explicitly. For issued or construction-critical drawings, require competent human review before release.

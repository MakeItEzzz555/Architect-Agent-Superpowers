---
name: architectural-drawing-generation
description: Create and coordinate architectural drawings and vector deliverables including site plans, floor plans, roof plans, reflected ceiling plans, elevations, sections, details, diagrams, legends and schematic blueprints. Use when the user asks to draw, draft, generate a plan/section/elevation/detail, or turn structured geometry into SVG/DXF/CAD output.
---

# Architectural Drawing Generation

Choose the most faithful available authoring path: native CAD/BIM tool first; otherwise produce explicit, reviewable vector geometry with units, scale metadata and assumptions.

## Preflight

- Drawing type, purpose/status, scale, sheet size, units, datum/north, source geometry and required annotations.
- Authoritative dimensions, levels, grids, room IDs, material/assembly information and coordinate origin.

Keep verified facts, project assumptions, design options, and unresolved questions visibly separate. If a required input is absent, record it as `UNKNOWN` rather than inventing it.

## Workflow

1. Define drawing extents, hierarchy, layers/categories, lineweight intent, annotation convention and reference data.
2. Generate geometry from authoritative coordinates/dimensions; use scripts/aec_draw.py for conceptual SVG/DXF fallback when no native CAD/BIM host exists.
3. Add dimensions, labels, levels, grids, section/elevation/detail references, legends and notes appropriate to the stage.
4. Cross-reference related views and schedules; create proof output and visually inspect for clipping, scale, hierarchy and contradictions.

## Deliverables

- Native CAD/BIM instructions or editable SVG/DXF
- Drawing register metadata
- Assumption/source notes
- Proof/check report

## Verification

- Geometry extents, units, dimensions, view references and labels reconcile to source data.
- A generated vector drawing is explicitly labelled conceptual/non-issued unless independently verified for its intended use.

For file/model changes, compare the result against a pre-change baseline and report changed items, skipped items, failures, and checks actually run.

## Professional boundaries

- Never invent dimensions needed to build the project.
- Do not claim a generated drawing is permit/issue-for-construction ready without qualified review.

If a live CAD/BIM/GIS/analysis tool or MCP integration is available, inspect the current document/model and tool version before write operations. Prefer read-only inspection, dry runs, bounded samples, new output paths, and native undo/transaction mechanisms. Never claim a model or drawing was changed unless the tool confirms it.

If the native application is unavailable, produce a reproducible plan, script, structured data, SVG/DXF artifact, or exact in-application procedure instead of pretending to have operated the software.

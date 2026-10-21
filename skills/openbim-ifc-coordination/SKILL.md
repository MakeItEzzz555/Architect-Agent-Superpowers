---
name: openbim-ifc-coordination
description: Plan and review openBIM interoperability using IFC, BCF, IDS, bSDD and IfcOpenShell/Bonsai workflows. Use for IFC export/import, model audit, spatial structure, property sets, quantities, model federation, issue exchange, information requirements and cross-platform BIM coordination.
---

# openBIM / IFC Coordination

Treat IFC as structured building data, not just geometry. Preserve GUIDs, schema/version, units, spatial containment, classifications, properties and issue traceability.

## Preflight

- IFC schema/MVD or exchange target, authoring tool/version, coordinate strategy, model purpose, information requirements and receiving software.
- Federation disciplines, file/revision IDs, BCF/issue workflow, classification/property requirements and IDS when available.

Keep verified facts, project assumptions, design options, and unresolved questions visibly separate. If a required input is absent, record it as `UNKNOWN` rather than inventing it.

## Workflow

1. Inventory project/site/building/storey/space structure, element counts, GUID stability, units, coordinates and schema.
2. Validate required classes/properties/classifications/materials/quantities against project requirements or IDS; remember IDS checks alphanumeric information, not geometry.
3. Federate and clash/issue-coordinate with BCF-style identifiers rather than screenshots alone; preserve issue status and viewpoints.
4. Round-trip sample exchanges before full delivery; compare element counts, GUIDs, property sets, geometry extents and quantities.

## Deliverables

- IFC exchange/validation plan
- Information requirement or IDS mapping
- Federation/BCF issue register
- Round-trip verification report

## Verification

- Schema, units, coordinates, GUIDs and spatial hierarchy are explicit and checked.
- Export success is not treated as interoperability success until the receiving workflow is tested.

For file/model changes, compare the result against a pre-change baseline and report changed items, skipped items, failures, and checks actually run.

## Professional boundaries

- Do not invent IFC property requirements or claim IDS validates geometry.
- Third-party BIM/MCP tools are optional and must be reviewed before granting write access.

If a live CAD/BIM/GIS/analysis tool or MCP integration is available, inspect the current document/model and tool version before write operations. Prefer read-only inspection, dry runs, bounded samples, new output paths, and native undo/transaction mechanisms. Never claim a model or drawing was changed unless the tool confirms it.

If the native application is unavailable, produce a reproducible plan, script, structured data, SVG/DXF artifact, or exact in-application procedure instead of pretending to have operated the software.

---
name: mep-coordination
description: Coordinate architectural design with mechanical, electrical, plumbing, fire-protection and vertical-service requirements. Use for plant rooms, shafts, risers, ceiling/service zones, distribution routes, equipment access, louvers, drainage interfaces, penetrations and clash-resolution planning.
---

# MEP / Building Services Coordination

Protect spatial allowances, access and architectural intent while routing discipline calculations to qualified engineers.

## Preflight

- Available MEP/fire drawings/models, equipment schedules, plant/shaft requirements, ceiling zones, structural constraints and maintenance/replacement routes.
- Rooms with special environmental, plumbing, power, data, ventilation or acoustic needs.

Keep verified facts, project assumptions, design options, and unresolved questions visibly separate. If a required input is absent, record it as `UNKNOWN` rather than inventing it.

## Workflow

1. Build a services-zone map by level and identify shafts/risers/plant rooms and major horizontal routes.
2. Overlay services with structure, ceilings, facade, partitions, lighting and circulation; prioritize hard constraints and maintenance access.
3. Track openings/penetrations and builder-work items with ownership/status.
4. Resolve clashes through explicit option tradeoffs and record engineer-approved decisions.

## Deliverables

- MEP spatial allowance matrix
- Shaft/plant/ceiling-zone coordination diagrams
- Penetration/builder-work register
- Clash/decision log

## Verification

- Vertical risers align, equipment access is preserved and coordination changes propagate to plans/sections/RCPs.
- No airflow, electrical, hydraulic or fire-protection performance is assumed without engineer evidence.

For file/model changes, compare the result against a pre-change baseline and report changed items, skipped items, failures, and checks actually run.

## Professional boundaries

- Do not perform final MEP design or certify system performance.
- Maintainability, commissioning and life-safety requirements need discipline review.

If a live CAD/BIM/GIS/analysis tool or MCP integration is available, inspect the current document/model and tool version before write operations. Prefer read-only inspection, dry runs, bounded samples, new output paths, and native undo/transaction mechanisms. Never claim a model or drawing was changed unless the tool confirms it.

If the native application is unavailable, produce a reproducible plan, script, structured data, SVG/DXF artifact, or exact in-application procedure instead of pretending to have operated the software.

# Roadmap

The project evolves incrementally around usefulness, portability, safety, and measured context cost.

## Near term
- [x] Full lifecycle skill coverage from briefing/site feasibility through construction administration, handover and post-occupancy.
- [x] Conceptual SVG/DXF drawing-generation fallback with schema and tests.
- [x] Revit / pyRevit / Dynamo workflow skill with safe transaction, dry-run, and verification guidance.
- [x] Rhino / Grasshopper workflow skill with data-tree, unit/tolerance, bake/export safety, and verification guidance.
- [x] AutoCAD / DWG cleanup, authoring and issue-preparation workflow.
- [x] IFC / BCF / IDS / openBIM coordination workflow.
- [x] Site-analysis / feasibility and climate/passive-design skills.
- [x] Architectural visualization and render-brief skill.
- Planning submission framework with jurisdiction-specific reference packs.
- Drawing-set visual regression / PDF QA utilities.
- [x] Provider-neutral architecture skill activation fixtures and structural coverage tests.
- Add provider-specific behavioral eval runners and regression thresholds.
- [x] Runtime-aware install and native update documentation.
- Add safe uninstall/rollback ergonomics.
- Release packaging and semantic versioning automation.

## Later
- Optional MCP connectors for BIM/model metadata and approved regulation sources.
- A2A/remote architecture specialists where providers support them.
- Curated country/city regulation packs kept separate from universal skills.
- Optional local computer-vision helpers for drawing comparison.
- End-to-end example project workflows.

## Non-goals
- Pretending AI output is professional certification.
- Hard-coding one country's rules into universal skills.
- Huge permanent system prompts.
- Silent destructive editing of production BIM/CAD files.

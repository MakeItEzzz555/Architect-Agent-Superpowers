# Roadmap

The project evolves incrementally around usefulness, portability, safety, and measured context cost.

## Direction

First users: small practices and independent architects, Cyprus and the wider EU first, with standards that stay configurable for anywhere. The principle: **one source of truth, deliverables derived from it, a checker before anything is presented, and a named architect who signs.**

## Next, in order
1. **Agent reliability (P1).** Read-only reviewer agents; baseline activation and negative-trigger evals on the existing cases; more negative cases.
2. **Audit existing drawings.** Run the standards checks (layers, ByLayer properties, text heights, title blocks, sheet register) on a practice's *own* DXF files, not only generated ones. Most offices already have drawings; checking them is immediate value.
3. **Sections and elevations from the same spec.** Levels, wall heights, sills and opening heights are already in the spec; derive elevations and a simple section, plus door/window type legends and a finishes schedule.
4. **Live AutoCAD loop.** A recipe for autocad-mcp (AutoCAD LT 2024+ on Windows): open the generated DXF, read back entity counts per layer, plot to PDF, and compare against `check`.
5. **IFC from the same spec.** Walls, openings and spaces through IfcOpenShell for Revit/Archicad import and IDS checks.
6. **Revisions and issue.** Revision table and clouds, register history per revision, transmittals.
7. **Cyprus/EU reference pack.** Planning and building-control sources as data with authority, edition, effective date and limitations; no rule is applied without its citation.
8. **Quality benchmark.** The same tasks with and without the pack across providers: drawing validity, coordination errors, unsupported assumptions, human corrections.

## Done
- [x] Full lifecycle skill coverage from briefing/site feasibility through construction administration, handover and post-occupancy.
- [x] Coordinated CAD pipeline: one spec -> standard-layered DXF sheets, PDFs, schedules, sheet register, and an independent checker (0.6.0).
- [x] ISO 13567 and US NCS standards profiles with office overrides (0.6.0).
- [x] Self-contained skills on every install path; ownership-safe, rollback-safe installers (0.5.1).
- [x] Conceptual SVG/DXF drawing fallback with schema and tests.
- [x] Revit, Rhino/Grasshopper, AutoCAD/DWG and IFC/BCF/IDS workflow skills.
- [x] Provider-neutral activation fixtures and structural coverage tests.

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

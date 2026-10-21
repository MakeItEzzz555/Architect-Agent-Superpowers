# Full AEC Superpowers Overhaul — Execution Plan

## Goal
Turn Architect Agent Superpowers from a small architecture skill pack into a provider-neutral, progressively disclosed AEC workflow system that can assist across the complete building-project lifecycle, generate real vector drawing artifacts when no native CAD/BIM host is available, and route safely into specialist CAD/BIM/civil/coordination workflows.

## Research basis
- Benchmark onboarding and release discipline against TuckBit, Claude Widget Kit, and Codex Widget Kit.
- Use Prompt Master's agentic pattern: explicit outcome, scoped paths, tool permissions, stop conditions, verification, and no hidden-reasoning requests.
- Use AIA basic services and RIBA Plan of Work as lifecycle coverage maps, not universal contractual rules.
- Ground interoperability in buildingSMART IFC/BCF/IDS/openBIM concepts.
- Benchmark public AEC agent work for version-aware Revit/Grasshopper skills, guarded MCP bridges, visual verification, BIM authoring, and construction-drawing generation.

## Workstreams
1. Rewrite README for architect-first onboarding with a prominent copyable install prompt, cross-agent `npx skills` install, native Codex/Claude/Gemini paths, workflow coverage, tools, safety, and validation.
2. Expand the canonical skill library from 11 skills to a broad lifecycle suite covering feasibility, design generation, documentation, BIM/openBIM, common authoring tools, civil/site, structural/MEP coordination, performance, specifications/cost, procurement, construction administration, visualization, and handover.
3. Upgrade the orchestrator with safety-priority routing and lifecycle/tool routing.
4. Add specialist subagents for independent drawing production, civil/site, openBIM, performance, technical documentation, and construction administration.
5. Add a dependency-free vector drawing utility plus JSON schema/example so agents can create conceptual plans, sections, elevations, details, diagrams and DXF/SVG deliverables without pretending a native CAD app was used.
6. Add reusable AEC templates and lifecycle/tool/research documentation.
7. Add at least two activation cases for every stable skill and regression cases for overlapping tool domains.
8. Strengthen CI/tests so manifest counts, provider copies, native adapters, vector drawing output, and installer paths stay synchronized.

## Constraints
- Do not encode one jurisdiction's code as universal truth; regulations require jurisdiction, source and edition.
- Do not claim licensed architectural/engineering approval, structural capacity, fire compliance, accessibility compliance, cost certainty, or issue-for-construction readiness without competent review.
- Do not auto-install third-party MCP servers or grant them model/file write access.
- Prefer reversible outputs, copies, dry runs, stable IDs, explicit coordinate/unit conventions, and before/after verification.
- Keep always-loaded metadata compact; deep procedures, scripts, references and templates load only when relevant.

## Done
- README is beginner-usable and includes one-click-copy installation instructions.
- Canonical skill suite covers the project lifecycle and major architecture/AEC authoring environments.
- Drawing generation has a tested SVG/DXF fallback path.
- Provider manifests and Claude skill copies are synchronized.
- Repository validation, unit tests, native provider checks available on this machine, and installer smoke tests pass.
- Changes are committed to a feature branch, pushed, and opened as a merge-ready PR with evidence.

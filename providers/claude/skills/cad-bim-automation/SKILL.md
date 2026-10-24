---
name: cad-bim-automation
description: Safely automate repetitive architecture CAD/BIM/model/document workflows using available tools. Use for Revit, IFC, DWG, DXF, SVG, Blender, FreeCAD, batch edits, exports, naming, or model-data extraction.
---

# CAD/BIM Automation

Inspect formats/versions, available tools/APIs, source-vs-issued status, units, coordinates/origin, levels/grids, layers/categories, naming, and revisions.

Choose the least destructive method: read/report → export to new file → supported API/script → original edit only with explicit permission. For proprietary formats, produce an application-native workflow rather than pretending an unsupported direct edit occurred.

Batch protocol: inventory → dry run → sample → validate → full run → post-change audit.

Verify counts, units, geometry bounds, naming, missing objects/categories, export integrity, and deltas. Never alter surveyed coordinates, structural geometry, life-safety elements, or issued information outside explicit scope and review.

**Opt-in local Blender prototype:** when an actual Blender executable is available and the user requests a NEW conceptual 3D scene from the supported Gridline building-spec, consult repository `docs/BLENDER_NATIVE_BRIDGE.md` and use `python3 scripts/blender_native.py doctor` before an explicitly scoped `build` to a fresh output directory. This creates simple editable Blender mesh geometry and .glb with native reopen/readback; it does not edit live documents, install a Blender MCP, generate hidden architectural details from images, or establish IFC/AutoCAD compliance. Report unsupported model elements and require image/measurement clarification for detailed reference matching.

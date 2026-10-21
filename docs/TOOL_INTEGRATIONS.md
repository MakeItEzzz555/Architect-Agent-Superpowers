# CAD, BIM, GIS and AEC Tool Integrations

The skill pack is intentionally **tool-aware but tool-independent**.

## Preferred order

1. Use an already connected, trusted native tool/API/MCP integration.
2. Inspect host/version/document/model before writes.
3. Use read-only queries and screenshots/previews to establish a baseline.
4. For writes: dry run or bounded sample, explicit scope, native transaction/undo where verified, then before/after checks.
5. If no native host exists, produce a script, structured exchange file, SVG/DXF artifact, or exact manual workflow instead of pretending the application was operated.

## Tool families

- **Revit / pyRevit / Dynamo / Revit API** → `revit-workflow`
- **Rhino / Grasshopper / RhinoCommon** → `rhino-grasshopper-workflow`
- **AutoCAD / DWG / AutoLISP / .NET** → `autocad-dwg-workflow`
- **IFC / IfcOpenShell / Bonsai / BCF / IDS** → `openbim-ifc-coordination`
- **Civil 3D / grading / surfaces / networks** → `civil-site-design`
- **Blender, FreeCAD, generic DXF/SVG transforms** → `cad-bim-automation`

Public AEC MCP projects show that live Revit, Rhino/Grasshopper, AutoCAD, Archicad, Vectorworks, SketchUp and IFC/Bonsai operations are possible. This repository does **not** auto-install or trust those servers. Review source, permissions and write surfaces first.

A tool reporting "command succeeded" is not enough. Confirm geometry/data state, counts, identifiers, warnings and visual output where applicable.

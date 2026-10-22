# Gridline: coordination, openBIM validation and native tool integrations

Research checkpoint: **2026-10-22**. This is an implementation plan grounded in current vendor documentation, not a claim that all host adapters are installed or tested.

## Why the priorities changed

Two real architectural problems should drive the next work:
1. **A window schedule revision** can invalidate numerous plans, elevations, sections, details and schedules. Catching that must start with stable element IDs, explicit sheet references and detectable revision impact, not an LLM reading 40 PDFs and guessing.
2. **A model that exports as IFC is not necessarily valid or fit for a client's information requirements.** Use separate schema/normative validation and project-specific IDS checks. IDS generally checks specified data requirements, **not geometric correctness**.

A third research objective is **scanned / hand-marked plan reconstruction**. This is inherently uncertain; unscaled scans, handwriting, erasures and non-orthogonal photographs require confidence flags, calibration, user confirmation and geometry review before generating any BIM element.

## Execution phases and acceptance gates

### Phase 1 — Read-only revision dependency/coordination index (started)

- Baseline and proposed building specifications; compare stable opening, wall, room and level IDs.
- Emit machine-readable changed fields, impacted indexed sheets and affected schedules.
- Let authored sheet records declare `references` e.g. `{"openings":["W01"],"walls":["E1"]}` for cross-level sections or details.
- Compare **all** window schedule fields, not width alone; flag duplicate IDs and stale revision/title blocks.
- Never claim comprehensive 40-sheet coverage: unindexed PDFs, sections/elevations or hand markups remain UNKNOWN.
- Gate: positive and negative tests for changes to window width, height, sill, type, wall, and sheet revisions.

Command (stdlib-only, **does not edit** the input project):
```bash
python3 skills/architectural-drawing-generation/scripts/revision_impact.py before.building.json after.building.json --out impact.json
```

Output is a **review queue, not certification**. Downstream hosts or drawing-specific readers must verify that geometry and annotation really match.


Optional **Gridline Read-Only MCP** integration (MCP SDK **v2**, Python 3.11+):

```bash
python3 -m pip install 'mcp>=2,<3'
export GRIDLINE_MCP_PROJECT_ROOT=/absolute/path/to/your/architectural-project
python3 skills/architectural-drawing-generation/scripts/gridline_mcp.py
```

Configure the MCP client to launch that script by its **absolute path** with a Python environment containing the v2 SDK, using local **stdio** transport. For example, a client's generic `mcpServers` format, if supported:

```json
{
  "mcpServers": {
    "gridline-review": {
      "command": "/absolute/path/to/python-with-mcp",
      "args": ["/absolute/path/to/Gridline/skills/architectural-drawing-generation/scripts/gridline_mcp.py"],
      "env": {
        "GRIDLINE_MCP_PROJECT_ROOT": "/absolute/path/to/your/architectural-project"
      }
    }
  }
}
```

This is a **Gridline-owned local review server**, not the Autodesk AutoCAD or Revit MCP server. It exposes only `compare_gridline_revisions` and `get_gridline_capabilities`; it cannot write model files or use arbitrary shell commands. It refuses to start without an explicit project root; input file paths must resolve under that root, preventing symlink escapes. It does not connect to any native CAD/BIM application. The client configuration keys vary by provider; verify their official documentation.

Official MCP Python SDK v2: https://py.sdk.modelcontextprotocol.io/

### Phase 2 — IFC/IDS local validation gate

- For an IFC export: validate syntax and IFC schema (and where supported the EXPRESS rules) using the `ifcopenshell` validation tools or a self-hosted buildingSMART validator.
- Separately run IfcTester against supplied, version-controlled project IDS requirements, and report pass/fail per requirement.
- Preserve schema version (IFC2X3, IFC4, IFC4.3 as supported), GUIDs, model revision, coordinate reference, units, source hashes, software/validator version and structured issues.
- Block release on parser/schema errors, failed mandatory IDS checks, and missing required validators. Report geometry / clashes / code compliance as **NOT CHECKED** until separately validated.
- Test against known-valid and deliberately defective IFC fixtures, including invalid schema/entity, missing property, incorrect spatial assignment and GUID changes.
- Gate: deterministic nonzero exit codes, JSON reports and reproduced failures. Never upload production IFC externally without project-owner authorization.

Sources:
- IFC official schema: https://technical.buildingsmart.org/standards/ifc/ifc-schema-specifications/
- buildingSMART validation: https://dev.validate.buildingsmart.org/
- Local IfcOpenShell: https://docs.ifcopenshell.org/ifcopenshell-python/validation.html
- Project IDS with IfcTester: https://docs.ifcopenshell.org/ifctester.html

### Phase 3 — MCP/native AEC tool adapters (read-only first)

| Host | Verified connection surface | Important constraint / next adapter |
| --- | --- | --- |
| **AutoCAD / Civil 3D** | Official Autodesk AutoCAD/Civil 3D MCP tech preview; native AutoCAD .NET/ObjectARX/AutoLISP; APS cloud Automation | As documented, native preview currently runs **inside Autodesk Assistant on Windows**; AutoCAD exposes read/analysis, Civil 3D includes edit tools. Do not assume arbitrary external MCP clients can connect or that read-only tools can modify AutoCAD. Build a supported local bridge only after confirming the client's transport and user authorizations. |
| **Revit** | Autodesk Revit 2027.2 Public MCP Server via local STDIO, read/write/experimental choices; Revit .NET/APS AEC Data Model | A real Windows Revit host and add-on are required. Default to **read-only** server; writing needs separate explicit approval, transaction boundaries and rollback/undo. |
| **Rhino / Grasshopper** | Rhino.Compute REST geometry; Rhino.Inside.Revit on Windows; RhinoCommon/Grasshopper native scripting | Rhino.Compute is a geometry service, **not necessarily a native MCP server**. A Gridline MCP wrapper must authenticate the underlying service and limit calls; licensed host and deployment requirements apply. |
| **Archicad** | Graphisoft JSON Automation API over loopback HTTP and official Python connection | Uses local ports and requires running host. Verify which commands can read/write; do not expose loopback to untrusted clients. |
| **Blender** | Official `bpy` Python API (local add-on or headless Blender script) | A bounded MCP wrapper can expose allowlisted actions (inspect, build sample scene, render, export); **never** offer unrestricted Python evaluation by default. |
| **FreeCAD** | Native Python/document APIs and file exchange | Build a local sandboxed adapter, verify version, and use copied documents/transaction boundaries. |
| **IFC / openBIM** | IfcOpenShell / IfcTester local Python, BCF issue interchange | Prefer pure local deterministic validators before any hosted API. |

Additional authoritative references:
- Autodesk MCP index: https://help.autodesk.com/view/ADSKMCP/ENU/
- Autodesk AutoCAD/Civil3D: https://help.autodesk.com/view/ADSKMCP/ENU/?guid=ADSKMCP_AutoCADCivil3DMcp_autodesk_autocad_civil_3d_mcp_html
- Autodesk Revit: https://help.autodesk.com/view/ADSKMCP/ENU/?guid=ADSKMCP_RevitMcp_revit_mcp_server_html
- Rhino.Compute: https://developer.rhino3d.com/guides/compute/compute-faq/
- Archicad JSON: https://archicadapi.graphisoft.com/JSONInterfaceDocumentation/
- Blender API: https://docs.blender.org/api/4.5/

**MCP connector protocol requirements:** capability discovery with supported host/version, `read` vs `write` permission separation, user-scoped resources, model/drawing ID and revision, dry-run change sets, user approval, backups / undo, timeouts and output size limits, audit logs, no credential exfiltration, and post-edit native readback. Tool failures are never silently converted to success.

### Phase 4 — Coherent 2D → editable 3D pipeline

1. Prefer authoritative measured 2D geometry (room boundaries, wall centerlines, opening types and dimensions) from an editable DXF/BIM spec.
2. Validate topology (closed boundaries, wall joins, nonoverlapping openings), units and levels before extruding.
3. Create walls/doors/windows with stable IDs; export a reproducible neutral scene (e.g. glTF) for **visual review**; only export IFC after adding spatial/semantic BIM data and passing Phase 2.
4. Use Rhino.Compute/Grasshopper, Blender, FreeCAD or native Revit/Archicad as backends based on actually detected host capabilities.
5. After a revision, regenerate incrementally and verify geometric quantities / opening positions against the authoritative spec.

**3D appearance ≠ coordinated BIM**. A mesh or Gaussian splat is not a substitute for IFC entities, layers, element properties or editable architectural geometry.

### Phase 5 — Scans and annotations (research/experimental)

- Pipeline: page rectification → calibration from user-supplied dimensions/scale → line/arc detection → candidate walls/openings → OCR/markup separation → confidence scoring → editable 2D review → 3D/BIM conversion.
- Mixed scans and hand annotations are **untrusted input**. Flag overlaps, overwritten notes, missing scale, unknown wall types and uncertain symbols; never invent missing dimensions.
- Benchmark with consented redacted examples: vector PDFs, 300 DPI scans, damaged scans, handwritten revisions, misregistered pages and variant symbol conventions.
- Explicit human sign-off gates precede geometry and IFC export. Evaluate false negatives (missed changed dimensions) more heavily than false positives.

## Near-term evaluation protocol

- **Accuracy:** precision and recall of affected sheet/schedule IDs; report missed references and uncertainty, not just apparent successes.
- **IFC:** schema-valid count, IDS requirement success, GUID stability, unit/coordinate integrity, and client-app import roundtrip on a representative sample.
- **Host adapters:** discovery works, read-only mode cannot write, permissions are respected, unauthorized action rejected, dry-run/undo available and confirmed on a licensed application.
- **3D:** errors in dimensions/opening locations and mesh watertightness / BIM semantic preservation, not attractiveness of renders.
- **Humans:** architectural reviewer signs off, with time-to-review and false negative rates recorded.

**Not yet done:** real application sessions, native Autodesk MCP connections, schema/IDS integration tests, geometry/IFC generation, and scanned image reconstruction. These are separate deliverables, not implied by the Phase 1 tooling.

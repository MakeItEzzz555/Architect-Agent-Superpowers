# Drawing and Blueprint Outputs

Gridline can help plan site plans, floor plans, roof plans, reflected ceiling plans, elevations, sections, construction details, diagrams and schedules. Complete, editable drawings come from a connected native CAD/BIM host; the bundled fallback produces simple conceptual vector drawings.

## Authoring priority

**Native editable model/drawing > verified exchange workflow > repository SVG/DXF fallback > textual instructions.**

When Revit, Rhino, AutoCAD, IFC/Bonsai or another trusted authoring host is connected, use its native objects and verify the live document.

When no native host is available, the `architectural-drawing-generation` skill ships two engines.

## Coordinated CAD pipeline (`scripts/aec_cad.py`)

One building spec (levels, grids, walls, openings, rooms, sheets, title data, in millimetres) produces the whole set, so a change made once reaches every output:

- one DXF per sheet: the plan in model space at 1:1 and a paper-space layout with a frame using ISO 5457 margins, a title block within ISO 7200's 180 mm width, a status stamp, a scale bar, a north arrow and a locked viewport at the sheet scale;
- a vector PDF per sheet;
- room, door and window schedules and a sheet register (CSV).

Layers, lineweights, text sizes, paper sizes and statuses come from a standards profile: `iso13567` (default), `ncs`, or an office profile that `extends` one of them.

```bash
pip install ezdxf==1.4.5 matplotlib==3.11.2 pypdf==6.21.2
D=skills/architectural-drawing-generation
python3 $D/scripts/aec_cad.py build $D/references/example-house.building.json /tmp/example-house
python3 $D/scripts/aec_cad.py check $D/references/example-house.building.json /tmp/example-house
```

`check` reads exact output snapshots and independently compares wall outlines, opening jamb/frame/leaf/swing primitives and room boundaries with the spec (0.01 mm tolerance). Missing, changed and duplicated critical primitives fail with sheet/element evidence. New entities carry `GRIDLINE` XDATA; legacy entities can be matched geometrically. These associations have not been proven through a native roundtrip.

The required PDF gate parses the actual vector stream: one page, intended page dimensions and straight plan segments at the intended plot mapping (0.05 point tolerance). It detects missing, blank, wrong-sheet and incorrectly scaled PDFs. It does not establish raster visibility, clipping, font quality, door-arc plotting or annotation collision freedom. Existing standards, title/tag/schedule checks remain, including the sheet-register date. A missing validator fails rather than silently passing.

`check-report.json` retains the old `errors`, `warnings`, `standard` and `checked` keys and adds a versioned receipt with exact consumed spec/profile/output hashes, validator file/dependency versions, Git source revision, artifact manifest hash and explicit per-gate coverage. Each run also retains `receipts/<id>.json`. A missing/oversized input has a null hash with a failure diagnostic; it is never described as inspected. Legacy PDFs without document metadata report identity `UNKNOWN`; geometry still must match. Standalone installs without tracked Git source report `code_sha: "UNKNOWN"` while retaining validator file hashes. See [receipt contract](VERIFICATION_RECEIPTS.md).

**PASS means supported local 2D checks passed.** Grid positions, dimension/hatch geometry, topology, complete source-detail coverage, semantic 3D, IFC/IDS, native AutoCAD and professional approval remain explicitly unverified. The checker does not verify arbitrary external drawing sets. It currently draws plans only; sections, elevations and details are not generated. Use a fresh output directory for every revision until staged atomic publication is implemented; retained receipts bind snapshots, not future edits to mutable files.

For detailed models from briefs, images, maquettes or top-down drawings, first retain a source-detail inventory: each requirement/observed feature, provenance, dimensions, confidence, model element and verification state. Missing scale, hidden geometry and conflicting details require resolution. Unsupported items remain `UNKNOWN`/`BLOCKED`; do not infer completion from render appearance. Semantic 3D and native exchange follow the prerequisite gates in the [implementation package plan](VERIFICATION_PACKAGE_2026-10-23.md).

## Simple diagrams (`scripts/aec_draw.py`)

The dependency-free `scripts/aec_draw.py` can render an explicit JSON drawing specification to:

- editable SVG for diagrams and conceptual architectural drawings;
- ASCII DXF entities for interchange and continued CAD editing.

Example:

```bash
python3 skills/architectural-drawing-generation/scripts/aec_draw.py skills/architectural-drawing-generation/references/concept-plan.drawing.json /tmp/concept-plan.svg
python3 skills/architectural-drawing-generation/scripts/aec_draw.py skills/architectural-drawing-generation/references/concept-plan.drawing.json /tmp/concept-plan.dxf
```

It ships inside the skill folder, so it is available after every install path. It draws six primitives: `line`, `rect`, `circle`, `polyline`, `text` and `dimension`. It has no wall, door, hatch, title-block or scale-bar entities; compose those from primitives or use a native host.

The fallback never derives missing dimensions. Its default footer is **CONCEPT / NOT FOR CONSTRUCTION**. A human must verify geometry, dimensions, code/engineering coordination and intended issue status before professional use.

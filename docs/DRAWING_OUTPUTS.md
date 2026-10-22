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
pip install ezdxf matplotlib
D=skills/architectural-drawing-generation
python3 $D/scripts/aec_cad.py build $D/references/example-house.building.json /tmp/example-house
python3 $D/scripts/aec_cad.py check $D/references/example-house.building.json /tmp/example-house
```

`check` reads the outputs back and fails on off-standard layers, undersized text, empty title fields, a missing stamp or viewport, and any schedule, tag or room area that disagrees with the geometry. It currently draws plans only; sections, elevations and details are not generated.

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

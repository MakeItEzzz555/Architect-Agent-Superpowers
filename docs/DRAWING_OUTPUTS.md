# Drawing and Blueprint Outputs

Architect Agent Superpowers can help plan site plans, floor plans, roof plans, reflected ceiling plans, elevations, sections, construction details, diagrams and schedules. Complete, editable drawings come from a connected native CAD/BIM host; the bundled fallback produces simple conceptual vector drawings.

## Authoring priority

**Native editable model/drawing > verified exchange workflow > repository SVG/DXF fallback > textual instructions.**

When Revit, Rhino, AutoCAD, IFC/Bonsai or another trusted authoring host is connected, use its native objects and verify the live document.

When no native host is available, the `architectural-drawing-generation` skill's bundled `scripts/aec_draw.py` can render an explicit JSON drawing specification to:

- editable SVG for diagrams and conceptual architectural drawings;
- ASCII DXF entities for interchange and continued CAD editing.

Example:

```bash
python3 skills/architectural-drawing-generation/scripts/aec_draw.py skills/architectural-drawing-generation/references/concept-plan.drawing.json /tmp/concept-plan.svg
python3 skills/architectural-drawing-generation/scripts/aec_draw.py skills/architectural-drawing-generation/references/concept-plan.drawing.json /tmp/concept-plan.dxf
```

It ships inside the skill folder, so it is available after every install path. It draws six primitives: `line`, `rect`, `circle`, `polyline`, `text` and `dimension`. It has no wall, door, hatch, title-block or scale-bar entities; compose those from primitives or use a native host.

The fallback never derives missing dimensions. Its default footer is **CONCEPT / NOT FOR CONSTRUCTION**. A human must verify geometry, dimensions, code/engineering coordination and intended issue status before professional use.

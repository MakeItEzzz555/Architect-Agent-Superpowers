# Drawing and Blueprint Outputs

Architect Agent Superpowers can help create site plans, floor plans, roof plans, reflected ceiling plans, elevations, sections, construction details, diagrams and schedules.

## Authoring priority

**Native editable model/drawing > verified exchange workflow > repository SVG/DXF fallback > textual instructions.**

When Revit, Rhino, AutoCAD, IFC/Bonsai or another trusted authoring host is connected, use its native objects and verify the live document.

When no native host is available, `scripts/aec_draw.py` can render an explicit JSON drawing specification to:

- editable SVG for diagrams and conceptual architectural drawings;
- ASCII DXF entities for interchange and continued CAD editing.

Example:

```bash
python3 scripts/aec_draw.py examples/concept-plan.drawing.json /tmp/concept-plan.svg
python3 scripts/aec_draw.py examples/concept-plan.drawing.json /tmp/concept-plan.dxf
```

The fallback never derives missing dimensions. Its default footer is **CONCEPT / NOT FOR CONSTRUCTION**. A human must verify geometry, dimensions, code/engineering coordination and intended issue status before professional use.

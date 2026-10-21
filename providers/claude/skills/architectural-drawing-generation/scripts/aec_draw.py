#!/usr/bin/env python3
"""Render a small, explicit AEC drawing spec to SVG or DXF.

This is a conceptual/vector fallback for agents without a live CAD/BIM host.
It never infers missing dimensions and is not a construction-document certifier.
"""
from __future__ import annotations

import argparse
import html
import json
import math
from pathlib import Path


def load_spec(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("drawing spec must be a JSON object")
    if not isinstance(data.get("entities"), list):
        raise ValueError("drawing spec requires an entities array")
    return data


def fnum(value, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric")
    if not math.isfinite(float(value)):
        raise ValueError(f"{name} must be finite")
    return float(value)


def points(value, name="points"):
    if not isinstance(value, list) or len(value) < 2:
        raise ValueError(f"{name} must contain at least two [x,y] points")
    out = []
    for i, point in enumerate(value):
        if not isinstance(point, list) or len(point) != 2:
            raise ValueError(f"{name}[{i}] must be [x,y]")
        out.append((fnum(point[0], f"{name}[{i}].x"), fnum(point[1], f"{name}[{i}].y")))
    return out


def layer_style(spec: dict, entity: dict) -> dict:
    layer = str(entity.get("layer", "default"))
    raw = (spec.get("layers") or {}).get(layer, {})
    return {
        "layer": layer,
        "stroke": str(raw.get("stroke", "#111111")),
        "stroke_width": fnum(raw.get("stroke_width", 1.5), "stroke_width"),
        "fill": str(raw.get("fill", "none")),
        "dash": str(raw.get("dash", "")),
    }


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def svg_coord(spec: dict, x: float, y: float) -> tuple[float, float]:
    if spec.get("origin", "top-left") == "bottom-left":
        height = fnum(spec.get("height", 1000), "height")
        return x, height - y
    return x, y

def svg_line(x1, y1, x2, y2, style, extra=""):
    dash = f' stroke-dasharray="{esc(style["dash"])}"' if style["dash"] else ""
    return (
        f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" '
        f'stroke="{esc(style["stroke"])}" stroke-width="{style["stroke_width"]:g}" '
        f'fill="none"{dash}{extra}/>'
    )


def render_svg(spec: dict) -> str:
    width = fnum(spec.get("width", 1000), "width")
    height = fnum(spec.get("height", 700), "height")
    view = spec.get("viewBox", [0, 0, width, height])
    if not isinstance(view, list) or len(view) != 4:
        raise ValueError("viewBox must be [x,y,width,height]")
    vx, vy, vw, vh = [fnum(v, "viewBox") for v in view]
    title = esc(spec.get("title", "AEC drawing"))
    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:g}" height="{height:g}" viewBox="{vx:g} {vy:g} {vw:g} {vh:g}">',
        f"<title>{title}</title>",
        '<rect x="0" y="0" width="100%" height="100%" fill="white"/>',
    ]
    for index, entity in enumerate(spec["entities"]):
        if not isinstance(entity, dict):
            raise ValueError(f"entities[{index}] must be an object")
        kind = entity.get("type")
        style = layer_style(spec, entity)
        attrs = f' data-layer="{esc(style["layer"])}"'
        if kind == "line":
            x1, y1 = svg_coord(spec, fnum(entity["x1"], "x1"), fnum(entity["y1"], "y1"))
            x2, y2 = svg_coord(spec, fnum(entity["x2"], "x2"), fnum(entity["y2"], "y2"))
            body.append(svg_line(x1, y1, x2, y2, style, attrs))
        elif kind == "polyline":
            pts = [svg_coord(spec, *p) for p in points(entity["points"])]
            pts_text = " ".join(f"{x:g},{y:g}" for x, y in pts)
            tag = "polygon" if entity.get("closed", False) else "polyline"
            dash = f' stroke-dasharray="{esc(style["dash"])}"' if style["dash"] else ""
            body.append(
                f'<{tag} points="{pts_text}" stroke="{esc(style["stroke"])}" '
                f'stroke-width="{style["stroke_width"]:g}" fill="{esc(style["fill"])}"{dash}{attrs}/>'
            )
        elif kind == "rect":
            x, y = svg_coord(spec, fnum(entity["x"], "x"), fnum(entity["y"], "y"))
            w, h = fnum(entity["width"], "width"), fnum(entity["height"], "height")
            if spec.get("origin", "top-left") == "bottom-left":
                y -= h
            body.append(
                f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" '
                f'stroke="{esc(style["stroke"])}" stroke-width="{style["stroke_width"]:g}" '
                f'fill="{esc(style["fill"])}"{attrs}/>'
            )
        elif kind == "circle":
            cx, cy = svg_coord(spec, fnum(entity["cx"], "cx"), fnum(entity["cy"], "cy"))
            r = fnum(entity["r"], "r")
            body.append(
                f'<circle cx="{cx:g}" cy="{cy:g}" r="{r:g}" stroke="{esc(style["stroke"])}" '
                f'stroke-width="{style["stroke_width"]:g}" fill="{esc(style["fill"])}"{attrs}/>'
            )

        elif kind == "text":
            x, y = svg_coord(spec, fnum(entity["x"], "x"), fnum(entity["y"], "y"))
            size = fnum(entity.get("size", 16), "size")
            anchor = str(entity.get("anchor", "start"))
            if anchor not in {"start", "middle", "end"}:
                raise ValueError("text anchor must be start, middle, or end")
            body.append(
                f'<text x="{x:g}" y="{y:g}" font-family="Arial, sans-serif" '
                f'font-size="{size:g}" text-anchor="{anchor}" fill="{esc(style["stroke"])}"{attrs}>'
                f'{esc(entity.get("text", ""))}</text>'
            )
        elif kind == "dimension":
            x1, y1 = fnum(entity["x1"], "x1"), fnum(entity["y1"], "y1")
            x2, y2 = fnum(entity["x2"], "x2"), fnum(entity["y2"], "y2")
            offset = fnum(entity.get("offset", 20), "offset")
            dx, dy = x2 - x1, y2 - y1
            length = math.hypot(dx, dy)
            if length == 0:
                raise ValueError("dimension endpoints must differ")
            nx, ny = -dy / length, dx / length
            ax, ay = x1 + nx * offset, y1 + ny * offset
            bx, by = x2 + nx * offset, y2 + ny * offset
            sx1, sy1 = svg_coord(spec, x1, y1)
            sax, say = svg_coord(spec, ax, ay)
            sx2, sy2 = svg_coord(spec, x2, y2)
            sbx, sby = svg_coord(spec, bx, by)
            body.extend([
                svg_line(sx1, sy1, sax, say, style, attrs),
                svg_line(sx2, sy2, sbx, sby, style, attrs),
                svg_line(sax, say, sbx, sby, style, attrs),
            ])
            label = entity.get("label", f"{length:g}")
            mx, my = svg_coord(spec, (ax + bx) / 2, (ay + by) / 2)
            body.append(
                f'<text x="{mx:g}" y="{my:g}" font-family="Arial, sans-serif" font-size="14" '
                f'text-anchor="middle" fill="{esc(style["stroke"])}"{attrs}>{esc(label)}</text>'
            )
        else:
            raise ValueError(f"unsupported entity type: {kind!r}")
    note = spec.get("status", "CONCEPT / NOT FOR CONSTRUCTION")
    body.append(
        f'<text x="{vx + 10:g}" y="{vy + vh - 10:g}" font-family="Arial, sans-serif" '
        f'font-size="12" fill="#666">{esc(note)}</text>'
    )
    body.append("</svg>")
    return "\n".join(body) + "\n"


def dxf_pair(code, value):
    return f"{code}\n{value}\n"


def dxf_line(parts, x1, y1, x2, y2, layer):
    parts.extend([
        dxf_pair(0, "LINE"), dxf_pair(8, layer),
        dxf_pair(10, f"{x1:g}"), dxf_pair(20, f"{y1:g}"),
        dxf_pair(11, f"{x2:g}"), dxf_pair(21, f"{y2:g}"),
    ])


def render_dxf(spec: dict) -> str:
    parts = [dxf_pair(0, "SECTION"), dxf_pair(2, "HEADER"), dxf_pair(0, "ENDSEC"),
             dxf_pair(0, "SECTION"), dxf_pair(2, "ENTITIES")]
    for index, entity in enumerate(spec["entities"]):
        if not isinstance(entity, dict):
            raise ValueError(f"entities[{index}] must be an object")
        kind = entity.get("type")
        layer = str(entity.get("layer", "default"))
        if kind == "line":
            dxf_line(parts, fnum(entity["x1"], "x1"), fnum(entity["y1"], "y1"),
                     fnum(entity["x2"], "x2"), fnum(entity["y2"], "y2"), layer)
        elif kind in {"polyline", "rect"}:
            if kind == "rect":
                x, y = fnum(entity["x"], "x"), fnum(entity["y"], "y")
                w, h = fnum(entity["width"], "width"), fnum(entity["height"], "height")
                pts = [(x, y), (x+w, y), (x+w, y+h), (x, y+h)]
                closed = True
            else:
                pts = points(entity["points"])
                closed = bool(entity.get("closed", False))
            pairs = list(zip(pts, pts[1:]))
            if closed:
                pairs.append((pts[-1], pts[0]))
            for (x1, y1), (x2, y2) in pairs:
                dxf_line(parts, x1, y1, x2, y2, layer)

        elif kind == "circle":
            parts.extend([
                dxf_pair(0, "CIRCLE"), dxf_pair(8, layer),
                dxf_pair(10, f"{fnum(entity['cx'], 'cx'):g}"),
                dxf_pair(20, f"{fnum(entity['cy'], 'cy'):g}"),
                dxf_pair(40, f"{fnum(entity['r'], 'r'):g}"),
            ])
        elif kind == "text":
            parts.extend([
                dxf_pair(0, "TEXT"), dxf_pair(8, layer),
                dxf_pair(10, f"{fnum(entity['x'], 'x'):g}"),
                dxf_pair(20, f"{fnum(entity['y'], 'y'):g}"),
                dxf_pair(40, f"{fnum(entity.get('size', 16), 'size'):g}"),
                dxf_pair(1, str(entity.get("text", ""))),
            ])
        elif kind == "dimension":
            x1, y1 = fnum(entity["x1"], "x1"), fnum(entity["y1"], "y1")
            x2, y2 = fnum(entity["x2"], "x2"), fnum(entity["y2"], "y2")
            offset = fnum(entity.get("offset", 20), "offset")
            dx, dy = x2 - x1, y2 - y1
            length = math.hypot(dx, dy)
            if length == 0:
                raise ValueError("dimension endpoints must differ")
            nx, ny = -dy / length, dx / length
            ax, ay = x1 + nx * offset, y1 + ny * offset
            bx, by = x2 + nx * offset, y2 + ny * offset
            dxf_line(parts, x1, y1, ax, ay, layer)
            dxf_line(parts, x2, y2, bx, by, layer)
            dxf_line(parts, ax, ay, bx, by, layer)
            parts.extend([
                dxf_pair(0, "TEXT"), dxf_pair(8, layer),
                dxf_pair(10, f"{(ax+bx)/2:g}"), dxf_pair(20, f"{(ay+by)/2:g}"),
                dxf_pair(40, "14"), dxf_pair(1, str(entity.get("label", f"{length:g}"))),
            ])
        else:
            raise ValueError(f"unsupported entity type: {kind!r}")
    parts.extend([dxf_pair(0, "ENDSEC"), dxf_pair(0, "EOF")])
    return "".join(parts)


def main():
    parser = argparse.ArgumentParser(description="Render explicit AEC drawing JSON to SVG or DXF")
    parser.add_argument("spec", type=Path, help="input JSON drawing specification")
    parser.add_argument("output", type=Path, nargs="?", help="output .svg or .dxf")
    parser.add_argument("--format", choices=("svg", "dxf"), dest="fmt")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    spec = load_spec(args.spec)
    # Render during validation so all entity fields/types are checked.
    fmt = args.fmt or (args.output.suffix.lower().lstrip(".") if args.output else "svg")
    if fmt not in {"svg", "dxf"}:
        raise ValueError("format must be svg or dxf")
    rendered = render_svg(spec) if fmt == "svg" else render_dxf(spec)
    if args.validate_only:
        print(f"VALID: {len(spec['entities'])} entities; format={fmt}")
        return
    if args.output is None:
        raise ValueError("output path is required unless --validate-only is used")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    print(f"WROTE {args.output} ({len(spec['entities'])} entities)")


if __name__ == "__main__":
    main()

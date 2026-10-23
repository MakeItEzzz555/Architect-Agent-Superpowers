"""Shape/type preconditions for building-spec.v1, before geometric arithmetic."""
import math


def finite(value):
    try:
        return type(value) in (int, float) and math.isfinite(value)
    except OverflowError:
        return False


def shape_errors(spec):
    errors = []
    if spec.get("schema_version", "building-spec.v1") != "building-spec.v1":
        errors.append("unsupported schema_version (expected building-spec.v1)")
    if not isinstance(spec.get("project"), dict):
        errors.append("project must be an object")
    for group in ("levels", "grids", "walls", "openings", "rooms", "sheets"):
        items = spec.get(group)
        if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
            errors.append(f"{group} must be an array of objects")
    if errors:
        return errors

    def numbers(value, path):
        if type(value) in (int, float) and not finite(value):
            errors.append(f"{path} must be finite")
        elif isinstance(value, dict):
            for key, item in value.items():
                numbers(item, f"{path}.{key}")
        elif isinstance(value, list):
            for i, item in enumerate(value):
                numbers(item, f"{path}[{i}]")
    numbers(spec, "spec")
    for key in ("name", "number", "architect", "drawn_by", "status", "revision", "date"):
        if not isinstance(spec["project"].get(key), str):
            errors.append(f"project.{key} must be a string")
    for key in ("client", "address", "checked_by"):
        if key in spec["project"] and not isinstance(spec["project"][key], str):
            errors.append(f"project.{key} must be a string")
    if "north_deg" in spec["project"] and not finite(spec["project"]["north_deg"]):
        errors.append("project.north_deg must be a finite number")
    numeric = {"levels": ("elevation", "height"), "walls": ("thickness",),
               "openings": ("offset", "width", "height"), "sheets": ("scale",)}
    for group in ("levels", "grids", "walls", "openings", "rooms", "sheets"):
        for index, item in enumerate(spec[group]):
            label = f"{group}[{index}]"
            id_key = "number" if group == "sheets" else "id"
            ident = item.get(id_key)
            if not isinstance(ident, str) or not ident.strip() or len(ident.encode("utf-8")) > 255:
                errors.append(f"{label}.{id_key} must be a nonempty string of at most 255 bytes")
            for key in numeric.get(group, ()):
                # Missing wall/opening fields retain the existing precise diagnostics.
                if key in item and not finite(item[key]):
                    errors.append(f"{label}.{key} must be a finite number, not text or boolean")
            for key in ("level", "wall", "kind", "type", "size", "hinge", "opens"):
                if key in item and not isinstance(item[key], str):
                    errors.append(f"{label}.{key} must be a string")
            if group in ("levels", "rooms") and not isinstance(item.get("name"), str):
                errors.append(f"{label}.name must be a string")
            if group in ("walls", "grids"):
                for key in ("start", "end"):
                    if key in item and not point(item[key]):
                        errors.append(f"{label}.{key} must contain exactly two finite numeric coordinates")
            if group == "rooms":
                boundary = item.get("boundary", [])
                if not isinstance(boundary, list) or any(not point(p) for p in boundary):
                    errors.append(f"{label}.boundary must be an array of finite 2D points")
            if group == "openings" and "sill" in item and not finite(item["sill"]):
                errors.append(f"{label}.sill must be a finite number")
            if group == "sheets" and isinstance(ident, str) and ("/" in ident or "\\" in ident or ident in (".", "..")):
                errors.append(f"{label}.number cannot contain path separators")
    return errors


def point(value):
    return isinstance(value, list) and len(value) == 2 and all(finite(v) for v in value)

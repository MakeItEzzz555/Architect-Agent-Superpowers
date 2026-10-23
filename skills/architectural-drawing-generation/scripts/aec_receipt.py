"""Versioned, byte-bound local verification receipts; no native acceptance implied."""
import hashlib
import importlib.metadata
import json
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

UNVERIFIED = {
    "source_detail_coverage": "Only supported plan primitives are checked; a complete brief/image/detail inventory and human resolution are required before claiming completeness.",
    "pdf_visibility": "Raster visibility, clipping, fonts, text collisions and door-arc plotting need visual review.",
    "other_dxf_geometry": "Grid positions, dimensions, hatches, topology and unsupported entity types are not measured.",
    "semantic_3d": "No semantic 3D, materials, render model or image/maquette reconstruction has been verified.",
    "autocad_native": "No licensed AutoCAD open/AUDIT/edit/plot/DWG roundtrip evidence.",
    "native_identity_mapping": "GRIDLINE XDATA and DXF handles are not validated cross-application identities; lost associations are inferred geometrically.",
    "ifc_ids": "IFC schema, IDS and BIM exchange were not run.",
    "professional_review": "No architectural, engineering or regulatory approval is established.",
    "atomic_publication": "Build still writes mutable output files; use a fresh output directory per revision.",
}


def digest(data):
    return hashlib.sha256(data).hexdigest() if data is not None else None


def coverage():
    return {**{key: {"status": "NOT_RUN", "sheets": {}} for key in
               ("spec", "dxf_standards", "dxf_geometry", "pdf_vectors", "schedules")},
            **{key: {"status": "NOT_RUN", "reason": reason} for key, reason in UNVERIFIED.items()}}


def finish(out, standard, sources, outputs, gates, errors, warnings, checked):
    changed, consumed_count = [], 0
    for path, consumed in [(Path(name), data) for name, data in sources.items()] + [(out / name, data) for name, data in outputs.items()]:
        if consumed is None:
            continue
        consumed_count += 1
        try:
            with path.open("rb") as stream:
                same = stream.read(len(consumed) + 1) == consumed
        except OSError:
            same = False
        if not same:
            changed.append(str(path))
    if changed:
        errors.append(f"files changed during verification: {changed}")
    gates["snapshot_consistency"] = {"status": "FAIL" if changed else "PASS" if consumed_count else "NOT_RUN",
                                     "files_compared": consumed_count, "changed_paths": changed,
                                     "scope": "consumed bytes only; no atomic multi-file publication claim"}
    script_dir = Path(__file__).resolve().parent
    files = {name: digest((script_dir / name).read_bytes()) for name in
             ("aec_cad.py", "aec_readback.py", "building_spec.py", "aec_receipt.py")}
    schema = script_dir.parent / "references/building-spec.v1.schema.json"
    if schema.exists():
        files[schema.name] = digest(schema.read_bytes())
    revision = "UNKNOWN"
    dirty = None
    try:
        root = Path(subprocess.check_output(["git", "-C", str(script_dir), "rev-parse", "--show-toplevel"],
                                           text=True, stderr=subprocess.DEVNULL).strip())
        relative = str((script_dir / "aec_cad.py").relative_to(root))
        subprocess.check_output(["git", "-C", str(root), "ls-files", "--error-unmatch", relative], stderr=subprocess.DEVNULL)
        revision = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
        dirty = bool(subprocess.check_output(["git", "-C", str(root), "status", "--porcelain", "--", str(script_dir), str(schema)], text=True))
    except (OSError, ValueError, subprocess.CalledProcessError):
        pass
    versions = {}
    for name in ("ezdxf", "matplotlib", "pypdf"):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = "UNAVAILABLE"
    for gate in gates.values():
        states = [s["status"] for s in gate.get("sheets", {}).values()]
        if states:
            gate["status"] = ("FAIL" if "FAIL" in states else "PASS" if all(s == "PASS" for s in states)
                              else "NOT_RUN" if all(s == "NOT_RUN" for s in states) else "UNKNOWN")
    hashes = {name: digest(data) for name, data in outputs.items()}
    report = {"schema_version": "gridline-check-receipt.v1", "receipt_id": uuid.uuid4().hex,
              "timestamp": datetime.now(timezone.utc).isoformat(), "code_sha": revision,
              "validator_worktree_dirty": dirty,
              "validator": {"name": "Gridline supported-plan readback", "python": sys.version.split()[0],
                            "versions": versions, "files": files},
              "ruleset_id": "building-spec.v1/plan-readback.v1", "standard": standard,
              "status": "FAIL" if errors else "PASS", "return_code": 1 if errors else 0,
              "input_hashes": {name: digest(data) for name, data in sources.items()},
              "output_directory": str(out.resolve()), "operator": "UNKNOWN",
              "output_hashes": hashes,
              "artifact_manifest_hash": digest(json.dumps(hashes, sort_keys=True, separators=(",", ":")).encode()),
              "coverage": gates, "unverified_items": list(UNVERIFIED.values()),
              "native_host_verified": False, "architect_review_status": "NOT_RUN",
              "errors": errors, "warnings": warnings, "checked": checked}
    report["evidence_file_paths"] = [str(out / name) for name in outputs]
    data = json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    receipts = out / "receipts"
    receipts.mkdir(parents=True, exist_ok=True)
    # A new immutable receipt is retained even when the convenience report is overwritten.
    with (receipts / f"{report['receipt_id']}.json").open("x", encoding="utf-8") as stream:
        stream.write(data)
    (out / "check-report.json").write_text(data, encoding="utf-8")
    for error in errors:
        print(f"ERROR: {error}")
    for warning in warnings:
        print(f"WARNING: {warning}")
    print(f"{report['status']}: {len(errors)} errors, {len(warnings)} warnings; checked {len(checked)} items; scope=SUPPORTED_2D_ONLY")
    return report["return_code"]

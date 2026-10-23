import csv
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "architectural-drawing-generation"
SCRIPT = SKILL / "scripts" / "aec_cad.py"
EXAMPLE = SKILL / "references" / "example-house.building.json"

try:
    import ezdxf
except ImportError:
    if os.environ.get("GRIDLINE_REQUIRE_CAD_TESTS") == "1":
        raise
    ezdxf = None


def run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True)


@unittest.skipIf(ezdxf is None, "aec_cad.py needs ezdxf (pip install ezdxf matplotlib)")
class CoordinatedCadTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.out = self.dir / "out"

    def tearDown(self):
        self.tmp.cleanup()

    def spec(self, change=None):
        data = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        if change:
            change(data)
        path = self.dir / "spec.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def build_and_check(self, spec, *extra):
        built = run("build", spec, self.out, *extra)
        self.assertEqual(built.returncode, 0, built.stderr)
        return run("check", spec, self.out, *extra)

    def test_example_builds_a_coordinated_set_that_passes_its_checks(self):
        checked = self.build_and_check(EXAMPLE)
        self.assertEqual(checked.returncode, 0, checked.stdout)
        for number in ("A-101", "A-102"):
            doc = ezdxf.readfile(self.out / f"{number}.dxf")
            self.assertFalse(doc.audit().has_errors)
            self.assertIn(number, doc.layouts.names())
            self.assertTrue((self.out / f"{number}.pdf").read_bytes().startswith(b"%PDF"))
        with (self.out / "room-schedule.csv").open(encoding="utf-8") as fh:
            areas = {row["id"]: row["area_m2"] for row in csv.DictReader(fh)}
        self.assertEqual(areas["R01"], "59.16")  # 6.80 m x 8.70 m inside faces
        self.assertEqual(json.loads((self.out / "check-report.json").read_text(encoding="utf-8"))["errors"], [])

    def test_ncs_and_office_profiles(self):
        self.assertEqual(self.build_and_check(EXAMPLE, "--standard", "ncs").returncode, 0)
        office = self.dir / "office.json"
        office.write_text(json.dumps({"extends": "iso13567", "name": "Office",
                                      "layers": {"wall_external": {"name": "A-21----E-EXT"}}}), encoding="utf-8")
        checked = self.build_and_check(EXAMPLE, "--standard", office)
        self.assertEqual(checked.returncode, 0, checked.stdout)
        self.assertTrue(ezdxf.readfile(self.out / "A-101.dxf").layers.has_entry("A-21----E-EXT"))

    def test_opening_larger_than_its_wall_is_rejected(self):
        spec = self.spec(lambda d: d["openings"][4].update(width=9000))
        built = run("build", spec, self.out)
        self.assertEqual(built.returncode, 1)
        self.assertIn("W01", built.stderr)

    def test_plan_too_large_for_the_sheet_is_rejected(self):
        spec = self.spec(lambda d: d["sheets"][0].update(size="A4", scale=50))
        built = run("build", spec, self.out)
        self.assertEqual(built.returncode, 1)
        self.assertIn("A-101", built.stderr)

    def test_check_catches_a_schedule_that_no_longer_matches_the_geometry(self):
        self.assertEqual(self.build_and_check(EXAMPLE).returncode, 0)
        path = self.out / "room-schedule.csv"
        path.write_text(path.read_text(encoding="utf-8").replace("59.16", "61.00"), encoding="utf-8")
        checked = run("check", EXAMPLE, self.out)
        self.assertEqual(checked.returncode, 1)
        self.assertIn("room-schedule.csv", checked.stdout)

    def test_check_catches_off_standard_layers_and_empty_title_fields(self):
        self.assertEqual(self.build_and_check(EXAMPLE).returncode, 0)
        path = self.out / "A-101.dxf"
        doc = ezdxf.readfile(path)
        doc.modelspace().add_line((0, 0), (1000, 0), dxfattribs={"layer": "WALLS"})
        block = next(e for e in doc.layouts.get("A-101").query("INSERT") if e.dxf.name == "AAS-TITLE-BLOCK")
        next(a for a in block.attribs if a.dxf.tag == "DRAWN").dxf.text = ""
        doc.saveas(path)
        checked = run("check", EXAMPLE, self.out)
        self.assertEqual(checked.returncode, 1)
        self.assertIn("non-standard layer 'WALLS'", checked.stdout)
        self.assertIn("DRAWN is empty", checked.stdout)

    def test_check_catches_stale_window_height_type_and_sill(self):
        self.assertEqual(self.build_and_check(EXAMPLE).returncode, 0)
        path = self.out / "window-schedule.csv"
        rows = list(csv.DictReader(path.open(newline="", encoding="utf-8")))
        rows[0]["height_mm"] = "999"
        rows[0]["type"] = "Stale window type"
        rows[0]["sill_mm"] = "999"
        with path.open("w", newline="", encoding="utf-8") as out:
            writer = csv.DictWriter(out, fieldnames=rows[0])
            writer.writeheader()
            writer.writerows(rows)
        checked = run("check", EXAMPLE, self.out)
        self.assertEqual(checked.returncode, 1)
        self.assertIn("window-schedule.csv does not match spec fields", checked.stdout)

    def test_check_catches_duplicate_schedule_rows(self):
        self.assertEqual(self.build_and_check(EXAMPLE).returncode, 0)
        path = self.out / "window-schedule.csv"
        rows = path.read_text(encoding="utf-8").splitlines()
        path.write_text("\n".join([*rows, rows[1], ""]), encoding="utf-8")
        checked = run("check", EXAMPLE, self.out)
        self.assertEqual(checked.returncode, 1)
        self.assertIn("duplicate or missing IDs", checked.stdout)

    def test_check_catches_stale_revision_in_one_sheet(self):
        self.assertEqual(self.build_and_check(EXAMPLE).returncode, 0)
        path = self.out / "A-102.dxf"
        doc = ezdxf.readfile(path)
        block = next(e for e in doc.layouts.get("A-102").query("INSERT")
                     if e.dxf.name == "AAS-TITLE-BLOCK")
        next(a for a in block.attribs if a.dxf.tag == "REVISION").dxf.text = "OLD"
        doc.saveas(path)
        checked = run("check", EXAMPLE, self.out)
        self.assertEqual(checked.returncode, 1)
        self.assertIn("A-102: title block REVISION differs", checked.stdout)

    def test_incomplete_spec_reports_errors_instead_of_crashing(self):
        def strip(d):
            del d["openings"]
            del d["walls"][0]["thickness"]
        built = run("build", self.spec(strip), self.out)
        self.assertEqual(built.returncode, 1)
        self.assertIn("wall E1: missing thickness", built.stderr)
        self.assertNotIn("Traceback", built.stderr)

    def test_issued_status_requires_a_checker(self):
        spec = self.spec(lambda d: d["project"].update(status="FOR CONSTRUCTION", checked_by=""))
        built = run("build", spec, self.out)
        self.assertEqual(built.returncode, 1)
        self.assertIn("checked_by", built.stderr)


if __name__ == "__main__":
    unittest.main()

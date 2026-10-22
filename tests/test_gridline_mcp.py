import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "skills/architectural-drawing-generation/scripts"
sys.path.insert(0, str(TOOLS))
import gridline_mcp

EXAMPLE = ROOT / "skills/architectural-drawing-generation/references/example-house.building.json"


class GridlineReadOnlyMCPTests(unittest.TestCase):
    def test_requires_opt_in_project_root(self):
        with self.assertRaisesRegex(ValueError, "GRIDLINE_MCP_PROJECT_ROOT"):
            gridline_mcp.compare_revisions("one.json", "two.json", project_root="")

    def test_rejects_outside_root_and_traversal(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            (base / "source.json").write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "authorized"):
                gridline_mcp.project_file("../../etc/passwd", base)
            with self.assertRaisesRegex(ValueError, "authorized"):
                gridline_mcp.project_file(str(EXAMPLE), base)

    def test_rejects_symlink_escape(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            (base / "escape.json").symlink_to(EXAMPLE)
            with self.assertRaisesRegex(ValueError, "authorized"):
                gridline_mcp.project_file("escape.json", base)

    def test_rejects_non_json_and_large_files(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            (base / "note.txt").write_text("x", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "JSON file"):
                gridline_mcp.project_file("note.txt", base)
            (base / "huge.json").write_bytes(b"x" * (gridline_mcp.MAX_SPEC_SIZE + 1))
            with self.assertRaisesRegex(ValueError, "5 MB"):
                gridline_mcp.project_file("huge.json", base)

    def test_reads_under_root_without_mutating_inputs(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            spec = json.loads(EXAMPLE.read_text(encoding="utf-8"))
            old, new = base / "old.json", base / "new.json"
            old.write_text(json.dumps(spec), encoding="utf-8")
            spec["openings"][4]["width"] = 2150
            new.write_text(json.dumps(spec), encoding="utf-8")
            before_bytes, after_bytes = old.read_bytes(), new.read_bytes()
            result = gridline_mcp.compare_revisions("old.json", "new.json", project_root=td)
            self.assertIn("window-schedule.csv", result["schedules_to_recheck"])
            self.assertEqual(before_bytes, old.read_bytes())
            self.assertEqual(after_bytes, new.read_bytes())

    def test_capabilities_do_not_claim_native_connections(self):
        cap = gridline_mcp.capabilities()
        self.assertFalse(cap["native_autocad_or_revit_connection"])
        self.assertFalse(cap["edits_models"])

    def test_server_without_explicit_root_refuses_start(self):
        env = dict(os.environ)
        env.pop("GRIDLINE_MCP_PROJECT_ROOT", None)
        p = subprocess.run([sys.executable, str(TOOLS / "gridline_mcp.py")],
                           capture_output=True, text=True, env=env, timeout=10)
        self.assertEqual(p.returncode, 2)
        self.assertIn("GRIDLINE_MCP_PROJECT_ROOT", p.stderr)


if __name__ == "__main__":
    unittest.main()

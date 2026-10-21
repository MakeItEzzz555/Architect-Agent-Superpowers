import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "aec_draw.py"
spec = importlib.util.spec_from_file_location("aec_draw", MODULE_PATH)
aec_draw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(aec_draw)


class AecDrawTests(unittest.TestCase):
    def setUp(self):
        self.example = aec_draw.load_spec(ROOT / "examples" / "concept-plan.drawing.json")

    def test_svg_contains_geometry_and_status(self):
        svg = aec_draw.render_svg(self.example)
        self.assertIn("<svg", svg)
        self.assertIn("<rect", svg)
        self.assertIn("<line", svg)
        self.assertIn("ROOM A", svg)
        self.assertIn("CONCEPT / NOT FOR CONSTRUCTION", svg)

    def test_dxf_contains_entities(self):
        dxf = aec_draw.render_dxf(self.example)
        self.assertIn("SECTION\n2\nENTITIES", dxf)
        self.assertIn("LINE", dxf)
        self.assertIn("TEXT", dxf)
        self.assertTrue(dxf.endswith("0\nEOF\n"))

    def test_invalid_zero_length_dimension_rejected(self):
        bad = {
            "entities": [
                {"type": "dimension", "x1": 1, "y1": 1, "x2": 1, "y2": 1}
            ]
        }
        with self.assertRaisesRegex(ValueError, "endpoints must differ"):
            aec_draw.render_svg(bad)

    def test_example_roundtrip_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            svg = root / "drawing.svg"
            dxf = root / "drawing.dxf"
            svg.write_text(aec_draw.render_svg(self.example), encoding="utf-8")
            dxf.write_text(aec_draw.render_dxf(self.example), encoding="utf-8")
            self.assertGreater(svg.stat().st_size, 100)
            self.assertGreater(dxf.stat().st_size, 100)


if __name__ == "__main__":
    unittest.main()

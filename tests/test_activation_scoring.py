import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "scripts" / "score-activation-evals.py"
spec = importlib.util.spec_from_file_location("activation_scoring", MODULE)
scorer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scorer)


class ActivationScoringTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.cases = {"p1": "alpha", "p2": "alpha", "p3": "beta", "p4": "beta", "n1": None, "n2": None}
        self.fixture = self.root / "cases.json"
        self.fixture.write_text(json.dumps({"schemaVersion": 1, "cases": [{"id": k, "expected_skill": v} for k, v in self.cases.items()]}))

    def observations(self, values=None, provider="codex", version=None):
        path = self.root / f"observations-{len(list(self.root.glob('observations-*')))}.jsonl"
        values = self.cases if values is None else values
        items = []
        for cid, activated in values.items():
            row = {"case_id": cid, "provider": provider, "activated_skill": activated}
            if version is not None:
                row["runtime_version"] = version
            items.append(row)
        path.write_text("\n".join(json.dumps(x) for x in items) + "\n")
        return path

    def test_perfect(self):
        result = scorer.score(self.cases, scorer.read_observations(self.observations(), self.cases))
        self.assertEqual((result["accuracy"], result["positive_recall"], result["negative_false_positive_rate"]), (1, 1, 0))

    def test_positive_miss_and_negative_false_positive(self):
        values = dict(self.cases, p1=None, n1="alpha")
        result = scorer.score(self.cases, scorer.read_observations(self.observations(values), self.cases))
        self.assertAlmostEqual(result["accuracy"], 4/6)
        self.assertEqual(result["positive_recall"], 0.75)
        self.assertEqual(result["negative_false_positive_rate"], 0.5)
        self.assertEqual(result["per_skill"]["alpha"]["recall"], 0.5)

    def test_duplicate_observation(self):
        path = self.observations()
        path.write_text(path.read_text() + path.read_text().splitlines()[0] + "\n")
        with self.assertRaisesRegex(scorer.EvalError, "duplicate"):
            scorer.read_observations(path, self.cases)

    def test_missing_observation(self):
        path = self.observations({k: v for k, v in self.cases.items() if k != "p1"})
        with self.assertRaisesRegex(scorer.EvalError, "missing observations"):
            scorer.read_observations(path, self.cases)

    def test_unknown_case(self):
        path = self.observations(dict(self.cases, unexpected="alpha"))
        with self.assertRaisesRegex(scorer.EvalError, "unknown case_id"):
            scorer.read_observations(path, self.cases)

    def test_mixed_provider(self):
        path = self.observations()
        path.write_text(path.read_text().replace('"provider": "codex"', '"provider": "claude"', 1))
        with self.assertRaisesRegex(scorer.EvalError, "mixed providers"):
            scorer.read_observations(path, self.cases)

    def test_mixed_runtime_version(self):
        path = self.observations(version="1")
        path.write_text(path.read_text().replace('"runtime_version": "1"', '"runtime_version": "2"', 1))
        with self.assertRaisesRegex(scorer.EvalError, "mixed runtime_version"):
            scorer.read_observations(path, self.cases)

    def test_partial_runtime_version(self):
        path = self.observations(version="1")
        path.write_text(path.read_text().replace(', "runtime_version": "1"', '', 1))
        with self.assertRaisesRegex(scorer.EvalError, "supplied for all"):
            scorer.read_observations(path, self.cases)

    def test_missing_activation_field(self):
        path = self.observations()
        path.write_text(path.read_text().replace(', "activated_skill": "alpha"', '', 1))
        with self.assertRaisesRegex(scorer.EvalError, "requires"):
            scorer.read_observations(path, self.cases)

    def test_invalid_fixture_duplicate(self):
        self.fixture.write_text(json.dumps({"schemaVersion": 1, "cases": [{"id": "x", "expected_skill": None}] * 2}))
        with self.assertRaisesRegex(scorer.EvalError, "duplicate fixture"):
            scorer.read_cases(self.fixture)

    def test_invalid_fixture_expected_type(self):
        self.fixture.write_text(json.dumps({"schemaVersion": 1, "cases": [{"id": "x", "expected_skill": 3}]}))
        with self.assertRaisesRegex(scorer.EvalError, "invalid expected_skill"):
            scorer.read_cases(self.fixture)

    def test_regression_even_when_accuracy_unchanged(self):
        before = scorer.read_observations(self.observations(dict(self.cases, p1=None)), self.cases)
        after = scorer.read_observations(self.observations(dict(self.cases, p2=None)), self.cases)
        diff = scorer.compare(self.cases, before, after)
        self.assertEqual(diff["accuracy_delta"], 0)
        self.assertEqual(diff["newly_failing_cases"], ["p2"])
        self.assertEqual(diff["recovered_cases"], ["p1"])

    def test_cross_provider_comparison_rejected(self):
        before = scorer.read_observations(self.observations(provider="claude"), self.cases)
        after = scorer.read_observations(self.observations(), self.cases)
        with self.assertRaisesRegex(scorer.EvalError, "providers differ"):
            scorer.compare(self.cases, before, after)

    def test_cross_version_comparison_allowed(self):
        before = scorer.read_observations(self.observations(version="1"), self.cases)
        after = scorer.read_observations(self.observations(version="2"), self.cases)
        self.assertEqual(scorer.compare(self.cases, before, after)["newly_failing_cases"], [])

    def test_cli_json_output_and_provenance(self):
        output = self.root / "report.json"
        self.assertEqual(scorer.main(["--cases", str(self.fixture), "--observations", str(self.observations()), "--json-out", str(output)]), 0)
        result = json.loads(output.read_text())
        self.assertTrue(result["passed"])
        self.assertEqual(len(result["provenance"]["cases_sha256"]), 64)

    def test_cli_refuses_to_overwrite_fixture(self):
        original = self.fixture.read_bytes()
        code = scorer.main(["--cases", str(self.fixture), "--observations", str(self.observations()),
                            "--json-out", str(self.fixture)])
        self.assertEqual(code, 2)
        self.assertEqual(self.fixture.read_bytes(), original)

    def test_cli_refuses_to_overwrite_observations(self):
        observations = self.observations()
        original = observations.read_bytes()
        code = scorer.main(["--cases", str(self.fixture), "--observations", str(observations),
                            "--json-out", str(observations)])
        self.assertEqual(code, 2)
        self.assertEqual(observations.read_bytes(), original)

    def test_cli_rejects_per_skill_failure(self):
        values = dict(self.cases, p1=None)
        code = scorer.main(["--cases", str(self.fixture), "--observations", str(self.observations(values)), "--min-accuracy", "0", "--min-positive-recall", "0", "--min-skill-recall", "0.75"])
        self.assertEqual(code, 1)

    def test_cli_rejects_new_case_regression(self):
        before = self.observations(dict(self.cases, p1=None))
        after = self.observations(dict(self.cases, p2=None))
        code = scorer.main(["--cases", str(self.fixture), "--observations", str(after), "--baseline", str(before), "--min-accuracy", "0", "--min-positive-recall", "0", "--fail-on-regression"])
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Score recorded Agent Skills activations; never calls a model."""
import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path


class EvalError(ValueError):
    pass


def read_cases(path):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise EvalError(f"cannot read cases: {exc}") from exc
    if not isinstance(data, dict) or data.get("schemaVersion") != 1 or not isinstance(data.get("cases"), list) or not data["cases"]:
        raise EvalError("cases must contain schemaVersion=1 and a nonempty cases list")
    cases = {}
    for case in data["cases"]:
        if not isinstance(case, dict) or not isinstance(case.get("id"), str) or not case["id"].strip() or "expected_skill" not in case:
            raise EvalError("each case needs a nonempty string id and expected_skill")
        target = case["expected_skill"]
        if target is not None and (not isinstance(target, str) or not target.strip()):
            raise EvalError(f"invalid expected_skill for {case['id']}")
        if case["id"] in cases:
            raise EvalError(f"duplicate fixture case: {case['id']}")
        cases[case["id"]] = target
    return cases


def read_observations(path, cases):
    observations = {}
    provider = None
    version = None
    version_seen = None
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise EvalError(f"cannot read observations: {exc}") from exc
    for line_no, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except ValueError as exc:
            raise EvalError(f"observations line {line_no}: invalid JSON: {exc}") from exc
        if not isinstance(item, dict) or not isinstance(item.get("case_id"), str) or not isinstance(item.get("provider"), str) or not item["provider"].strip() or "activated_skill" not in item:
            raise EvalError(f"observations line {line_no}: requires case_id, provider, activated_skill")
        cid = item["case_id"]
        skill = item["activated_skill"]
        if skill is not None and (not isinstance(skill, str) or not skill.strip()):
            raise EvalError(f"observations line {line_no}: activated_skill must be a name or null")
        if cid not in cases:
            raise EvalError(f"observations line {line_no}: unknown case_id {cid}")
        if cid in observations:
            raise EvalError(f"observations line {line_no}: duplicate case_id {cid}")
        if provider is not None and item["provider"] != provider:
            raise EvalError("mixed providers in one observation file")
        provider = item["provider"]
        has_version = "runtime_version" in item
        if version_seen is not None and has_version != version_seen:
            raise EvalError("runtime_version must be supplied for all cases or none")
        version_seen = has_version
        if has_version:
            if not isinstance(item["runtime_version"], str) or not item["runtime_version"].strip():
                raise EvalError("runtime_version must be a nonempty string")
            if version is not None and item["runtime_version"] != version:
                raise EvalError("mixed runtime_version values in one observation file")
            version = item["runtime_version"]
        observations[cid] = skill
    missing = sorted(set(cases) - set(observations))
    if missing:
        raise EvalError(f"missing observations for {len(missing)} cases: {', '.join(missing[:6])}")
    return {"provider": provider, "runtime_version": version, "observations": observations}


def score(cases, observations):
    actual = observations["observations"]
    positive = [cid for cid, expected in cases.items() if expected is not None]
    negative = [cid for cid, expected in cases.items() if expected is None]
    correct = [cid for cid, expected in cases.items() if actual[cid] == expected]
    per_skill = {}
    for skill in sorted(set(x for x in cases.values() if x is not None)):
        matching = [cid for cid in positive if cases[cid] == skill]
        count = sum(actual[cid] == skill for cid in matching)
        per_skill[skill] = {"correct": count, "total": len(matching), "recall": count / len(matching)}
    return {
        "provider": observations["provider"],
        "runtime_version": observations["runtime_version"],
        "total": len(cases), "correct": len(correct),
        "accuracy": len(correct) / len(cases),
        "positive_recall": sum(cid in correct for cid in positive) / len(positive) if positive else 1.0,
        "negative_false_positive_rate": sum(actual[cid] is not None for cid in negative) / len(negative) if negative else 0.0,
        "per_skill": per_skill,
        "failures": [{"case_id": cid, "expected_skill": expected, "activated_skill": actual[cid]}
                     for cid, expected in cases.items() if actual[cid] != expected],
    }


def compare(cases, baseline, candidate):
    if baseline["provider"] != candidate["provider"]:
        raise EvalError("baseline and candidate providers differ")
    before = score(cases, baseline)
    after = score(cases, candidate)
    b_fail = {x["case_id"] for x in before["failures"]}
    a_fail = {x["case_id"] for x in after["failures"]}
    return {
        "accuracy_delta": after["accuracy"] - before["accuracy"],
        "positive_recall_delta": after["positive_recall"] - before["positive_recall"],
        "negative_false_positive_rate_delta": after["negative_false_positive_rate"] - before["negative_false_positive_rate"],
        "newly_failing_cases": sorted(a_fail - b_fail),
        "recovered_cases": sorted(b_fail - a_fail),
        "per_skill_recall_delta": {name: after["per_skill"][name]["recall"] - before["per_skill"][name]["recall"]
                                   for name in after["per_skill"]},
    }


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def threshold(value):
    number = float(value)
    if not 0 <= number <= 1:
        raise argparse.ArgumentTypeError("threshold must be between 0 and 1")
    return number


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=Path(__file__).resolve().parents[1] / "evals/activation-cases.json")
    parser.add_argument("--observations", type=Path, required=True, help="JSONL: case_id, provider, activated_skill, optional runtime_version")
    parser.add_argument("--baseline", type=Path, help="prior observations for regression comparison")
    parser.add_argument("--min-accuracy", type=threshold, default=0.85)
    parser.add_argument("--min-positive-recall", type=threshold, default=0.80)
    parser.add_argument("--max-negative-fpr", type=threshold, default=0.10)
    parser.add_argument("--min-skill-recall", type=threshold, default=None)
    parser.add_argument("--fail-on-regression", action="store_true", help="reject any newly failing case (requires --baseline)")
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args(argv)
    if args.fail_on_regression and not args.baseline:
        parser.error("--fail-on-regression requires --baseline")
    try:
        cases = read_cases(args.cases)
        candidate = read_observations(args.observations, cases)
        result = score(cases, candidate)
        result["provenance"] = {"cases_sha256": sha256(args.cases), "observations_sha256": sha256(args.observations)}
        if args.baseline:
            baseline = read_observations(args.baseline, cases)
            result["comparison"] = compare(cases, baseline, candidate)
            result["provenance"]["baseline_sha256"] = sha256(args.baseline)
        failures = []
        if result["accuracy"] < args.min_accuracy:
            failures.append("accuracy below threshold")
        if result["positive_recall"] < args.min_positive_recall:
            failures.append("positive recall below threshold")
        if result["negative_false_positive_rate"] > args.max_negative_fpr:
            failures.append("negative false-positive rate above threshold")
        if args.min_skill_recall is not None:
            for name, metrics in result["per_skill"].items():
                if metrics["recall"] < args.min_skill_recall:
                    failures.append(f"{name}: per-skill recall below threshold")
        if args.fail_on_regression and result["comparison"]["newly_failing_cases"]:
            failures.append("newly failing cases: " + ", ".join(result["comparison"]["newly_failing_cases"]))
        result["passed"] = not failures
        result["gate_failures"] = failures
        report = json.dumps(result, indent=2, sort_keys=True) + "\n"
        if args.json_out:
            protected = [args.cases, args.observations]
            if args.baseline:
                protected.append(args.baseline)
            if args.json_out.resolve() in {path.resolve() for path in protected}:
                raise EvalError("--json-out must not overwrite evaluation inputs")
            temp_path = None
            try:
                with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=args.json_out.parent,
                                                 prefix=".activation-report-", suffix=".tmp", delete=False) as handle:
                    temp_path = Path(handle.name)
                    handle.write(report)
                os.replace(temp_path, args.json_out)
            finally:
                if temp_path is not None:
                    temp_path.unlink(missing_ok=True)
        print(report, end="")
        return 0 if result["passed"] else 1
    except (EvalError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

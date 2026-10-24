# Skill evaluation

The repository keeps provider-neutral activation cases in `evals/activation-cases.json`.

## What CI proves

CI checks that every stable canonical skill has at least two positive natural-language activation cases; case IDs are unique; target skills exist in `skills/manifest.json`; negative controls are present; and provider-copied skills remain synchronized.

These are **structural guarantees**, not claims about model behavior.

## Behavioral evaluation

A real model/runtime must execute the prompts to measure whether the intended skill activates and whether the result follows the skill contract.

Claude Code provides `claude plugin eval`. Those evals make real model calls and consume plan/API usage, so they are intentionally not run automatically by the repository's free CI.

For Codex/OpenAI, use the portable cases as the seed set for skill evals and compare behavior before and after skill changes.

For Gemini CLI, use the same prompts to verify skill activation after `/skills reload` or in a clean extension session.

## Offline scoring of real observations

Run every fixture through the actual target provider with Gridline installed. Record the observed skill, not the expected answer, as JSONL:

```json
{"case_id":"orchestrator-multidiscipline-01","provider":"codex","runtime_version":"recorded-runtime-version","activated_skill":"architecture-orchestrator"}
```

Use `null` for no activation, including negative controls. Record every case from `evals/activation-cases.json` exactly once, one provider per file, and consistent optional `runtime_version`. Never synthesize expected answers and report them as behavioral evidence.

```bash
python3 scripts/score-activation-evals.py --observations codex-observations.jsonl --json-out codex-report.json
python3 scripts/score-activation-evals.py --observations codex-after.jsonl --baseline codex-before.jsonl --fail-on-regression --min-skill-recall 0.75
```

The dependency-free scorer reports overall accuracy, positive recall, negative-control false-positive rate, per-skill recall, failed cases and SHA-256 input provenance. Default gates: accuracy >= 0.85, positive recall >= 0.80, negative false-positive rate <= 0.10. Baseline comparisons identify newly failing and recovered cases even when aggregate accuracy is unchanged; different runtime versions are allowed, different providers are not. Exit codes: 0 pass, 1 gate failure, 2 invalid input/error. The optional JSON report is written atomically and cannot overwrite fixture or observation inputs.

CI automatically runs deterministic scorer unit tests without model calls. Actual provider behavioral evaluations require an explicit maintainer run and are not included in the CI accuracy claim.

## Maintainer rule

When adding a stable skill, add at least two realistic activation cases. When tightening a description, add a regression case for wording that previously failed or over-triggered.

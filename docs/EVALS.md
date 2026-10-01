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

## Maintainer rule

When adding a stable skill, add at least two realistic activation cases. When tightening a description, add a regression case for wording that previously failed or over-triggered.

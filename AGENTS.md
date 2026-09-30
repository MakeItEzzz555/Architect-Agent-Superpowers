# Repository Agent Instructions

This repository maintains portable architecture/AEC Agent Skills and provider adapters.

## Priorities
- Keep canonical portable skills in `skills/<name>/SKILL.md`.
- Keep provider-specific behavior thin; do not fork domain logic unnecessarily.
- Treat token/context efficiency as a feature.
- Preserve beginner-first installation paths and documentation.
- Never claim architectural, planning, structural, fire, accessibility, legal, or construction compliance without authoritative evidence and appropriate human review.
- Verify provider formats against current official documentation before changing manifests, install locations, or agent schemas.
- Keep Claude plugin skill copies synchronized with canonical `skills/`; CI must fail on drift.
- Prefer additive, backward-compatible changes.
- Run `python3 tests/check_repo.py` before committing repository changes.

## Release discipline
For substantial changes, update CHANGELOG.md and relevant docs. Keep versions synchronized across provider manifests.

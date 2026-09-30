# Contributing

Contributions are welcome from architects, students, BIM specialists, engineers, visualization artists, and agent-tool developers.

## Principles
1. Keep domain workflows provider-neutral where possible.
2. Add a new skill only when it has a distinct trigger, workflow, and output.
3. Put enduring domain logic in `skills/`; keep provider adapters thin.
4. Cite authoritative sources in regulation-specific reference packs.
5. Never encode unverified jurisdictional requirements as universal rules.
6. Avoid prompts that demand hidden chain-of-thought.
7. Prefer deterministic scripts for arithmetic, validation, and repetitive transformations.
8. Include approval/stop boundaries for destructive operations.

## Before a PR
```bash
python3 scripts/sync-provider-skills.py --check
python3 tests/check_repo.py
```

See ROADMAP.md for contribution ideas.

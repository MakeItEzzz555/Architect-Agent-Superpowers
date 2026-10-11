# Changelog

## 0.2.0 - 2026-10-09
- Added the provider-neutral `revit-workflow` skill for Revit, pyRevit, Dynamo, and Revit API tasks with explicit dry-run, transaction, worksharing, verification, and rollback guidance.
- Added Revit-specific routing plus activation regression cases while preserving generic IFC/DWG/DXF/SVG work under `cad-bim-automation`.
- Made global installers discover canonical skills and agents dynamically so future additions do not require hard-coded installer lists.
- Made Linux and Windows CI installer smoke tests derive expected skill/agent counts dynamically.
- Added `scripts/validate-native.sh` with safe Claude strict validation, isolated Codex marketplace/plugin installation, and Gemini extension validation when each CLI is available.
- Documented the maintainer native-validation path and marked the first Revit workflow milestone complete.

## 0.1.1 - 2026-10-01
- Modernized the portable OpenAI plugin manifest to the current Agent Plugins layout and metadata.
- Added a native repo marketplace for verified two-command Codex plugin installation.
- Made Claude plugin components explicit and added strict manifest-validation compatibility.
- Added bounded turn/time budgets to Claude and Gemini specialist subagents.
- Added beginner-safe `auto` runtime detection to global installers while preserving explicit/all targets.
- Added canonical skill registry, provider-neutral activation eval cases, eval documentation, and stronger CI contract checks.
- Added Linux and Windows installer smoke-test jobs to CI.
- Updated GitHub Actions to the current Node 24 generations (`checkout@v7`, `setup-python@v7`).
- Added update instructions for clone installs, Claude plugins, and Gemini extensions.
- Corrected Codex documentation to avoid unnecessary global AGENTS.md routing context.

## 0.1.0 - 2026-10-01
- Initial public repository.
- Nine portable architecture/AEC Agent Skills.
- Beginner-first ZIP and CLI guidance.
- Codex user-scoped installation adapter.
- Claude Code marketplace/plugin adapter with specialist subagents.
- Gemini CLI extension adapter with specialist subagents.
- Provider-neutral global-adoption prompt and project template.
- Repository validation and provider-sync tooling.

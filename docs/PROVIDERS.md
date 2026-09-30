# Provider Support

## OpenAI Codex
Canonical skills install to the current user's Codex skill directory. The installer can add a small marked routing block to global Codex instructions while preserving existing content.

## Claude Code
Claude Code supports personal skills, user-level subagents, and plugins. This repository is a Claude marketplace whose plugin lives in `providers/claude`.

## Gemini CLI
The repository root is a Gemini CLI extension. Gemini discovers root `skills/` and `agents/` components. Canonical skills can also be copied into user scope.

## Other agents
Canonical `skills/<name>/SKILL.md` directories follow the open Agent Skills pattern: YAML frontmatter plus Markdown instructions. Compatible tools can import or copy these directories.

Provider adapters may add subagents, manifests, hooks, policies, or MCP integrations, but reusable architecture knowledge belongs in the canonical skills.

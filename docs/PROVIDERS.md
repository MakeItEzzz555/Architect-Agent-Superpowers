# Provider Support

## OpenAI Codex

Native plugin install:

```bash
codex plugin marketplace add MakeItEzzz555/Architect-Agent-Superpowers
codex plugin add architect-agent-superpowers@architect-agent-superpowers
```

The direct installer copies canonical skills into the current user's Codex skill directory. It deliberately does not add permanent routing prose to global AGENTS.md; skill metadata is sufficient for discovery and avoids extra always-on context.

## Claude Code
Claude Code supports personal skills, user-level subagents, and plugins. This repository is a Claude marketplace whose plugin lives in `providers/claude`.

## Gemini CLI
The repository root is a Gemini CLI extension. Gemini discovers root `skills/` and `agents/` components. Canonical skills can also be copied into user scope.

## Other agents
Canonical `skills/<name>/SKILL.md` directories follow the open Agent Skills pattern: YAML frontmatter plus Markdown instructions. Compatible tools can import or copy these directories.

Provider adapters may add subagents, manifests, hooks, policies, or MCP integrations, but reusable architecture knowledge belongs in the canonical skills.


## Versioning and updates

All provider manifests share one repository version. See [UPDATING.md](UPDATING.md) for provider-native update commands.
